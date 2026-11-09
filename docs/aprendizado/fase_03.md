# Fase 03 — Base analítica em SQL e regra anti-vazamento

## O que foi feito

Montei a base analítica em SQL com DuckDB (`src/oraculo/features/build.py`): 728.640 linhas e 21 variáveis, uma linha por dia × bloco × público, incluindo os 28 dias futuros.
O teste anti-vazamento obrigatório passa, e criei um segundo teste que prova que ele falharia se houvesse vazamento.

## Conceitos

### Lag

- Em uma frase: o valor da mesma série em um momento anterior.
- Analogia: olhar a conta de luz do mesmo mês em anos passados para estimar a próxima.
- No projeto: `lag_28` é o rating do mesmo bloco e público 28 dias antes. Múltiplos de 7 mantêm o dia da semana: terça olha para terça.
- Por que importa para o negócio: o histórico do horário é o sinal mais forte, e ele existe no momento da venda. Em 2022, não existia nenhum lag.

### Vazamento de dados

- Em uma frase: usar no treino informação que não existiria na hora de prever.
- Analogia: fazer a prova com o gabarito na mesa. A nota é ótima e não vale nada.
- No projeto: para prever 28/jan, o dado mais recente conhecido é 31/dez. Usar a audiência de 20/jan seria vazamento.
- Por que importa para o negócio: um modelo com vazamento parece ótimo no teste e faz o comercial prometer o que não vai entregar.

### Por que 28 dias

- Em uma frase: é a antecedência realista de uma venda neste projeto.
- Analogia: encomendar o bolo com um mês de antecedência. Você só sabe o que sabia naquele dia.
- No projeto: `horizonte_dias: 28`. Mudar esse número desloca todos os lags.
- Por que importa para o negócio: quanto maior a antecedência, menos informação e maior o erro. O horizonte é uma decisão comercial.

### Modelo global e variáveis de grade

- Em uma frase: um único modelo aprende todos os públicos, com o público como variável.
- Analogia: um professor que conhece a turma toda, em vez de um professor por aluno.
- No projeto: categoria, programa e o que as concorrentes exibem são permitidos porque a grade é planejada com antecedência.
- Por que importa para o negócio: públicos pequenos aprendem com os grandes. Em 2022, a concorrência foi descartada em FE 28.

## O teste anti-vazamento

Passo a passo em `tests/test_dados_e_features.py`:

1. Monto as features com todos os dados.
2. Apago audiência e TLE dos últimos 28 dias do histórico.
3. Remonto as features.
4. Comparo as variáveis de histórico das linhas desses 28 dias.

Se forem **idênticas**, nenhuma delas dependia do que foi apagado.

Um teste que nunca falha não prova nada. Por isso `test_o_teste_de_vazamento_pegaria_um_lag_curto` usa horizonte de 7 dias e exige que os valores mudem.

## A média móvel em SQL, linha a linha

```sql
AVG(rating) OVER (serie ROWS BETWEEN 56 PRECEDING AND 28 PRECEDING) AS media_hora_28_56
...
WINDOW serie AS (PARTITION BY publico, hora ORDER BY data)
```

- `WINDOW serie AS (...)`: dá nome à "fila" usada pelas janelas.
- `PARTITION BY publico, hora`: uma fila para cada público em cada bloco. As 21h do feminino não se misturam com as 21h do masculino.
- `ORDER BY data`: a fila anda no tempo.
- `ROWS BETWEEN 56 PRECEDING AND 28 PRECEDING`: de 56 a 28 linhas atrás. Como há uma linha por dia, são 56 a 28 dias atrás.
- `AVG(rating) OVER`: tira a média só dessa faixa, em cada linha.

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| Merges no pandas em células soltas | Uma consulta SQL testada | Lógica revisável em um lugar |
| Sem histórico da audiência | Lags de 4 a 7 e de 52 semanas | O sinal mais forte estava faltando |
| Concorrência descartada | `categoria_conc_a` e `categoria_conc_b` | A disputa muda o share |
| `Ano` criado e não usado | `tendencia_dias` | Queda estrutural da TV aberta |
| One-hot de 27 colunas | Categórica nativa do LightGBM | Menos colunas, sem perder informação |

## Como responder na entrevista

- **30 segundos:** "Construí a base em SQL, com funções de janela, respeitando a regra de que a previsão é feita 28 dias antes. Toda variável de histórico olha pelo menos 28 dias para trás, e um teste automático prova isso apagando os últimos 28 dias e exigindo o mesmo resultado."
- **2 minutos:** "O ponto central é separar o que se conhece na hora da venda. A grade é planejada, então posso usar categoria e o que a concorrência exibe. Audiência e TVs ligadas só com 28 dias de defasagem. Uso `LAG` com múltiplos de 7 para manter o dia da semana e uma média móvel de 28 a 56 dias para o nível recente. A média das 4 semanas é também o baseline de negócio. O teste apaga os dados recentes, reconstrói e compara. E para garantir que o teste serve, tenho outro que usa horizonte de 7 dias e precisa acusar diferença."

## Perguntas que o gestor pode fazer

1. **Como você garante que não há vazamento?** Com um teste que remove o futuro e exige variáveis idênticas, e que é provado com um caso de falha.
2. **E se a grade mudar depois da previsão?** A previsão fica desatualizada. Por isso ela roda toda semana.
3. **Por que DuckDB?** SQL analítico sem servidor. O mesmo SQL migra com poucas mudanças para Spark SQL.
4. **`lag_364`, por que não 365?** 364 é múltiplo de 7, então mantém o dia da semana.
5. **Tem nulo nos lags?** Sim, no início do histórico. O LightGBM trata nulos, e `media_4sem` nula tira a linha do treino e da avaliação.

## Para praticar

Em `build.py`, troque `horizonte` por `0` só na linha de `tle_lag_28`. Antes de rodar, diga qual teste deve falhar e por quê. Rode `make test`, compare e desfaça.
