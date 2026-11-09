"""Orquestração local: roda as etapas em ordem. Em produção, ver pipelines/airflow_dag.py."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from oraculo.config import argumentos_cli, carregar_config
from oraculo.data.generate import gerar
from oraculo.data.validate import validar
from oraculo.features.build import construir
from oraculo.models.predict import prever
from oraculo.models.train import treinar
from oraculo.monitoring.monitor import monitorar

log = logging.getLogger(__name__)

ETAPAS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "dados": gerar,
    "validar": validar,
    "features": construir,
    "treinar": treinar,
    "prever": prever,
    "monitorar": monitorar,
}


def executar(cfg: dict[str, Any], etapas: list[str] | None = None) -> dict[str, Any]:
    """Executa as etapas pedidas, sempre na ordem do pipeline."""
    escolhidas = etapas or list(ETAPAS)
    desconhecidas = set(escolhidas) - set(ETAPAS)
    if desconhecidas:
        raise ValueError(f"Etapas desconhecidas: {sorted(desconhecidas)}")
    resultados = {}
    for nome, funcao in ETAPAS.items():
        if nome in escolhidas:
            log.info("=== Etapa: %s ===", nome)
            resultados[nome] = funcao(cfg)
    return resultados


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argumentos_cli("Executa o pipeline")
    parser.add_argument("--etapas", nargs="+", choices=list(ETAPAS), help="etapas a rodar (padrão: todas)")
    argumentos = parser.parse_args()
    executar(carregar_config(argumentos.config), argumentos.etapas)


if __name__ == "__main__":
    main()
