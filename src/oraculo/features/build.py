"""Base analítica em SQL (DuckDB).

Regra de ouro: a previsão é feita 28 dias antes. Toda variável de histórico olha pelo menos
`horizonte_dias` para trás. Variáveis de grade são permitidas, porque a grade é planejada.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from oraculo.config import argumentos_cli, carregar_config, pasta_dados

log = logging.getLogger(__name__)

# Definição das variáveis: múltiplos de 7 dias preservam o dia da semana.
DIAS_EM_SEMANA = 7
DIAS_JANELA_NIVEL = 28
DIAS_LAG_ANUAL = 364

VARIAVEIS_HISTORICO = [
    "lag_28",
    "lag_35",
    "lag_42",
    "lag_49",
    "lag_364",
    "media_4sem",
    "media_hora_28_56",
    "tle_lag_28",
]
VARIAVEIS_NUMERICAS = [
    "hora",
    "dow",
    "mes",
    "dia_ano",
    "feriado",
    "fim_de_semana",
    "tendencia_dias",
    "dias_desde_estreia",
    *VARIAVEIS_HISTORICO,
]
VARIAVEIS_CATEGORICAS = ["categoria", "faixa_programa", "categoria_conc_a", "categoria_conc_b", "publico"]
VARIAVEIS_MODELO = VARIAVEIS_NUMERICAS + VARIAVEIS_CATEGORICAS


def consulta_features(horizonte: int, max_dias_estreia: int) -> str:
    """Monta o SQL. Como a grade é completa (contrato), LAG(x, 28) é exatamente 28 dias antes."""
    # Os nomes seguem o horizonte padrão de 28 dias; o deslocamento real vem sempre da configuração.
    nomes_lag = ["lag_28", "lag_35", "lag_42", "lag_49"]
    colunas_lag = ",\n        ".join(
        f"LAG(rating, {horizonte + DIAS_EM_SEMANA * passo}) OVER serie AS {nome}"
        for passo, nome in enumerate(nomes_lag)
    )
    soma_lags = " + ".join(nomes_lag)
    fim_janela = horizonte + DIAS_JANELA_NIVEL
    return f"""
    WITH publicos AS (
        SELECT DISTINCT publico FROM audiencia WHERE emissora = 'principal'
    ),
    base AS (
        SELECT g.*, p.publico
        FROM grade g
        CROSS JOIN publicos p
    ),
    unida AS (
        SELECT b.*, a.rating, t.tle
        FROM base b
        LEFT JOIN audiencia a
          ON a.emissora = 'principal' AND a.data = b.data AND a.hora = b.hora AND a.publico = b.publico
        LEFT JOIN tle t
          ON t.data = b.data AND t.hora = b.hora
    ),
    com_janelas AS (
        SELECT
            *,
            {colunas_lag},
            LAG(rating, {DIAS_LAG_ANUAL}) OVER serie AS lag_364,
            AVG(rating) OVER (serie ROWS BETWEEN {fim_janela} PRECEDING AND {horizonte} PRECEDING) AS media_hora_28_56,
            LAG(tle, {horizonte}) OVER serie AS tle_lag_28
        FROM unida
        WINDOW serie AS (PARTITION BY publico, hora ORDER BY data)
    )
    SELECT
        data,
        hora,
        publico,
        programa,
        dow,
        feriado,
        CAST(dow >= 5 AS INTEGER) AS fim_de_semana,
        MONTH(data) AS mes,
        DAYOFYEAR(data) AS dia_ano,
        DATE_DIFF('day', MIN(data) OVER (), data) AS tendencia_dias,
        LEAST(DATE_DIFF('day', MIN(data) OVER (PARTITION BY programa), data), {max_dias_estreia}) AS dias_desde_estreia,
        categoria,
        REGEXP_REPLACE(programa, '_E[0-9]+$', '') AS faixa_programa,
        categoria_conc_a,
        categoria_conc_b,
        lag_28, lag_35, lag_42, lag_49, lag_364,
        ({soma_lags}) / {len(nomes_lag)}.0 AS media_4sem,
        media_hora_28_56,
        tle_lag_28,
        rating
    FROM com_janelas
    ORDER BY data, hora, publico
    """


def montar_features(
    audiencia: pd.DataFrame, grade: pd.DataFrame, tle: pd.DataFrame, horizonte: int, max_dias_estreia: int
) -> pd.DataFrame:
    """Executa o SQL sobre as tabelas em memória."""
    conexao = duckdb.connect(":memory:")
    try:
        conexao.register("audiencia", audiencia)
        conexao.register("grade", grade)
        conexao.register("tle", tle)
        tabela = conexao.execute(consulta_features(horizonte, max_dias_estreia)).df()
    finally:
        conexao.close()
    tabela["data"] = pd.to_datetime(tabela["data"])
    return tabela


def preparar_categoricas(tabela: pd.DataFrame) -> pd.DataFrame:
    """Categóricas viram `category`: o LightGBM as trata sem one-hot."""
    tabela = tabela.copy()
    for coluna in VARIAVEIS_CATEGORICAS:
        tabela[coluna] = tabela[coluna].astype("category")
    return tabela


def construir(cfg: dict[str, Any]) -> pd.DataFrame:
    """Lê `data/raw`, constrói e grava `data/features/features.parquet`."""
    raiz: Path = pasta_dados(cfg)
    bruto = raiz / "raw"
    tabela = montar_features(
        pd.read_parquet(bruto / "audiencia.parquet"),
        pd.read_parquet(bruto / "grade.parquet"),
        pd.read_parquet(bruto / "tle.parquet"),
        cfg["horizonte_dias"],
        cfg["features"]["max_dias_estreia"],
    )
    destino = raiz / "features"
    destino.mkdir(parents=True, exist_ok=True)
    tabela.to_parquet(destino / "features.parquet", index=False)
    log.info("Features: %d linhas, %d variáveis do modelo", len(tabela), len(VARIAVEIS_MODELO))
    return tabela


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argumentos = argumentos_cli("Constrói a base analítica").parse_args()
    construir(carregar_config(argumentos.config))


if __name__ == "__main__":
    main()
