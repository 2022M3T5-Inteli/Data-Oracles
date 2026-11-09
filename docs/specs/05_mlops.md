# 05 — MLOps: rastreio, registro, porta de qualidade, previsão em lote e monitoramento

MLOps = práticas para o modelo sair do notebook e funcionar sozinho, de forma confiável. Responde a 4 perguntas: consigo refazer? o novo é melhor? roda sozinho? continua bom?

## 1. MLflow Tracking (`train.py`)

- `tracking_uri: sqlite:///mlflow.db` (local). Experimento `oraculo-audiencia`.
- Cada treino = um *run* com: parâmetros (lgbm, horizonte, quantis, fim do histórico), métricas (backtest, baseline, horário nobre, split aleatório, cobertura conformal), artefatos (`relatorio_treino.json`, `metricas_por_publico.csv`, `shap_importancia.png/.csv`, `backtest_previsoes.parquet`, `ajuste_conformal.json`) e o modelo pyfunc com `input_example`.

## 2. Porta de qualidade e Model Registry

O candidato só vira **champion** se:
1. WAPE pelo menos `melhoria_minima_vs_baseline` (5%) menor que o baseline;
2. cobertura da faixa no backtest ≥ `cobertura_min` (70%);
3. WAPE não pior que o do champion atual (`tolerancia_vs_campeao`).

Se aprovado: `mlflow.register_model(...)` e `set_registered_model_alias(nome, "champion", versao)`. Se reprovado: tag `porta_qualidade=reprovado` com os motivos; o champion anterior continua. Rollback = mover o alias para a versão anterior.

## 3. Previsão em lote (`predict.py`)

- Carrega `models:/<nome>@champion` (nunca um arquivo solto).
- Prevê `(fim_historico, fim_historico + 28 dias]`.
- Saídas em `data/outputs/`:
  - `previsoes_bloco.parquet/.csv`: data, hora, público, programa, categoria, p10, p50, p90, versão do modelo, data da previsão;
  - `resumo_comercial.csv`: semana × faixa do programa × público com `rating_previsto` (p50), `entrega_segura_p10`, `cenario_otimista_p90`.
- Por que lote e não API: o comercial planeja por semana; uma tabela atualizada semanalmente basta. API (como o Flask de 2022) só se alguém precisar de resposta na hora (ex.: escolher anúncio no Globoplay em tempo real).

## 4. Monitoramento (`monitoring/monitor.py`)

Quando a audiência real chega (`audiencia_chegada.parquet`):
- desempenho: WAPE, viés, cobertura; geral, por semana e no horário nobre; comparado ao WAPE esperado no backtest;
- drift (PSI) entre os últimos 90 dias de treino e o período previsto: `lag_28`, `media_4sem`, `tle_lag_28` (numéricas, 10 faixas por quantis da referência), `categoria_conc_b` (categórica), `rating_real`;
- PSI: < 0,1 estável; 0,1–0,2 atenção; > 0,2 mudou;
- alertas por limites da config (`wape_alerta` 15%, `cobertura_min` 65%, `psi_alerta` 0,2);
- relatório `data/relatorios/monitoramento.md` e `.json`; opção `--falhar-em-alerta` (sai com erro → dispara retreino ou chama alguém).

Resultado esperado com o choque simulado: **ALERTA** (WAPE ~23%, viés ~+0,8, cobertura ~39%). É a demonstração de "o modelo não prevê o imprevisível, mas o sistema detecta rápido".

## 5. Orquestração

- `src/oraculo/pipeline.py`: roda as etapas em ordem (`--etapas` para escolher).
- `pipelines/airflow_dag.py`: exemplo (não executado) com as mesmas etapas como tarefas, agenda semanal, retries. Explicar o equivalente em Databricks Workflows.

## 6. Critérios de aceite

- [ ] `make treinar` cria run no MLflow e, se aprovado, versão com alias `champion`.
- [ ] Rodar `make treinar` duas vezes: a segunda compara com o champion (testar também forçando reprovação, ex.: exigir 50% de melhoria).
- [ ] `make prever` gera as duas tabelas; p10 ≤ p50 ≤ p90; nada negativo.
- [ ] `make monitorar` gera o relatório e mostra ALERTA com o choque.
- [ ] Testes de PSI (estável < 0,05; deslocado > 0,2).
- [ ] `docs/aprendizado/fase_05.md`: MLflow explicado (run, experimento, artefato, registry, alias), porta de qualidade, batch × online, drift e PSI com exemplo, o que fazer quando o alerta dispara.
