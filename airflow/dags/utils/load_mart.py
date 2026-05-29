import duckdb
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values
import logging

logger = logging.getLogger(__name__)

def load_mart_to_postgres(pg_conn_id="postgres_dwh"):
    logger.info("=" * 60)
    logger.info("🚀 [START] Mengunggah Data Mart dari DuckDB ke PostgreSQL")
    logger.info("=" * 60)

    # 1. Inisialisasi DuckDB & Airflow PostgresHook
    duck_conn = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")
    pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)
    
    # Ambil object raw connection dan cursor dari Hook Airflow
    pg_conn = pg_hook.get_conn()
    pg_cursor = pg_conn.cursor()

    mart_tables = [
        "dim_airport", "dim_booking_channel", "dim_currency",
        "dim_customer", "dim_date", "dim_driver", "dim_hotel_property",
        "dim_payment_method", "dim_reservation_status", "dim_room_inventory",
        "dim_vehicle", "fact_flight", "fact_hotel",
        "fact_payment_transaction", "fact_rental",
    ]

    try:
        for table in mart_tables:
            # Fetch data dari DuckDB menjadi Pandas DataFrame
            df = duck_conn.execute(f"SELECT * FROM {table}").fetchdf()

            if df.empty:
                logger.info(f"ℹ️ [SKIP] Tabel {table} di DuckDB kosong.")
                continue

            # 2. Drop table lama di PostgreSQL jika ada
            pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            
            # 3. Bangun definisi kolom secara dinamis berdasarkan tipe data DataFrame
            column_defs = []
            for col, dtype in zip(df.columns, df.dtypes):
                if 'int' in str(dtype):
                    pg_type = 'INTEGER'
                elif 'float' in str(dtype):
                    pg_type = 'DECIMAL(10,2)'
                elif 'bool' in str(dtype):
                    pg_type = 'BOOLEAN'
                elif 'datetime' in str(dtype):
                    pg_type = 'TIMESTAMP'
                else:
                    pg_type = 'TEXT'
                column_defs.append(f'"{col}" {pg_type}')
            
            # 4. Buat tabel baru di PostgreSQL
            create_sql = f"CREATE TABLE {table} ({', '.join(column_defs)})"
            pg_cursor.execute(create_sql)
            pg_conn.commit()
            logger.info(f"🆕 [CREATE] Tabel {table} berhasil dibuat di PostgreSQL.")

            # 5. Memasukkan data menggunakan execute_values (Batch Insert)
            columns = ", ".join([f'"{col}"' for col in df.columns])
            
            # Bersihkan nilai NaN bawaan Pandas menjadi None (NULL di Postgres)
            values = [
                tuple(None if hasattr(val, 'isna') and val.isna() else val for val in row)
                for row in df.itertuples(index=False, name=None)
            ]
            
            insert_sql = f"INSERT INTO {table} ({columns}) VALUES %s"
            execute_values(pg_cursor, insert_sql, values)
            pg_conn.commit()
            
            logger.info(f"✅ [OK] {table}: {len(df)} baris berhasil dimuat.")

        logger.info("=" * 60)
        logger.info("🏁 [DONE] Semua mart tables berhasil diload ke PostgreSQL dengan sukses!")
        logger.info("=" * 60)

    except Exception as e:
        pg_conn.rollback()
        logger.error(f"❌ [ERROR] Pengunggahan mart gagal: {str(e)}")
        raise e

    finally:
        # Menutup seluruh koneksi database dengan aman
        duck_conn.close()
        pg_cursor.close()
        pg_conn.close()

if __name__ == "__main__":
    # Untuk kebutuhan testing lokal di luar Airflow UI, pastikan env AIRFLOW_CONN_ sudah siap
    load_mart_to_postgres()