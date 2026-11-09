# 03 — Base analítica em SQL e regra anti-vazamento

Módulo: `src/oraculo/features/build.py`. Saída: `data/features/features.parquet`.

## 1. Granularidade

Uma linha por **dia × bloco de 15 min × público** da emissora principal, incluindo **dias futuros** (sem audiência ainda) para a previsão em lote. Base = `grade` CROSS JOIN públicos, LEFT JOIN audiência e TLE.

## 2. Regra de ouro

A previsão é feita **28 dias antes** (`horizonte_dias`). Toda variável de histórico usa dados de **pelo menos 28 dias atrás**. Para prever 28/jan, o mais recente conhecido é 31/dez. Variáveis de grade (categoria, programa, o que a concorrência exibe) são permitidas porque a grade é planejada com antecedência.

## 3. Variáveis

Implementar em SQL (DuckDB) com funções de janela. Série = mesmo público e mesmo bloco, ordenada por data (`WINDOW w AS (PARTITION BY publico, hora ORDER BY data)`). Como a grade é completa (contrato garante 96 blocos/dia), `LAG(x, 28)` = 28 dias antes.

| Variável | Definição | Por quê |
| --- | --- | --- |
| hora, dow, mes, dia_ano, feriado, fim_de_semana | calendário | mantidas de 2022 |
| tendencia_dias | dias desde o início | queda estrutural da TV aberta |
| dias_desde_estreia | dias desde a 1ª aparição do programa (máx. 365) | estreias e programas novos |
| categoria, faixa_programa | categoria; programa sem o sufixo `_E<n>` | conteúdo (faixa evita categoria nunca vista) |
| categoria_conc_a, categoria_conc_b | o que as concorrentes exibem no mesmo bloco | concorrência (faltou em 2022) |
| publico | categórica | um **modelo global** para todos os públicos |
| lag_28, lag_35, lag_42, lag_49 | rating do mesmo bloco 4, 5, 6 e 7 semanas antes | mesmo dia da semana |
| lag_364 | 52 semanas antes | sazonalidade anual |
| media_4sem | média de lag_28..lag_49 | **também é o baseline de negócio** |
| media_hora_28_56 | média do bloco entre 56 e 28 dias antes | nível recente |
| tle_lag_28 | TLE 28 dias antes | TVs ligadas |

Categóricas viram `category` do pandas (LightGBM trata nativamente; não usar one-hot).

## 4. Critérios de aceite

- [ ] `make features` em poucos segundos; imprime nº de linhas e de variáveis.
- [ ] Teste: `lag_28` de uma linha = rating do mesmo bloco/público 28 dias antes.
- [ ] **Teste anti-vazamento (obrigatório):** copiar os dados brutos, apagar audiência e TLE dos últimos 28 dias do histórico, reconstruir as features e verificar que as variáveis de histórico das linhas desses 28 dias são **idênticas** às da base completa (`np.testing.assert_allclose(..., equal_nan=True)`).
- [ ] Explicação em `docs/aprendizado/fase_03.md`: o que é lag, o que é vazamento, por que 28 dias, como o teste prova a ausência de vazamento, e a consulta SQL de média móvel explicada linha a linha.
