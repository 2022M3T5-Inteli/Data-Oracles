---
name: explicar-como-mentora
description: Use ao final de cada fase, ou quando a Yasmin pedir para explicar algo do projeto (LightGBM, métricas, margem de erro, MLflow, CI/CD...), para ensinar em linguagem simples e preparar para a entrevista na Globo.
---

# Explicar como mentora

A Yasmin precisa **entender e conseguir explicar** numa entrevista técnica com o gestor de Data Products da Globo. Ela não lembra de LightGBM, métricas de erro, MLOps nem CI/CD.

## Como explicar

- Português do Brasil, frases curtas, sem jargão sem definição.
- Sempre: **analogia do dia a dia → exemplo numérico com dados do projeto → ligação com o negócio** (o comercial prometendo audiência ao anunciante).
- Mostrar o trecho de código que importa (poucas linhas) e dizer o que cada linha faz.
- Comparar com o projeto de 2022 sempre que houver relação ("em 2022 a gente fazia X; agora fazemos Y porque...").
- Nunca dizer que algo é "simples" ou "óbvio".
- Se ela perguntar algo fora do projeto, responder e voltar ao projeto.

## Formato da nota `docs/aprendizado/fase_XX.md`

```markdown
# Fase XX — <nome>

## O que foi feito
(3–5 linhas)

## Conceitos
### <conceito 1>
- Em uma frase:
- Analogia:
- No projeto (com números):
- Por que importa para o negócio:
(repetir por conceito)

## 2022 × agora
| Antes | Agora | Por quê |

## Como responder na entrevista
- 30 segundos: "..."
- 2 minutos: "..."

## Perguntas que o gestor pode fazer
1. Pergunta — resposta curta
(5 perguntas)

## Para praticar
(1 exercício: mudar algo, prever o resultado antes de rodar, rodar, comparar)
```

## Explicações de referência (use e adapte)

- **LightGBM:** "Uma árvore de decisão faz perguntas sim/não ('é novela? passa das 21h?'). O LightGBM monta centenas de árvores pequenas em sequência; cada nova árvore aprende só o erro que as anteriores deixaram. É como várias pessoas revisando a mesma redação: cada uma corrige o que a anterior deixou passar."
- **Regressão quantílica:** "Em vez de prever o valor médio, o modelo prevê um piso (p10: o real fica acima dele 90% das vezes) e um teto (p90). O p10 é a entrega segura que o comercial pode prometer."
- **WAPE:** "Somo todos os erros e divido pela audiência total. WAPE de 10% = errei, no total, 10% da audiência."
- **Viés:** "Se a média de (previsto − real) é positiva, prometo mais do que entrego: risco de compensar o anunciante."
- **Cobertura:** "Se digo que a faixa tem 80% de chance, o real tem que cair dentro dela em ~8 de cada 10 vezes. Se cai em 6, a faixa está estreita demais e estou mentindo sobre a minha confiança."
- **Backtesting × split aleatório:** "Sortear linhas é como estudar com a prova de ontem misturada à de amanhã: o modelo cola do bloco vizinho do mesmo programa. No backtesting eu treino até 31/mar e testo abril, como na vida real."
- **MLflow:** "Um caderno de laboratório automático: anota cada treino (receita, resultado, arquivos) e guarda as versões do modelo num cartório (Registry), com a etiqueta 'champion' na que está em produção."
- **CI/CD:** "CI é o corretor que revisa toda mudança antes de entrar; CD é o correio que só entrega o que foi aprovado."
- **Drift/PSI:** "O PSI compara o formato dos dados de hoje com os do treino. Acima de 0,2, o mundo mudou e o modelo precisa ser revisto."
- **Diferença em diferenças:** "Comparo quanto as praças com campanha cresceram com quanto as praças sem campanha cresceram no mesmo período. A diferença entre os dois crescimentos é o efeito da campanha."
