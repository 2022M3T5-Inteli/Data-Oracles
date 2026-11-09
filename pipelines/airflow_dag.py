"""Exemplo (não executado) de como o pipeline rodaria no Airflow, toda segunda-feira.

O Airflow não é dependência do projeto: aqui o pipeline roda por `oraculo.pipeline` e pelo GitHub
Actions. O equivalente no Databricks Workflows seria um job com as mesmas seis tarefas, cada uma
chamando o módulo correspondente, e o agendamento no próprio job.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

CONFIG = "configs/config.yaml"
ETAPAS = ["dados", "validar", "features", "treinar", "prever", "monitorar"]

with DAG(
    dag_id="oraculo_previsao_audiencia",
    schedule="0 9 * * 1",
    start_date=datetime(2025, 1, 6),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
    tags=["audiencia", "comercial"],
) as dag:
    tarefas = [
        BashOperator(
            task_id=etapa,
            bash_command=f"python -m oraculo.pipeline --config {CONFIG} --etapas {etapa}",
        )
        for etapa in ETAPAS
    ]
    for anterior, seguinte in zip(tarefas, tarefas[1:], strict=False):
        anterior >> seguinte
