# Como usar este pacote

Este pacote contém o contexto, as specs e as skills para transformar o seu fork do **Data-Oracles** (O Oráculo, Rede Gazeta 2022) no projeto de portfólio para a vaga da Globo.

## 1. Preparar o repositório

```bash
# 1. Faça o fork de github.com/2022M3T5-Inteli/Data-Oracles no GitHub e clone
git clone https://github.com/<seu-usuario>/Data-Oracles.git oraculo
cd oraculo
git checkout -b reconstrucao-mlops

# 2. Descompacte este pacote NA RAIZ do repositório (mantém as pastas):
#    CLAUDE.md, LEIA-ME_PRIMEIRO.md, docs/specs/, docs/aprendizado/, .claude/skills/, .github/copilot-instructions.md
git add CLAUDE.md docs .claude .github LEIA-ME_PRIMEIRO.md
git commit -m "fase 0: contexto, specs e roteiro da reconstrução"
```

Pré-requisitos na sua máquina: Python 3.11+, Git, VS Code. Opcionais: Docker Desktop (fase 6) e R (fase 7). Se não tiver, o CI do GitHub roda por você.

## 2. Abrir no VS Code com o assistente

- **Claude Code (extensão ou terminal):** ele lê o `CLAUDE.md` e as skills de `.claude/skills/` automaticamente. Comece com:

  > Leia o CLAUDE.md e o docs/specs/ROADMAP.md. Execute a fase 0 usando a skill oraculo-executar-fase e me explique o projeto de 2022 com a skill explicar-como-mentora.

  Depois, a cada fase:

  > Execute a fase N. Antes de codar, me explique o plano. No fim, escreva a nota de aprendizado e pare para eu revisar.

- **GitHub Copilot Chat:** ele lê `.github/copilot-instructions.md`. Peça: "Siga o CLAUDE.md e execute a fase N do docs/specs/ROADMAP.md".

## 3. Gabarito

O arquivo `oraculo-mlops-referencia.zip` (entregue junto) tem a implementação completa que já foi rodada e testada. Use para conferir números ou destravar, não para copiar de uma vez: a ideia é você acompanhar fase a fase e entender.

## 4. O que estudar enquanto o agente trabalha

1. `docs/specs/01_negocio.md` e `GLOSSARIO.md`
2. `docs/specs/00_visao_geral.md` (o diagnóstico de 2022: é o seu discurso de "o que eu faria diferente")
3. As notas em `docs/aprendizado/`, uma por fase
