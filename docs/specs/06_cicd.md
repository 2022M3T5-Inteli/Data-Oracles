# 06 — CI/CD, testes, Docker e Makefile

CI/CD = um robô que confere e entrega o código automaticamente a cada mudança.
- **CI (integração contínua):** a cada pull request, roda estilo, testes e um pipeline de fumaça. Falhou → mudança bloqueada.
- **CD (entrega contínua):** quando entra na `main`, treina o modelo completo, passa pela porta de qualidade e publica os resultados.
- **CT (treino contínuo, específico de ML):** retreino agendado (toda segunda) ou disparado pelo monitoramento.

## 1. Testes (`tests/`)

| Arquivo | O que testa |
| --- | --- |
| `conftest.py` | fixture que copia `configs/smoke.yaml` para pasta temporária (dados e MLflow em `tmp_path`, sem sujar o projeto) e gera os dados uma vez por sessão |
| `test_metricas.py` | MAE, WAPE, viés (sinal), cobertura, R², PSI numérico e categórico |
| `test_dados_e_features.py` | contratos aceitam dados bons e rejeitam ruins; lag correto; **anti-vazamento** |
| `test_pipeline_smoke.py` | pipeline inteiro (validar → features → treinar → prever → monitorar) na config de fumaça; porta aprovada; p10 ≤ p50 ≤ p90 |

Config de fumaça (`configs/smoke.yaml`): 6 meses, 2 públicos, 2 cortes, 60 árvores, porta sem exigência de qualidade. Deve rodar em segundos.

## 2. GitHub Actions

`.github/workflows/ci.yml` (em `pull_request` e push na `main`):
1. checkout, Python 3.11 com cache de pip;
2. `pip install -e ".[dev]"`;
3. `ruff check .` e `ruff format --check .`;
4. `pytest` (com `MLFLOW_DISABLE_AGENT_HINT=1`);
5. job `docker` (depende do anterior): `docker build` e `docker run ... --config configs/smoke.yaml`.

`.github/workflows/cd.yml` (push na `main`, `cron: "0 9 * * 1"` = segunda 6h em Brasília, e `workflow_dispatch`):
1. instalar; `make dados validar features`; `make treinar`; `make prever`;
2. `python -m oraculo.monitoring.monitor --falhar-em-alerta` com `continue-on-error: true` (alerta aparece como aviso, não apaga resultados);
3. `upload-artifact` com `data/relatorios/`, `data/outputs/resumo_comercial.csv`, `mlflow.db`.
Comentar no arquivo que, numa empresa, o mesmo fluxo apontaria para o MLflow/Databricks e o data warehouse da casa.

## 3. Docker

`python:3.11-slim` + `libgomp1` (exigido pelo LightGBM) + `make`; copiar `pyproject.toml` e `src` antes (cache de camadas), instalar, copiar `configs`; `ENTRYPOINT ["python", "-m", "oraculo.pipeline"]`, `CMD ["--config", "configs/config.yaml"]`. Relacionar com o Dockerfile de 2022 (Flask) no aprendizado.

## 4. Makefile

Alvos: `setup, dados, validar, features, treinar, prever, monitorar, pipeline, smoke, test, lint, formatar, mlflow-ui, incrementalidade, docker-build, docker-run, limpar`. Exportar `MLFLOW_DISABLE_AGENT_HINT=1`.

## 5. Qualidade de código

`pyproject.toml` com `ruff` (line-length 120, regras E, F, I, B, UP; ignorar E501) e pytest (`testpaths = ["tests"]`). `.gitignore` para `data/`, `data_smoke/`, `mlruns/`, `mlflow*.db`, `*.parquet`, caches.

## 6. Critérios de aceite

- [ ] `make lint` e `make test` passam localmente.
- [ ] Push num branch + pull request no GitHub: CI verde.
- [ ] Merge na `main`: CD roda e publica os artefatos.
- [ ] Docker builda e roda a fumaça (local se tiver Docker; senão, pelo CI).
- [ ] Badge do CI no README.
- [ ] `docs/aprendizado/fase_06.md`: o que acontece passo a passo num pull request, como ler um log de CI que falhou, diferença CI × CD × CT, Docker com analogia, e a frase de 1 minuto para a entrevista.
