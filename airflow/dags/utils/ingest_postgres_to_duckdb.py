# import duckdb
# import logging

# logger = logging.getLogger(__name__)

# def ingest_postgres_to_duckdb():
#     con_duck = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")

#     try:
#         # Aktifkan extension postgres_scanner
#         con_duck.execute("INSTALL postgres_scanner;")
#         con_duck.execute("LOAD postgres_scanner;")

#         PG_CONN = (
#             "host=postgres port=5432 "
#             "user=airflow password=airflow_rahasia_tim_123 "
#             "dbname=data_warehouse"
#         )

#         tables = {
#             "ch_booking_source": ["src_book_channel"],
#             "customer_source":   ["src_customer"],
#             "flight_source":     ["src_aircraft", "src_airport", "src_booking", "src_flight_segment"],
#             # ✅ Fix Problem 2: src_reservation dipindah ke hotel_source
#             "hotel_source":      ["src_guest_profile", "src_hotel_property", "src_hotel_stay",
#                                   "src_reservation", "src_room_inventory"],
#             "payment_source":    ["src_currency", "src_payment_method", "src_payment_transaction"],
#             "rental_source":     ["src_driver", "src_rental_order", "src_rental_trip", "src_vehicle"]
#         }

#         for schema, tbls in tables.items():
#             # ✅ Fix Problem 1: Buat schema dulu sebelum isi tabelnya
#             con_duck.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
#             logger.info(f"Schema '{schema}' siap.")

#             for tbl in tbls:
#                 # ✅ Fix Problem 1: Tambahkan schema prefix di nama tabel
#                 con_duck.execute(f"""
#                     CREATE OR REPLACE TABLE {schema}.{tbl} AS
#                     SELECT * FROM postgres_scan(
#                         '{PG_CONN}',
#                         '{schema}',
#                         '{tbl}'
#                     )
#                 """)
#                 logger.info(f"  ✓ Ingested {schema}.{tbl}")

#         logger.info("Ingestion selesai.")

#     except Exception as e:
#         logger.error(f"Ingestion GAGAL: {e}")
#         raise

#     finally:
#         con_duck.close()

import duckdb
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

logger = logging.getLogger(__name__)

def ingest_postgres_to_duckdb(pg_conn_id="postgres_dwh"):
    logger.info("=" * 60)
    logger.info("🚀 [START] Ingest Data dari PostgreSQL ke DuckDB")
    logger.info("=" * 60)

    con_duck = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")

    try:
        # Aktifkan extension postgres_scanner
        con_duck.execute("INSTALL postgres_scanner;")
        con_duck.execute("LOAD postgres_scanner;")

        # 🚀 Ambil kredensial dari Airflow Connections secara aman
        pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)
        conn_config = pg_hook.get_connection(pg_conn_id)
        
        # Susun string koneksi secara dinamis untuk fungsi postgres_scan
        PG_CONN = (
            f"host={conn_config.host} "
            f"port={conn_config.port or 5432} "
            f"user={conn_config.login} "
            f"password={conn_config.password} "
            f"dbname={conn_config.schema}"
        )

        tables = {
            "ch_booking_source": ["src_book_channel"],
            "customer_source":   ["src_customer"],
            "flight_source":     ["src_aircraft", "src_airport", "src_booking", "src_flight_segment"],
            "hotel_source":      ["src_guest_profile", "src_hotel_property", "src_hotel_stay",
                                  "src_reservation", "src_room_inventory"],
            "payment_source":    ["src_currency", "src_payment_method", "src_payment_transaction"],
            "rental_source":     ["src_driver", "src_rental_order", "src_rental_trip", "src_vehicle"]
        }

        for schema, tbls in tables.items():
            # Buat schema dulu sebelum isi tabelnya
            con_duck.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            logger.info(f"Schema '{schema}' siap.")

            for tbl in tbls:
                con_duck.execute(f"""
                    CREATE OR REPLACE TABLE {schema}.{tbl} AS
                    SELECT * FROM postgres_scan(
                        '{PG_CONN}',
                        '{schema}',
                        '{tbl}'
                    )
                """)
                logger.info(f"   ✓ Ingested {schema}.{tbl}")

        logger.info("=" * 60)
        logger.info("🏁 [DONE] Ingestion ke DuckDB selesai dengan sukses!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ [ERROR] Ingestion GAGAL: {str(e)}")
        raise e

    finally:
        con_duck.close()

# 🚀 Blok Main untuk kebutuhan testing luar Airflow (CMD)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    ingest_postgres_to_duckdb()