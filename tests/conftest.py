"""Fixtures: configuração de fumaça em pasta temporária, sem sujar o projeto."""

from __future__ import annotations

import pytest

from oraculo.config import carregar_config
from oraculo.data.generate import gerar


@pytest.fixture(scope="session")
def cfg_smoke(tmp_path_factory):
    """Config de fumaça apontando dados (e MLflow, a partir da fase 5) para uma pasta temporária."""
    pasta = tmp_path_factory.mktemp("oraculo")
    cfg = carregar_config("configs/smoke.yaml")
    cfg["caminhos"]["dados"] = str(pasta / "dados")
    return cfg


@pytest.fixture(scope="session")
def dados_gerados(cfg_smoke):
    """Gera os dados de fumaça uma vez por sessão de testes."""
    gerar(cfg_smoke)
    return cfg_smoke
