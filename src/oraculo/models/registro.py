"""Conexão com o MLflow: rastreio e cartório (Model Registry) de versões."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

from oraculo.config import resolver_caminho

PREFIXO_SQLITE = "sqlite:///"


def uri_rastreio(cfg: dict[str, Any]) -> str:
    """Variável de ambiente tem prioridade; banco SQLite relativo parte da raiz do projeto."""
    uri = os.environ.get("MLFLOW_TRACKING_URI") or cfg["mlops"]["tracking_uri"]
    if uri.startswith(PREFIXO_SQLITE):
        caminho = uri.removeprefix(PREFIXO_SQLITE)
        if not Path(caminho).is_absolute():
            return PREFIXO_SQLITE + resolver_caminho(caminho).as_posix()
    return uri


def configurar_mlflow(cfg: dict[str, Any]) -> MlflowClient:
    """Aponta o MLflow para o destino configurado e garante o experimento."""
    mlflow.set_tracking_uri(uri_rastreio(cfg))
    cliente = MlflowClient()
    nome = cfg["mlops"]["experimento"]
    if cliente.get_experiment_by_name(nome) is None:
        pasta = resolver_caminho(cfg["mlops"]["pasta_artefatos"])
        pasta.mkdir(parents=True, exist_ok=True)
        cliente.create_experiment(nome, artifact_location=pasta.as_uri())
    mlflow.set_experiment(nome)
    return cliente


def versao_campea(cliente: MlflowClient, cfg: dict[str, Any]) -> Any | None:
    """Versão com a etiqueta de campeã, ou None se ainda não existir."""
    try:
        return cliente.get_model_version_by_alias(cfg["mlops"]["nome_modelo"], cfg["mlops"]["alias_campeao"])
    except MlflowException:
        return None


def uri_campeao(cfg: dict[str, Any]) -> str:
    return f"models:/{cfg['mlops']['nome_modelo']}@{cfg['mlops']['alias_campeao']}"
