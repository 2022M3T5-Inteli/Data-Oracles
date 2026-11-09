"""Gerador de dados SINTÉTICOS com a estrutura do Kantar IBOPE.

Nenhum número aqui é real: os dados da emissora de 2022 são confidenciais. O gerador só reproduz
a estrutura e os padrões que importam para o modelo (ver docs/specs/02_dados.md).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from oraculo.config import argumentos_cli, carregar_config, pasta_dados

log = logging.getLogger(__name__)

DIAS_NO_ANO = 365.25


def eixo_horas(dados: dict[str, Any]) -> np.ndarray:
    """Os blocos do dia de TV (6h às 5h59; horas 24 a 29 são a madrugada seguinte)."""
    return dados["hora_inicio"] + np.arange(dados["blocos_por_dia"]) * dados["passo_hora"]


def calendario(cfg: dict[str, Any]) -> tuple[pd.DatetimeIndex, pd.Timestamp]:
    """Datas da grade (incluem o futuro planejado) e o último dia do histórico."""
    dados = cfg["dados"]
    fim_historico = pd.Timestamp(dados["fim_historico"])
    fim_grade = fim_historico + pd.Timedelta(days=max(dados["dias_chegada"], cfg["horizonte_dias"]))
    return pd.date_range(pd.Timestamp(dados["inicio"]), fim_grade, freq="D"), fim_historico


def _tipo_dia(dow: int) -> str:
    return {5: "sabado", 6: "domingo"}.get(dow, "util")


def _preencher(colunas: dict[str, np.ndarray], horas: np.ndarray, grade: list[list[Any]], linha: int) -> None:
    for bloco in grade:
        marca = (horas >= bloco[0]) & (horas < bloco[1])
        colunas["categoria"][linha, marca] = bloco[2]
        if "faixa" in colunas:
            colunas["faixa"][linha, marca] = bloco[3]


def _sufixo_novela(datas: pd.DatetimeIndex, inicio: pd.Timestamp, dias_edicao: int, faixa: str) -> np.ndarray:
    """Número da edição de cada dia. Cada faixa troca de novela em um momento próprio."""
    deslocamento = sum(ord(letra) for letra in faixa) % dias_edicao
    return ((datas - inicio).days + deslocamento) // dias_edicao + 1


def gerar_grade(cfg: dict[str, Any], datas: pd.DatetimeIndex, horas: np.ndarray) -> pd.DataFrame:
    """Monta a grade planejada das três emissoras."""
    gerador = cfg["gerador"]
    n_dias, n_horas = len(datas), len(horas)
    principal = {
        "categoria": np.empty((n_dias, n_horas), dtype=object),
        "faixa": np.empty((n_dias, n_horas), dtype=object),
    }
    conc_a = {"categoria": np.empty((n_dias, n_horas), dtype=object)}
    conc_b = {"categoria": np.empty((n_dias, n_horas), dtype=object)}
    grade_principal = gerador["grade_principal"]

    for linha, data in enumerate(datas):
        tipo = _tipo_dia(data.dayofweek)
        _preencher(principal, horas, grade_principal[tipo], linha)
        _preencher(conc_a, horas, gerador["grade_concorrentes"]["concorrente_a"][tipo], linha)
        _preencher(conc_b, horas, gerador["grade_concorrentes"]["concorrente_b"][tipo], linha)
        if data.month not in gerador["futebol_pausa_meses"]:
            for jogo in grade_principal["futebol"]:
                if data.dayofweek in jogo["dows"]:
                    marca = (horas >= jogo["hora_inicio"]) & (horas < jogo["hora_fim"])
                    principal["categoria"][linha, marca] = "FUTEBOL"
                    principal["faixa"][linha, marca] = jogo["faixa"]
        if data.month in gerador["reality_meses"]:
            for bloco in grade_principal["reality"]:
                if data.dayofweek in bloco["dows"]:
                    marca = (horas >= bloco["hora_inicio"]) & (horas < bloco["hora_fim"])
                    livre = principal["categoria"][linha] != "FUTEBOL"
                    principal["categoria"][linha, marca & livre] = "REALITY SHOW"
                    principal["faixa"][linha, marca & livre] = bloco["faixa"]

    feriados = {pd.Timestamp(d) for d in gerador["feriados"]}
    grade = pd.DataFrame(
        {
            "data": datas.repeat(n_horas),
            "hora": np.tile(horas, n_dias),
            "dow": datas.dayofweek.to_numpy().repeat(n_horas).astype(int),
            "feriado": np.array([int(d in feriados) for d in datas]).repeat(n_horas),
            "categoria": principal["categoria"].ravel(),
            "faixa": principal["faixa"].ravel(),
            "categoria_conc_a": conc_a["categoria"].ravel(),
            "categoria_conc_b": conc_b["categoria"].ravel(),
        }
    )
    edicoes = gerador["edicoes"]
    inicio = datas[0]
    grade["programa"] = grade["faixa"]
    for categoria in edicoes["categorias"]:
        marca = grade["categoria"] == categoria
        if categoria == "NOVELA":
            for faixa, parte in grade[marca].groupby("faixa"):
                numeros = _sufixo_novela(pd.DatetimeIndex(parte["data"]), inicio, edicoes["dias_novela"], str(faixa))
                grade.loc[parte.index, "programa"] = [f"{faixa}_E{n}" for n in numeros]
        else:
            grade.loc[marca, "programa"] = (
                grade.loc[marca, "faixa"] + "_E" + grade.loc[marca, "data"].dt.year.astype(str)
            )
    return grade


def gerar_tle(cfg: dict[str, Any], grade: pd.DataFrame, rng: np.random.Generator) -> pd.Series:
    """Total de TVs ligadas (%): curva diária, fim de semana, verão, feriado, sorte do dia e queda estrutural."""
    parametros = cfg["gerador"]["tle"]
    hora = grade["hora"].to_numpy()
    curva = np.full(len(grade), float(parametros["base"]))
    for centro, altura, largura in parametros["picos"]:
        curva += altura * np.exp(-0.5 * ((hora - centro) / largura) ** 2)

    data = grade["data"]
    fim_de_semana = np.where(grade["dow"] >= 5, parametros["fim_de_semana"], 1.0)
    verao = np.where(data.dt.month.isin(parametros["meses_verao"]), parametros["verao"], 1.0)
    feriado = np.where(
        grade["feriado"] == 0,
        1.0,
        np.where(hora < parametros["hora_corte_feriado"], parametros["feriado_dia"], parametros["feriado_noite"]),
    )
    anos = (data - data.min()).dt.days.to_numpy() / DIAS_NO_ANO
    tendencia = (1 - parametros["queda_anual"]) ** anos
    dias, codigos = np.unique(data.to_numpy(), return_inverse=True)
    fator_dia = rng.lognormal(0.0, parametros["sigma_dia"], len(dias))[codigos]
    return pd.Series(
        np.clip(curva * fim_de_semana * verao * feriado * tendencia * fator_dia, 0.5, 95.0), index=grade.index
    )


def _fator_por_chave(chaves: pd.Series, sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Sorteia um fator lognormal por valor distinto de `chaves`."""
    codigos, unicos = pd.factorize(chaves)
    return rng.lognormal(0.0, sigma, len(unicos))[codigos]


