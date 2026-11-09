# 01 — O negócio: para que serve esta previsão

## 1. Como a Globo ganha dinheiro com publicidade

A Globo é um **veículo**: produz conteúdo que atrai audiência e vende para as marcas o acesso a essa atenção. A vaga é do lado de quem **vende** (não é marketing da própria Globo).

Atores: **anunciante** (marca com objetivo e verba) → **agência** (planeja e negocia) → **Globo** (vende espaços) → **audiência**. A **Kantar IBOPE Media** mede a audiência de forma independente; é a "régua" que todo o mercado usa.

Formatos vendidos:
- **Comercial avulso:** inserções de 30"/15" em programas, praças e datas escolhidos; paga por inserção.
- **Cota de patrocínio:** vaga de patrocinador num projeto (BBB, Copa, futebol), com pacote fechado de aparições (vinhetas, comerciais, ações no conteúdo, digital), exclusividade de segmento, preço fixo e prioridade de renovação.
- **Merchandising** e **digital/streaming** (Globoplay: Pause Ads, Binge Ads, inserção dinâmica no simulcast).

## 2. O mito: o anunciante não compra o horário

Ele compra **a audiência prevista daquele programa no público dele**. O horário não garante nada: uma novela nova pode fracassar no mesmo horário em que a anterior foi um sucesso. A promessa ao anunciante é feita em **pontos de audiência entregues**.

## 3. Por que prever (se todo mundo sabe que o horário nobre é forte)

1. **A venda acontece meses antes.** O dado da Kantar mostra o passado.
2. **O passado não se repete:** novela nova, edição fraca de reality, migração para o streaming, concorrência (ex.: jogos exclusivos da CazéTV na Copa 2026), feriados, eventos.
3. **Errar custa dinheiro, e não igual nos dois lados:**
   - **Prometer mais do que entrega** (viés positivo) → a Globo compensa o anunciante com inserções grátis (*make-good*). Pior caso.
   - **Prometer menos do que podia** → vendeu barato (custo de oportunidade).
4. **O detalhe importa:** por programa, praça, público e semana. Nenhuma tabela de "picos" responde isso.

Consequências para o modelo:
- Prever com **margem de erro** (faixa p10–p90), não só um número.
- Avaliar o **viés** (direção do erro), não só o tamanho.
- A saída para o comercial é a **entrega segura (p10)**: quanto pode prometer com baixo risco de compensação.
- Horizonte realista: previsão feita **28 dias antes**.

## 4. Lidar com o imprevisível

Nenhum modelo prevê um choque que ainda não aconteceu (crise de imagem, migração de público, evento exclusivo na concorrência). A resposta madura:
1. faixa de previsão calibrada;
2. atualização frequente e **monitoramento** (o real chega D+1; se o erro sobe, alerta);
3. mecanismos de negócio (reserva de espaço, compensação, garantia sobre o total da campanha, diversificação entre plataformas);
4. aprender depois (tratar períodos atípicos).

O projeto demonstra o item 2 com um choque simulado em janeiro que nenhuma variável explica.

## 5. As métricas de audiência

Exemplo: 1.000 domicílios; 600 com TV ligada; 120 no canal (média); 300 passaram pelo canal.

| Métrica | Pergunta | Conta | Exemplo |
| --- | --- | --- | --- |
| Rating (Rat%) | Quantos do universo estão no canal? | no canal ÷ universo | 12 pontos |
| Share (Shr%) | Dos que veem TV, quantos escolheram o canal? | no canal ÷ TVs ligadas (TLE) | 20% |
| Reach (Rch%) | Quantos diferentes passaram pelo canal? | alcançados ÷ universo | 30% |
| Fidelidade (Fid%) | Quem chegou ficou quanto? | rating ÷ reach | 40% |

**Rating é a moeda comercial** (o "ponto" vendido; TRP = rating num público-alvo). Por isso é o alvo do modelo.

## 6. Públicos

O anunciante compra público, não audiência total. Os 14 públicos de 2022: total domicílios/indivíduos, classes AB, C1, C2, DE (Critério Brasil), masculino, feminino, 4–11, 12–17, 18–24, 25–34, 35–49, 50–59, 60+. Na versão nova usamos 10 recortes (ver `02_dados.md`). Públicos menores têm amostra menor no painel e, portanto, dado mais ruidoso.

## 7. Onde o projeto se conecta com a vaga

| Atribuição da vaga | Como o projeto mostra |
| --- | --- |
| Previsão de entrega | Modelo de rating com faixa, 28 dias antes |
| Estimativa de resultado de campanha | `resumo_comercial.csv` por semana × programa × público |
| Incrementalidade | DiD em R |
| Precificação baseada em valor | entrega segura + custo por resultado incremental |
| Distinguir modelagem × automação × processo simples | Baseline simples comparado ao modelo; README explica quando o baseline bastaria |
