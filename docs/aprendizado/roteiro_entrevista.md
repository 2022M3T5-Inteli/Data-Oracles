# Roteiro de entrevista — O Oráculo 2.0

Em todos os números, deixe claro: **são dados sintéticos**.

## Pitch de 1 minuto

"Em 2022, no Inteli, meu time previu a audiência da TV Gazeta por faixa horária. Tínhamos um R² de 0,956, mas revisando vi que a divisão aleatória inflava esse número. Também descobri um bug na nossa API que ignorava a data e a categoria.

Refiz pensando em quem vende. O comercial promete audiência semanas antes, e errar para cima vira compensação ao anunciante. Então prevejo cada bloco 28 dias antes, com uma faixa, e o p10 é a entrega segura. Valido no tempo e comparo com o que o comercial já faria, uma média das últimas semanas. Em dados sintéticos, o erro foi 8,7% contra 9,9%. Em meses normais, o baseline quase empata; o modelo se paga quando a grade muda.

Em volta disso, há MLflow com porta de qualidade, previsão em lote, monitoramento que disparou no choque simulado, CI/CD, e um teste de incrementalidade em R que separa o efeito de uma campanha da sazonalidade."

## Números para decorar

| Tema | Número |
| --- | --- |
| 2022 | R² 0,956 no teste; MSE 0,63, cerca de 0,8 ponto; divisão aleatória |
| Backtest | WAPE 8,7% contra 9,9% do baseline (12% melhor) |
| Dezembro | 8,9% contra 12,9%; o baseline promete 0,43 ponto a mais |
| Meses normais | Modelo 2% a 6% melhor |
| Viés | −0,01 ponto |
| Cobertura | 68,6% → 79,6% com conformal |
| Divisão aleatória | WAPE 7,8%, mais otimista |
| Choque | WAPE 17,4%, viés +0,61, cobertura 49%; controle sem choque: 9,3%, OK |
| Incrementalidade | Ingênuo +23,2%; DiD +11,5%; placebo 0,0%; p = 0,001; simulado +12% |

## 15 perguntas prováveis

**Negócio**

1. **Por que prever audiência, se todo mundo sabe que o horário nobre é forte?** Porque a venda acontece antes, o programa muda e o erro custa diferente nos dois lados. O detalhe por programa, público e semana é o que importa.
2. **Qual erro custa mais?** Prometer a mais, porque vira compensação com inserções grátis. Por isso olho o viés e uso o p10.
3. **Quando um baseline bastaria?** Com grade estável. Meu modelo ganhou só 2% a 6% nesses meses. Ele se paga quando a grade muda.
4. **Como o comercial usaria o resultado?** Uma tabela por semana, programa e público: "dá para prometer 14 pontos, o esperado é 16,5".
5. **Como isso ajuda na precificação por valor?** A previsão define o que prometer, e a incrementalidade prova o retorno. O custo por resultado incremental sustenta o preço.

**Modelagem**

6. **Por que o R² de 2022 enganava?** Sorteamos linhas de uma série temporal, e mês, dia e dia da semana identificavam a data exata. O modelo via o próprio dia no treino.
7. **Como você garante que não há vazamento?** Toda variável histórica olha pelo menos 28 dias para trás. Um teste apaga esses dias e exige valores idênticos, e outro prova que o teste falharia.
8. **O que é LightGBM?** Muitas árvores pequenas em sequência, cada uma corrigindo o erro das anteriores.
9. **Como você calcularia a margem de erro?** Regressão de quantis p10 e p90, calibrada com conformal em erros fora da amostra, e medida pela cobertura.
10. **Por que WAPE e não R²?** O WAPE tem unidade de negócio: "errei 8,7% da audiência". R² mede variação explicada e fica alto por causa do padrão diário.

**MLOps e engenharia**

11. **O que acontece se um treino novo for pior?** A porta de qualidade reprova, registra os motivos e o campeão atual continua.
12. **Por que lote, e não API?** O comercial planeja por semana. A API só se justifica se alguém precisar de resposta na hora.
13. **Como você detecta que o modelo piorou?** Comparando previsto × real quando o dado chega, e com PSI nas variáveis. No meu teste, o PSI não pegou o choque; o desempenho pegou. Por isso uso os dois.
14. **Explique seu CI/CD.** A cada mudança proposta, um robô roda estilo, testes e a imagem Docker. Ao entrar na main, e toda segunda, treina, passa pela porta e publica os resultados.

**Causalidade**

15. **Como você mediu o efeito de uma campanha?** Diferença em diferenças com efeitos fixos de praça e semana, permutação para o p-valor e placebo. A premissa é a de tendências paralelas, e o ideal seria sortear as praças antes.

## Se perguntarem o que você faria diferente

- Buscaria dados reais, ou ao menos validaria a estrutura com alguém do comercial.
- Incluiria os eventos das concorrentes como variável.
- Calibraria o limite de alerta com o custo real de um falso alarme.
- Avaliaria a soma de blocos de uma campanha, que é o que o anunciante compra.

## Como falar do uso de IA

Se perguntarem como o projeto foi construído, diga que usou um assistente de IA para implementar a partir de um roteiro seu, e que revisou e estudou cada decisão. Só afirme o que você consegue explicar com as próprias palavras. As notas em `docs/aprendizado/` existem para isso.
