# Fase 06 — CI/CD e Docker

## O que foi feito

Criei o `Dockerfile` e os workflows `.github/workflows/ci.yml` e `cd.yml`.
A imagem construiu e rodou o pipeline de fumaça na sua máquina, e o CI passou no GitHub nos dois jobs (testes e Docker), em um push na branch.

**O que ainda não foi verificado:** o CD só roda quando o código entra na `main`, e a abertura do pull request depende do seu login no GitHub. Quando você fizer o merge, confira a aba Actions.

## Conceitos

### CI, CD e CT

- Em uma frase: CI confere cada mudança, CD entrega o que foi aprovado, CT retreina o modelo.
- Analogia: CI é o corretor que revisa antes de publicar. CD é o correio que só entrega o aprovado. CT é a edição atualizada toda semana.
- No projeto: CI roda em cada pull request. CD roda ao entrar na `main` e, por agendamento, toda segunda às 6h de Brasília.
- Por que importa para o negócio: uma mudança que quebra o teste anti-vazamento não chega à previsão que o comercial usa.

### O que acontece em um pull request, passo a passo

1. Você propõe a mudança e o GitHub dispara o `ci.yml`.
2. Uma máquina Linux limpa baixa o código e instala o Python 3.11.
3. `pip install -e ".[dev]"` instala o projeto.
4. `ruff check` e `ruff format --check` conferem o estilo.
5. `pytest` roda os 42 testes, inclusive o anti-vazamento e o pipeline de fumaça.
6. Se tudo passar, o segundo job constrói a imagem e roda a fumaça dentro dela.
7. O pull request mostra verde ou vermelho.

### Como ler um log de CI que falhou

1. Abra a aba Actions e clique na execução vermelha.
2. Clique no job com X e abra o passo com X.
3. Vá para o **fim** do log: o erro real costuma estar nas últimas linhas.
4. Procure `FAILED` (pytest) ou `Error`.
5. Reproduza no seu computador com o mesmo comando (`make test`, por exemplo).

O CI desta fase passou de primeira, então não houve falha de CI para explicar. Os erros reais apareceram antes, nos testes locais:

| Fase | Erro | Como foi pego |
| --- | --- | --- |
| 2 | O YAML leu `4_17` como o número 417 | O `pyarrow` recusou a coluna |
| 5 | Com ajuste conformal negativo, o p10 ficava acima do p50 | Teste de fumaça da ordem dos quantis |
| 5 | MLflow recusou inteiro onde o esquema pedia decimal | Execução de `make prever` |

### Docker

- Em uma frase: uma caixa com o código e tudo de que ele precisa, que roda igual em qualquer máquina.
- Analogia: um contêiner de navio. O porto não precisa saber o que tem dentro.
- No projeto: `python:3.11-slim` com `libgomp1`, que o LightGBM exige. Copio `pyproject.toml` e `src` antes de instalar, e as camadas ficam em cache.
- Por que importa para o negócio: acaba com o "na minha máquina funciona".

Em 2022, o Dockerfile subia uma API Flask com Python 3.8 e instalava um `requirements.txt` sem `lightgbm`. Agora a imagem roda o pipeline em lote, sem usuário root, e o CI prova que ela funciona a cada mudança.

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| Nenhum CI | Estilo, testes e Docker a cada mudança | Erro aparece antes de entrar |
| Deploy manual na Fly.io | CD que treina e publica resultados | Repetível e auditável |
| `requirements.txt` incompleto | Imagem testada no CI | A entrega funciona de verdade |
| Treino manual no Colab | Retreino agendado toda segunda | O modelo acompanha os dados |

## Como responder na entrevista

- **Frase de 1 minuto:** "Cada mudança passa por um robô que confere estilo, roda os testes, incluindo o anti-vazamento, e constrói a imagem Docker. Se algo falha, a mudança não entra. Ao chegar na main, e toda segunda, o CD treina o modelo completo, passa pela porta de qualidade e publica relatórios e a tabela do comercial. No meu projeto os artefatos ficam no GitHub, e numa empresa esse mesmo fluxo apontaria para o MLflow do Databricks e para o data warehouse."
- **30 segundos:** "CI confere, CD entrega e CT retreina. O Docker garante que o que testei é o que roda."

## Perguntas que o gestor pode fazer

1. **Qual a diferença entre CI e CD?** CI verifica a mudança antes de entrar. CD entrega o que entrou.
2. **O que é específico de ML nisso?** O CT, a porta de qualidade e os testes de dados: o código pode estar certo e o modelo piorar.
3. **O alerta do monitor bloqueia o CD?** Não. Ele aparece como aviso, para os resultados continuarem publicados.
4. **Por que a config de fumaça?** O CI precisa ser rápido. Ela roda o pipeline inteiro com dados pequenos.
5. **Como você migraria para Databricks?** O SQL vai para Spark SQL, o MLflow já é o mesmo e o agendamento vira um Workflow.

## Para praticar

Crie uma branch, mude `horizonte_dias` para 14 em `configs/config.yaml` e abra um pull request. Antes, escreva se o CI deve passar e por quê. Veja o resultado na aba Actions.
