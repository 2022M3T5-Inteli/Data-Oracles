# Fase 00 — Entender o projeto de 2022 e o negócio

## O que foi feito

Li o README, os notebooks de feature engineering, LightGBM e inputs, o backend Flask, o front-end (só a parte que chama a API) e as seções centrais do PDF V4.0. Nos notebooks de KNN, Random Forest e Árvore, conferi a divisão dos dados e as métricas.
Conferi cada item do diagnóstico de `docs/specs/00_visao_geral.md` §1–2, apontando arquivo e célula.
Nenhum código de produção foi escrito. Os notebooks não foram reexecutados, porque os dados reais não estão no repositório.
Resultado: os 10 problemas da spec se confirmam, e apareceram 6 problemas novos. O mais grave é que a API ignorava quase todas as variáveis.
Depois da leitura, removi das saídas dos notebooks as tabelas com linhas de audiência e de grade, porque os dados são confidenciais. Código, métricas, logs e gráficos continuam lá.

**Como ler as referências:** "FE" é `legado/notebooks/Feature_Engineering.ipynb` e "LGBM" é `legado/notebooks/LightGBM_Avaliação_dos_Modelos_e_Hyperparâmetros.ipynb`. A numeração de células começa em 0.

## O que o time fez em cada etapa, e por quê

O time seguiu o CRISP-DM, um roteiro que começa no negócio e termina na implantação.

| Etapa | O que foi feito | Por quê | Onde |
| --- | --- | --- | --- |
| Negócio | Problema: decidir grade e estreias sem base preditiva. Persona: Thiago, gerente de programação | Definir quem usa a previsão e para qual decisão | PDF §1–2 e §4.1.6 |
| Dados | Planilha Kantar de 18 abas e 437.754 KB; grade diária; feriados | Audiência sozinha não diz o que estava no ar | PDF §4.2 |
| Preparação | Extrair programa e categoria (FE 10); juntar seg-sex, sáb e dom (FE 17); unir com a grade (FE 26); criar mês, dia e ano (FE 35); converter hora e dia da semana em número (FE 37–38); one-hot da categoria (FE 40); marcar feriado (FE 48–50) | Modelos só leem números, e cada linha precisa dizer o que estava no ar | FE 4–55 |
| Modelagem | Regressão linear, KNN, random forest, árvore e LightGBM | Comparar famílias de modelo diferentes | FE 75–98 e notebooks por modelo |
| Ajuste | GridSearch e RandomSearch no KNN; Optuna via verstack no LightGBM | Extrair o melhor de cada modelo | KNN 20–24, LGBM 18–25 |
| Avaliação | R² e MSE em treino e teste; LightGBM escolhido | Escolher o modelo final | LGBM 14, PDF §4.5–4.6 e §5 |
| Implantação | Pickle no Drive → API Flask → Docker → Fly.io → site React | Dar acesso a quem não programa | `legado/backend/`, `legado/frontend/` |

## Diagnóstico conferido (`00_visao_geral.md` §1)

| Item | Veredito | Evidência |
| --- | --- | --- |
| Pergunta de negócio | Confirmado | `README.md` linha 19; PDF §2.1 |
| Usuário | Confirmado | PDF §4.1.6 |
| Dados | Confirmado, com ajuste | PDF §4.2; FE 4 e 15. O período tem 760 dias (1/6/2020 a 30/6/2022), cerca de 25 meses, e não 24 |
| Alvos | Confirmado | `legado/backend/modelo_geral.py:18-38`; fidelidade comentada nas linhas 25–32 |
| Variáveis | Confirmado, com ajuste | `legado/backend/modelos.py:67`; LGBM 6. Ver "blocos de 15 min" abaixo |
| Modelos | Confirmado | FE 75, 81, 84, 90 e 96; LGBM 13 |
| Ajuste de hiperparâmetros | Confirmado, com ajuste | LGBM 21, 23 e 25: o ajuste usou só o público Total, e os parâmetros valeram para os 14 |
| Validação | Confirmado | LGBM 9; FE 62; KNN 8; Random Forest 8; Árvore 8. Sem `test_size`, vale o padrão de 25% |
| Métricas | Confirmado | LGBM 14 |
| Resultado | Confirmado, com ajuste | LGBM 14. Sobre fidelidade, ver a seção de resultados |
| Entrega | Confirmado, com ajuste | LGBM 28; `legado/backend/app.py:80,100`; `legado/backend/Dockerfile`; `legado/backend/fly.toml`. Ver achado 6 |

