# 00 — Visão geral: do projeto de 2022 ao projeto para a Globo

## 1. O que o projeto de 2022 fez (diagnóstico lido no código)

| Item | Como era | Onde está no repositório original |
| --- | --- | --- |
| Pergunta | Prever audiência de uma faixa horária para apoiar decisões de **grade/programação** | `README.md`, `documentos/` |
| Usuário | Gerente de operação e programação da TV Gazeta (persona "Thiago") | `documentos/Documentação ... V4.0` |
| Dados | Kantar IBOPE: planilha de ~440 MB, 18 abas (emissora principal, concorrentes, TLE), 24 meses, blocos de 5 min; grade diária com programa/categoria; feriados | `notebooks/Feature_Engineering.ipynb` |
| Alvos | Rating (Rat%), Share (Shr%), Fidelidade (Fid%) para 14 públicos | `src/backend/modelo_geral.py` |
| Variáveis | Hora de início (blocos de 15 min, 6h–29h59), dia da semana, mês, dia do mês, feriado, categoria do programa (27, one-hot) | `src/backend/modelos.py` |
| Modelos | Regressão linear, árvore de decisão, KNN, random forest, LightGBM (escolhido, com `MultiOutputRegressor`) | `notebooks/*_Avaliação_dos_Modelos*.ipynb` |
| Ajuste | GridSearch/RandomSearch (KNN), Optuna/verstack (LightGBM) | idem |
| Validação | `train_test_split` **aleatório** 75/25, `random_state=42` | idem |
| Métricas | R² (chamado de "precisão") e MSE | idem |
| Resultado (teste) | Rating: R² 0,956, MSE 0,63 (~0,8 ponto). Share: R² 0,89, MSE 37 (~6 pontos). Fidelidade descartada por overfitting | idem |
| Entrega | Pickle no Google Drive → API Flask (`/api/lgbm/rat`, `/api/lgbm/share`) → Docker → Fly.io → front-end React | `src/backend/`, `src/frontend/` |

## 2. Problemas encontrados

1. **Divisão aleatória em série temporal:** blocos vizinhos do mesmo programa caem no treino e no teste; o modelo "cola" do vizinho. Indício: KNN quase empatou com LightGBM. O R² de 0,95 é otimista.
2. **Sem histórico da própria audiência (lags):** a informação mais forte para prever audiência não existia.
3. **Concorrência ignorada:** as abas dos concorrentes e o TLE existiam, mas não viraram variáveis. Por isso o share foi pior.
4. **Sem tendência/ano:** não captura a queda estrutural da TV aberta.
5. **Sem baseline de negócio:** nenhuma comparação com "média das últimas semanas".
6. **Previsão pontual:** sem margem de erro, que é o que o comercial precisa.
7. **Métricas mal nomeadas:** R² chamado de "precisão"; MSE em unidade quadrática, difícil de comunicar.
8. **Bug silencioso:** `tabela_programacao.dropna()` sem atribuição (não remove nada).
9. **Erro conceitual na documentação:** "Reach é o RAT dividido pelo TLE" — essa conta é o **share**.
10. **Sem engenharia de produção:** treino manual no Colab, modelo em pickle no Drive, sem testes, sem versionamento de modelo, sem monitoramento.

## 3. Manter, mudar, acrescentar

| Decisão de 2022 | Veredito | O que fazer |
| --- | --- | --- |
| CRISP-DM, começar pelo negócio | Manter | Reposicionar para o uso **comercial** |
| Unir audiência + grade + feriados | Manter | Em SQL (DuckDB), testado |
| Calendário + categoria como variáveis | Manter | Somar às novas |
| Hora em blocos de 15 min, dia de TV 6h–5h59 | Manter | Convenção do mercado |
| LightGBM como modelo principal | Manter | Agora quantílico (p10/p50/p90) |
| Regressão linear como baseline | Manter e ampliar | + baseline de negócio "média de 4 a 7 semanas atrás" |
| Divisão aleatória | Mudar | Backtesting temporal com horizonte de 28 dias |
| R²/MSE | Mudar | MAE (pontos), WAPE, viés, cobertura da faixa, erro por segmento |
| Ignorar concorrência | Mudar | Grade das concorrentes como variável |
| Notebook + pickle | Mudar | Pipeline em `src/`, MLflow Tracking + Registry |
| Flask em tempo real | Mudar | Previsão em **lote** semanal (o comercial não precisa de tempo real); API opcional |
| Lags, tendência, dias desde estreia | Acrescentar | Ver `03_features.md` |
| Faixa de previsão calibrada | Acrescentar | Quantis + ajuste conformal |
| SHAP | Acrescentar | Explicar previsões |
| Testes, contratos de dados, CI/CD, Docker | Acrescentar | Ver `06_cicd.md` |
| Monitoramento | Acrescentar | Previsto × real + drift (PSI) |
| Incrementalidade em R | Acrescentar | Ver `07_incrementalidade_r.md` |
| Fidelidade | Fora do escopo | Documentar o motivo (overfitting em 2022) |
| Front-end React | Fora do escopo | Fica em `legado/`; saída agora é tabela para o comercial |

