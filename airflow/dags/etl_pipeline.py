from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import subprocess
import logging

# Import fungsi ingestion dari utils
from utils.ingest_postgres_to_duckdb import ingest_postgres_to_duckdb

# Setup logging
logger = logging.getLogger(__name__)

def run_dbt():
    """
    Menjalankan dbt dengan debug mode untuk error yang lebih detail
    """
    try:
        logger.info("Starting dbt run dengan debug mode...")
        result = subprocess.run(
            [
                "dbt", 
                "run", 
                "--target", "duckdb", 
                "--profiles-dir", "/opt/airflow/dbt_project",
                "--debug"  # Tambahkan ini untuk output lebih verbose
            ],
            check=True,
            cwd="/opt/airflow/dbt_project",
            capture_output=True,  # Capture stdout dan stderr
            text=True  # Return sebagai string, bukan bytes
        )
        
        # Log output dari dbt
        logger.info("dbt run berhasil!")
        logger.info("STDOUT:\n%s", result.stdout)
        if result.stderr:
            logger.info("STDERR:\n%s", result.stderr)
            
    except subprocess.CalledProcessError as e:
        # Capture error output yang detail
        logger.error("dbt run GAGAL dengan exit code: %s", e.returncode)
        logger.error("STDOUT:\n%s", e.stdout)
        logger.error("STDERR:\n%s", e.stderr)
        raise  # Re-raise exception agar Airflow tahu task gagal

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