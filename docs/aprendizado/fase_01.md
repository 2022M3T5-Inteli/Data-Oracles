# Fase 01 — Reorganizar o repositório

## O que foi feito

O código de 2022 foi para `legado/` com `git mv`, o que preserva o histórico de cada arquivo.
Criei o esqueleto novo: `pyproject.toml`, `Makefile`, `configs/`, `src/oraculo/config.py`, `.env.example` e `tests/`.
`make setup` cria um ambiente virtual com Python 3.11 e instala tudo. `import oraculo`, `make test` (3 testes) e `make lint` passaram.

## Conceitos

### `git mv` e o histórico

- Em uma frase: mover um arquivo avisando o Git, para ele continuar sabendo de onde o arquivo veio.
- Analogia: mudar de endereço fazendo a transferência do correio, em vez de abandonar a casa.
- No projeto: 89 arquivos foram para `legado/`. `git log --follow legado/backend/app.py` ainda mostra os commits de 2022.
- Por que importa para o negócio: dá para mostrar o antes e o depois, que é o centro do seu discurso na entrevista.

### Ambiente virtual e `pyproject.toml`

- Em uma frase: uma instalação isolada de Python, com a lista de dependências declarada em um arquivo.
- Analogia: uma cozinha separada para cada receita, com a lista de ingredientes colada na porta.
- No projeto: `requires-python = ">=3.11"`. Em 2022, o `requirements.txt` usado pelo Docker não tinha `lightgbm`, e isso quebrava a imagem.
- Por que importa para o negócio: o resultado que vai para o comercial precisa poder ser refeito por outra pessoa.

### Configuração fora do código

- Em uma frase: todo número que alguém pode querer mudar fica em um YAML.
- Analogia: o termostato fica na parede, você não abre a parede para mudar a temperatura.
- No projeto: `configs/smoke.yaml` tem a linha `herda: config.yaml` e declara só o que muda. Em 2022, `random_state=42` e os hiperparâmetros estavam espalhados pelas células.
- Por que importa para o negócio: mudar o horizonte de 28 para 42 dias vira uma linha revisável, não uma caça no código.

### Makefile

- Em uma frase: um arquivo de atalhos para comandos longos.
- Analogia: botões de "lavagem rápida" e "lavagem pesada" na máquina de lavar.
- No projeto: `make test` roda `python -m pytest` no ambiente certo. O CI e você usam os mesmos comandos.
- Por que importa para o negócio: reduz o "na minha máquina funciona".

## 2022 × agora

| Antes | Agora | Por quê |
| --- | --- | --- |
| `notebooks/` e `src/` misturando tudo | `legado/` separado de `src/oraculo/` | Comparar antes e depois sem confundir |
| Dependências incompletas | `pyproject.toml` e `.venv` | Instalação repetível |
| Parâmetros dentro das células | `configs/*.yaml` | Mudança pequena, revisável e testada |
| Caminhos do Google Drive | `pasta_dados(cfg)`, relativo ou absoluto | Roda em qualquer máquina |

## Como responder na entrevista

- **30 segundos:** "Separei o código original em uma pasta de legado, preservando o histórico, e criei uma estrutura de pacote Python com configuração em YAML e um Makefile. Assim, qualquer pessoa instala e roda com dois comandos."
- **2 minutos:** "O projeto de 2022 vivia em notebooks do Colab, com caminhos do Drive e parâmetros dentro das células. Antes de melhorar o modelo, eu precisava de uma base que pudesse ser repetida. Movi tudo com `git mv`, criei um pacote com `pyproject.toml` e um ambiente isolado, coloquei os parâmetros em YAML, com uma configuração de fumaça que herda da principal, e padronizei os comandos no Makefile. O ganho é que CI, Docker e eu usamos exatamente o mesmo caminho."

## Perguntas que o gestor pode fazer

1. **Por que não apagar o código antigo?** Porque ele é a linha de base da comparação e tem autoria de seis pessoas.
2. **Por que YAML e não variáveis no código?** Permite mudar parâmetros sem mexer em lógica, e o valor usado fica registrado.
3. **Para que serve o `.env.example`?** Mostra quais variáveis locais existem. O `.env` de verdade não vai para o Git.
4. **Por que Python 3.11, se a máquina tinha o 3.14?** Bibliotecas de ML demoram para suportar versões novas. Fixei a versão que o CI e o Docker também usam.
5. **O que é a configuração de fumaça?** Uma versão reduzida do pipeline, que roda rápido, para descobrir cedo se algo quebrou.

## Para praticar

Abra `configs/smoke.yaml`, troque `dados: data_smoke` por `dados: minha_pasta` e preveja qual dos três testes de `tests/test_config.py` vai falhar. Rode `make test`, compare e desfaça a mudança.
