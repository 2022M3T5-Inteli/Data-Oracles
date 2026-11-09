# CLAUDE.md — Contexto do projeto (leia antes de qualquer tarefa)

## Quem sou eu e o que estamos fazendo

Sou a Yasmin, analista de dados, me preparando para a vaga de **Cientista/Analista de Dados Pleno em Data Products (mídia e publicidade) na Globo**.

Este repositório é um **fork do projeto "O Oráculo" (Data-Oracles)**, que fiz em 2022 no Inteli com um time de 6 pessoas, usando dados da **Rede Gazeta** (Kantar IBOPE). O projeto original prevê a audiência de TV por faixa de 15 minutos para 14 públicos.

**Objetivo:** transformar este projeto acadêmico num projeto de portfólio com padrão de produção, que demonstre os requisitos da vaga: modelagem preditiva aplicada a mídia, estatística aplicada, SQL, Python, R, MLOps, CI/CD, explicabilidade, documentação e, acima de tudo, **entendimento do negócio de publicidade**.

**Importante sobre mim:** não lembro bem de LightGBM, métricas de erro, margem de erro, MLOps e CI/CD. **Você vai implementar e, a cada fase, me explicar o que fez e por quê**, como uma mentora. Eu preciso conseguir explicar tudo numa entrevista técnica.

## Regras de trabalho (obrigatórias)

1. **Negócio antes da técnica.** Toda decisão técnica deve ser justificada pelo uso no negócio (o comercial da Globo prometendo audiência a anunciantes). Leia `docs/specs/01_negocio.md` antes de modelar.
2. **Siga o roteiro.** Trabalhe uma fase por vez, na ordem de `docs/specs/ROADMAP.md`. Não pule fases. Ao terminar uma fase, confira os critérios de aceite dela.
3. **Explique ao final de cada fase.** Use a skill `explicar-como-mentora` e crie `docs/aprendizado/fase_XX.md` (o que foi feito, conceitos em linguagem simples, como responder na entrevista, perguntas que o gestor pode fazer).
4. **Nunca apague o projeto original.** O código de 2022 fica em `legado/` (notebooks e backend Flask). O novo código fica em `src/oraculo/`. Precisamos poder comparar antes × depois.
5. **Dados sintéticos.** Os dados reais da Gazeta são confidenciais por contrato e não estão no repositório. Gere dados sintéticos com a **mesma estrutura do Kantar** (spec `02_dados.md`). Nunca invente que são reais.
6. **Sem vazamento de dados.** A previsão é feita com 28 dias de antecedência: nenhuma variável pode usar informação dos últimos 28 dias antes da data prevista. Isso tem teste automático obrigatório.
7. **Tudo configurável.** Nada de número mágico no código: parâmetros ficam em `configs/*.yaml`.
8. **Tudo testado.** Cada módulo novo vem com teste em `tests/`. `make test` e `make lint` precisam passar antes de encerrar uma fase.
9. **Português.** Comentários, docstrings, mensagens de log, documentação e explicações em português do Brasil. Nomes de variáveis em português também (ex.: `previsoes`, `publico`), exceto termos técnicos consagrados.
10. **Comunique em linguagem de negócio.** Métricas sempre em unidade que o negócio entende (pontos de audiência, %), nunca só "MSE = 0,63".
11. **Honestidade.** Se um resultado for ruim, diga. Se algo não puder ser rodado no meu ambiente, diga o que faltou.

## Mapa dos documentos

| Arquivo | Para quê |
| --- | --- |
| `docs/specs/00_visao_geral.md` | Diagnóstico do projeto de 2022, o que manter/mudar/acrescentar, arquitetura alvo, requisitos da vaga |
| `docs/specs/01_negocio.md` | Como a Globo vende publicidade, métricas de audiência, para que serve a previsão |
| `docs/specs/02_dados.md` | Gerador de dados sintéticos e contratos de dados |
| `docs/specs/03_features.md` | Base analítica em SQL (DuckDB), lags, regra anti-vazamento |
| `docs/specs/04_modelagem.md` | Baseline, LightGBM quantílico, backtesting, métricas, faixa de previsão, SHAP |
| `docs/specs/05_mlops.md` | MLflow, porta de qualidade, previsão em lote, monitoramento, orquestração |
| `docs/specs/06_cicd.md` | GitHub Actions, Docker, Makefile, testes |
| `docs/specs/07_incrementalidade_r.md` | Teste de efeito de campanha em R (diferença em diferenças) |
| `docs/specs/08_documentacao.md` | README, model card, notas de aprendizado |
| `docs/specs/ROADMAP.md` | Ordem das fases, tarefas e critérios de aceite |
| `docs/specs/GLOSSARIO.md` | Termos de negócio e técnicos em linguagem simples |

## Comandos (depois da fase 1)

```bash
make setup      # instala
make smoke      # pipeline inteiro em segundos (dados pequenos)
make pipeline   # pipeline completo
make test       # testes
make lint       # estilo
make mlflow-ui  # interface do MLflow
```

## Stack

Python 3.11+, pandas, DuckDB (SQL), LightGBM, scikit-learn, MLflow, pandera, matplotlib, pytest, ruff, Docker, GitHub Actions, R (base, sem pacotes extras).
