"""Métricas com contas feitas à mão: se a régua estiver errada, tudo o mais fica errado."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from oraculo.models.evaluate import (
    aplicar_conformal,
    calibrar_conformal,
    cobertura,
    largura_media,
    mae,
    r2,
    rmse,
    vies,
    wape,
)
from oraculo.models.pyfunc import ordenar_quantis

REAL = np.array([10.0, 20.0, 30.0])
PREVISTO = np.array([12.0, 18.0, 33.0])


def test_mae_em_pontos():
    assert mae(REAL, PREVISTO) == pytest.approx(7 / 3)


def test_rmse_pune_erros_grandes():
    assert rmse(REAL, PREVISTO) == pytest.approx(np.sqrt(17 / 3))
    assert rmse(REAL, PREVISTO) > mae(REAL, PREVISTO)


def test_wape_e_erro_total_sobre_audiencia_total():
    assert wape(REAL, PREVISTO) == pytest.approx(7 / 60)


def test_vies_positivo_significa_prometer_demais():
    assert vies(REAL, REAL + 1) == pytest.approx(1.0)
    assert vies(REAL, REAL - 1) == pytest.approx(-1.0)


def test_r2_perfeito_e_de_prever_a_media():
    assert r2(REAL, REAL) == pytest.approx(1.0)
    assert r2(REAL, np.full(3, REAL.mean())) == pytest.approx(0.0)


def test_cobertura_conta_quem_ficou_dentro():
    assert cobertura(REAL, np.array([5, 25, 25]), np.array([15, 35, 35])) == pytest.approx(2 / 3)


def test_largura_media():
    assert largura_media(np.array([1, 2]), np.array([3, 6])) == pytest.approx(3.0)


def test_quantis_ficam_ordenados_e_sem_negativos():
    resultado = ordenar_quantis(np.array([[3.0, 1.0, 2.0], [-1.0, 0.5, 0.2]]))
    assert resultado.tolist() == [[1.0, 2.0, 3.0], [0.0, 0.2, 0.5]]


def test_conformal_atinge_a_cobertura_pedida():
    rng = np.random.default_rng(1)
    real = rng.normal(10, 2, 20_000)
    tabela = pd.DataFrame({"publico": "a", "rating": real, "p10": 9.5, "p90": 10.5})
    ajuste = calibrar_conformal(tabela, 0.8)
    novos = rng.normal(10, 2, 20_000)
    p10, p90 = aplicar_conformal(
        np.full(20_000, 9.5), np.full(20_000, 10.5), np.full(20_000, "a", dtype=object), ajuste
    )
    assert ajuste["a"] > 0
    assert cobertura(novos, p10, p90) == pytest.approx(0.8, abs=0.02)


def test_conformal_nao_gera_p10_negativo():
    p10, _ = aplicar_conformal(np.array([0.5]), np.array([2.0]), np.array(["a"], dtype=object), {"a": 3.0})
    assert p10[0] == 0.0
