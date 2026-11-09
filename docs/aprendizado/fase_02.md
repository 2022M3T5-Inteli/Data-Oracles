# Fase 02 — Dados sintéticos e contratos

## O que foi feito

Criei um gerador de dados **sintéticos** com a estrutura do Kantar (`src/oraculo/data/generate.py`) e contratos que param o pipeline se o dado estiver errado (`validate.py`).
Parâmetros ficam em `configs/config.yaml`, e a semente fixa torna o resultado repetível.
`make dados validar` gera e valida 842.112 linhas de audiência, em cerca de 4 segundos.

### Ordem de grandeza conferida (total domicílios, emissora principal)

| Medida | Spec | Obtido |
| --- | --- | --- |
| Rating médio | ~5–6 pontos | 5,91 |
| Pico noturno (média do bloco) | ~16 | 16,63 às 21h15 |
| Share médio | ~32% | 31,2% |
| Share das concorrentes | ~15% cada | 17,0% e 17,5% |

As concorrentes ficaram um pouco acima da referência. A diferença não muda nenhuma conclusão.

## Conceitos

### Dados sintéticos

- Em uma frase: dados inventados por um programa, que imitam a estrutura e os padrões dos dados reais.
- Analogia: um simulador de voo. O avião não existe, mas as situações treinam o piloto de verdade.
- No projeto: 2 anos de histórico, 96 blocos por dia, 10 públicos. O contrato da Gazeta proíbe usar os dados reais aqui.
- Por que importa para o negócio: permite mostrar método sem violar contrato. Só que o resultado vale para o simulador: **os números não medem audiência real**.

### Por que cada padrão existe

- Em uma frase: cada comportamento gerado justifica uma variável do modelo.
- Analogia: uma prova com questões de cada matéria que você estudou.
- No projeto: novelas trocam de edição a cada ~180 dias e têm apelo sorteado, o que obriga a lidar com estreias. O efeito episódio (um fator por programa e dia) faz blocos vizinhos se parecerem, e é isso que engana a divisão aleatória.
- Por que importa para o negócio: novela nova no mesmo horário pode fracassar. O horário sozinho não garante a entrega.

### Choque na chegada

- Em uma frase: depois do histórico, "outros" (streaming) cresce 55% de uma vez, sem aviso em nenhuma variável.
- Analogia: um treino de incêndio surpresa.
- No projeto: o share médio cai de 31,2% para 25,6% no período de chegada.
- Por que importa para o negócio: nenhum modelo prevê o que ainda não aconteceu. O que dá para fazer é perceber rápido.

### Contrato de dados

- Em uma frase: regras que o dado precisa cumprir antes de seguir adiante.
- Analogia: o controle de qualidade na entrada da fábrica, que devolve a carga estragada.
- No projeto: `rating` entre 0 e 100, chave única, 96 blocos por dia, nenhuma data faltando, todo dia com grade.
- Por que importa para o negócio: é melhor o pipeline parar do que entregar ao comercial um número calculado com dado quebrado.

Os blocos completos não são detalhe. Os lags em SQL contam linhas, então um bloco faltando faria "28 linhas atrás" deixar de ser "28 dias atrás".

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| Dados reais em CSV no Drive | Sintéticos gerados por código | Confidencialidade e reprodução |
| `dropna()` sem atribuição, sem efeito | Contrato com pandera, que para o pipeline | O erro aparece na hora |
| Datas `dd/mm` lidas como `mm/dd` nos feriados | Datas ISO e teste de 12/10 | Era o achado 2 da fase 0 |
| Blocos de 5 min com rótulo de 15 | 96 blocos reais de 15 min | Uma linha por bloco |

## Como responder na entrevista

- **30 segundos:** "Os dados reais são confidenciais, então criei um gerador sintético com a estrutura do Kantar e os padrões que importam: curva diária, tendência de queda, estreias e concorrência. Antes de qualquer modelo, contratos de dados travam o pipeline se algo vier errado."
- **2 minutos:** "O gerador segue a lógica do negócio: o share é o apelo da emissora dividido pela soma dos apelos das concorrentes e do streaming, e o rating é TVs ligadas vezes share. Cada padrão existe por um motivo. As novelas têm sorte de edição, para simular estreia ruim. Há efeito episódio, para mostrar o problema da divisão aleatória. E públicos pequenos têm mais ruído, como num painel. Também coloquei um choque depois do histórico, que nenhuma variável explica, para testar o monitoramento. Sei que é um simulador: ele prova o método, não a acurácia em dado real."

## Perguntas que o gestor pode fazer

1. **Por que confiar em resultados sintéticos?** Não para afirmar a acurácia real, e sim para demonstrar método, validação e operação.
2. **Por que pandera, e não `assert`?** Dá regras declarativas e um relatório de quais linhas falharam.
3. **O que acontece se chegar um dia incompleto?** O pipeline para com erro dizendo quais combinações falharam.
4. **Por que 10 públicos e não 14?** Para reduzir recortes e manter o método. Os públicos ficam em configuração.
5. **Os eventos das concorrentes viram variável?** Não. São um choque parcial que o modelo não enxerga, e é um próximo passo natural.

## Para praticar

Em `configs/config.yaml`, mude `sigma_apelo` de 0,16 para 0,40. Antes de rodar, escreva o que acontece com a diferença entre edições de novela. Rode `make dados` e compare as médias de `novela_21h_E1` e `novela_21h_E2`.

Um tropeço real desta fase: o YAML leu `4_17` como o número 417, porque `_` é separador numérico. A correção foi pôr aspas, e `tests/test_config.py` agora protege isso.
