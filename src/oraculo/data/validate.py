"""Contratos de dados: se o dado estiver errado, o pipeline para aqui."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors

from oraculo.config import argumentos_cli, carregar_config, pasta_dados
from oraculo.data.generate import eixo_horas

log = logging.getLogger(__name__)

RATING_MAX = 100.0


class ErroContratoDados(ValueError):
    """Violação de uma regra que depende de mais de uma linha ou tabela."""


def _schema_audiencia(cfg: dict[str, Any]) -> pa.DataFrameSchema:
    dados = cfg["dados"]
    horas = [float(h) for h in eixo_horas(dados)]
    return pa.DataFrameSchema(
        {
            "data": pa.Column("datetime64[ns]", nullable=False),
            "hora": pa.Column(float, pa.Check.isin(horas), nullable=False),
            "emissora": pa.Column(str, pa.Check.isin(dados["emissoras"]), nullable=False),
            "publico": pa.Column(str, pa.Check.isin(dados["publicos"]), nullable=False),
            "rating": pa.Column(float, pa.Check.in_range(0.0, RATING_MAX), nullable=False),
            "share": pa.Column(float, pa.Check.in_range(0.0, RATING_MAX), nullable=False),
        },
        unique=["data", "hora", "emissora", "publico"],
        strict=True,
    )


def _schema_grade(cfg: dict[str, Any]) -> pa.DataFrameSchema:
    horas = [float(h) for h in eixo_horas(cfg["dados"])]
    texto = pa.Column(str, nullable=False)
    return pa.DataFrameSchema(
        {
            "data": pa.Column("datetime64[ns]", nullable=False),
            "hora": pa.Column(float, pa.Check.isin(horas), nullable=False),
            "dow": pa.Column(int, pa.Check.in_range(0, 6), nullable=False),
            "feriado": pa.Column(int, pa.Check.isin([0, 1]), nullable=False),
            "categoria": texto,
            "programa": texto,
            "categoria_conc_a": texto,
            "categoria_conc_b": texto,
        },
        unique=["data", "hora"],
        strict=True,
    )


def _exigir_dias_completos(audiencia: pd.DataFrame, blocos_por_dia: int) -> None:
    """Cada dia × série precisa ter todos os blocos: os lags em SQL contam linhas."""
    blocos = audiencia.groupby(["data", "emissora", "publico"], observed=True)["hora"].nunique()
    incompletos = blocos[blocos != blocos_por_dia]
    if not incompletos.empty:
        raise ErroContratoDados(
            f"{len(incompletos)} combinações dia × série sem {blocos_por_dia} blocos: {incompletos.head(3).to_dict()}"
        )


def _exigir_datas_continuas(datas: pd.Series, nome: str) -> None:
    unicas = pd.DatetimeIndex(datas.drop_duplicates().sort_values())
    esperado = pd.date_range(unicas.min(), unicas.max(), freq="D")
    faltando = esperado.difference(unicas)
    if len(faltando):
        raise ErroContratoDados(f"{nome}: {len(faltando)} datas faltando, a primeira é {faltando[0].date()}")


def validar_audiencia(audiencia: pd.DataFrame, cfg: dict[str, Any], nome: str = "audiencia") -> None:
    _schema_audiencia(cfg).validate(audiencia, lazy=True)
    _exigir_dias_completos(audiencia, cfg["dados"]["blocos_por_dia"])
    _exigir_datas_continuas(audiencia["data"], nome)


def validar_grade(grade: pd.DataFrame, cfg: dict[str, Any]) -> None:
    _schema_grade(cfg).validate(grade, lazy=True)
    _exigir_datas_continuas(grade["data"], "grade")


def validar_relacoes(audiencia: pd.DataFrame, grade: pd.DataFrame) -> None:
    """Todo dia com audiência precisa ter grade."""
    sem_grade = np.setdiff1d(audiencia["data"].unique(), grade["data"].unique())
    if len(sem_grade):
        raise ErroContratoDados(f"{len(sem_grade)} dias com audiência sem grade")


def validar(cfg: dict[str, Any]) -> None:
    """Valida todas as tabelas de `data/raw`. Levanta exceção na primeira regra violada."""
    pasta = pasta_dados(cfg) / "raw"
    audiencia = pd.read_parquet(pasta / "audiencia.parquet")
    chegada = pd.read_parquet(pasta / "audiencia_chegada.parquet")
    grade = pd.read_parquet(pasta / "grade.parquet")
    validar_audiencia(audiencia, cfg)
    validar_audiencia(chegada, cfg, "audiencia_chegada")
    validar_grade(grade, cfg)
    validar_relacoes(pd.concat([audiencia, chegada]), grade)
    log.info(
        "Contratos OK: %d linhas de audiência, %d de chegada, %d de grade", len(audiencia), len(chegada), len(grade)
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argumentos = argumentos_cli("Valida os contratos de dados").parse_args()
    try:
        validar(carregar_config(argumentos.config))
    except SchemaErrors as erro:
        log.error("Contrato violado:\n%s", erro.failure_cases.head(20))
        raise SystemExit(1) from erro


if __name__ == "__main__":
    main()
