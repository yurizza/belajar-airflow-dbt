from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd


# 1. Fungsi ingestion CSV
def fungsi_ingest_dari_csv():

    # Path file CSV
    path_file_csv = os.path.join(
        os.environ.get('AIRFLOW_HOME', '/opt/airflow'),
        'raw_data',
        'employees.csv'
    )

    print(f"Membaca file dari: {path_file_csv}")

    # Baca CSV
    df = pd.read_csv(
        path_file_csv,
        sep=';'
    )

    # Bersihkan kolom reportsTo
    df['reportsTo'] = pd.to_numeric(
        df['reportsTo'],
        errors='coerce'
    )

    print(df.head())
    print(df.dtypes)

    # Connect PostgreSQL
    postgres_hook = PostgresHook(
        postgres_conn_id='postgres_dwh'
    )

    conn = postgres_hook.get_conn()
    cursor = conn.cursor()

    # Hindari duplicate data
    cursor.execute("""
        TRUNCATE TABLE classic_models.employees;
    """)

    # Insert data
    for row in df.itertuples(index=False):

        cursor.execute("""
            INSERT INTO classic_models.employees (
                employeeNumber,
                lastName,
                firstName,
                extension,
                email,
                officeCode,
                reportsTo,
                jobTitle
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            int(row.employeeNumber),
            row.lastName,
            row.firstName,
            row.extension,
            row.email,
            str(row.officeCode),
            None if pd.isna(row.reportsTo) else int(row.reportsTo),
            row.jobTitle
        ))

    # Commit perubahan
    conn.commit()

    # Tutup koneksi
    cursor.close()
    conn.close()

    print(f"Sukses mengimpor {len(df)} baris data!")


# 2. Default arguments
default_args = {
    'owner': 'yurizza_team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


# 3. Definisi DAG
with DAG(
    dag_id='ingest_csv_ke_postgres',
    default_args=default_args,
    description='DAG ingest CSV employees ke PostgreSQL data warehouse',
    schedule=None,
    start_date=datetime(2026, 5, 1),
    catchup=False,
) as dag:

    # TASK 1 - Create schema & table
    create_table = SQLExecuteQueryOperator(
        task_id='create_table_employee',
        conn_id='postgres_dwh',
        sql="""

            CREATE SCHEMA IF NOT EXISTS classic_models;

            CREATE TABLE IF NOT EXISTS classic_models.employees (
                employeeNumber INT PRIMARY KEY,
                lastName VARCHAR(50),
                firstName VARCHAR(50),
                extension VARCHAR(10),
                email VARCHAR(100),
                officeCode VARCHAR(10),
                reportsTo INT,
                jobTitle VARCHAR(50)
            );

        """,
    )

    # TASK 2 - Ingestion CSV
    eksekusi_ingestion_csv = PythonOperator(
        task_id='jalankan_ingest_csv',
        python_callable=fungsi_ingest_dari_csv,
    )

    # Dependency
    create_table >> eksekusi_ingestion_csv