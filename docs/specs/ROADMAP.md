# ROADMAP — fases, ordem e critérios de aceite

Uma fase por vez. Ao fim de cada uma: rodar `make test` e `make lint` (a partir da fase 1), conferir os critérios da spec, escrever `docs/aprendizado/fase_XX.md`, fazer um commit com mensagem clara (`fase 03: features em SQL com teste anti-vazamento`) e **parar para a Yasmin revisar** antes da próxima.

Estimativa total: 1 a 2 dias de trabalho com o agente.

| Fase | Entrega | Spec | Critério de saída |
| --- | --- | --- | --- |
| 0 | Entender o projeto de 2022 e o negócio | `00`, `01` | `docs/aprendizado/fase_00.md` com o resumo do projeto original e das métricas de audiência |
| 1 | Reorganizar o repositório | `00` §5, `06` §4–5 | Código de 2022 em `legado/`; esqueleto novo; `make setup` funciona |
| 2 | Dados sintéticos + contratos | `02` | `make dados validar` ok; testes de contrato |
| 3 | Base analítica em SQL | `03` | `make features` ok; teste anti-vazamento verde |
| 4 | Modelagem e avaliação | `04` | Backtest melhor que baseline; conformal; SHAP; split aleatório comparado |
| 5 | MLOps | `05` | MLflow + champion; previsão em lote; monitor com ALERTA no choque |
| 6 | CI/CD e Docker | `06` | CI verde num PR; CD publica artefatos |
| 7 | Incrementalidade em R | `07` | Resultado com ingênuo × DiD × placebo |
| 8 | Documentação e entrevista | `08` | README, model card, roteiro de entrevista |

## Fase 0 — Entender (sem escrever código de produção)

- Ler `README.md`, `notebooks/Feature_Engineering.ipynb`, `notebooks/LightGBM_*.ipynb`, `src/backend/*.py` e o PDF em `documentos/`.
- Confirmar o diagnóstico de `00_visao_geral.md` §1–2 apontando arquivo e célula de cada item.
- Nota de aprendizado: o que o time fez em cada etapa e por quê; rating/share/reach/fidelidade com exemplo; os 14 públicos; os resultados lidos criticamente.

## Fase 1 — Reorganizar

- Mover `notebooks/`, `src/backend/`, `src/frontend/` para `legado/` (com `git mv`, preservando histórico). Manter `documentos/`.
- Criar `pyproject.toml`, `Makefile`, `.gitignore`, `configs/config.yaml`, `configs/smoke.yaml`, `src/oraculo/__init__.py`, `src/oraculo/config.py` (carrega YAML; `pasta_dados(cfg)` aceita caminho relativo à raiz ou absoluto).
- Copiar `CLAUDE.md` e `docs/specs/` para o repositório (se ainda não estiverem).
- Aceite: `make setup` instala; `python -c "import oraculo"` funciona.

## Fase 2 — Dados

Implementar `generate.py` e `validate.py` conforme `02_dados.md`, com `tests/conftest.py` e testes de contrato.

## Fase 3 — Features

Implementar `features/build.py` conforme `03_features.md`, com o teste anti-vazamento.

## Fase 4 — Modelagem

Implementar `evaluate.py`, `train.py` (por enquanto **sem** MLflow: salvar relatórios em `data/relatorios/`), `pyfunc.py`. Conferir números com `00_visao_geral.md` §7.

## Fase 5 — MLOps

Adicionar MLflow e a porta de qualidade ao `train.py`; implementar `predict.py`, `monitoring/monitor.py`, `pipeline.py`, `pipelines/airflow_dag.py`; teste de fumaça do pipeline.

## Fase 6 — CI/CD

`.github/workflows/ci.yml`, `cd.yml`, `Dockerfile`. Criar branch, abrir PR, ver o CI rodar, corrigir o que falhar **explicando cada falha**.

## Fase 7 — R

`r/incrementalidade_did.R` + alvo `make incrementalidade`. Se não houver R instalado: instruções de instalação no aprendizado e rodar pelo CI (opcional: job extra com `r-lib/actions/setup-r`).

## Fase 8 — Documentação

README, model card, roteiro de entrevista. Revisar todas as notas de aprendizado.

## Gabarito

Existe uma implementação de referência já rodada (`oraculo-mlops-referencia.zip`, entregue à parte). Use **só para conferir** quando algo não bater ou travar; implemente fase a fase no fork para que a Yasmin acompanhe e aprenda.
