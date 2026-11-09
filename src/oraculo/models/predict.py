"""Previsão em lote: o comercial planeja por semana, então uma tabela semanal basta."""

from __future__ import annotations

import logging
from typing import Any

import mlflow.pyfunc
import pandas as pd

from oraculo.config import argumentos_cli, carregar_config, pasta_dados
from oraculo.features.build import VARIAVEIS_MODELO
from oraculo.models.registro import configurar_mlflow, uri_campeao, versao_campea

log = logging.getLogger(__name__)

CASAS_DECIMAIS = 3


def montar_resumo_comercial(previsoes: pd.DataFrame) -> pd.DataFrame:
    """Semana × faixa do programa × público. Média dos blocos: a linguagem de quem vende."""
    tabela = previsoes.assign(semana=previsoes["data"].dt.to_period("W-SUN").dt.start_time.dt.date)
    resumo = (
        tabela.groupby(["semana", "faixa_programa", "publico"], observed=True)
        .agg(
            rating_previsto=("p50", "mean"),
            entrega_segura_p10=("p10", "mean"),
            cenario_otimista_p90=("p90", "mean"),
            blocos=("p50", "size"),
        )
        .reset_index()
    )
    colunas = ["rating_previsto", "entrega_segura_p10", "cenario_otimista_p90"]
    resumo[colunas] = resumo[colunas].round(2)
    return resumo


def prever(cfg: dict[str, Any]) -> pd.DataFrame:
    """Carrega o champion do Registry e prevê os próximos 28 dias."""
    cliente = configurar_mlflow(cfg)
    campea = versao_campea(cliente, cfg)
    if campea is None:
        raise RuntimeError("Não existe modelo champion: rode o treino e passe pela porta de qualidade.")
    modelo = mlflow.pyfunc.load_model(uri_campeao(cfg))

    raiz = pasta_dados(cfg)
    features = pd.read_parquet(raiz / "features" / "features.parquet")
    fim_historico = pd.Timestamp(cfg["dados"]["fim_historico"])
    limite = fim_historico + pd.Timedelta(days=cfg["horizonte_dias"])
    futuro = features[(features["data"] > fim_historico) & (features["data"] <= limite)].reset_index(drop=True)

    faixa = modelo.predict(futuro[VARIAVEIS_MODELO])
    previsoes = futuro[["data", "hora", "publico", "programa", "categoria", "faixa_programa"]].copy()
    previsoes[["p10", "p50", "p90"]] = faixa[["p10", "p50", "p90"]].round(CASAS_DECIMAIS).to_numpy()
    previsoes["versao_modelo"] = str(campea.version)
    previsoes["data_previsao"] = fim_historico

    destino = raiz / "outputs"
    destino.mkdir(parents=True, exist_ok=True)
    previsoes.to_parquet(destino / "previsoes_bloco.parquet", index=False)
    previsoes.to_csv(destino / "previsoes_bloco.csv", index=False)
    resumo = montar_resumo_comercial(previsoes)
    resumo.to_csv(destino / "resumo_comercial.csv", index=False)
    log.info(
        "Previsão em lote: %d blocos, %d linhas no resumo, modelo v%s", len(previsoes), len(resumo), campea.version
    )
    return previsoes


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argumentos = argumentos_cli("Gera a previsão em lote").parse_args()
    prever(carregar_config(argumentos.config))


if __name__ == "__main__":
    main()
