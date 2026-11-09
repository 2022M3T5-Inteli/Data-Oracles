# Model card — O Oráculo 2.0

| | |
| --- | --- |
| Dona | Yasmin Rocha |
| Versão | 2.0.0 (a versão em uso é a que tem o alias `champion` no MLflow) |
| Data | novembro de 2026 |
| Como reportar problema | Issue no repositório |

> Modelo treinado e avaliado somente com **dados sintéticos**. É uma demonstração de método.

## Objetivo e uso pretendido

Prever o rating de cada bloco de 15 minutos, para 10 públicos, 28 dias antes, com faixa de previsão p10–p90. O uso pretendido é apoiar o comercial a definir quanta audiência prometer, usando o p10 como entrega segura.

## Uso não pretendido

- Tomar decisões reais de venda: o modelo não foi treinado com audiência real.
- Prever eventos sem sinal nas variáveis, como crises ou fuga súbita de público.
- Medir efeito causal de uma campanha: isso é feito em `r/incrementalidade_did.R`.
- Prever com antecedência menor que 28 dias esperando ganho: os lags não usam dados mais recentes.

## Dados

| Item | Descrição |
| --- | --- |
| Origem | Gerador sintético com a estrutura do Kantar IBOPE (`src/oraculo/data/generate.py`) |
| Período | Histórico de 01/01/2023 a 31/12/2024, mais 28 dias de chegada para monitoramento |
| Granularidade | Dia × bloco de 15 min × público; 654.720 linhas válidas de treino |
| Públicos | total_dom, ab, c, de, masculino, feminino, 4_17, 18_34, 35_49, 50_mais |

## Variáveis (21)

- **Calendário:** hora, dia da semana, mês, dia do ano, feriado, fim de semana.
- **Tendência e conteúdo:** dias desde o início, dias desde a estreia, categoria, faixa do programa.
- **Concorrência:** categoria exibida por cada concorrente no mesmo bloco.
- **Público:** variável categórica de um modelo global.
- **Histórico (pelo menos 28 dias):** lag_28, lag_35, lag_42, lag_49, lag_364, media_4sem, media_hora_28_56, tle_lag_28.

## Modelo

Três LightGBM com perda quantílica (p10, p50, p90), mais ajuste conformal (CQR) por público. Hiperparâmetros: 300 árvores, taxa 0,05, 63 folhas, `min_child_samples` 50, `subsample` 0,8, `colsample_bytree` 0,8, `reg_lambda` 5. Não houve busca de hiperparâmetros.

## Métricas (backtest em 4 cortes, 28 dias cada)

| Recorte | WAPE | Baseline | MAE | Viés | Cobertura sem ajuste |
| --- | --- | --- | --- | --- | --- |
| Geral | 8,7% | 9,9% | 0,42 | −0,01 | 69,5% |
| Horário nobre (19h–23h) | 8,5% | 9,7% | 0,99 | −0,07 | 77,7% |

| Público | WAPE | Baseline | Cobertura sem ajuste |
| --- | --- | --- | --- |
| total_dom | 6,8% | 7,9% | 63,4% |
| feminino | 7,6% | 8,4% | 65,4% |
| 50_mais | 7,8% | 8,9% | 69,9% |
| c | 8,1% | 9,3% | 67,2% |
| masculino | 8,2% | 9,7% | 68,8% |
| 35_49 | 9,0% | 10,2% | 68,8% |
| de | 9,1% | 10,4% | 71,0% |
| 18_34 | 10,1% | 11,2% | 72,8% |
| ab | 10,6% | 11,9% | 73,5% |
| 4_17 | 13,6% | 15,0% | 74,4% |

Cobertura com ajuste conformal, medida no último corte: 79,6%, contra 68,6% antes.

Porta de qualidade: WAPE pelo menos 5% melhor que o baseline; cobertura da faixa calibrada de pelo menos 70%; não pior que o campeão atual, com tolerância de 2%.

## Premissas

- A grade da emissora e das concorrentes é conhecida 28 dias antes.
- Nenhuma variável de histórico usa os últimos 28 dias, o que é verificado por teste automático.
- Os blocos estão completos: os contratos de dados garantem 96 blocos por dia.

## Limitações e riscos

- O ganho sobre o baseline é pequeno em meses de grade estável (2% a 6%).
- Públicos pequenos têm mais ruído: o WAPE de 4_17 é o dobro do de total_dom.
- Um choque não previsto dobra o erro. No teste simulado, o WAPE foi a 17,4%, com viés positivo, o lado caro.
- O PSI das variáveis não detectou esse choque. O alerta veio do desempenho, que depende da chegada do dado real.
- A cobertura sem ajuste é baixa. A faixa precisa do ajuste conformal.
- O `resumo_comercial.csv` usa a média dos p10 dos blocos, o que é conservador para uma campanha somando muitos blocos.

## Explicabilidade

Contribuições SHAP nativas do LightGBM, em pontos de rating, numa amostra de 3.000 linhas (`shap_importancia.png`). As maiores: `media_4sem` (2,12), `media_hora_28_56` (0,50), `lag_35` (0,20), `lag_364` (0,13) e `faixa_programa` (0,12).

## Governança e LGPD

Não há dado pessoal: os dados são sintéticos e agregados por público. Em produção, a audiência do Kantar também é agregada, mas o contrato com o fornecedor limita o uso e a divulgação. Cada modelo em uso tem run, parâmetros e métricas registrados no MLflow, e o rollback é mover o alias para a versão anterior.
