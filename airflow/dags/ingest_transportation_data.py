# airflow/dags/2_ingest_transportation_data_to_postgres.py
from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
# Import operator SQL untuk buat table jika belum ada
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from utils.mapping_tables import LIST_TABEL_TRANSPORTATION
from utils.etl_executor import fungsi_insert_all

default_args = {
    'owner': 'transportation_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='ingest_transportation_data',
    default_args=default_args,
    description='DAG Integrasi - Otomatis Buat Tabel & Ingest Data',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
    template_searchpath=['/opt/airflow/dags/sql'], # Ditambahkan agar bisa baca file SQL
) as dag:

    # 1. TUGAS PERTAMA: Pastikan semua tabel sudah siap (Idempotent DDL)
    # Jangan lupa ubah isi 'integrated_schema.sql' pake CREATE TABLE IF NOT EXISTS
    ensure_schema_exists = SQLExecuteQueryOperator(
        task_id='ensure_transportation_schema_exists',
        conn_id='postgres_dwh',
        sql='integrated_schema.sql',
    )

    # Kita pakai task ini sebagai jangkar/hulu awal
    task_sebelumnya = ensure_schema_exists

    # 2. LOOPING INGESTION (Berjalan setelah DDL dipastikan aman)
    for id_task, konfig in LIST_TABEL_TRANSPORTATION.items():
        task_sync = PythonOperator(
            task_id=f'sync_{id_task}',
            python_callable=fungsi_insert_all,
            op_kwargs={
                'schema_tabel': konfig['schema_tabel'],
                'query_bq': konfig['bq_query'],
                'pg_conn_id': 'postgres_dwh',
                'gcp_conn_id': 'google_cloud_default'
            },
        )
        
        # Mengunci alur berurutan: DDL -> Task 1 -> Task 2 -> dst.
        task_sebelumnya >> task_sync
        task_sebelumnya = task_sync