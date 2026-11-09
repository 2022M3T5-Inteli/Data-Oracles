"""Treino: backtest temporal contra o baseline, faixa calibrada e explicabilidade."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import lightgbm as lgb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from oraculo.config import argumentos_cli, carregar_config, pasta_dados  # noqa: E402
from oraculo.features.build import VARIAVEIS_MODELO, preparar_categoricas  # noqa: E402
from oraculo.models.evaluate import (  # noqa: E402
    aplicar_conformal,
    calibrar_conformal,
    cobertura,
    filtrar_horario_nobre,
    largura_media,
    metricas_por,
    metricas_previsao,
    r2,
    wape,
)
from oraculo.models.pyfunc import NOMES_QUANTIS, prever_boosters  # noqa: E402

log = logging.getLogger(__name__)

COR_BARRA = "#2a78d6"
COR_TEXTO = "#52514e"
COR_GRADE = "#E4E4E4"


def carregar_base(cfg: dict[str, Any]) -> pd.DataFrame:
    """Linhas com alvo e baseline conhecidos, com categóricas prontas para o LightGBM."""
    tabela = pd.read_parquet(pasta_dados(cfg) / "features" / "features.parquet")
    tabela = preparar_categoricas(tabela)
    return tabela[tabela[cfg["modelo"]["alvo"]].notna() & tabela["media_4sem"].notna()].reset_index(drop=True)


def treinar_quantil(x: pd.DataFrame, y: pd.Series, alpha: float, cfg: dict[str, Any]) -> lgb.Booster:
    parametros = dict(cfg["modelo"]["lgbm"])
    modelo = lgb.LGBMRegressor(objective="quantile", alpha=alpha, random_state=cfg["seed"], **parametros)
    modelo.fit(x, y)
    return modelo.booster_


def treinar_quantis(x: pd.DataFrame, y: pd.Series, cfg: dict[str, Any]) -> dict[str, lgb.Booster]:
    return {nome: treinar_quantil(x, y, cfg["modelo"]["quantis"][nome], cfg) for nome in NOMES_QUANTIS}


def executar_backtest(base: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Em cada corte: treina até a data e testa os 28 dias seguintes, como o comercial usaria."""
    horizonte = pd.Timedelta(days=cfg["horizonte_dias"])
    alvo = cfg["modelo"]["alvo"]
    partes = []
    for corte_config in cfg["modelo"]["backtest"]["cortes"]:
        corte = pd.Timestamp(corte_config)
        treino = base[base["data"] <= corte]
        teste = base[(base["data"] > corte) & (base["data"] <= corte + horizonte)]
        boosters = treinar_quantis(treino[VARIAVEIS_MODELO], treino[alvo], cfg)
        previsoes = prever_boosters(boosters, teste)
        parte = teste[["data", "hora", "publico", "programa", alvo, "media_4sem"]].copy()
        parte = parte.rename(columns={alvo: "rating", "media_4sem": "baseline"})
        parte["corte"] = corte
        parte["publico"] = parte["publico"].astype(str)
        parte["p10"], parte["p50"], parte["p90"] = previsoes[:, 0], previsoes[:, 1], previsoes[:, 2]
        partes.append(parte)
        log.info(
            "Corte %s: WAPE modelo %.1f%% | baseline %.1f%%",
            corte.date(),
            100 * wape(parte["rating"], parte["p50"]),
            100 * wape(parte["rating"], parte["baseline"]),
        )
    return pd.concat(partes, ignore_index=True)


def medir_conformal(backtest: pd.DataFrame, nivel: float) -> dict[str, float]:
    """Medição honesta: calibra com os cortes anteriores e mede no último."""
    ultimo = backtest["corte"].max()
    calibracao = backtest[backtest["corte"] < ultimo]
    avaliacao = backtest[backtest["corte"] == ultimo]
    ajustes = calibrar_conformal(calibracao, nivel)
    p10, p90 = aplicar_conformal(avaliacao["p10"], avaliacao["p90"], avaliacao["publico"].to_numpy(), ajustes)
    return {
        "cobertura_antes": cobertura(avaliacao["rating"], avaliacao["p10"], avaliacao["p90"]),
        "cobertura_depois": cobertura(avaliacao["rating"], p10, p90),
        "largura_antes": largura_media(avaliacao["p10"], avaliacao["p90"]),
        "largura_depois": largura_media(p10, p90),
    }


def comparar_split_aleatorio(base: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, float]:
    """Repete o erro de 2022: sortear linhas de treino e teste. Serve de prova numérica."""
    alvo = cfg["modelo"]["alvo"]
    treino, teste = train_test_split(
        base, test_size=cfg["modelo"]["split_aleatorio"]["proporcao_teste"], random_state=cfg["seed"]
    )
    booster = treinar_quantil(treino[VARIAVEIS_MODELO], treino[alvo], cfg["modelo"]["quantis"]["p50"], cfg)
    previsto = np.clip(booster.predict(teste[VARIAVEIS_MODELO]), 0.0, None)
    return {"wape": wape(teste[alvo], previsto), "r2": r2(teste[alvo], previsto)}


def importancia_shap(booster: lgb.Booster, base: pd.DataFrame, cfg: dict[str, Any]) -> pd.DataFrame:
    """Média de |contribuição| de cada variável, em pontos de rating."""
    tamanho = min(cfg["modelo"]["shap"]["amostra"], len(base))
    amostra = base.sample(tamanho, random_state=cfg["seed"])[VARIAVEIS_MODELO]
    contribuicoes = booster.predict(amostra, pred_contrib=True)[:, :-1]
    tabela = pd.DataFrame({"variavel": VARIAVEIS_MODELO, "shap_medio_pontos": np.abs(contribuicoes).mean(axis=0)})
    return tabela.sort_values("shap_medio_pontos", ascending=False).reset_index(drop=True)


