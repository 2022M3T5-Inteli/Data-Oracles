---
name: oraculo-executar-fase
description: Use para executar uma fase do ROADMAP de transformação do projeto O Oráculo (Rede Gazeta) no projeto de portfólio para a vaga da Globo, seguindo as specs e critérios de aceite.
---

# Executar uma fase do roadmap

Quando a Yasmin pedir "faça a fase N" (ou "próxima fase"):

1. **Ler o contexto.** `CLAUDE.md`, `docs/specs/ROADMAP.md` (seção da fase) e a spec indicada. Conferir em `docs/aprendizado/` quais fases já foram feitas. Se a fase anterior não tem nota de aprendizado nem commit, avisar antes de seguir.
2. **Explicar o plano em 5 linhas**, em linguagem de negócio, antes de mexer em código: o que será feito, por que importa para o comercial da Globo e o que muda em relação a 2022.
3. **Implementar** só o que a fase pede. Código em `src/oraculo/`, parâmetros em `configs/`, testes em `tests/`. Comentários e logs em português. Nada de número mágico.
4. **Rodar e conferir.** `make test`, `make lint` e o alvo da fase (`make dados`, `make features`...). Comparar números com `docs/specs/00_visao_geral.md` §7. Se algo divergir muito, investigar e explicar; nunca esconder resultado ruim.
5. **Checar os critérios de aceite** da spec, marcando cada um como ok ou não, com evidência (saída de comando, arquivo gerado).
6. **Escrever `docs/aprendizado/fase_XX.md`** com a skill `explicar-como-mentora`.
7. **Commit** com mensagem `fase XX: <resumo>` (só se a Yasmin tiver pedido commits; senão, sugerir a mensagem).
8. **Parar** e resumir em até 8 linhas: o que foi entregue, números principais, o que ela deve ler primeiro e a pergunta de entrevista mais provável sobre esta fase.

Regras fixas: nunca apagar `legado/`; dados sempre sintéticos e declarados como tal; teste anti-vazamento sempre verde a partir da fase 3; se algo não puder rodar no ambiente dela (ex.: Docker ou R ausentes), dizer o que falta e como instalar.
