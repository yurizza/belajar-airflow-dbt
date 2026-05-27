from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess

# Import fungsi ingestion dari utils
from utils.ingest_postgres_to_duckdb import ingest_postgres_to_duckdb

def run_dbt():
    subprocess.run(
        ["dbt", "run", "--target", "duckdb", "--profiles-dir", "/opt/airflow/dbt_project"],
        check=True,
        cwd="/opt/airflow/dbt_project"
    )

with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2026, 5, 27),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    ingestion = PythonOperator(
        task_id="ingest_postgres_to_duckdb",
        python_callable=ingest_postgres_to_duckdb,
    )

    dbt_run = PythonOperator(
        task_id="dbt_run_duckdb",
        python_callable=run_dbt,
    )

    ingestion >> dbt_run