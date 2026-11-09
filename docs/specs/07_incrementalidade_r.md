# 07 — Incrementalidade em R: a campanha causou resultado?

Arquivo: `r/incrementalidade_did.R` (R base, sem pacotes). Dados: `data/raw/campanha_praca.csv`.

## 1. Pergunta de negócio

"O anunciante fez uma campanha na TV em 8 praças nas semanas 30–37. Quantos cadastros no app a campanha **causou**?" É a base da **precificação por valor**: provar o retorno incremental para defender renovação e preço.

## 2. Métodos (todos no mesmo script)

1. **Comparação ingênua** antes × depois nas praças tratadas → mistura campanha com sazonalidade (deve dar ~+23%, inflado).
2. **Diferença em diferenças** com efeitos fixos de praça e semana: `lm(log(cadastros) ~ did + praca + semana_f)`, onde `did = tratado × pos`. Efeito = `exp(coef) − 1` (deve dar perto de +12%).
3. **Inferência por permutação:** sortear 999 vezes quais praças seriam "tratadas"; p-valor = proporção de efeitos sorteados ≥ o observado; IC de 95% por inversão. Robusta com poucas praças e sem pacotes.
4. **Placebo:** fingir campanha nas semanas 20–27 só com dados pré-campanha → efeito ~0.
5. **Cadastros incrementais** e leitura de negócio: custo por cadastro incremental = investimento ÷ incrementais.

## 3. Critérios de aceite

- [ ] `make incrementalidade` imprime as 5 linhas de resultado.
- [ ] Ingênuo claramente acima do DiD; DiD perto de +12%; placebo perto de 0; p-valor < 0,05.
- [ ] `docs/aprendizado/fase_07.md`: contrafactual, por que a comparação ingênua engana, DiD com a tabela 2×2, efeitos fixos, p-valor e permutação em linguagem simples, placebo, premissa de tendências paralelas, quando usar geo-experimento, A/B, controle sintético e MMM.
