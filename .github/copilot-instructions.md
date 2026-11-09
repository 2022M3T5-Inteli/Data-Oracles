# Instruções para o GitHub Copilot (e outros assistentes no VS Code)

Este repositório segue o contexto e as regras de `CLAUDE.md` na raiz. Leia esse arquivo antes de sugerir código.

Resumo:
- Projeto: transformação do "O Oráculo" (Inteli/Rede Gazeta, 2022) num pipeline de previsão de audiência com MLOps para a vaga de Data Products da Globo.
- Trabalhe fase a fase conforme `docs/specs/ROADMAP.md`; specs detalhadas em `docs/specs/`.
- Código novo em `src/oraculo/`; código de 2022 preservado em `legado/`.
- Dados sintéticos (os reais são confidenciais). Sem vazamento: variáveis de histórico com ≥ 28 dias de defasagem.
- Português em comentários, logs e docs. Parâmetros em `configs/*.yaml`. Testes em `tests/`.
- Ao final de cada fase, gere `docs/aprendizado/fase_XX.md` explicando os conceitos de forma didática (ver `.claude/skills/explicar-como-mentora/SKILL.md`).
