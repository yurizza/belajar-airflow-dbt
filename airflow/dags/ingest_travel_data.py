# airflow/dags/2_ingest_travel_data_to_postgres.py
from datetime import datetime, timedelta
import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator

# Proteksi Python Path: Memaksa Airflow mengenali folder utils lokal di dalam folder dags
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import modul setelah jalur sistem dipastikan aman
from utils.mapping_tables import LIST_TABEL_TRAVEL
from utils.etl_executor import fungsi_insert_all

default_args = {
    'owner': 'yurizza_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='ingest_travel_data',
    default_args=default_args,
    description='DAG Terpisah - Orkestrasi Pipeline Data Travel Multi-Schema',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
) as dag:

    task_sebelumnya = None

    # Looping pembentukan task secara otomatis memanjang ke kanan
    for id_task, konfig in LIST_TABEL_TRAVEL.items():
        task_sync = PythonOperator(
            task_id=f'sync_{id_task}',
            python_callable=fungsi_insert_all,
            op_kwargs={
                'schema_tabel': konfig['schema_tabel'],
                'query_bq': konfig['bq_query'],
                'pg_conn_id': 'postgres_dwh',         # Menyuapi nama koneksi Postgres
                'gcp_conn_id': 'google_cloud_default' # Menyuapi nama koneksi BigQuery
            },
        )
        
        # Mengunci alur agar berjalan berurutan sesuai relasi Foreign Key parent-child
        if task_sebelumnya:
            task_sebelumnya >> task_sync
            
        task_sebelumnya = task_sync