**Ajuste sobre os "blocos de 15 min".** FE 37–38 só arredondam o rótulo da hora. As linhas continuam de 5 em 5 minutos, sem agregação (a saída de LGBM 2 mostrava três linhas por rótulo, antes da limpeza descrita em "O que foi feito"). Por isso, três linhas têm as mesmas variáveis e alvos diferentes.

**Ajuste sobre as 27 categorias.** São 29 valores em FE 31. `NAO CONSTA` sai em FE 33 e `drop_first` remove `AUDITORIO` em FE 40. Sobram 27 colunas, e auditório vira "todas as colunas em zero".

## Problemas da spec (`00_visao_geral.md` §2)

| # | Problema | Veredito | Evidência |
| --- | --- | --- | --- |
| 1 | Divisão aleatória | Confirmado | LGBM 9. KNN com R² 0,953 (FE 82) contra LightGBM com 0,956 (LGBM 14) |
| 2 | Sem lags | Confirmado | LGBM 6; nenhum `shift` ou `rolling` nos seis notebooks |
| 3 | Concorrência ignorada | Confirmado | FE 28 descarta `Emissora B` e `Emissora C`; FE 15 só lê a Emissora A; as abas de TLE nunca são carregadas |
| 4 | Sem tendência ou ano | Confirmado | `Ano` é criado (FE 35) e mantido (FE 53), mas fica fora do `X` (LGBM 6) |
| 5 | Sem baseline de negócio | Confirmado | A única comparação de base é a regressão linear (FE 75) |
| 6 | Previsão pontual | Confirmado | `modelo_geral.py:14` devolve um único valor |
| 7 | Métricas mal nomeadas | Confirmado, e é pior | LGBM 14 chama R² de "Precisão". FE 104–105, 111–112 e 118–119 plotam MSE com o título "Mean Absolute Error" |
| 8 | `dropna()` sem efeito | Confirmado | FE 33. Sem os dados, não dá para medir quantas linhas seriam removidas |
| 9 | Erro conceitual de reach | Confirmado | PDF §4.2, Tabela 1, p. 24: a linha `Rch%` diz "É o RAT e divide pelo TLE" e a linha `Shr%` está em branco. Conferido no `.docx`. Provavelmente a descrição caiu uma linha abaixo da certa |
| 10 | Sem engenharia de produção | Confirmado | LGBM 3 e 28; `modelos.py:26-28`; `.gitignore` exclui `**/modelos`; `teste.py` importa `KNN_MODELO`, que não existe mais, e não tem nenhum `assert` |

## Achados novos (fora da spec)

### 1. A API ignorava data, feriado e categoria (grave)

Em `legado/backend/modelo_geral.py:66` e `:76`, o código faz `X[0] = start`. `X` é uma matriz com uma linha, então `X[0]` é a linha inteira. A intenção era trocar só a hora, com `X[0][0] = start`.

Testei a classe real com um modelo falso que registra o que recebe:

```text
enviado:              [20.0, 3, 7, 15, 0, ...]
recebido pelo modelo: [20.0, 20.0, 20.0, 20.0, 20.0, ...]   (as 32 colunas iguais)
```

Duas entradas bem diferentes (uma novela numa quarta e um futebol num feriado, às 20h) geraram vetores idênticos. Portanto, **no código versionado, o site dava a mesma previsão para qualquer dia e categoria naquela hora**. O R² de 0,956 foi medido no notebook e nunca descreveu o que aparecia no site.

Ligação com o negócio: é o tipo de erro que só aparece com um teste. O modelo responde um número plausível e ninguém percebe.

### 2. Feriados com dia e mês trocados

FE 46 usa `pd.to_datetime` em datas `dd/mm/aaaa`. O padrão do pandas lê primeiro o mês. A saída da própria célula mostra o Carnaval de `04/03/2019` virando 3 de abril e o de `05/03/2019` virando 3 de maio. Datas com dia maior que 12 escapam, como `19/04/2019`, porque não existe mês 19. Pela mesma regra, 7 de setembro viraria 9 de julho.

Consequência: a variável `Feriado` marcava dias errados.

### 3. Três codificações de dia da semana