def grafico_shap(importancia: pd.DataFrame, destino: Path, top: int) -> None:
    dados = importancia.head(top).iloc[::-1]
    figura, eixo = plt.subplots(figsize=(8, 5.2), dpi=150)
    eixo.barh(dados["variavel"], dados["shap_medio_pontos"], height=0.55, color=COR_BARRA)
    maximo = dados["shap_medio_pontos"].max()
    for posicao, valor in enumerate(dados["shap_medio_pontos"]):
        eixo.text(
            valor + maximo * 0.012, posicao, f"{valor:.2f}".replace(".", ","), va="center", fontsize=8, color=COR_TEXTO
        )
    eixo.set_title("O que mais move a previsão de rating (dados sintéticos)", loc="left", fontsize=11, color=COR_TEXTO)
    eixo.set_xlabel("Contribuição média absoluta, em pontos de rating", fontsize=9, color=COR_TEXTO)
    eixo.tick_params(axis="both", length=0, labelsize=8.5, colors=COR_TEXTO)
    eixo.grid(axis="x", color=COR_GRADE, linewidth=0.8)
    eixo.set_axisbelow(True)
    for lado in ("top", "right", "bottom", "left"):
        eixo.spines[lado].set_visible(False)
    figura.tight_layout()
    figura.savefig(destino)
    plt.close(figura)


def montar_relatorio(backtest: pd.DataFrame, cfg: dict[str, Any], aleatorio: dict[str, float]) -> dict[str, Any]:
    nivel = cfg["modelo"]["nivel_faixa"]
    nobre = filtrar_horario_nobre(backtest, cfg["modelo"]["horario_nobre"])
    return {
        "aviso": "Resultados sobre dados SINTÉTICOS.",
        "fim_historico": str(cfg["dados"]["fim_historico"]),
        "horizonte_dias": cfg["horizonte_dias"],
        "backtest_geral": metricas_previsao(backtest),
        "backtest_horario_nobre": metricas_previsao(nobre),
        "backtest_por_corte": metricas_por(backtest.assign(corte=backtest["corte"].astype(str)), "corte").to_dict(
            "records"
        ),
        "conformal": medir_conformal(backtest, nivel),
        "split_aleatorio": aleatorio,
    }


def treinar(cfg: dict[str, Any]) -> dict[str, Any]:
    """Executa a avaliação completa, treina o modelo final e grava os relatórios."""
    raiz = pasta_dados(cfg)
    pasta_relatorios = raiz / "relatorios"
    pasta_modelo = raiz / "modelo"
    pasta_relatorios.mkdir(parents=True, exist_ok=True)
    pasta_modelo.mkdir(parents=True, exist_ok=True)

    base = carregar_base(cfg)
    log.info("Base de treino: %d linhas", len(base))
    backtest = executar_backtest(base, cfg)
    aleatorio = comparar_split_aleatorio(base, cfg)
    relatorio = montar_relatorio(backtest, cfg, aleatorio)

    log.info("Treinando o modelo final com todo o histórico...")
    alvo = cfg["modelo"]["alvo"]
    boosters = treinar_quantis(base[VARIAVEIS_MODELO], base[alvo], cfg)
    ajustes = calibrar_conformal(backtest, cfg["modelo"]["nivel_faixa"])
    importancia = importancia_shap(boosters["p50"], base, cfg)
    relatorio["top_variaveis_shap"] = importancia.head(cfg["modelo"]["shap"]["top"]).to_dict("records")

    for nome, booster in boosters.items():
        booster.save_model(str(pasta_modelo / f"{nome}.txt"))
    arquivos = {
        "relatorio": pasta_relatorios / "relatorio_treino.json",
        "por_publico": pasta_relatorios / "metricas_por_publico.csv",
        "shap_csv": pasta_relatorios / "shap_importancia.csv",
        "shap_png": pasta_relatorios / "shap_importancia.png",
        "backtest": pasta_relatorios / "backtest_previsoes.parquet",
        "conformal": pasta_modelo / "ajuste_conformal.json",
    }
    arquivos["relatorio"].write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    metricas_por(backtest, "publico").to_csv(arquivos["por_publico"], index=False)
    importancia.to_csv(arquivos["shap_csv"], index=False)
    grafico_shap(importancia, arquivos["shap_png"], cfg["modelo"]["shap"]["top"])
    backtest.to_parquet(arquivos["backtest"], index=False)
    arquivos["conformal"].write_text(json.dumps(ajustes, ensure_ascii=False, indent=2), encoding="utf-8")

    geral = relatorio["backtest_geral"]
    log.info(
        "Backtest: WAPE %.1f%% (baseline %.1f%%) | MAE %.2f ponto | viés %+.2f | cobertura %.1f%%",
        100 * geral["wape"],
        100 * geral["wape_baseline"],
        geral["mae"],
        geral["vies"],
        100 * geral["cobertura"],
    )
    log.info("Split aleatório (como em 2022): WAPE %.1f%% | R² %.3f", 100 * aleatorio["wape"], aleatorio["r2"])
    return relatorio


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argumentos = argumentos_cli("Treina e avalia o modelo").parse_args()
    treinar(carregar_config(argumentos.config))


if __name__ == "__main__":
    main()
