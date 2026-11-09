# Fase 07 — Incrementalidade em R

## O que foi feito

`r/incrementalidade_did.R` responde em R base, sem pacotes: "quantos cadastros a campanha causou?".
Um anunciante simulado fez campanha em 8 de 20 praças, nas semanas 30 a 37. O efeito real programado foi de +12%, e uma sazonalidade de +10% atingiu todas as praças ao mesmo tempo.

| Método | Resultado (dados sintéticos) |
| --- | --- |
| 1. Comparação ingênua | +23,2% |
| 2. Diferença em diferenças | **+11,5%** (IC 95%: +10,2% a +12,7%) |
| 3. Permutação, 999 sorteios | p-valor = 0,001 |
| 4. Placebo, semanas 20 a 27 | +0,0% |
| 5. Cadastros incrementais | 15.083, custo de R$ 9,94 cada (investimento ilustrativo de R$ 150 mil) |

## Conceitos

### Contrafactual

- Em uma frase: o que teria acontecido sem a campanha.
- Analogia: não dá para saber como seria seu dia se você não tivesse tomado o café. Dá para olhar alguém parecido que não tomou.
- No projeto: as 12 praças sem campanha fazem o papel do "sem".
- Por que importa para o negócio: efeito é sempre uma comparação com algo que não aconteceu.

### Por que a comparação ingênua engana

- Em uma frase: ela soma a campanha com tudo mais que mudou no período.
- Analogia: vender mais sorvete no verão e dar o crédito ao novo cartaz.
- No projeto: +23,2% é o efeito de +12% multiplicado pela sazonalidade de +10% (1,12 × 1,10 ≈ 1,23).
- Por que importa para o negócio: dobrar o efeito leva a pagar caro por algo que aconteceria de qualquer jeito.

### Diferença em diferenças (DiD)

- Em uma frase: quanto o grupo com campanha cresceu, menos quanto o grupo sem campanha cresceu.
- Analogia: comparar duas turmas antes e depois de um reforço. O ganho que importa é o que a turma do reforço teve a mais.

Em números redondos:

| | Antes | Durante | Crescimento |
| --- | --- | --- | --- |
| Praças com campanha | 100 | 123 | +23% |
| Praças sem campanha | 100 | 110 | +10% |
| **Diferença entre os crescimentos** | | | **cerca de +12%** |

A conta é feita em logaritmo, por isso 1,23 ÷ 1,10 ≈ 1,12.

- Por que importa para o negócio: é a base da **precificação por valor**. Provar o retorno incremental defende renovação e preço.

### Efeitos fixos

- Em uma frase: uma constante para cada praça e para cada semana.
- Analogia: comparar cada aluno consigo mesmo, para o mais estudioso não parecer "efeito do reforço".
- No projeto: `lm(log(cadastros) ~ did + praca + semana_f)`. A praça grande não pesa por ser grande, e a semana boa vale para todo mundo.

### P-valor e permutação

- Em uma frase: o p-valor é a chance de ver um efeito desse tamanho só por acaso, se não houvesse efeito.
- Analogia: se eu sortear ao acaso 8 praças para fingir que tiveram campanha, quantas vezes vejo um efeito tão grande?
- No projeto: em 999 sorteios, nenhum chegou ao efeito observado, então p = 1 ÷ 1.000 = 0,001. É o menor valor possível com esse número de sorteios.
- Por que importa para o negócio: com poucas praças, as fórmulas padrão de erro são frágeis. A permutação não depende delas.

### Placebo

- Em uma frase: fingir uma campanha onde não houve nenhuma.
- Analogia: dar comprimido de açúcar. Se melhorar igual, o remédio não é o motivo.
- No projeto: usei só dados anteriores à campanha, e o efeito foi 0,0%.

### Tendências paralelas

- Em uma frase: sem a campanha, os dois grupos teriam evoluído de forma parecida.
- Analogia: dois corredores no mesmo ritmo. Se um acelera depois de beber o isotônico, faz sentido dar o crédito ao isotônico.
- No projeto: é a premissa central e não dá para provar. O placebo é uma evidência a favor.
- Risco: se a campanha foi para as praças que já estavam crescendo, o DiD superestima.

### Qual método usar

| Método | Quando |
| --- | --- |
| Teste A/B | Dá para sortear pessoas, como no digital |
| Geo-experimento | Dá para sortear praças antes da campanha, o ideal na TV |
| DiD | A campanha já aconteceu e há praças sem campanha |
| Controle sintético | Poucas praças tratadas: combinar praças para criar um "gêmeo" |
| MMM | Visão agregada de vários canais ao longo do tempo |

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| Não existia prova de efeito | DiD com permutação e placebo | O anunciante quer saber o que comprou |
| Só previsão de audiência | Previsão antes, efeito depois | Ciclo completo da venda |
| Sem R | R base em um script | Requisito da vaga, sem dependências |

## Como responder na entrevista

- **30 segundos:** "Medi o efeito de uma campanha com diferença em diferenças. A comparação ingênua dava +23%, porque misturava sazonalidade. O DiD deu +11,5%, perto do +12% simulado, com p-valor de 0,001 por permutação e placebo zero. Isso permite falar em custo por resultado incremental."
- **2 minutos:** "O anunciante pergunta quantos resultados a campanha causou. Antes e depois não responde, porque o período era bom para todas as praças. Usei praças sem campanha como contrafactual, com efeitos fixos de praça e semana. Como são poucas praças, fiz inferência por permutação: sorteei 999 vezes quais seriam tratadas. Também rodei um placebo em período sem campanha, que deu zero. A premissa é a de tendências paralelas, que não dá para provar. O ideal seria sortear as praças antes, num geo-experimento. Para o comercial, isso vira custo por cadastro incremental e sustenta a renovação de uma cota."

## Perguntas que o gestor pode fazer

1. **O efeito é causal?** Sob a premissa de tendências paralelas. O placebo ajuda, mas não prova.
2. **Por que log?** Porque praças têm tamanhos diferentes. O efeito fica em porcentagem.
3. **Por que não a estatística t do `lm`?** Com poucas praças e erros correlacionados na mesma praça, ela tende a ser otimista.
4. **O que você faria com orçamento para teste?** Sortearia as praças antes, equilibrando tamanho e tendência.
5. **Como isso entra no preço?** O custo por resultado incremental mostra o valor gerado e sustenta o preço de renovação.

## Para praticar

Em `configs/config.yaml`, mude `sazonalidade` de 0,10 para 0,30. Antes de rodar, escreva o que muda no método ingênuo e o que muda no DiD. Rode `make dados incrementalidade` e compare.
