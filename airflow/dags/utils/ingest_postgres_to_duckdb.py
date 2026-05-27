import duckdb

def ingest_postgres_to_duckdb():
    con_duck = duckdb.connect("/opt/airflow/dbt_project/warehouse.duckdb")

    # aktifkan extension postgres_scanner
    con_duck.execute("INSTALL postgres_scanner;")
    con_duck.execute("LOAD postgres_scanner;")

    tables = {
        "ch_booking_source": ["src_book_channel"],
        "customer_source": ["src_customer"],
        "flight_source": ["src_aircraft", "src_airport", "src_booking", "src_flight_segment"],
        "hotel_source": ["src_guest_profile", "src_hotel_property", "src_hotel_stay", "src_reservation", "src_room_inventory"],
        "payment_source": ["src_currency", "src_payment_method", "src_payment_transaction"],
        "rental_source": ["src_driver", "src_rental_order", "src_rental_trip", "src_vehicle"]
    }

    for schema, tbls in tables.items():
        for tbl in tbls:
            # langsung scan dari Postgres
            con_duck.execute(f"""
                CREATE OR REPLACE TABLE {tbl} AS
                SELECT * FROM postgres_scan(
                    'host=postgres port=5432 user=airflow password=airflow_rahasia_tim_123 dbname=data_warehouse',
                    '{schema}',
                    '{tbl}'
                )
            """)

    con_duck.close()
