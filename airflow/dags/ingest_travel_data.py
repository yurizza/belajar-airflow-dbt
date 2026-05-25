# airflow/dags/ingest_travel_data.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd

# ============================================================================
# LOGIKA UTAMA: Audit Row Count & Incremental Ingestion (Langsung di sini)
# ============================================================================
def fungsi_ingest_incremental(schema_tabel, query_bq, incremental_column):
    print(f"🔍 [START] Memulai proses audit untuk tabel: {schema_tabel}")
    
    # 1. Hubungkan ke PostgreSQL Target (Gunakan conn_id dari DAG 1 yang sukses)
    pg_hook = PostgresHook(postgres_conn_id='postgres_dwh')
    nama_schema = schema_tabel.split('.')[0]
    nama_tabel = schema_tabel.split('.')[1]
    
    # Cek apakah tabelnya sudah siap di Postgres
    check_table_query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = '{nama_schema}' 
            AND table_name = '{nama_tabel}'
        );
    """
    table_exists = pg_hook.get_first(check_table_query)[0]
    if not table_exists:
        print(f"❌ [ERROR] Tabel {schema_tabel} BELUM TERBUAT di Postgres!")
        return

    row_count_pg = pg_hook.get_first(f"SELECT COUNT(*) FROM {schema_tabel};")[0]
    
    # 2. Hubungkan ke Google BigQuery Source (Menggunakan koneksi UI-mu yang sukses!)
    bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
    bq_client = bq_hook.get_client()
    
    query_count_bq = f"SELECT COUNT(*) FROM ({query_bq}) AS count_query"
    row_count_bq = list(bq_client.query(query_count_bq).result())[0][0]
    
    print(f"📊 Hasil Audit -> BigQuery: {row_count_bq} baris | Postgres: {row_count_pg} baris")
    
    # 3. Ambil Keputusan Strategi Data
    if row_count_bq == row_count_pg:
        print(f"✅ [SKIP] Jumlah data SAMA. Ingestion dilewati!")
        return
    elif row_count_pg == 0:
        print(f"🔄 [FULL LOAD] Postgres kosong. Menarik seluruh data...")
        query_to_run = query_bq
    else:
        print(f"🚀 [INCREMENTAL LOAD] Perbedaan terdeteksi! Mengambil data terbaru...")
        max_val_pg = pg_hook.get_first(f"SELECT MAX({incremental_column}) FROM {schema_tabel};")[0]
        
        if isinstance(max_val_pg, (int, float)):
            query_to_run = f"SELECT * FROM ({query_bq}) WHERE {incremental_column} > {max_val_pg}"
        else:
            query_to_run = f"SELECT * FROM ({query_bq}) WHERE {incremental_column} > '{max_val_pg}'"

    # 4. Ambil dan Simpan Data ke Postgres
    query_job = bq_client.query(query_to_run)
    results = query_job.result()
    
    df = pd.DataFrame([dict(row) for row in results])
    if df.empty:
        print("ℹ️ Tidak ada baris baru untuk dimasukkan.")
        return

    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    kolom = list(df.columns)
    string_kolom = ", ".join(kolom)
    string_placeholders = ", ".join(["%s"] * len(kolom))
    query_insert = f"INSERT INTO {schema_tabel} ({string_kolom}) VALUES ({string_placeholders})"
    
    print(f"📥 Memasukkan {len(df)} baris data baru ke {schema_tabel}...")
    for row in df.itertuples(index=False):
        row_clean = tuple(None if pd.isna(value) else value for value in row)
        cursor.execute(query_insert, row_clean)
        
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ [SUCCESS] Sinkronisasi {schema_tabel} selesai!\n" + "="*50)


# ============================================================================
# CONFIGURATION MAP: Mapping Tabel Resmi
# ============================================================================
LIST_TABEL_TRAVEL = {
    'dim_date': {
        'schema_tabel': 'public.dim_date',
        'bq_query': "SELECT * FROM `multidimensional-modelling.time_info.dim_date`",
        'incremental_column': 'date_key'
    },
    'dim_time_of_day': {
        'schema_tabel': 'public.dim_time_of_day',
        'bq_query': "SELECT * FROM `multidimensional-modelling.time_info.dim_time_day`",
        'incremental_column': 'time_key'
    },
    'dim_airport': {
        'schema_tabel': 'airline.dim_airport',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_info.dim_airport`",
        'incremental_column': 'airport_key'
    },
    'dim_aircraft': {
        'schema_tabel': 'airline.dim_aircraft',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_info.dim_aircraft`",
        'incremental_column': 'aircraft_key'
    },
    'dim_passenger': {
        'schema_tabel': 'airline.dim_passenger',
        'bq_query': "SELECT * FROM `multidimensional-modelling.passanger_info.dim_passanger`",
        'incremental_column': 'passenger_key'
    },
    'dim_hotel_property': {
        'schema_tabel': 'hotel.dim_hotel_property',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_info.dim_hotel_prop`",
        'incremental_column': 'hotel_property_key'
    },
    'dim_customer': {
        'schema_tabel': 'hotel.dim_customer',
        'bq_query': "SELECT * FROM `multidimensional-modelling.customer_info.dim_customer`",
        'incremental_column': 'customer_key'
    },
    'dim_payment_method': {
        'schema_tabel': 'payment.dim_payment_method',
        'bq_query': "SELECT * FROM `multidimensional-modelling.payment_info.dim_payment_method`",
        'incremental_column': 'payment_method_key'
    },
    'fact_segment_flight_activity': {
        'schema_tabel': 'airline.fact_segment_flight_activity',
        'bq_query': "SELECT * FROM `multidimensional-modelling.fact_table.fact_flight`",
        'incremental_column': 'flight_segment_key'
    },
    'fact_hotel_stay': {
        'schema_tabel': 'hotel.fact_hotel_stay',
        'bq_query': "SELECT * FROM `multidimensional-modelling.fact_table.fact_hotel`",
        'incremental_column': 'arrival_date_key'
    },
    'fact_payment_transaction': {
        'schema_tabel': 'payment.fact_payment_transaction',
        'bq_query': "SELECT * FROM `multidimensional-modelling.fact_table.fact_transaction`",
        'incremental_column': 'payment_date_key'
    }
}

# ============================================================================
# INTI WORKFLOW DAG
# ============================================================================
default_args = {
    'owner': 'yurizza_team',
    'retries': 3,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='2_ingest_travel_data_to_postgres',
    default_args=default_args,
    description='DAG Otomatisasi Rekonsiliasi & Incremental Load Travel DWH dari BigQuery',
    schedule_interval='@daily',
    start_date=datetime(2026, 5, 1),
    catchup=False,
) as dag:

    for id_task, konfig in LIST_TABEL_TRAVEL.items():
        task_sync = PythonOperator(
            task_id=f'sync_{id_task}',
            python_callable=fungsi_ingest_incremental,
            op_kwargs={
                'schema_tabel': konfig['schema_tabel'],
                'query_bq': konfig['bq_query'],
                'incremental_column': konfig['incremental_column']
            },
        )
        task_sync