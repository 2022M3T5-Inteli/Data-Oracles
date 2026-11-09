# 02 — Dados: gerador sintético e contratos

Módulos: `src/oraculo/data/generate.py`, `src/oraculo/data/validate.py`.

## 1. Por que sintético

Os dados da Gazeta/Kantar são confidenciais (contrato proíbe até revelar nomes de emissoras) e não estão no repositório. O gerador reproduz **a estrutura e os padrões** que importam para o modelo. Tudo deve deixar claro que é sintético.

## 2. O que gerar

Período configurável (`configs/config.yaml`): histórico de 2023-01-01 a 2024-12-31 + 28 dias "que chegam depois" (para o monitoramento). A grade vai até `fim_historico + max(dias_chegada, horizonte)` (a grade futura é planejada, então é conhecida).

### Tabelas (em `data/raw/`, parquet)

| Arquivo | Colunas | Observação |
| --- | --- | --- |
| `audiencia.parquet` | data, hora, emissora, publico, rating, share | histórico até `fim_historico` |
| `audiencia_chegada.parquet` | idem | período depois do histórico (só o monitor lê) |
| `tle.parquet` | data, hora, tle | % de TVs ligadas |
| `grade.parquet` | data, hora, dow, feriado, categoria, programa, categoria_conc_a, categoria_conc_b | inclui dias futuros |
| `eventos.parquet` | data, hora_inicio, hora_fim, emissora, tipo | eventos exclusivos na concorrência |
| `campanha_praca.csv` | praca, semana, tratado, pos, cadastros | para o teste em R |

### Convenções

- **Dia de TV das 6h às 5h59**: `hora` de 6,00 a 29,75 em passos de 0,25 (96 blocos). 24–29 = madrugada do dia seguinte (convenção de mercado, mantida de 2022).
- Emissoras: `principal`, `concorrente_a`, `concorrente_b`.
- Públicos (10): `total_dom, ab, c, de, masculino, feminino, 4_17, 18_34, 35_49, 50_mais`. Concorrentes só com `total_dom`.

### Padrões que o gerador precisa ter (cada um justifica uma variável do modelo)

1. **TLE** com curva diária (picos manhã, almoço, noite ~21h), fim de semana, verão mais baixo, feriado (mais de dia, menos à noite), fator diário aleatório e **tendência de queda** (~3,5% ao ano).
2. **Grade da principal** por dia da semana com categorias reais de 2022 (JORNALISMO, NOVELA, FILME, FUTEBOL, REALITY SHOW, FEMININO, INFANTIL, SHOW, REPORTAGEM, ESPORTE, RURAL, RELIGIOSO, SERIES, HUMORISTICO, ENTREVISTA). Reality show de jan a abr; futebol quarta à noite e domingo à tarde, com pausa em dez–jan.
3. **Novelas trocam de edição a cada ~180 dias**; cada edição tem "apelo" sorteado (lognormal, desvio ~0,16): algumas fazem sucesso, outras não. Nome do programa com sufixo `_E<n>`.
4. **Concorrentes** com grade própria e **eventos exclusivos** esporádicos (~1 por mês, à noite) que roubam audiência.
5. **"Outros" (streaming)** cresce no tempo e corrói o share.
6. **Share** = apelo da principal ÷ soma dos apelos (principal + concorrentes + outros). **Rating** = TLE × share.
7. **Efeito episódio:** um fator aleatório por programa por dia (blocos vizinhos do mesmo programa se parecem). É isso que torna a divisão aleatória enganosa.
8. **Afinidade por público** (ex.: novela + feminino/50+; futebol + masculino; reality + 18–34; infantil + 4–17) e **mais ruído nos públicos pequenos**.
9. **Choque na chegada** (`choque_chegada: true`): a partir do dia seguinte ao histórico, "outros" cresce ~55% de uma vez (fuga de público para o streaming / crise de imagem). **Não aparece em nenhuma variável.** O monitor deve detectar.
10. **Campanha por praça:** 20 praças × 52 semanas; 8 praças tratadas nas semanas 30–37 com efeito real de +12%; uma sazonalidade de +10% atinge **todas** as praças nas mesmas semanas (engana a comparação ingênua).

Ordem de grandeza esperada (total domicílios, principal): rating médio ~5–6 pontos, pico noturno ~16, share médio ~32%, concorrentes ~15% cada.

Semente fixa (`seed`) → resultados reprodutíveis.

## 3. Contratos de dados (`validate.py`)

O pipeline **para** se algo falhar. Usar `pandera`:
- `rating` e `share` entre 0 e 100, sem nulos;
- `hora` ∈ os 96 valores válidos; `emissora` e `publico` nos conjuntos esperados;
- chave única `(data, hora, emissora, publico)`; `strict=True`;
- grade com chave única `(data, hora)`, `dow` 0–6, `feriado` 0/1;
- cada dia × série com exatamente 96 blocos; nenhuma data faltando;
- todo dia com audiência tem grade.

## 4. Critérios de aceite

- [ ] `make dados` gera todos os arquivos em ~segundos (config completa) e imprime contagens.
- [ ] `make validar` passa nos dados gerados.
- [ ] Teste: contrato rejeita rating negativo (`SchemaErrors`).
- [ ] Teste: contrato rejeita dia com bloco faltando.
- [ ] Ordem de grandeza conferida e anotada em `docs/aprendizado/fase_02.md`.
