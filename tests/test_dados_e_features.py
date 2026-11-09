"""Contratos de dados aceitam dado bom e rejeitam dado ruim."""

from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaErrors

from oraculo.config import pasta_dados
from oraculo.data.generate import gerar
from oraculo.data.validate import ErroContratoDados, validar, validar_audiencia, validar_grade


def _audiencia(cfg):
    return pd.read_parquet(pasta_dados(cfg) / "raw" / "audiencia.parquet")


def test_contratos_aceitam_dados_gerados(dados_gerados):
    validar(dados_gerados)


def test_contrato_rejeita_rating_negativo(dados_gerados):
    audiencia = _audiencia(dados_gerados)
    audiencia.loc[0, "rating"] = -1.0
    with pytest.raises(SchemaErrors):
        validar_audiencia(audiencia, dados_gerados)


def test_contrato_rejeita_publico_desconhecido(dados_gerados):
    audiencia = _audiencia(dados_gerados)
    audiencia.loc[0, "publico"] = "marcianos"
    with pytest.raises(SchemaErrors):
        validar_audiencia(audiencia, dados_gerados)


def test_contrato_rejeita_chave_duplicada(dados_gerados):
    audiencia = _audiencia(dados_gerados)
    with pytest.raises(SchemaErrors):
        validar_audiencia(pd.concat([audiencia, audiencia.head(1)], ignore_index=True), dados_gerados)


def test_contrato_rejeita_dia_com_bloco_faltando(dados_gerados):
    audiencia = _audiencia(dados_gerados)
    with pytest.raises(ErroContratoDados):
        validar_audiencia(audiencia.drop(index=audiencia.index[0]), dados_gerados)


def test_contrato_rejeita_data_faltando(dados_gerados):
    audiencia = _audiencia(dados_gerados)
    datas = sorted(audiencia["data"].unique())
    with pytest.raises(ErroContratoDados):
        validar_audiencia(audiencia[audiencia["data"] != datas[10]], dados_gerados)


def test_contrato_de_grade_rejeita_dow_invalido(dados_gerados):
    grade = pd.read_parquet(pasta_dados(dados_gerados) / "raw" / "grade.parquet")
    grade.loc[0, "dow"] = 7
    with pytest.raises(SchemaErrors):
        validar_grade(grade, dados_gerados)


def test_gerador_e_reprodutivel(dados_gerados, tmp_path):
    copia = {**dados_gerados, "caminhos": {"dados": str(tmp_path)}}
    gerar(copia)
    pd.testing.assert_frame_equal(_audiencia(dados_gerados), _audiencia(copia))


def test_feriado_com_dia_menor_que_12_na_data_certa(dados_gerados):
    """Em 2022, dia e mês saíram trocados. 12/10 precisa ser outubro, não 10 de dezembro."""
    grade = pd.read_parquet(pasta_dados(dados_gerados) / "raw" / "grade.parquet")
    por_dia = grade.groupby("data")["feriado"].max()
