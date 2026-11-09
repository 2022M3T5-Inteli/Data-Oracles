"""Roda o script em R e confere as cinco leituras. Pulado onde o R não estiver instalado."""

from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from oraculo.config import RAIZ_PROJETO, pasta_dados

EFEITO_SIMULADO = 12.0
TOLERANCIA_DID = 4.0
LIMITE_PLACEBO = 3.0


def _percentual(linha: str) -> float:
    return float(re.search(r"([+-]\d+,\d+)%", linha).group(1).replace(",", "."))


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="R não instalado")
def test_incrementalidade_separa_campanha_de_sazonalidade(dados_gerados):
    arquivo = pasta_dados(dados_gerados) / "raw" / "campanha_praca.csv"
    saida = subprocess.run(
        ["Rscript", "r/incrementalidade_did.R", str(arquivo), "150000", "42", "199"],
        cwd=RAIZ_PROJETO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    linhas = {linha[0]: linha for linha in saida.splitlines() if re.match(r"[1-5]\. ", linha)}

    assert set(linhas) == set("12345")
    ingenuo, did, placebo = _percentual(linhas["1"]), _percentual(linhas["2"]), _percentual(linhas["4"])
    assert ingenuo > did
    assert did == pytest.approx(EFEITO_SIMULADO, abs=TOLERANCIA_DID)
    assert abs(placebo) < LIMITE_PLACEBO
    assert float(re.search(r"p-valor = (\d+,\d+)", linhas["3"]).group(1).replace(",", ".")) < 0.05
