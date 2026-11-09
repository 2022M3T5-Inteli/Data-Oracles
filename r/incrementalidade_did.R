# Incrementalidade: quantos cadastros a campanha CAUSOU? (dados sintéticos, R base, sem pacotes)
#
# Uso: Rscript r/incrementalidade_did.R <csv> <investimento> <semente> <permutacoes>

argumentos <- commandArgs(trailingOnly = TRUE)
arquivo <- if (length(argumentos) >= 1) argumentos[1] else "data/raw/campanha_praca.csv"
investimento <- if (length(argumentos) >= 2) as.numeric(argumentos[2]) else 150000
semente <- if (length(argumentos) >= 3) as.integer(argumentos[3]) else 42L
permutacoes <- if (length(argumentos) >= 4) as.integer(argumentos[4]) else 999L
semanas_placebo <- 20:27

set.seed(semente)
dados <- read.csv(arquivo, stringsAsFactors = FALSE)
dados$log_cadastros <- log(dados$cadastros)
dados$semana_f <- factor(dados$semana)
dados$did <- dados$tratado * dados$pos

por_cento <- function(x) gsub(".", ",", sprintf("%+.1f%%", 100 * x), fixed = TRUE)
efeito_pct <- function(coeficiente) exp(coeficiente) - 1

# Em painel balanceado, retirar as médias de praça e de semana equivale aos efeitos fixos do lm.
retirar_efeitos_fixos <- function(x, praca, semana) {
  x - ave(x, praca) - ave(x, semana) + mean(x)
}

estimar_did <- function(tabela) {
  unname(coef(lm(log_cadastros ~ did + praca + semana_f, data = tabela))["did"])
}

# 1. Comparação ingênua: mistura a campanha com a sazonalidade, que atinge todas as praças.
tratadas <- dados[dados$tratado == 1, ]
semana_inicio <- min(dados$semana[dados$pos == 1])
media_durante <- mean(tratadas$cadastros[tratadas$pos == 1])
media_antes <- mean(tratadas$cadastros[tratadas$pos == 0 & tratadas$semana < semana_inicio])
ingenuo <- media_durante / media_antes - 1

# 2. Diferença em diferenças com efeitos fixos de praça e de semana.
coeficiente <- estimar_did(dados)
efeito <- efeito_pct(coeficiente)

# 3. Inferência por permutação: sorteia quais praças seriam "tratadas". Robusta com poucas praças.
pracas <- sort(unique(dados$praca))
n_tratadas <- length(unique(tratadas$praca))
semanas_campanha <- sort(unique(dados$semana[dados$pos == 1]))
y <- retirar_efeitos_fixos(dados$log_cadastros, dados$praca, dados$semana)
d <- retirar_efeitos_fixos(dados$did, dados$praca, dados$semana)
d_sorteados <- sapply(seq_len(permutacoes), function(i) {
  sorteadas <- sample(pracas, n_tratadas)
  falso <- as.numeric(dados$praca %in% sorteadas & dados$semana %in% semanas_campanha)
  retirar_efeitos_fixos(falso, dados$praca, dados$semana)
})
coef_de <- function(resposta, regressor) sum(regressor * resposta) / sum(regressor^2)
denominadores <- colSums(d_sorteados^2)
coefs_sorteados <- as.numeric(crossprod(d_sorteados, y)) / denominadores
p_valor <- (1 + sum(coefs_sorteados >= coef_de(y, d))) / (permutacoes + 1)

# IC de 95% por inversão: mantém os efeitos candidatos que a permutação não consegue rejeitar.
candidatos <- seq(-0.10, 0.35, by = 0.0025)
nao_rejeitados <- vapply(candidatos, function(candidato) {
  residuo <- y - candidato * d
  sorteados <- as.numeric(crossprod(d_sorteados, residuo)) / denominadores
  mean(abs(sorteados) >= abs(coef_de(residuo, d))) > 0.05
}, logical(1))
ic <- efeito_pct(range(candidatos[nao_rejeitados]))

# 4. Placebo: finge uma campanha antes da campanha real. O efeito precisa ser próximo de zero.
pre <- dados[dados$semana < semana_inicio, ]
pre$did <- pre$tratado * as.numeric(pre$semana %in% semanas_placebo)
placebo <- efeito_pct(estimar_did(pre))

# 5. Leitura de negócio: quanto a campanha causou e quanto custou cada resultado incremental.
observado <- sum(dados$cadastros[dados$did == 1])
incrementais <- observado - observado / exp(coeficiente)
custo <- investimento / incrementais

cat("Dados sintéticos. Efeito real simulado: +12%.\n")
cat(sprintf("1. Ingênuo (antes x durante, praças tratadas): %s\n", por_cento(ingenuo)))
cat(sprintf("2. Diferença em diferenças: %s (IC 95%%: %s a %s)\n", por_cento(efeito), por_cento(ic[1]), por_cento(ic[2])))
cat(sprintf("3. Permutação (%d sorteios): p-valor = %s\n", permutacoes, gsub(".", ",", sprintf("%.3f", p_valor), fixed = TRUE)))
cat(sprintf("4. Placebo (semanas %d a %d): %s\n", min(semanas_placebo), max(semanas_placebo), por_cento(placebo)))
cat(sprintf("5. Cadastros incrementais: %.0f | custo por cadastro incremental: R$ %s\n", incrementais, gsub(".", ",", sprintf("%.2f", custo), fixed = TRUE)))
