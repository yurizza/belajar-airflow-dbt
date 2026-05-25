# airflow/dags/init_travel_dwh.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

default_args = {
    'owner': 'yurizza_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='initialize_public_table',
    default_args=default_args,
    description='DAG ad-hoc untuk inisialisasi awal skema DDL Travel DWH di PostgreSQL',
    schedule=None,  # Set None karena hanya perlu dijalankan sekali saja di awal lewat UI
    start_date=datetime(2026, 5, 1),
    catchup=False,
    # Mengizinkan Airflow mencari file SQL ke dalam sub-folder dags/sql
    template_searchpath=['/opt/airflow/dags/sql'], 
) as dag:

    # Task tunggal untuk mengeksekusi seluruh isi travel_dw_schema.sql
    execute_full_ddl = SQLExecuteQueryOperator(
        task_id='execute_full_travel_ddl',
        conn_id='postgres_dwh',         # Membaca koneksi dari .env
        sql='public_db.sql',     # Nama file sql kamu yang berada di folder dags/sql/
    )

    execute_full_ddl