## 4. Arquitetura alvo

```
configs/*.yaml
   │
   ▼
[1 dados] gerador sintético (formato Kantar) ──► data/raw/*.parquet
   │
[2 validar] contratos (pandera) — PARA se o dado estiver errado
   │
[3 features] SQL DuckDB: lags ≥ 28 dias, concorrência, calendário ──► data/features/
   │
[4 treinar] backtest temporal → baseline vs LightGBM p10/p50/p90 → ajuste conformal
   │         → SHAP → MLflow (parâmetros, métricas, artefatos, modelo)
   │         → PORTA DE QUALIDADE → se aprovado: Registry alias "champion"
   │
[5 prever] carrega models:/...@champion → previsões dos próximos 28 dias
   │         ──► previsoes_bloco.csv + resumo_comercial.csv (entrega segura = p10)
   │
[6 monitorar] previsto × real (quando chega) + drift (PSI) → OK / ALERTA → retreino
```

Orquestração: `src/oraculo/pipeline.py` local; `pipelines/airflow_dag.py` como exemplo de produção. CI/CD: GitHub Actions.

## 5. Estrutura de pastas alvo

```
.
├── CLAUDE.md
├── README.md                      # reescrito: negócio + como rodar + resultados
├── legado/                        # TODO o código de 2022 movido para cá (notebooks, src/backend, src/frontend)
├── documentos/                    # documentação original de 2022 (manter)
├── configs/  config.yaml, smoke.yaml
├── src/oraculo/
│   ├── config.py
│   ├── pipeline.py
│   ├── data/      generate.py, validate.py
│   ├── features/  build.py
│   ├── models/    evaluate.py, train.py, pyfunc.py, predict.py
│   └── monitoring/ monitor.py
├── tests/
├── r/incrementalidade_did.R
├── pipelines/airflow_dag.py
├── docs/ specs/, aprendizado/, model_card.md
├── .github/workflows/ ci.yml, cd.yml
├── Dockerfile, Makefile, pyproject.toml, .gitignore
```

## 6. Requisitos da vaga × entregas

| Requisito da vaga | Onde o projeto demonstra |
| --- | --- |
| Modelos preditivos aplicados à mídia (previsão de entrega) | Previsão de rating por bloco/público com faixa (fases 4–5) |
| Estatística aplicada: inferência, regressão, significância, desenho de testes | Quantis, cobertura, conformal; DiD com permutação e placebo em R |
| Incrementalidade, testes A/B | `r/incrementalidade_did.R` |
| Precificação baseada em valor | `resumo_comercial.csv` (entrega segura p10) + custo por resultado incremental no R |
| Python, SQL, R | `src/`, SQL no DuckDB, `r/` |
| Tratamento e validação de qualidade de dados | Contratos pandera + testes |
| Bases analíticas | `features/build.py` |
| Métricas de erro e avaliação | `models/evaluate.py`, backtesting, métricas por segmento |
| Versionamento e boas práticas | Git, ruff, pytest, configs, Makefile |
| MLOps e modelos em produção | MLflow Registry, porta de qualidade, batch, monitoramento |
| Explainable AI | SHAP nativo do LightGBM |
| Documentar premissas, métricas e limitações | `docs/model_card.md` |
| Comunicação com o negócio | README de negócio, resumo comercial, notas de aprendizado |
| LGPD e governança | Dados sintéticos, sem dado pessoal, nota no model card |
| PySpark/Databricks (desejável) | Explicar no README como migraria (SQL do DuckDB → Spark SQL; MLflow já é o do Databricks) |

## 7. Resultado esperado (referência)

Rodando a implementação de referência com os dados sintéticos da spec, os números ficaram nesta ordem de grandeza. Servem para conferir se a sua execução está coerente, não como meta exata:

- Backtest (4 cortes, horizonte de 28 dias): WAPE do modelo ~10,8% vs baseline ~12,5% (≈13% melhor). No horário nobre: 10,7% vs 12,7%. No corte de dezembro (feriados, pausa do futebol) o baseline piora para ~16% e o modelo fica em ~11%.
- MAE ~0,56 ponto de rating; viés pequeno (~−0,1 ponto, levemente conservador).
- Cobertura da faixa p10–p90: ~72% sem ajuste → ~80% com ajuste conformal (medido no último corte).
- Divisão aleatória (como em 2022) mostra WAPE ~9,8% e R² ~0,965: **mais otimista** que a validação temporal.
- Monitoramento em janeiro com choque não previsível: WAPE ~23%, viés +0,8 ponto (+2 no horário nobre), cobertura ~39% → ALERTA.
- Variáveis mais importantes (SHAP): lag_28, média de 4 semanas, média do horário, faixa do programa.
