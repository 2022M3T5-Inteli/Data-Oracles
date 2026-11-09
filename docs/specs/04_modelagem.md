# 04 — Modelagem: baseline, LightGBM quantílico, backtesting, faixa e SHAP

Módulos: `src/oraculo/models/evaluate.py`, `train.py`, `pyfunc.py`.

## 1. Alvo e baseline

- Alvo: `rating` (pontos). Share fica como extensão documentada.
- **Baseline de negócio:** `media_4sem` ("a média do mesmo horário e dia da semana de 4 a 7 semanas atrás"). O modelo só tem valor se bater esse baseline.
- A regressão linear de 2022 fica no `legado/` como referência histórica (R² 0,32: provou a não linearidade).

## 2. Modelo

- **LightGBM** (gradient boosting de árvores): árvores em sequência, cada uma corrigindo o erro das anteriores.
- **Um modelo global** (todos os públicos e horários juntos), com `publico` como variável.
- **Três modelos de quantil** (`objective="quantile"`, `alpha` = 0,1 / 0,5 / 0,9): p10, p50 (mediana, usada como previsão pontual) e p90. A mediana combina com a métrica de erro absoluto.
- Ordenar as três previsões por linha (evita p10 > p50) e cortar negativos.
- Hiperparâmetros em `configs/config.yaml` (`n_estimators`, `learning_rate`, `num_leaves`, `min_child_samples`, `subsample`, `colsample_bytree`, `reg_lambda`).

## 3. Backtesting temporal

Para cada data de corte em `modelo.backtest.cortes`: treinar com `data <= corte` e testar `corte < data <= corte + 28 dias` (exatamente como o comercial usaria). Cortes da config completa: 2024-03-31, 2024-06-30, 2024-09-30, 2024-12-03 (o último cobre dezembro: feriados e pausa do futebol).

## 4. Métricas (`evaluate.py`)

| Métrica | Uso |
| --- | --- |
| MAE (pontos) | principal para comunicar |
| RMSE | pune erros grandes |
| WAPE = Σ\|erro\| ÷ Σ real | métrica da porta de qualidade |
| Viés = média(previsto − real) | positivo = risco de compensar o anunciante |
| R² | só para comparar com 2022 (não é "precisão") |
| Cobertura = % do real dentro de [p10, p90] | deveria ficar perto de 80% |
| Largura média da faixa | faixa útil ou larga demais? |

Reportar: geral, **horário nobre** (19h–23h, configurável), **por público** e por corte.

## 5. Comparação com 2022

Treinar também com `train_test_split` aleatório 75/25 (como em 2022) e registrar WAPE e R². Espera-se que seja **mais otimista** que o backtesting: é a prova numérica do problema de 2022.

## 6. Faixa calibrada (conformal)

Quantis do LightGBM tendem a gerar faixa estreita demais (cobertura < 80%). Aplicar **CQR (Conformalized Quantile Regression)**:
- erro de conformidade `E = max(p10 − y, y − p90)` nas previsões fora da amostra do backtest;
- por público, `q = quantil de E no nível ceil((n+1)·0,8)/n`;
- faixa final `[p10 − q, p90 + q]` (p10 cortado em 0).
- **Medição honesta:** calibrar com os cortes anteriores e medir a cobertura no último corte (antes × depois). Em produção, calibrar com todos.

## 7. Explicabilidade

SHAP pelas contribuições nativas do LightGBM (`booster.predict(X, pred_contrib=True)`), numa amostra de 3.000 linhas. Salvar gráfico de barras (média |SHAP|, em pontos) e CSV. Explicar em linguagem de negócio: "esta previsão está X pontos acima porque...".

## 8. Empacotamento

`pyfunc.py`: classe `OraculoModel(mlflow.pyfunc.PythonModel)` que carrega os 3 boosters + o JSON de ajuste conformal e devolve `p10, p50, p90`. Quem consome não precisa saber que são 3 modelos.

## 9. Critérios de aceite

- [ ] Backtest imprime WAPE do modelo e do baseline por corte.
- [ ] Modelo melhor que o baseline no geral (referência: ~13% menor WAPE).
- [ ] Viés geral pequeno (|viés| < 0,2 ponto); métricas por público e no horário nobre salvas.
- [ ] Cobertura antes e depois do conformal registrada (referência: ~72% → ~80%).
- [ ] Métrica do split aleatório registrada e comparada.
- [ ] Gráfico SHAP gerado; top variáveis listadas.
- [ ] Testes unitários das métricas (`tests/test_metricas.py`).
- [ ] `docs/aprendizado/fase_04.md` explica: o que é gradient boosting/LightGBM (com analogia), regressão quantílica, por que mediana, cada métrica com exemplo numérico, backtesting × split aleatório, conformal, SHAP, e como responder "como você calcularia a margem de erro?".