| Dia | Treino (FE 37) | API (`modelos.py:58`) | Notebook de inputs (célula 5) |
| --- | --- | --- | --- |
| Segunda | 1 | 0 | 1 |
| Sábado | 6 | 5 | 6 |
| Domingo | 0 | 6 | 7 |

A API deslocava todos os dias. O notebook de inputs enviava um valor (7) que o modelo nunca viu. O achado 1 escondia esse problema na API.

### 4. O LightGBM não venceu pelos números do próprio documento

No PDF §4.5.2, o KNN ajustado tem R² 0,958 e MSE 0,608 em rating, contra 0,956 e 0,634 do LightGBM. Em share, o KNN tem 0,895 e 35,1, e o LightGBM tem 0,889 e 37,2. Mesmo assim, o §5 afirma que o LightGBM teve os melhores valores.

Existe um argumento defensável: o KNN levou 27 minutos em FE 81 e precisa guardar todo o treino para prever. Só que esse argumento não está na conclusão.

### 5. Erros de leitura no PDF

- Na seção de Random Forest, os MSE citados (0,2797 e 0,6821) são os do KNN (FE 82). Os do Random Forest são 0,2178 e 0,7965 (FE 85).
- O §4.6 trata "MSE acima de zero" como sinal de overfitting. MSE nunca é negativo, e o que indica overfitting é a distância entre treino e teste.

### 6. O deploy não é reproduzível a partir do repositório

- O `Dockerfile` instala `requirements.txt`, que não tem `lightgbm`. O pacote está só em `requirementsv2.txt`.
- O `fly.toml` espera a porta 8080, e `flask run` usa a 5000.
- O front-end aponta para `localhost:5000` (`legado/frontend/src/data/oracle.tsx:3`).
- Os modelos estão fora do Git.

Dois detalhes menores: a API devolvia a média de uma hora inteira, e não de 15 minutos. E o minuto 5 gera a chave `20:5:00`, que não existe no dicionário (o site só oferecia horas cheias, então isso não chegava a aparecer).

## Conceitos

Os exemplos usam 1.000 domicílios, 600 com TV ligada, 120 no canal (média) e 300 que passaram pelo canal.

### Rating (Rat%)

- Em uma frase: a porcentagem do universo que está no canal.
- Analogia: de todos os moradores do prédio, quantos estão na festa do 3º andar.
- No projeto: 120 ÷ 1.000 = 12 pontos. Era o alvo principal em 2022.
- Por que importa para o negócio: é a moeda. O anunciante compra pontos de rating no público dele.

### Share (Shr%)

- Em uma frase: dos que estão vendo TV, quantos escolheram o canal.
- Analogia: dos moradores que saíram de casa, quantos foram à festa do 3º andar.
- No projeto: 120 ÷ 600 = 20%. O denominador é o TLE, o total de TVs ligadas.
- Por que importa para o negócio: mostra a disputa com a concorrência. Um rating pode cair e o share subir, se a TV inteira perdeu público.

### Reach (Rch%)

- Em uma frase: quantas pessoas diferentes passaram pelo canal, nem que por pouco tempo.
- Analogia: a lista de quem entrou na festa, mesmo que por cinco minutos.
- No projeto: 300 ÷ 1.000 = 30%. O PDF de 2022 descreve reach como RAT ÷ TLE. Essa conta dá 12 ÷ 60 = 20%, que é o share.
- Por que importa para o negócio: uma campanha que quer ser vista por muita gente precisa de alcance, não só de pontos.

### Fidelidade (Fid%)

- Em uma frase: de quem chegou, quanto ficou.
- Analogia: quem entrou na festa ficou até o fim ou só pegou um salgadinho?
- No projeto: rating ÷ reach = 12 ÷ 30 = 40%. Foi descartada em 2022.
- Por que importa para o negócio: indica se o público fica até o intervalo comercial. Em público pequeno, é muito ruidosa.

### Os 14 públicos

- Em uma frase: os recortes de audiência que o anunciante compra.
- Analogia: não basta saber quantos foram à festa, a marca de fralda quer saber quantos têm filhos pequenos.
- No projeto: 1 total + 4 classes + 2 sexos + 7 faixas etárias.

