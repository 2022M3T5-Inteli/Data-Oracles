---
name: negocio-publicidade-globo
description: Use quando uma decisão técnica do projeto precisar ser justificada pelo negócio de publicidade da Globo, ou quando a Yasmin pedir para relacionar o projeto com a vaga (comercial, cotas, precificação, mensuração).
---

# Negócio de publicidade da Globo — guia rápido para decisões

Fonte completa: `docs/specs/01_negocio.md`. Use este resumo para justificar escolhas.

## Fatos para não errar

- A vaga é do lado de quem **vende** publicidade (veículo), na célula de Data Products, junto de engenharia e inteligência de dados.
- O anunciante compra **a audiência prevista do programa no público dele**, não o horário.
- Venda acontece com semanas ou meses de antecedência → horizonte de previsão de 28 dias no projeto.
- **Rating** é a moeda comercial (ponto vendido). Share mostra disputa com a concorrência.
- Prometer mais do que entrega → **make-good** (compensação grátis): é o erro mais caro. Por isso viés e p10 importam.
- **Cotas de patrocínio:** pacote fechado, preço fixo, exclusividade de segmento, prioridade de renovação. Precisam de previsão de entrega antes e prova de resultado depois.
- **Precificação por valor** depende de **incrementalidade** (quanto a mídia causou de resultado).
- Mercado em fragmentação: streaming e canais digitais (ex.: CazéTV na Copa 2026) dividem a atenção. A Globo segue líder somando plataformas, mas a previsão ficou mais difícil e a prova de efeito mais valiosa.
- Dados de audiência vêm do painel da Kantar (amostra): públicos pequenos têm mais ruído.

## Perguntas para justificar uma escolha técnica

1. Que decisão do comercial isso apoia?
2. Qual erro custa mais nessa decisão (para cima ou para baixo)?
3. A informação usada existiria no momento da venda?
4. Um baseline simples resolveria? (a vaga valoriza saber quando NÃO modelar)
5. Como eu explico o resultado em pontos ou reais para alguém do comercial?

## Ligações projeto → vaga

previsão de entrega (modelo + faixa) · estimativa de resultado (resumo comercial) · incrementalidade (DiD em R) · precificação por valor (entrega segura + custo por resultado incremental) · documentação de premissas (model card) · MLOps (MLflow, porta, monitor) · CI/CD (GitHub Actions) · XAI (SHAP) · LGPD (dados sintéticos e agregados).
