"""Contratos de dados aceitam dado bom e rejeitam dado ruim."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pandera.errors import SchemaErrors

from oraculo.config import pasta_dados
from oraculo.data.generate import gerar
from oraculo.data.validate import ErroContratoDados, validar, validar_audiencia, validar_grade
from oraculo.features.build import VARIAVEIS_HISTORICO, montar_features


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
    assert por_dia[pd.Timestamp("2024-10-12")] == 1
    assert por_dia[pd.Timestamp("2024-12-10")] == 0


# --- Features -------------------------------------------------------------------------------------


def _tabelas_brutas(cfg):
    pasta = pasta_dados(cfg) / "raw"
    return (
        pd.read_parquet(pasta / "audiencia.parquet"),
        pd.read_parquet(pasta / "grade.parquet"),
        pd.read_parquet(pasta / "tle.parquet"),
    )


def _montar(cfg, audiencia, grade, tle):
    return montar_features(audiencia, grade, tle, cfg["horizonte_dias"], cfg["features"]["max_dias_estreia"])


@pytest.fixture(scope="module")
def features_smoke(dados_gerados):
    return _montar(dados_gerados, *_tabelas_brutas(dados_gerados))


def test_uma_linha_por_dia_bloco_publico(features_smoke):
    assert not features_smoke.duplicated(["data", "hora", "publico"]).any()


def test_inclui_dias_futuros_sem_rating(features_smoke, dados_gerados):
    fim = pd.Timestamp(dados_gerados["dados"]["fim_historico"])
    futuro = features_smoke[features_smoke["data"] > fim]
    assert not futuro.empty
    assert futuro["rating"].isna().all()
    assert futuro["lag_28"].notna().all()


def test_lag_28_e_o_rating_de_28_dias_antes(features_smoke):
    alvo = features_smoke[(features_smoke["publico"] == "feminino") & (features_smoke["hora"] == 21.0)]
    linha = alvo[alvo["data"] == pd.Timestamp("2024-10-15")].iloc[0]
    anterior = alvo[alvo["data"] == pd.Timestamp("2024-10-15") - pd.Timedelta(days=28)].iloc[0]
    assert linha["lag_28"] == pytest.approx(anterior["rating"])


def test_media_4sem_e_a_media_dos_quatro_lags(features_smoke):
    linha = features_smoke.dropna(subset=["media_4sem"]).iloc[0]
    assert linha["media_4sem"] == pytest.approx(
        (linha["lag_28"] + linha["lag_35"] + linha["lag_42"] + linha["lag_49"]) / 4
    )


def test_faixa_programa_remove_a_edicao(features_smoke):
    assert not features_smoke["faixa_programa"].str.contains(r"_E\d+$").any()


def test_sem_vazamento_dos_ultimos_28_dias(dados_gerados, features_smoke):
    """Apagar o que ainda não seria conhecido não pode mudar nenhuma variável de histórico."""
    audiencia, grade, tle = _tabelas_brutas(dados_gerados)
    fim = pd.Timestamp(dados_gerados["dados"]["fim_historico"])
    corte = fim - pd.Timedelta(days=dados_gerados["horizonte_dias"])

    cega = _montar(
        dados_gerados,
        audiencia[audiencia["data"] <= corte],
        grade,
        tle[tle["data"] <= corte],
    )

    chave = ["data", "hora", "publico"]
    janela = (features_smoke["data"] > corte) & (features_smoke["data"] <= fim)
    completa = features_smoke[janela].sort_values(chave).reset_index(drop=True)
    sem_futuro = cega[(cega["data"] > corte) & (cega["data"] <= fim)].sort_values(chave).reset_index(drop=True)
    assert len(completa) == len(sem_futuro) > 0
    for coluna in VARIAVEIS_HISTORICO:
        np.testing.assert_allclose(
            completa[coluna].to_numpy(dtype=float),
            sem_futuro[coluna].to_numpy(dtype=float),
            equal_nan=True,
            err_msg=coluna,
        )


def test_o_teste_de_vazamento_pegaria_um_lag_curto(dados_gerados):
    """Prova de que o teste funciona: com horizonte de 7 dias, os valores precisam mudar."""
    audiencia, grade, tle = _tabelas_brutas(dados_gerados)
    fim = pd.Timestamp(dados_gerados["dados"]["fim_historico"])
    corte = fim - pd.Timedelta(days=dados_gerados["horizonte_dias"])
    maximo = dados_gerados["features"]["max_dias_estreia"]
    com_tudo = montar_features(audiencia, grade, tle, 7, maximo)
    cega = montar_features(audiencia[audiencia["data"] <= corte], grade, tle[tle["data"] <= corte], 7, maximo)
    alvo = pd.Timestamp(fim)
    a = com_tudo[com_tudo["data"] == alvo]["lag_28"].to_numpy(dtype=float)
    b = cega[cega["data"] == alvo]["lag_28"].to_numpy(dtype=float)
    assert not np.allclose(a, b, equal_nan=True)
