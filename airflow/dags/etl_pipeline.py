from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import logging

# Import fungsi ETL dari folder utils
from utils.ingest_postgres_to_duckdb import ingest_postgres_to_duckdb
from utils.load_mart import load_mart_to_postgres

logger = logging.getLogger(__name__)

def run_dbt():
    try:
        logger.info("Starting dbt run dengan debug mode...")
        result = subprocess.run(
            [
                "dbt",
                "run",
                "--target", "duckdb",
                "--profiles-dir", "/opt/airflow/dbt_project",
                "--debug"
            ],
            check=True,
            cwd="/opt/airflow/dbt_project",
            capture_output=True,
            text=True
        )
        logger.info("dbt run berhasil!")
        logger.info("STDOUT:\n%s", result.stdout)
        if result.stderr:
            logger.info("STDERR:\n%s", result.stderr)

    except subprocess.CalledProcessError as e:
        logger.error("dbt run GAGAL dengan exit code: %s", e.returncode)
        logger.error("STDOUT:\n%s", e.stdout)
        logger.error("STDERR:\n%s", e.stderr)
        raise

# Inisialisasi DAG Utama (Hilir)
with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2026, 5, 27),
    schedule_interval=None,  # 🔒 Tetap None karena dipicu oleh DAG pertama
    catchup=False,
) as dag:

    # 1. TASK INGESTION (Postgres DWH -> DuckDB)
    ingestion = PythonOperator(
        task_id="ingest_postgres_to_duckdb",
        python_callable=ingest_postgres_to_duckdb,
        op_kwargs={
            "pg_conn_id": "postgres_dwh"  # 🚀 Menyuntikkan ID koneksi langsung ke fungsi ingest
        },
    )

    # 2. TASK TRANSFORM (dbt run)
    dbt_run = PythonOperator(
        task_id="dbt_run_duckdb",
        python_callable=run_dbt,
    )

    # 3. TASK LOAD MART (DuckDB Data Mart -> Postgres DWH)
    load_mart = PythonOperator(
        task_id="load_mart_to_postgres",
        python_callable=load_mart_to_postgres,
        op_kwargs={
            "pg_conn_id": "postgres_dwh"  # 🚀 Menyuntikkan ID koneksi langsung ke fungsi load mart
        },
    )

    # Alur Pipeline ETL
    ingestion >> dbt_run >> load_mart