# 08 — Documentação: README, model card e notas de aprendizado

## 1. README.md (reescrever)

Ordem: negócio primeiro, técnica depois.
1. Título e badge do CI.
2. **O problema de negócio** em 1 parágrafo (comercial promete audiência ao anunciante semanas antes; errar para cima custa compensação).
3. **História do projeto:** 2022 (Inteli + Rede Gazeta, o que foi feito) → o que estava errado → o que mudou. Tabela antes × depois.
4. **Resultados** (preencher com os números da sua execução): backtest vs baseline, cobertura antes/depois do conformal, split aleatório vs temporal, monitoramento com o choque, incrementalidade.
5. **Arquitetura** (diagrama em texto ou Mermaid) e estrutura de pastas.
6. **Como rodar** (`make setup`, `make smoke`, `make pipeline`, `make mlflow-ui`, Docker).
7. **Como o comercial usaria** `resumo_comercial.csv` (exemplo de uma linha lida em voz alta).
8. **Limitações:** dados sintéticos; um mercado só; share e fidelidade fora; choque não previsível; faixa calibrada só no backtest.
9. **Próximos passos:** Spark/Databricks, feature store, previsão de share e de alcance de campanha, API para uso online, monitoramento em dashboard.
10. Aviso: dados sintéticos; projeto original © Inteli e integrantes (CC BY 4.0).

## 2. `docs/model_card.md`

Seções: objetivo e uso pretendido; uso **não** pretendido; dados (sintéticos, período, públicos); variáveis; modelo e hiperparâmetros; métricas (geral, horário nobre, por público, cobertura); premissas (grade conhecida com antecedência, horizonte de 28 dias); limitações e riscos (públicos pequenos mais ruidosos, choques); explicabilidade; governança e LGPD (sem dado pessoal, dados agregados); dono, versão, data, como reportar problema.

## 3. `docs/aprendizado/fase_XX.md` (uma por fase)

Modelo fixo (use a skill `explicar-como-mentora`):
1. **O que foi feito** (3–5 linhas).
2. **Conceitos em linguagem simples**, com analogia e exemplo numérico.
3. **Como era em 2022 × como ficou** e por quê.
4. **Como responder na entrevista** (frase de 30 segundos + versão de 2 minutos).
5. **Perguntas que o gestor pode fazer** (5) com respostas curtas.
6. **Para eu praticar:** 1 exercício pequeno (ex.: mudar um parâmetro e prever o efeito antes de rodar).

## 4. Critérios de aceite

- [ ] README lido por alguém de negócio faz sentido sem ler código.
- [ ] Model card completo.
- [ ] Uma nota de aprendizado por fase.
- [ ] `docs/aprendizado/roteiro_entrevista.md` final: pitch de 1 minuto do projeto, 15 perguntas prováveis com respostas, números-chave para decorar.
