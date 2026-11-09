"""Testes do carregamento de configuração."""

from oraculo.config import RAIZ_PROJETO, carregar_config, pasta_dados


def test_config_completa_carrega():
    cfg = carregar_config("configs/config.yaml")
    assert cfg["seed"] == 42
    assert pasta_dados(cfg) == RAIZ_PROJETO / "data"


def test_smoke_herda_e_sobrescreve():
    cfg = carregar_config("configs/smoke.yaml")
    assert cfg["seed"] == 42
    assert pasta_dados(cfg) == RAIZ_PROJETO / "data_smoke"
    assert "herda" not in cfg


def test_pasta_dados_aceita_caminho_absoluto(tmp_path):
    cfg = {"caminhos": {"dados": str(tmp_path)}}
    assert pasta_dados(cfg) == tmp_path
