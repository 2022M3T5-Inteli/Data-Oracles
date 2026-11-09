# Fase 08 — Documentação e entrevista

## O que foi feito

Reescrevi o `README.md` com o negócio primeiro e a técnica depois. Criei `docs/model_card.md` e `docs/aprendizado/roteiro_entrevista.md`.
Rodei o pipeline do zero (`make limpar` e `make pipeline`) e os números da documentação se repetiram exatamente.

## Conceitos

### Model card

- Em uma frase: a bula do modelo.
- Analogia: a bula diz para que serve, para quem não serve e os efeitos colaterais.
- No projeto: tem seção de uso **não** pretendido e limitações, como "o WAPE de 4_17 é o dobro do de total_dom".
- Por que importa para o negócio: quem usa precisa saber onde o modelo não é confiável.

### Comunicar em linguagem de negócio

- Em uma frase: dizer o que a pessoa decide com o número.
- Analogia: o médico diz "corte o sal", e não apenas o valor do exame.
- No projeto: em vez de "MAE 0,42", o README diz "dá para prometer 14 pontos, o esperado é 16,5".
- Por que importa para o negócio: é o último requisito da vaga, e o que costuma separar candidatos.

### Honestidade como vantagem

- Em uma frase: mostrar os limites aumenta a confiança no resto.
- Analogia: o vendedor que aponta o risco do carro usado.
- No projeto: o README diz que o baseline quase empata em meses normais, e que tudo é sintético.
- Por que importa para o negócio: a vaga pede saber distinguir quando modelar e quando uma média resolve, e esse é o exemplo.

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| README com integrantes e cronograma | README com problema, resultado e limites | Quem lê é gestor ou recrutador |
| PDF de 81 páginas | Model card e notas curtas | Fácil de consultar |
| R² apresentado como precisão | Métricas com leitura de negócio | Evita conclusão errada |

## Como responder na entrevista

- **30 segundos:** "Documentei o projeto para quem decide: o README começa pelo problema comercial e o model card diz para que o modelo serve e para que não serve."
- **2 minutos:** "Separei três públicos. Quem é de negócio lê o README, que explica o problema, mostra uma linha da tabela lida em voz alta e admite que em grade estável o baseline bastaria. Quem é técnico vai ao model card, com métricas por público, premissas e riscos. E as notas por fase registram o porquê de cada decisão. Reproduzi o pipeline do zero antes de escrever os números."

## Perguntas que o gestor pode fazer

1. **O que mais você mostraria a um executivo?** A tabela de entrega segura e a diferença de dezembro.
2. **O que é um model card?** Um documento curto com objetivo, dados, métricas, limites e riscos do modelo.
3. **Como garante que os números do README são verdadeiros?** Rodei o pipeline do zero, com semente fixa, e eles se repetiram.
4. **Qual a maior limitação?** Os dados são sintéticos. O método está demonstrado, a acurácia real não.
5. **Quem é o dono do modelo em produção?** Precisa haver um dono nomeado. Está no model card, e em uma empresa seria o time do produto.

## Para praticar

Sem olhar, explique em voz alta o pitch de 1 minuto do roteiro. Grave, ouça e veja se disse "dados sintéticos" e "entrega segura".