| Grupo | Públicos |
| --- | --- |
| Total | Total Domicílios (em rating e share); Total Indivíduos (em reach e fidelidade) |
| Classe (Critério Brasil) | AB, C1, C2, DE |
| Sexo | Masculino, Feminino |
| Idade | 4-11, 12-17, 18-24, 25-34, 35-49, 50-59, 60+ |

- Por que importa para o negócio: o preço depende do público. Quanto menor o recorte, menos casas na amostra e mais ruído. O total é medido em domicílios e os outros recortes em pessoas, então os pontos não se somam.

### Divisão aleatória × divisão no tempo

- Em uma frase: sortear linhas deixa o treino ver informação do mesmo dia que está sendo testado.
- Analogia: estudar com a prova de amanhã misturada à de ontem.
- No projeto: conferi que mês + dia + dia da semana formam uma combinação única nos 760 dias (760 combinações, nenhuma repetida). Essas variáveis funcionam como uma etiqueta da data exata. Com o sorteio, o treino recebe linhas do mesmo dia e da mesma faixa que estão no teste. Isso explica bem por que um KNN com 3 vizinhos, que só procura as linhas mais parecidas, empatou com o LightGBM. É uma hipótese forte, ainda não medida. A fase 4 vai medir em dados sintéticos.
- Por que importa para o negócio: uma data futura tem uma combinação que o modelo nunca viu, e a venda acontece semanas antes.

### R² e MSE

- Em uma frase: R² diz quanto da variação o modelo explica; MSE é a média dos erros ao quadrado.
- Analogia: R² é a nota de "quanto do padrão você captou". MSE é uma multa que cresce muito com erros grandes.
- No projeto: MSE de 0,634 tem raiz de cerca de 0,8 ponto. R² de 0,956 não significa "acertar 95,6%".
- Por que importa para o negócio: ninguém do comercial decide com "MSE 0,63". Decide com "erro de cerca de 0,8 ponto".

### Baseline

- Em uma frase: uma previsão de referência, barata, que o modelo precisa vencer.
- Analogia: antes de contratar um meteorologista, compare com "amanhã vai ser igual a hoje".
- No projeto: em 2022 só havia a regressão linear (R² 0,317), que é fácil demais de vencer. Na fase 4 entra "média de 4 a 7 semanas atrás".
- Por que importa para o negócio: se a média resolver, não há por que pagar a manutenção de um modelo.

## Resultados lidos criticamente

Teste com divisão aleatória, média dos 14 públicos. Modelos sem ajuste em FE 75–91; LightGBM ajustado em LGBM 14.

| Modelo | Rating R² | Rating MSE | Raiz (pontos) | Share R² | Share MSE | Raiz (pontos) | Fid. R² |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Regressão linear | 0,317 | 11,09 | 3,33 | 0,116 | 290,4 | 17,0 | 0,062 |
| Árvore | 0,935 | 0,950 | 0,97 | 0,875 | 41,9 | 6,5 | 0,527 |
| Random Forest | 0,945 | 0,796 | 0,89 | 0,895 | 35,5 | 6,0 | 0,611 |
| KNN | 0,953 | 0,682 | 0,83 | 0,889 | 37,2 | 6,1 | 0,602 |
| LightGBM | 0,956 | 0,634 | 0,80 | 0,890 | 37,2 | 6,1 | 0,525 |

1. **Os números são otimistas.** A divisão foi aleatória e a previsão usa só calendário e categoria, sem antecedência definida.
2. **A diferença entre os modelos é pequena.** LightGBM e KNN diferem em 0,03 ponto de rating.
3. **Em share, o LightGBM não lidera.** Nesta tabela, o Random Forest ganha.
4. **Há distância entre treino e teste.** O MSE de rating do LightGBM vai de 0,275 para 0,634, mais que o dobro.
5. **A raiz do MSE é aproximada.** Ela vem da média dos 14 públicos e não é o erro de um público específico.
6. **Falta a porcentagem.** WAPE e erro percentual exigem o valor real das previsões, e não dá para calcular sem os dados.
7. **Sobre fidelidade, o motivo é mais complicado do que "overfitting".** O §5 do PDF fala em overfitting, e ele existe na árvore e no Random Forest. Mas o LightGBM tem R² de 0,604 no treino e 0,525 no teste, uma distância pequena. O problema dele é explicar pouco: o erro fica em cerca de 17 pontos. O próprio §4.6 sugere que os dados não bastam. Minha hipótese é ruído de amostra em públicos pequenos.

