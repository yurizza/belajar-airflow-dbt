import duckdb
import psycopg2
from psycopg2.extras import execute_values

def load_mart_to_postgres():
    duck_conn = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")
    pg_conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow_rahasia_tim_123",
        host="postgres",
        port=5432
    )
    pg_cursor = pg_conn.cursor()

    mart_tables = [
        "dim_airport", "dim_booking_channel", "dim_currency",
        "dim_customer", "dim_date", "dim_driver", "dim_hotel_property",
        "dim_payment_method", "dim_reservation_status", "dim_room_inventory",
        "dim_vehicle", "fact_flight", "fact_hotel",
        "fact_payment_transaction", "fact_rental",
    ]

    for table in mart_tables:
        # 1. Fetch data dari DuckDB
        df = duck_conn.execute(f"SELECT * FROM {table}").fetchdf()

        if df.empty:
            print(f"[SKIP] {table} kosong")
            continue

        # 2. Drop table lama jika ada
        pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        # 3. Buat column definition dari DataFrame
        column_defs = []
        for col, dtype in zip(df.columns, df.dtypes):
            # Map pandas dtype ke PostgreSQL dtype
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
        
        # 4. Create table
        create_sql = f"CREATE TABLE {table} ({', '.join(column_defs)})"
        pg_cursor.execute(create_sql)
        pg_conn.commit()
        print(f"[CREATE] {table} created")

        # 5. Insert data
        if not df.empty:
            columns = ", ".join([f'"{col}"' for col in df.columns])
            values = [tuple(row) for row in df.itertuples(index=False)]
            
            execute_values(
                pg_cursor,
                f"INSERT INTO {table} ({columns}) VALUES %s",
                values
            )
            pg_conn.commit()
            print(f"[OK] {table}: {len(df)} baris")

    duck_conn.close()
    pg_cursor.close()
    pg_conn.close()
    print("[DONE] Semua mart tables berhasil diload ke PostgreSQL")

if __name__ == "__main__":
    load_mart_to_postgres()