def gerar_eventos(cfg: dict[str, Any], datas: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    """Eventos exclusivos nas concorrentes, cerca de um por mês, à noite."""
    parametros = cfg["gerador"]["eventos"]
    linhas = []
    for periodo in sorted(set(datas.to_period("M"))):
        for _ in range(rng.poisson(parametros["por_mes"])):
            dias_do_mes = datas[datas.to_period("M") == periodo]
            inicio = float(
                rng.choice(np.arange(parametros["hora_inicio"][0], parametros["hora_inicio"][1] + 0.25, 0.25))
            )
            duracao = float(
                rng.choice(np.arange(parametros["duracao_horas"][0], parametros["duracao_horas"][1] + 0.25, 0.25))
            )
            linhas.append(
                {
                    "data": pd.Timestamp(rng.choice(dias_do_mes.to_numpy())),
                    "hora_inicio": inicio,
                    "hora_fim": inicio + duracao,
                    "emissora": str(rng.choice(["concorrente_a", "concorrente_b"])),
                    "tipo": str(rng.choice(parametros["tipos"])),
                }
            )
    return pd.DataFrame(linhas, columns=["data", "hora_inicio", "hora_fim", "emissora", "tipo"])


def _multiplicador_eventos(grade: pd.DataFrame, eventos: pd.DataFrame, emissora: str, fator: float) -> np.ndarray:
    multiplicador = np.ones(len(grade))
    for evento in eventos[eventos["emissora"] == emissora].itertuples():
        marca = (
            (grade["data"] == evento.data) & (grade["hora"] >= evento.hora_inicio) & (grade["hora"] < evento.hora_fim)
        )
        multiplicador[marca.to_numpy()] = fator
    return multiplicador


def gerar_audiencia(
    cfg: dict[str, Any],
    grade: pd.DataFrame,
    tle: pd.Series,
    eventos: pd.DataFrame,
    fim_historico: pd.Timestamp,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Share = apelo da emissora ÷ soma dos apelos. Rating = TLE × share. Depois abre por público."""
    gerador = cfg["gerador"]
    edicoes = gerador["edicoes"]

    # A sorte de cada edição faz uma novela nova poder fracassar no mesmo horário da anterior.
    fator_edicao = np.ones(len(grade))
    marca_edicao = grade["categoria"].isin(edicoes["categorias"]).to_numpy()
    fator_edicao[marca_edicao] = _fator_por_chave(grade.loc[marca_edicao, "programa"], edicoes["sigma_apelo"], rng)

    # O efeito episódio faz blocos vizinhos do mesmo programa se parecerem: é o que engana a divisão aleatória.
    chave_episodio = grade["programa"] + "|" + grade["data"].dt.strftime("%Y%m%d")
    fator_episodio = _fator_por_chave(chave_episodio, gerador["sigma_episodio"], rng)
    ruido_bloco = rng.lognormal(0.0, gerador["sigma_bloco"], len(grade))
    apelo_principal = (
        grade["categoria"].map(gerador["apelo_categoria"]).to_numpy() * fator_edicao * fator_episodio * ruido_bloco
    )

    multiplicador = gerador["eventos"]["multiplicador_apelo"]
    sorte_a = _fator_por_chave(
        grade["categoria_conc_a"] + "|" + grade["data"].dt.strftime("%Y%m%d"), gerador["sigma_concorrente"], rng
    )
    sorte_b = _fator_por_chave(
        grade["categoria_conc_b"] + "|" + grade["data"].dt.strftime("%Y%m%d"), gerador["sigma_concorrente"], rng
    )
    apelo_a = grade["categoria_conc_a"].map(gerador["apelo_concorrente"]).to_numpy() * sorte_a
    apelo_a = apelo_a * _multiplicador_eventos(grade, eventos, "concorrente_a", multiplicador)
    apelo_b = grade["categoria_conc_b"].map(gerador["apelo_concorrente"]).to_numpy() * sorte_b
    apelo_b = apelo_b * _multiplicador_eventos(grade, eventos, "concorrente_b", multiplicador)

    # O streaming cresce e corrói o share. O choque não aparece em nenhuma variável do modelo.
    anos = (grade["data"] - grade["data"].min()).dt.days.to_numpy() / DIAS_NO_ANO
    apelo_outros = gerador["outros"]["base"] * (1 + gerador["outros"]["crescimento_anual"]) ** anos
    if gerador["choque_chegada"]:
        apelo_outros = apelo_outros * np.where(grade["data"] > fim_historico, 1 + gerador["choque_outros"], 1.0)

    soma = apelo_principal + apelo_a + apelo_b + apelo_outros
    tle_valores = tle.to_numpy()
    tabelas = []
    for emissora, apelo in (("concorrente_a", apelo_a), ("concorrente_b", apelo_b)):
        share = 100 * apelo / soma
        tabelas.append(
            pd.DataFrame(
                {
                    "data": grade["data"],
                    "hora": grade["hora"],
                    "emissora": emissora,
                    "publico": cfg["dados"]["publico_total"],
                    "rating": tle_valores * share / 100,
                    "share": share,
                }
            )
        )

    share_principal = 100 * apelo_principal / soma
    rating_total = tle_valores * share_principal / 100
    for publico in cfg["dados"]["publicos"]:
        ajuste = gerador["publicos"][publico]
        afinidade = grade["categoria"].map(lambda c, p=publico: gerador["afinidade"].get(c, {}).get(p, 1.0)).to_numpy()
        ruido = rng.lognormal(0.0, ajuste["sigma"], len(grade))
        rating = np.clip(rating_total * ajuste["fator"] * afinidade * ruido, 0.0, 100.0)
        tabelas.append(
            pd.DataFrame(
                {
                    "data": grade["data"],
                    "hora": grade["hora"],
                    "emissora": "principal",
                    "publico": publico,
                    "rating": rating,
                    "share": np.clip(100 * rating / tle_valores, 0.0, 100.0),
                }
            )
        )
    audiencia = pd.concat(tabelas, ignore_index=True)
    audiencia[["rating", "share"]] = audiencia[["rating", "share"]].round(3)
    return audiencia


def gerar_campanha(cfg: dict[str, Any], rng: np.random.Generator) -> pd.DataFrame:
    """Painel praça × semana para o teste de incrementalidade em R."""
    campanha = cfg["gerador"]["campanha"]
    semanas = np.arange(1, campanha["semanas"] + 1)
    pracas = [f"praca_{i:02d}" for i in range(1, campanha["pracas"] + 1)]
    tratadas = set(rng.choice(pracas, campanha["pracas_tratadas"], replace=False).tolist())
    linhas = []
    for praca in pracas:
        base = rng.uniform(*campanha["cadastros_base"])
        for semana in semanas:
            pos = int(campanha["semana_inicio"] <= semana <= campanha["semana_fim"])
            tratado = int(praca in tratadas)
            sazonal = 1 + campanha["sazonalidade"] * pos
            efeito = 1 + campanha["efeito"] * tratado * pos
            ruido = rng.lognormal(0.0, campanha["sigma_semana"])
            linhas.append(
                {
                    "praca": praca,
                    "semana": int(semana),
                    "tratado": tratado,
                    "pos": pos,
                    "cadastros": int(round(base * sazonal * efeito * ruido)),
                }
            )
    return pd.DataFrame(linhas)


def gerar(cfg: dict[str, Any]) -> dict[str, int]:
    """Gera todas as tabelas em `data/raw` e devolve as contagens de linhas."""
    rng = np.random.default_rng(cfg["seed"])
    pasta: Path = pasta_dados(cfg) / "raw"
    pasta.mkdir(parents=True, exist_ok=True)
    datas, fim_historico = calendario(cfg)
    horas = eixo_horas(cfg["dados"])

    grade = gerar_grade(cfg, datas, horas)
    tle = gerar_tle(cfg, grade, rng)
    eventos = gerar_eventos(cfg, datas, rng)
    audiencia = gerar_audiencia(cfg, grade, tle, eventos, fim_historico, rng)
    campanha = gerar_campanha(cfg, rng)

    historico = audiencia["data"] <= fim_historico
    tabela_tle = pd.DataFrame({"data": grade["data"], "hora": grade["hora"], "tle": tle.round(3)})
    tabela_tle = tabela_tle[tabela_tle["data"] <= fim_historico]
    tabela_grade = grade[
        ["data", "hora", "dow", "feriado", "categoria", "programa", "categoria_conc_a", "categoria_conc_b"]
    ]
    audiencia[historico].to_parquet(pasta / "audiencia.parquet", index=False)
    audiencia[~historico].to_parquet(pasta / "audiencia_chegada.parquet", index=False)
    tabela_tle.to_parquet(pasta / "tle.parquet", index=False)
    tabela_grade.to_parquet(pasta / "grade.parquet", index=False)
    eventos.to_parquet(pasta / "eventos.parquet", index=False)
    campanha.to_csv(pasta / "campanha_praca.csv", index=False)

    contagens = {
        "audiencia": int(historico.sum()),
        "audiencia_chegada": int((~historico).sum()),
        "tle": len(tabela_tle),
        "grade": len(tabela_grade),
        "eventos": len(eventos),
        "campanha_praca": len(campanha),
    }
    for tabela, linhas in contagens.items():
        log.info("%-18s %10d linhas", tabela, linhas)
    return contagens


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    argumentos = argumentos_cli("Gera os dados sintéticos").parse_args()
    log.info("Gerando dados SINTÉTICOS (estrutura Kantar, sem nenhum dado real)...")
    gerar(carregar_config(argumentos.config))


if __name__ == "__main__":
    main()
