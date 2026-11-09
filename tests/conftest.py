"""Fixtures: configuração de fumaça em pasta temporária, sem sujar o projeto."""

from __future__ import annotations

import os

import pytest

from oraculo.config import carregar_config
from oraculo.data.generate import gerar


@pytest.fixture(scope="session")
def cfg_smoke(tmp_path_factory):
    """Config de fumaça apontando dados e MLflow para uma pasta temporária."""
    pasta = tmp_path_factory.mktemp("oraculo")
    cfg = carregar_config("configs/smoke.yaml")
    cfg["caminhos"]["dados"] = str(pasta / "dados")
    cfg["mlops"]["tracking_uri"] = f"sqlite:///{(pasta / 'mlflow.db').as_posix()}"
    cfg["mlops"]["pasta_artefatos"] = str(pasta / "mlruns")
    os.environ.pop("MLFLOW_TRACKING_URI", None)
    return cfg


@pytest.fixture(scope="session")
def dados_gerados(cfg_smoke):
    """Gera os dados de fumaça uma vez por sessão de testes."""
    gerar(cfg_smoke)
    return cfg_smoke
