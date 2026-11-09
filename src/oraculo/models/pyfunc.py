"""Empacotamento: quem consome o modelo não precisa saber que são três boosters."""

from __future__ import annotations

import json

import lightgbm as lgb
import mlflow.pyfunc
import numpy as np
import pandas as pd

from oraculo.features.build import VARIAVEIS_CATEGORICAS, VARIAVEIS_MODELO
from oraculo.models.evaluate import aplicar_conformal

NOMES_QUANTIS = ("p10", "p50", "p90")
ARTEFATO_CONFORMAL = "ajuste_conformal"


def ordenar_quantis(previsoes: np.ndarray) -> np.ndarray:
    """Garante p10 ≤ p50 ≤ p90 em cada linha e corta negativos."""
    return np.clip(np.sort(previsoes, axis=1), 0.0, None)


def preparar_entrada(entrada: pd.DataFrame) -> pd.DataFrame:
    """Seleciona as variáveis na ordem do treino, com categóricas no tipo certo."""
    tabela = entrada[VARIAVEIS_MODELO].copy()
    for coluna in VARIAVEIS_CATEGORICAS:
        tabela[coluna] = tabela[coluna].astype("category")
    return tabela


def prever_boosters(boosters: dict[str, lgb.Booster], entrada: pd.DataFrame) -> np.ndarray:
    tabela = preparar_entrada(entrada)
    colunas = [boosters[nome].predict(tabela) for nome in NOMES_QUANTIS]
    return ordenar_quantis(np.column_stack(colunas))


class OraculoModel(mlflow.pyfunc.PythonModel):
    """Devolve p10, p50 e p90 já com o ajuste conformal."""

    def load_context(self, context):
        self.boosters = {nome: lgb.Booster(model_file=context.artifacts[nome]) for nome in NOMES_QUANTIS}
        with open(context.artifacts[ARTEFATO_CONFORMAL], encoding="utf-8") as arquivo:
            self.ajustes = json.load(arquivo)

    def predict(self, context, model_input: pd.DataFrame, params=None):
        previsoes = prever_boosters(self.boosters, model_input)
        p10, p90 = aplicar_conformal(previsoes[:, 0], previsoes[:, 2], model_input["publico"].to_numpy(), self.ajustes)
        return pd.DataFrame({"p10": p10, "p50": previsoes[:, 1], "p90": p90}, index=model_input.index)
