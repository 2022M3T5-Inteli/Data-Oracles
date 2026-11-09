"""Métricas em unidades que o negócio entende (pontos de audiência e %)."""

from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np
import pandas as pd


def mae(real: np.ndarray, previsto: np.ndarray) -> float:
    """Erro absoluto médio, em pontos de rating."""
    return float(np.mean(np.abs(np.asarray(previsto) - np.asarray(real))))


def rmse(real: np.ndarray, previsto: np.ndarray) -> float:
    """Raiz do erro quadrático médio: pune erros grandes."""
    return float(np.sqrt(np.mean((np.asarray(previsto) - np.asarray(real)) ** 2)))


def wape(real: np.ndarray, previsto: np.ndarray) -> float:
    """Soma dos erros ÷ soma do real. WAPE de 0,10 = errei 10% da audiência total."""
    real = np.asarray(real)
    return float(np.sum(np.abs(np.asarray(previsto) - real)) / np.sum(real))


def vies(real: np.ndarray, previsto: np.ndarray) -> float:
    """Média de (previsto − real). Positivo = prometo mais do que entrego."""
    return float(np.mean(np.asarray(previsto) - np.asarray(real)))


def r2(real: np.ndarray, previsto: np.ndarray) -> float:
    """% da variação explicada. Só para comparar com 2022: não é "precisão"."""
    real = np.asarray(real)
    return float(1 - np.sum((real - np.asarray(previsto)) ** 2) / np.sum((real - real.mean()) ** 2))


def cobertura(real: np.ndarray, p10: np.ndarray, p90: np.ndarray) -> float:
    """% de vezes em que o real caiu dentro da faixa. Deveria ficar perto de 80%."""
    real = np.asarray(real)
    return float(np.mean((real >= np.asarray(p10)) & (real <= np.asarray(p90))))


def largura_media(p10: np.ndarray, p90: np.ndarray) -> float:
    """Largura média da faixa, em pontos: faixa útil ou larga demais?"""
    return float(np.mean(np.asarray(p90) - np.asarray(p10)))


def metricas_ponto(real: np.ndarray, previsto: np.ndarray) -> dict[str, float]:
    return {
        "mae": mae(real, previsto),
        "rmse": rmse(real, previsto),
        "wape": wape(real, previsto),
        "vies": vies(real, previsto),
        "r2": r2(real, previsto),
    }


def metricas_previsao(tabela: pd.DataFrame) -> dict[str, float]:
    """Métricas do modelo, do baseline e da faixa para uma tabela do backtest."""
    resultado = metricas_ponto(tabela["rating"], tabela["p50"])
    resultado["cobertura"] = cobertura(tabela["rating"], tabela["p10"], tabela["p90"])
    resultado["largura_media"] = largura_media(tabela["p10"], tabela["p90"])
    resultado["wape_baseline"] = wape(tabela["rating"], tabela["baseline"])
    resultado["mae_baseline"] = mae(tabela["rating"], tabela["baseline"])
    resultado["vies_baseline"] = vies(tabela["rating"], tabela["baseline"])
    resultado["melhoria_wape_vs_baseline"] = 1 - resultado["wape"] / resultado["wape_baseline"]
    resultado["linhas"] = float(len(tabela))
    return resultado


def filtrar_horario_nobre(tabela: pd.DataFrame, faixa: list[float]) -> pd.DataFrame:
    return tabela[(tabela["hora"] >= faixa[0]) & (tabela["hora"] < faixa[1])]


def metricas_por(tabela: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Uma linha de métricas para cada valor de `coluna`."""
    linhas = [{coluna: valor, **metricas_previsao(parte)} for valor, parte in tabela.groupby(coluna, observed=True)]
    return pd.DataFrame(linhas)


def calibrar_conformal(tabela: pd.DataFrame, nivel: float) -> dict[str, float]:
    """CQR: por público, quanto a faixa precisa alargar para atingir a cobertura `nivel`.

    O erro de conformidade max(p10 − y, y − p90) é positivo quando o real caiu fora da faixa.
    """
    ajustes: dict[str, float] = {}
    for publico, parte in tabela.groupby("publico", observed=True):
        erro = np.maximum(
            parte["p10"].to_numpy() - parte["rating"].to_numpy(), parte["rating"].to_numpy() - parte["p90"].to_numpy()
        )
        n = len(erro)
        posicao = min(math.ceil((n + 1) * nivel) / n, 1.0)
        ajustes[str(publico)] = float(np.quantile(erro, posicao, method="higher"))
    return ajustes


def aplicar_conformal(
    p10: np.ndarray, p90: np.ndarray, publicos: np.ndarray, ajustes: Mapping[str, float]
) -> tuple[np.ndarray, np.ndarray]:
    """Alarga a faixa pelo ajuste de cada público. O p10 nunca fica negativo."""
    margem = pd.Series(np.asarray(publicos, dtype=object)).map(dict(ajustes)).fillna(0.0).to_numpy(dtype=float)
    return np.clip(np.asarray(p10) - margem, 0.0, None), np.asarray(p90) + margem
