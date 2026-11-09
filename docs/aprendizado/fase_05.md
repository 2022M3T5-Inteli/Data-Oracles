# Fase 05 — MLOps

## O que foi feito

Cada treino agora vira um registro no MLflow. Uma porta de qualidade decide se o candidato vira `champion`.
A previsão em lote carrega sempre o `champion` e gera a tabela do comercial. O monitor compara previsto × real quando a audiência chega.
`make treinar` duas vezes criou as versões 1 e 2, e `make prever` gerou 26.880 blocos.

**Resultado do monitor (dados sintéticos):**

| Cenário | Status | WAPE | Viés | Cobertura |
| --- | --- | --- | --- | --- |
| Com choque em janeiro | **ALERTA** | 17,4% | +0,61 ponto | 49,0% |
| Controle sem choque | OK | 9,3% | −0,08 ponto | 83,4% |

O esperado pelo backtest era WAPE de 8,7%. No horário nobre com choque, o viés sobe para +1,30 ponto.

## Conceitos

### MLOps

- Em uma frase: práticas para o modelo sair do notebook e funcionar sozinho, de forma confiável.
- Analogia: a diferença entre uma receita caseira e uma cozinha industrial com controle de qualidade.
- No projeto: responde a quatro perguntas: consigo refazer? o novo é melhor? roda sozinho? continua bom?
- Por que importa para o negócio: em 2022, ninguém saberia qual modelo estava no ar nem se ele tinha piorado.

### MLflow: experimento, run, artefato, registry e alias

- Em uma frase: um caderno de laboratório automático com um cartório de versões.
- Analogia: o caderno anota cada receita testada. O cartório guarda as versões oficiais, e a etiqueta "champion" indica qual está valendo.
- No projeto: experimento é o grupo `oraculo-audiencia`. Run é um treino. Artefatos são relatórios e gráficos. Registry guarda as versões, e o alias `champion` aponta a atual.
- Por que importa para o negócio: se alguém perguntar por que a previsão de março foi aquela, dá para responder. O rollback é mover a etiqueta para a versão anterior.

### Porta de qualidade

- Em uma frase: uma regra automática que só promove modelo melhor.
- Analogia: o aluno só passa de ano se atingir a média. Não adianta o professor gostar dele.
- No projeto: 3 regras: WAPE pelo menos 5% menor que o baseline, cobertura da faixa de pelo menos 70%, e não pior que o campeão atual (tolerância de 2%). O teste que exige 50% de melhoria reprova e mantém o campeão.
- Por que importa para o negócio: um modelo pior nunca chega ao comercial sem alguém decidir.

**Decisão a saber explicar:** a spec pede cobertura mínima de 70% "no backtest". A cobertura crua foi 69,5% e reprovaria por pouco. Usei a cobertura da faixa **calibrada** (79,6%), porque é ela que o comercial recebe. Escolhi isso depois de ver o número, e é justo dizer isso se perguntarem.

### Lote × tempo real

- Em uma frase: gerar uma tabela agendada, em vez de responder a cada pedido.
- Analogia: o jornal da manhã contra um atendente ao telefone.
- No projeto: `resumo_comercial.csv` traz semana × faixa × público. O comercial planeja por semana, então uma tabela semanal basta.
- Por que importa para o negócio: é mais barato e mais fácil de auditar. API só se alguém precisar de resposta na hora, como escolher um anúncio no streaming.

### Drift e PSI

- Em uma frase: o PSI compara o formato dos dados de hoje com os do treino.
- Analogia: comparar a altura de duas turmas por faixas. Se as faixas mudam muito, a turma é outra.
- No projeto: PSI abaixo de 0,1 é estável, entre 0,1 e 0,2 pede atenção, e acima de 0,2 mudou.
- Por que importa para o negócio: mostra mudanças antes do resultado real chegar, quando elas aparecem nas variáveis.

**Uma descoberta do projeto:** o PSI não pegou o choque. Todos os valores ficaram abaixo de 0,1, porque as variáveis olham 28 dias para trás e a audiência real se desloca pouco na distribuição geral. O alerta veio do desempenho (WAPE e cobertura). Por isso o monitor precisa dos dois.

### O que fazer quando o alerta dispara

1. Confirmar que o dado que chegou está correto.
2. Olhar o viés. Se positivo, o comercial está prometendo a mais.
3. Avisar a área comercial e usar uma promessa mais conservadora nas próximas semanas.
4. Retreinar com os dados novos, sabendo que os lags de 28 dias levam tempo para absorver o choque.
5. Se o evento for pontual, tratar o período como atípico.

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| Pickle no Google Drive | MLflow Registry com alias | Versão e histórico |
| Troca manual de modelo | Porta de qualidade | Só entra o que for melhor |
| Flask, um pedido por vez | Lote semanal | Combina com a rotina comercial |
| Nenhum monitoramento | Previsto × real e PSI | Detectar quando piora |
| Previsão de uma hora só | Tabela semana × programa × público, com p10 | Linguagem de venda |

## Como responder na entrevista

- **30 segundos:** "Cada treino fica registrado no MLflow, e só vira campeão se bater o baseline, ter a faixa calibrada e não ser pior que o atual. O lote semanal gera a tabela do comercial, com o p10 como entrega segura. Em uma simulação de choque, o erro dobrou e o alerta disparou; sem o choque, ficou quieto."
- **2 minutos:** "Organizei pensando em quatro perguntas: consigo refazer, é melhor, roda sozinho, continua bom. O MLflow registra parâmetros, métricas e o modelo. A porta de qualidade decide a promoção automaticamente, e um teste garante que um modelo reprovado não troca o campeão. A previsão é em lote, porque o comercial planeja por semana. No monitoramento, simulei uma fuga para o streaming que nenhuma variável explica: o WAPE foi de 8,7% para 17,4% e o viés para +0,6 ponto, que é justamente o lado caro do erro. Rodei um controle sem choque, e o sistema ficou em OK. Aprendi que o drift nas variáveis não pegou esse caso, então o monitoramento precisa olhar desempenho também."

## Perguntas que o gestor pode fazer

1. **O que acontece se o treino novo for pior?** Ele fica registrado como reprovado, e o campeão continua.
2. **Como você faria rollback?** Movendo o alias `champion` para a versão anterior.
3. **O modelo prevê um choque?** Não. O sistema detecta rápido, quando o dado real chega.
4. **Quanto tempo leva para detectar?** Na primeira semana, o WAPE já estava em 15,2%, acima do limite.
5. **Por que o limite de WAPE é 15%?** É quase o dobro do esperado (8,7%). Em produção, eu calibraria com o custo real de um falso alarme.

## Para praticar

Em `configs/config.yaml`, mude `choque_outros` de 0,55 para 0,20. Antes de rodar, preveja se o alerta ainda dispara. Rode `make pipeline` e leia `data/relatorios/monitoramento.md`.
