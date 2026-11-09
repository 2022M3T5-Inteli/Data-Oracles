# Atalhos do projeto. Funciona no Linux, no CI e no Windows (com Git Bash).
-include .env
export

export MLFLOW_DISABLE_AGENT_HINT = 1

ifeq ($(OS),Windows_NT)
  VENV_PY := .venv/Scripts/python.exe
  PY_BASE ?= py -3.11
else
  VENV_PY := .venv/bin/python
  PY_BASE ?= python3
endif

# Usa o ambiente virtual quando ele existe; no CI e no Docker usa o Python do sistema.
PYTHON ?= $(if $(wildcard $(VENV_PY)),$(VENV_PY),python)
CONFIG ?= configs/config.yaml
IMAGEM ?= oraculo-mlops

.PHONY: setup dados validar features treinar prever monitorar pipeline smoke test lint formatar \
        mlflow-ui incrementalidade docker-build docker-run limpar

setup:
	@test -x "$(VENV_PY)" || $(PY_BASE) -m venv .venv
	$(VENV_PY) -m pip install --quiet --upgrade pip
	$(VENV_PY) -m pip install -e ".[dev]"

dados:
	$(PYTHON) -m oraculo.data.generate --config $(CONFIG)

validar:
	$(PYTHON) -m oraculo.data.validate --config $(CONFIG)

features:
	$(PYTHON) -m oraculo.features.build --config $(CONFIG)

treinar:
	$(PYTHON) -m oraculo.models.train --config $(CONFIG)

prever:
	$(PYTHON) -m oraculo.models.predict --config $(CONFIG)

monitorar:
	$(PYTHON) -m oraculo.monitoring.monitor --config $(CONFIG)

pipeline:
	$(PYTHON) -m oraculo.pipeline --config $(CONFIG)

smoke:
	$(PYTHON) -m oraculo.pipeline --config configs/smoke.yaml

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

formatar:
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

mlflow-ui:
	$(PYTHON) -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

incrementalidade:
	Rscript r/incrementalidade_did.R data/raw/campanha_praca.csv

docker-build:
	docker build -t $(IMAGEM) .

docker-run:
	docker run --rm $(IMAGEM) --config configs/smoke.yaml

limpar:
	rm -rf data data_smoke mlruns mlartifacts mlflow.db mlflow_smoke.db .pytest_cache .ruff_cache
