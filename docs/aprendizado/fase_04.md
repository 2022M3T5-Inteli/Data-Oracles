# Fase 04 — Modelagem e avaliação

## O que foi feito

Treinei três modelos LightGBM de quantil (p10, p50, p90) e avaliei em 4 cortes temporais, sempre prevendo os 28 dias seguintes.
Comparei com o baseline de negócio, calibrei a faixa com conformal, repeti a divisão aleatória de 2022 como prova, e gerei explicações com SHAP.
**Tudo sobre dados sintéticos.**

| Medida (backtest, 4 cortes) | Modelo | Baseline |
| --- | --- | --- |
| WAPE geral | 8,7% | 9,9% |
| WAPE horário nobre | 8,5% | 9,7% |
| MAE | 0,42 ponto | 0,48 ponto |
| Viés | −0,01 ponto | +0,12 ponto |

| Corte | WAPE modelo | WAPE baseline | Viés baseline |
| --- | --- | --- | --- |
| março | 8,7% | 8,9% | −0,04 |
| junho | 8,5% | 8,7% | +0,04 |
| setembro | 8,7% | 9,2% | +0,03 |
| dezembro | 8,9% | **12,9%** | **+0,43** |

**A leitura honesta:** em meses normais, o baseline quase empata (2% a 6% pior). A melhoria de 12% vem principalmente de dezembro, quando a grade muda e o futebol para. O baseline repete o passado e promete a mais.

Outros resultados: cobertura no último corte de 68,6% para 79,6% com conformal. Divisão aleatória: WAPE 7,8% e R² 0,977, contra 8,7% e 0,973 no backtest.

## Conceitos

### Gradient boosting e LightGBM

- Em uma frase: muitas árvores pequenas em sequência, cada uma aprendendo o erro que as anteriores deixaram.
- Analogia: várias pessoas revisando a mesma redação. Cada uma corrige o que a anterior deixou passar.
- No projeto: 300 árvores com taxa de aprendizado 0,05. Uma árvore pergunta algo como "é novela? passa das 21h?".
- Por que importa para o negócio: captura combinações não lineares, como futebol mudar o público masculino às quartas.

### Regressão quantílica e o p10

- Em uma frase: em vez da média, o modelo prevê um piso (p10) e um teto (p90).
- Analogia: "chego entre 18h e 19h" ajuda mais do que "chego às 18h30".
- No projeto: o real deve ficar acima do p10 em 90% das vezes. Um bloco pode ter p10 = 9,1 e p90 = 11,8.
- Por que importa para o negócio: **o p10 é a entrega segura**, o que dá para prometer com baixo risco de compensar o anunciante.

### Por que a mediana (p50)

- Em uma frase: a mediana é o número que minimiza o erro absoluto.
- Analogia: entre os salários de uma sala, um bilionário muda a média e não muda a mediana.
- No projeto: é a previsão pontual, e combina com MAE e WAPE.
- Por que importa para o negócio: um episódio atípico não puxa a previsão de todos os blocos.

### As métricas, com um exemplo

Real = 10, 20, 30. Previsto = 12, 18, 33.

| Métrica | Conta | Resultado | Leitura |
| --- | --- | --- | --- |
| MAE | (2+2+3) ÷ 3 | 2,33 pontos | Erro típico |
| RMSE | √((4+4+9) ÷ 3) | 2,38 pontos | Pune erros grandes |
| WAPE | 7 ÷ 60 | 11,7% | Errei 11,7% da audiência total |
| Viés | (+2−2+3) ÷ 3 | +1 ponto | Prometo mais do que entrego |
| Cobertura | % do real dentro da faixa | deveria ser ~80% | Se der 60%, estou mentindo sobre a confiança |

### Backtesting × divisão aleatória

- Em uma frase: treinar até uma data e prever o período seguinte, em vez de sortear linhas.
- Analogia: sortear é estudar com a prova de ontem misturada à de amanhã.
- No projeto: a mesma receita deu WAPE 7,8% no sorteio e 8,7% no tempo. A variável `tendencia_dias` identifica o dia, e o efeito episódio deixa os blocos vizinhos parecidos.
- Por que importa para o negócio: a diferença é otimismo falso, que viraria promessa errada.

### Conformal (CQR)

- Em uma frase: alargar a faixa usando os erros passados, para ela cumprir o que promete.
- Analogia: se o GPS sempre erra 10 minutos para menos, você soma 10 minutos.
- No projeto: calculo `E = max(p10 − y, y − p90)` por público, pego o quantil e somo à faixa. Calibrei nos 3 primeiros cortes e medi no último: de 68,6% para 79,6%.
- Por que importa para o negócio: dizer "80% de confiança" precisa ser verdade.

### SHAP

- Em uma frase: quanto cada variável empurrou uma previsão para cima ou para baixo, em pontos.
- Analogia: a conta do restaurante, item por item.
- No projeto: `media_4sem` domina (2,12 pontos), depois `media_hora_28_56` (0,50). Dá para dizer: "esta previsão está 2 pontos acima porque o horário vem forte nas últimas semanas".
- Por que importa para o negócio: um executivo não confia em número sem explicação.

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| R² 0,956 chamado de precisão | WAPE, MAE, viés, cobertura | Unidade de quem decide |
| Divisão aleatória | 4 cortes temporais | Simula a venda real |
| LightGBM com MSE | Três quantis | Margem de erro |
| Um modelo por saída | Modelo global | Públicos pequenos aprendem com os grandes |
| Comparação só com regressão linear | Baseline de negócio | Saber se o modelo vale o custo |

## Como responder na entrevista

- **30 segundos:** "Treinei um LightGBM de quantis, avaliado em backtest temporal com 28 dias de antecedência. Em dados sintéticos, o WAPE foi 8,7% contra 9,9% do baseline. O mais interessante: em meses normais o baseline quase empata; o ganho aparece quando a grade muda, como em dezembro."
- **2 minutos:** "Em 2022 tínhamos R² de 0,956 com divisão aleatória. Refiz com quatro cortes no tempo e comparei com o que o comercial já faria: a média do mesmo horário de 4 a 7 semanas atrás. Quando reproduzo a divisão aleatória, o erro parece 10% menor, o que mostra o otimismo. Como quem vende precisa de margem, treinei três quantis e usei conformal para a faixa cobrir de fato cerca de 80%. O p10 vira a entrega segura. E sou honesta sobre onde o modelo agrega: se a grade é estável, o baseline resolve. O modelo justifica o custo quando há mudança de grade, e principalmente reduz o viés: em dezembro o baseline prometeria 0,43 ponto a mais."

## Perguntas que o gestor pode fazer

1. **Como você calcularia a margem de erro?** Com regressão de quantis p10 e p90, calibrada por conformal com erros fora da amostra, e medida pela cobertura.
2. **Por que não comparar só o WAPE?** Porque errar para cima custa mais. Por isso olho o viés e o p10.
3. **Quando você não usaria o modelo?** Em grade estável, se o custo de manter superar o ganho de 2% a 6%.
4. **Por que `media_4sem` domina o SHAP?** O histórico explica quase tudo. O modelo ganha nos desvios desse histórico.
5. **A cobertura de 69,5% antes do ajuste é problema?** É o motivo de existir o conformal. Quantis costumam gerar faixa estreita demais.

## Para praticar

Em `configs/config.yaml`, mude `nivel_faixa` de 0,8 para 0,9. Antes de rodar, preveja o que acontece com a cobertura e a largura. Rode `make treinar` e compare `conformal` em `data/relatorios/relatorio_treino.json`.