Para dar escala, com números ilustrativos: 0,8 ponto é 8% de um bloco de 10 pontos, e 40% de um bloco de 2 pontos. Um único número de erro esconde onde dói.

## 2022 × agora

A coluna "Agora" é o plano das próximas fases.

| Antes | Agora | Por quê |
| --- | --- | --- |
| Divisão aleatória | Backtesting com horizonte de 28 dias | A venda acontece antes e a data futura é inédita |
| Só calendário e categoria | Lags de 28 dias ou mais, concorrência, tendência | O histórico é o sinal mais forte e existe na hora da venda |
| R² chamado de precisão, MSE | MAE em pontos, WAPE, viés, cobertura | O comercial decide em pontos e porcentagem |
| Um número | Faixa p10–p90 | O p10 é o que dá para prometer com baixo risco |
| Sem baseline de negócio | Média de 4 a 7 semanas atrás | Saber se o modelo vale o custo |
| Pickle no Drive | MLflow com porta de qualidade | Saber qual versão está em uso e por quê |
| Sem testes | Testes de contrato e anti-vazamento | O achado 1 passaria despercebido sem eles |
| API que recebe um pedido por vez | Previsão em lote semanal | O comercial planeja por semana, não em tempo real |

## Como responder na entrevista

- **30 segundos:** "Em 2022, meu time previu a audiência da TV Gazeta por faixa horária e 14 públicos, com dados Kantar. O R² deu 0,956. Revisando o projeto, vi que a divisão aleatória inflava esse número, que não usávamos histórico de audiência e que nossa API tinha um bug que ignorava a data e a categoria. Estou refazendo com validação no tempo, previsão 28 dias antes e faixa de erro, porque o comercial precisa saber quanto pode prometer sem ter que compensar o anunciante."
- **2 minutos:** "O projeto nasceu para apoiar decisões de grade. Unimos a audiência da Kantar, a grade e os feriados, testamos cinco famílias de modelo e colocamos um LightGBM atrás de uma API. Olhando hoje, vejo três grupos de problema. Primeiro, a validação: sorteamos linhas de uma série temporal, e mês, dia e dia da semana identificavam a data exata, então o modelo via o próprio dia no treino. O sinal disso é que um KNN com 3 vizinhos empatou com o LightGBM. Segundo, o problema estava mal enquadrado para quem vende: sem previsão com antecedência, sem margem de erro e sem olhar a direção do erro. Quem promete mais do que entrega compensa o anunciante com inserções grátis. Terceiro, a engenharia: encontrei um bug em que uma atribuição sobrescrevia todas as variáveis com a hora, e as datas de feriado estavam com dia e mês trocados. Nenhum teste pegaria, porque não tínhamos testes. Por isso a nova versão começa pelo uso comercial, valida no tempo e testa contratos de dados."

## Perguntas que o gestor pode fazer

1. **O R² de 0,956 estava errado?** A conta estava certa, mas respondia à pergunta errada. Ele mede o acerto em linhas sorteadas do mesmo período, e não a previsão de uma data futura.
2. **Por que prever rating, e não share?** Rating é o que se vende. Share ajuda a entender a concorrência, mas o contrato com o anunciante é em pontos.
3. **Por que descartaram fidelidade?** O documento diz overfitting. Olhando os números, o LightGBM explicava pouco, com erro de cerca de 17 pontos. Faltava sinal, provavelmente por ruído de amostra em públicos pequenos.
4. **Como esse bug da API passou?** Não havia teste. Um teste de duas linhas pegaria: mudar a categoria e exigir que o vetor enviado ao modelo mude também.
5. **Qual a primeira coisa que você mudaria?** A validação. Sem validar como se fosse a vida real, não sei se qualquer outra melhoria ajuda ou só parece ajudar.

## Para praticar

Antes de rodar, escreva o que cada `print` vai mostrar. Depois rode e compare.

```python
import numpy as np

X = np.array([[20.0, 3, 7, 15, 0]])
X[0] = 99
print(X)

X = np.array([[20.0, 3, 7, 15, 0]])
X[0][0] = 99
print(X)
```

Depois responda em voz alta, em até 30 segundos: "Qual dessas duas linhas o time de 2022 queria escrever, e o que o usuário do site perdeu por causa da outra?"
