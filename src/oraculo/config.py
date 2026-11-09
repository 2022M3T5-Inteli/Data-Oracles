"""Leitura das configurações em YAML e resolução de caminhos."""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

import yaml

_CANDIDATA_RAIZ = Path(__file__).resolve().parents[2]
RAIZ_PROJETO = _CANDIDATA_RAIZ if (_CANDIDATA_RAIZ / "pyproject.toml").exists() else Path.cwd()
CONFIG_PADRAO = "configs/config.yaml"


def _mesclar(base: dict[str, Any], novo: dict[str, Any]) -> dict[str, Any]:
    """Mescla `novo` sobre `base`, descendo nos dicionários; listas e valores são substituídos."""
    resultado = copy.deepcopy(base)
    for chave, valor in novo.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = _mesclar(resultado[chave], valor)
        else:
            resultado[chave] = copy.deepcopy(valor)
    return resultado


def resolver_caminho(caminho: str | Path) -> Path:
    """Devolve o caminho absoluto; caminhos relativos partem da raiz do projeto."""
    caminho = Path(caminho)
    return caminho if caminho.is_absolute() else RAIZ_PROJETO / caminho


def carregar_config(caminho: str | Path = CONFIG_PADRAO) -> dict[str, Any]:
    """Carrega um YAML. A chave `herda` aponta para o arquivo-base, na mesma pasta."""
    caminho = resolver_caminho(caminho)
    with caminho.open(encoding="utf-8") as arquivo:
        config = yaml.safe_load(arquivo) or {}
    herda = config.pop("herda", None)
    if herda:
        return _mesclar(carregar_config(caminho.parent / herda), config)
    return config


def pasta_dados(cfg: dict[str, Any]) -> Path:
    """Pasta raiz dos dados; aceita caminho relativo à raiz do projeto ou absoluto."""
    return resolver_caminho(cfg["caminhos"]["dados"])


def argumentos_cli(descricao: str) -> argparse.ArgumentParser:
    """Parser comum a todos os módulos executáveis."""
    parser = argparse.ArgumentParser(description=descricao)
    parser.add_argument("--config", default=CONFIG_PADRAO, help="caminho do YAML de configuração")
    return parser
