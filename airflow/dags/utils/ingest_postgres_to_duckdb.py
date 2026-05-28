import duckdb
import logging

logger = logging.getLogger(__name__)

def ingest_postgres_to_duckdb():
    con_duck = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")

    try:
        # Aktifkan extension postgres_scanner
        con_duck.execute("INSTALL postgres_scanner;")
        con_duck.execute("LOAD postgres_scanner;")

        PG_CONN = (
            "host=postgres port=5432 "
            "user=airflow password=airflow_rahasia_tim_123 "
            "dbname=data_warehouse"
        )

        tables = {
            "ch_booking_source": ["src_book_channel"],
            "customer_source":   ["src_customer"],
            "flight_source":     ["src_aircraft", "src_airport", "src_booking", "src_flight_segment"],
            # ✅ Fix Problem 2: src_reservation dipindah ke hotel_source
            "hotel_source":      ["src_guest_profile", "src_hotel_property", "src_hotel_stay",
                                  "src_reservation", "src_room_inventory"],
            "payment_source":    ["src_currency", "src_payment_method", "src_payment_transaction"],
            "rental_source":     ["src_driver", "src_rental_order", "src_rental_trip", "src_vehicle"]
        }

        for schema, tbls in tables.items():
            # ✅ Fix Problem 1: Buat schema dulu sebelum isi tabelnya
            con_duck.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            logger.info(f"Schema '{schema}' siap.")

            for tbl in tbls:
                # ✅ Fix Problem 1: Tambahkan schema prefix di nama tabel
                con_duck.execute(f"""
                    CREATE OR REPLACE TABLE {schema}.{tbl} AS
                    SELECT * FROM postgres_scan(
                        '{PG_CONN}',
                        '{schema}',
                        '{tbl}'
                    )
                """)
                logger.info(f"  ✓ Ingested {schema}.{tbl}")

        logger.info("Ingestion selesai.")

    except Exception as e:
        logger.error(f"Ingestion GAGAL: {e}")
        raise

    finally:
        con_duck.close()