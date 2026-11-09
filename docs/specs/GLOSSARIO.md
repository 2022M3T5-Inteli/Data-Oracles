# Glossário em linguagem simples

## Negócio

| Termo | Significado |
| --- | --- |
| Veículo | Quem vende o espaço publicitário (a Globo) |
| Anunciante | A marca que compra o espaço |
| Agência | Planeja, negocia e cria a campanha para o anunciante |
| Kantar IBOPE Media | Empresa independente que mede audiência; a "régua" do mercado |
| People Meter | Aparelho nas casas da amostra que registra canal e quem assiste |
| Rating (ponto de audiência) | % do universo sintonizado no canal |
| Share | % das TVs ligadas sintonizadas no canal |
| TLE | Total de TVs ligadas (denominador do share) |
| Reach (alcance) | % de pessoas diferentes que viram pelo menos um pouco |
| Fidelidade | Quem chegou ficou quanto tempo (rating ÷ reach) |
| Frequência | Quantas vezes, em média, cada pessoa atingida viu |
| GRP / TRP | Alcance × frequência; TRP é dentro do público-alvo |
| CPP / CPM | Custo por ponto / custo por mil pessoas atingidas |
| Cota de patrocínio | Vaga de patrocinador num projeto, pacote fechado, preço fixo |
| Make-good | Compensação com inserções grátis quando a entrega fica abaixo do prometido |
| Entrega segura | Neste projeto: o p10, quanto dá para prometer com baixo risco |
| Incrementalidade | Resultado que só existiu por causa da mídia |
| Precificação por valor | Cobrar pelo retorno gerado, não só pela audiência |
| Dia de TV | 6h às 5h59; horas 24–29 = madrugada |

## Técnico

| Termo | Significado |
| --- | --- |
| Baseline | Previsão simples que serve de régua (média de 4 a 7 semanas atrás) |
| Lag | Valor da mesma série em outro momento (lag_28 = 28 dias antes) |
| Vazamento (data leakage) | Usar no treino informação que não existiria na hora de prever |
| Horizonte | Com quanta antecedência a previsão é feita (28 dias) |
| Backtesting | Simular o passado: treinar até uma data e prever o período seguinte, várias vezes |
| Split aleatório | Sortear linhas para treino/teste; errado em séries temporais |
| Overfitting | Modelo decora o treino e erra em dado novo |
| Árvore de decisão | Sequência de perguntas sim/não que leva a uma previsão |
| Gradient boosting | Muitas árvores pequenas em sequência, cada uma corrigindo o erro das anteriores |
| LightGBM | Implementação rápida de gradient boosting (Microsoft) |
| Regressão quantílica | Prever um quantil (ex.: p10 = valor que o real supera 90% das vezes) em vez da média |
| p10 / p50 / p90 | Limite inferior, mediana e limite superior da faixa de 80% |
| MAE | Erro absoluto médio, na unidade do alvo (pontos) |
| RMSE | Raiz do erro quadrático médio; pune erros grandes |
| MSE | Erro quadrático médio (unidade ao quadrado; usado em 2022) |
| WAPE | Soma dos erros ÷ soma do real |
| Viés | Média de (previsto − real); positivo = superestima |
| R² | % da variação explicada; não é "precisão" |
| Cobertura | % de vezes em que o real caiu dentro da faixa |
| Conformal (CQR) | Ajuste que alarga a faixa usando erros passados para garantir a cobertura |
| SHAP | Quanto cada variável empurrou uma previsão para cima ou para baixo |
| Drift | Os dados de agora deixaram de parecer com os do treino |
| PSI | Índice que mede drift (> 0,2 = mudou) |
| MLflow | Ferramenta que registra treinos (parâmetros, métricas, arquivos) e versões de modelo |
| Run / experimento | Um treino registrado / um grupo de treinos |
| Model Registry | "Cartório" de versões de modelo |
| Alias champion | Etiqueta que aponta a versão em produção |
| Porta de qualidade | Regra automática que só promove modelo melhor |
| Batch × online | Previsão em lote agendada × resposta na hora por API |
| Contrato de dados | Regras que o dado precisa cumprir (pandera) |
| CI | Robô que testa cada mudança proposta |
| CD | Robô que entrega/treina a versão aprovada |
| CT | Retreino contínuo (agendado ou por alerta) |
| GitHub Actions | Onde o CI/CD roda |
| Docker | "Caixa" com o código e tudo que ele precisa, roda igual em qualquer máquina |
| Makefile | Atalhos para comandos (`make treinar`) |
| DuckDB | Banco SQL que roda dentro do Python, sobre arquivos |
| Diferença em diferenças | Compara a mudança no grupo exposto com a mudança no não exposto |
| Placebo | Teste num período sem campanha; o efeito deveria ser zero |
| p-valor | Chance de ver um efeito desse tamanho só por acaso se não houvesse efeito |
