"""Monitoramento: previsto × real quando a audiência chega, e drift (PSI) das variáveis."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

import numpy as np
import pandas as pd

from oraculo.config import argumentos_cli, carregar_config, pasta_dados
from oraculo.models.evaluate import cobertura, filtrar_horario_nobre, largura_media, vies, wape

log = logging.getLogger(__name__)

VARIAVEIS_PSI_NUMERICAS = ["lag_28", "media_4sem", "tle_lag_28"]
VARIAVEIS_PSI_CATEGORICAS = ["categoria_conc_b"]


def _psi(proporcao_ref: np.ndarray, proporcao_atual: np.ndarray, epsilon: float) -> float:
    ref = np.clip(proporcao_ref, epsilon, None)
    atual = np.clip(proporcao_atual, epsilon, None)
    return float(np.sum((atual - ref) * np.log(atual / ref)))


def psi_numerico(referencia: pd.Series, atual: pd.Series, faixas: int = 10, epsilon: float = 1e-4) -> float:
    """Compara o formato de duas distribuições, com faixas pelos quantis da referência."""
    ref = pd.Series(referencia).dropna().to_numpy()
    agora = pd.Series(atual).dropna().to_numpy()
    cortes = np.unique(np.quantile(ref, np.linspace(0, 1, faixas + 1)))
    cortes[0], cortes[-1] = -np.inf, np.inf
    contagem_ref = np.histogram(ref, bins=cortes)[0]
    contagem_atual = np.histogram(agora, bins=cortes)[0]
    return _psi(contagem_ref / len(ref), contagem_atual / len(agora), epsilon)


def psi_categorico(referencia: pd.Series, atual: pd.Series, epsilon: float = 1e-4) -> float:
    """PSI para variáveis categóricas, com uma faixa por categoria."""
    ref = pd.Series(referencia).astype(str).value_counts(normalize=True)
    agora = pd.Series(atual).astype(str).value_counts(normalize=True)
    categorias = ref.index.union(agora.index)
    return _psi(
        ref.reindex(categorias, fill_value=0).to_numpy(), agora.reindex(categorias, fill_value=0).to_numpy(), epsilon
    )


def classificar_psi(valor: float, cfg: dict[str, Any]) -> str:
    limites = cfg["monitoramento"]
    if valor > limites["psi_alerta"]:
        return "mudou"
    return "atenção" if valor >= limites["psi_atencao"] else "estável"


def _desempenho(tabela: pd.DataFrame) -> dict[str, float]:
    return {
        "wape": wape(tabela["rating"], tabela["p50"]),
        "vies": vies(tabela["rating"], tabela["p50"]),
        "cobertura": cobertura(tabela["rating"], tabela["p10"], tabela["p90"]),
        "largura_media": largura_media(tabela["p10"], tabela["p90"]),
    }


def calcular_drift(features: pd.DataFrame, chegada: pd.DataFrame, cfg: dict[str, Any]) -> dict[str, float]:
    """PSI entre os últimos dias do treino e o período previsto."""
    fim = pd.Timestamp(cfg["dados"]["fim_historico"])
    inicio_ref = fim - pd.Timedelta(days=cfg["monitoramento"]["dias_referencia"])
    referencia = features[(features["data"] > inicio_ref) & (features["data"] <= fim)]
    atual = features[(features["data"] > fim) & (features["data"].isin(chegada["data"].unique()))]
    faixas = cfg["monitoramento"]["faixas_psi"]
    epsilon = cfg["monitoramento"]["psi_epsilon"]
    resultado = {v: psi_numerico(referencia[v], atual[v], faixas, epsilon) for v in VARIAVEIS_PSI_NUMERICAS}
    resultado.update({v: psi_categorico(referencia[v], atual[v], epsilon) for v in VARIAVEIS_PSI_CATEGORICAS})
    resultado["rating_real"] = psi_numerico(referencia["rating"], chegada["rating"], faixas, epsilon)
    return resultado


def avaliar_alertas(geral: dict[str, float], drift: dict[str, float], cfg: dict[str, Any]) -> list[str]:
    limites = cfg["monitoramento"]
    alertas = []
    if geral["wape"] > limites["wape_alerta"]:
        alertas.append(f"WAPE de {geral['wape']:.1%} acima do limite de {limites['wape_alerta']:.0%}")
    if geral["cobertura"] < limites["cobertura_min"]:
        alertas.append(f"Cobertura de {geral['cobertura']:.1%} abaixo do mínimo de {limites['cobertura_min']:.0%}")
    for variavel, valor in drift.items():
        if valor > limites["psi_alerta"]:
            alertas.append(f"Drift em {variavel}: PSI {valor:.2f} acima de {limites['psi_alerta']}")
    return alertas


def _texto_relatorio(resultado: dict[str, Any]) -> str:
    geral = resultado["geral"]
    nobre = resultado["horario_nobre"]
    linhas = [
        f"# Monitoramento do modelo: {resultado['status']}",
        "",
        "> Dados sintéticos. O choque simulado não aparece em nenhuma variável do modelo.",
        "",
        f"Versão do modelo: {resultado['versao_modelo']}. Período: {resultado['periodo'][0]} a {resultado['periodo'][1]}.",
        "",
        "## Desempenho",
        "",
        "| Recorte | WAPE | Viés (pontos) | Cobertura | Largura (pontos) |",
        "| --- | --- | --- | --- | --- |",
        f"| Geral | {geral['wape']:.1%} | {geral['vies']:+.2f} | {geral['cobertura']:.1%} | {geral['largura_media']:.2f} |",
        f"| Horário nobre | {nobre['wape']:.1%} | {nobre['vies']:+.2f} | {nobre['cobertura']:.1%} | {nobre['largura_media']:.2f} |",
    ]
    if resultado["wape_esperado_backtest"] is not None:
        linhas += ["", f"WAPE esperado pelo backtest: {resultado['wape_esperado_backtest']:.1%}."]
    linhas += ["", "## Por semana", "", "| Semana | WAPE | Viés (pontos) | Cobertura |", "| --- | --- | --- | --- |"]
    for semana in resultado["por_semana"]:
        linhas.append(
            f"| {semana['semana']} | {semana['wape']:.1%} | {semana['vies']:+.2f} | {semana['cobertura']:.1%} |"
        )
    linhas += ["", "## Drift (PSI)", "", "| Variável | PSI | Leitura |", "| --- | --- | --- |"]
    for variavel, valor in resultado["drift"].items():
        linhas.append(f"| {variavel} | {valor:.3f} | {resultado['drift_leitura'][variavel]} |")
    linhas += ["", "## Alertas", ""]
    linhas += [f"- {alerta}" for alerta in resultado["alertas"]] or ["Nenhum alerta."]
    return "\n".join(linhas) + "\n"


def monitorar(cfg: dict[str, Any]) -> dict[str, Any]:
    """Compara o previsto com o real que chegou e grava o relatório."""
    raiz = pasta_dados(cfg)
    previsoes = pd.read_parquet(raiz / "outputs" / "previsoes_bloco.parquet")
    chegada_bruta = pd.read_parquet(raiz / "raw" / "audiencia_chegada.parquet")
    chegada = chegada_bruta[chegada_bruta["emissora"] == "principal"][["data", "hora", "publico", "rating"]]
    tabela = previsoes.merge(chegada, on=["data", "hora", "publico"], how="inner")
    if tabela.empty:
        raise RuntimeError("Nenhuma audiência real chegou para o período previsto.")

    features = pd.read_parquet(raiz / "features" / "features.parquet")
    geral = _desempenho(tabela)
    nobre = _desempenho(filtrar_horario_nobre(tabela, cfg["modelo"]["horario_nobre"]))
    por_semana = [
        {"semana": str(semana.date()), **_desempenho(parte)}
        for semana, parte in tabela.groupby(tabela["data"].dt.to_period("W-SUN").dt.start_time)
    ]
    drift = calcular_drift(features, chegada, cfg)
    alertas = avaliar_alertas(geral, drift, cfg)

    caminho_treino = raiz / "relatorios" / "relatorio_treino.json"
    esperado = None
    if caminho_treino.exists():
        esperado = json.loads(caminho_treino.read_text(encoding="utf-8"))["backtest_geral"]["wape"]

    resultado = {
        "status": "ALERTA" if alertas else "OK",
        "versao_modelo": str(previsoes["versao_modelo"].iloc[0]),
        "periodo": [str(tabela["data"].min().date()), str(tabela["data"].max().date())],
        "wape_esperado_backtest": esperado,
        "geral": geral,
        "horario_nobre": nobre,
        "por_semana": por_semana,
        "drift": drift,
        "drift_leitura": {variavel: classificar_psi(valor, cfg) for variavel, valor in drift.items()},
        "alertas": alertas,
    }
    destino = raiz / "relatorios"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "monitoramento.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    (destino / "monitoramento.md").write_text(_texto_relatorio(resultado), encoding="utf-8")
    log.info(
        "Monitoramento: %s | WAPE %.1f%% | viés %+.2f | cobertura %.1f%%",
        resultado["status"],
        100 * geral["wape"],
        geral["vies"],
        100 * geral["cobertura"],
    )
    for alerta in alertas:
        log.warning("ALERTA: %s", alerta)
    return resultado


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argumentos_cli("Monitora o modelo em produção")
    parser.add_argument("--falhar-em-alerta", action="store_true", help="sai com erro se houver alerta")
    argumentos = parser.parse_args()
    resultado = monitorar(carregar_config(argumentos.config))
    if argumentos.falhar_em_alerta and resultado["status"] == "ALERTA":
        sys.exit(1)


if __name__ == "__main__":
    main()
