"""Pipeline inteiro na configuração de fumaça, com MLflow em pasta temporária."""

from __future__ import annotations

import copy

import mlflow
import pandas as pd
import pytest

from oraculo.config import pasta_dados
from oraculo.models.registro import configurar_mlflow, versao_campea
from oraculo.models.train import porta_qualidade
from oraculo.pipeline import executar


@pytest.fixture(scope="module")
def pipeline_rodado(dados_gerados):
    return dados_gerados, executar(dados_gerados, ["validar", "features", "treinar", "prever", "monitorar"])


def test_treino_cria_run_e_champion(pipeline_rodado):
    cfg, resultados = pipeline_rodado
    assert resultados["treinar"]["porta_qualidade"]["aprovado"] is True
    cliente = configurar_mlflow(cfg)
    campea = versao_campea(cliente, cfg)
    assert campea is not None
    assert cliente.get_run(campea.run_id).data.metrics["backtest_wape"] > 0


def test_previsao_respeita_ordem_dos_quantis(pipeline_rodado):
    cfg, _ = pipeline_rodado
    previsoes = pd.read_parquet(pasta_dados(cfg) / "outputs" / "previsoes_bloco.parquet")
    assert (previsoes["p10"] <= previsoes["p50"]).all()
    assert (previsoes["p50"] <= previsoes["p90"]).all()
    assert (previsoes[["p10", "p50", "p90"]] >= 0).all(axis=None)


def test_previsao_cobre_exatamente_o_horizonte(pipeline_rodado):
    cfg, _ = pipeline_rodado
    previsoes = pd.read_parquet(pasta_dados(cfg) / "outputs" / "previsoes_bloco.parquet")
    fim = pd.Timestamp(cfg["dados"]["fim_historico"])
    assert previsoes["data"].min() == fim + pd.Timedelta(days=1)
    assert previsoes["data"].max() == fim + pd.Timedelta(days=cfg["horizonte_dias"])


def test_resumo_comercial_tem_entrega_segura(pipeline_rodado):
    cfg, _ = pipeline_rodado
    resumo = pd.read_csv(pasta_dados(cfg) / "outputs" / "resumo_comercial.csv")
    assert {"semana", "faixa_programa", "publico", "rating_previsto", "entrega_segura_p10"} <= set(resumo.columns)
    assert (resumo["entrega_segura_p10"] <= resumo["rating_previsto"]).all()


def test_monitor_gera_relatorio_e_alerta_com_choque(pipeline_rodado):
    cfg, resultados = pipeline_rodado
    assert resultados["monitorar"]["status"] == "ALERTA"
    assert (pasta_dados(cfg) / "relatorios" / "monitoramento.md").exists()


def test_porta_reprovada_nao_troca_o_champion(pipeline_rodado):
    cfg, _ = pipeline_rodado
    exigente = copy.deepcopy(cfg)
    exigente["mlops"]["porta"]["melhoria_minima_vs_baseline"] = 0.5
    cliente = configurar_mlflow(exigente)
    antes = versao_campea(cliente, exigente).version

    relatorio = executar(exigente, ["treinar"])["treinar"]

    assert relatorio["porta_qualidade"]["aprovado"] is False
    assert relatorio["porta_qualidade"]["motivos"]
    assert versao_campea(cliente, exigente).version == antes
    ultima = mlflow.search_runs(order_by=["start_time DESC"], max_results=1).iloc[0]
    assert ultima["tags.porta_qualidade"] == "reprovado"


def test_porta_compara_com_o_campeao():
    relatorio = {
        "backtest_geral": {"wape": 0.12, "wape_baseline": 0.20},
        "conformal": {"cobertura_depois": 0.8},
    }
    porta = {"melhoria_minima_vs_baseline": 0.05, "cobertura_min": 0.7, "tolerancia_vs_campeao": 0.02}
    assert porta_qualidade(relatorio, porta, wape_campeao=0.15)[0] is True
    aprovado, motivos = porta_qualidade(relatorio, porta, wape_campeao=0.10)
    assert aprovado is False
    assert any("campeão" in motivo for motivo in motivos)
