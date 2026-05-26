# airflow/dags/utils/mapping_tables.py

LIST_TABEL_TRAVEL = {
    # ============================================================
    # --- GRUP 1: TABEL MASTER / INDUK (Wajib Diisi Lebih Dulu) ---
    # ============================================================
    
    # 1. flight_source (Master)
    'src_customer': {
        'schema_tabel': 'customer_source.src_customer',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_customer`"
    },
    'src_airport': {
        'schema_tabel': 'flight_source.src_airport',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_airport`"
    },
    'src_aircraft': {
        'schema_tabel': 'flight_source.src_aircraft',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_aircraft`"
    },
    'src_book_channel': {
        'schema_tabel': 'flight_source.src_book_channel',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_book_channel`"
    },
    
    # 2. hotel_source (Master)
    'src_hotel_property': {
        'schema_tabel': 'hotel_source.src_hotel_property',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_hotel_property`"
    },
    
    # 3. rental_source (Master)
    'src_vehicle': {
        'schema_tabel': 'rental_source.src_vehicle',
        'bq_query': "SELECT * FROM `multidimensional-modelling.rental_source.src_vehicle`"
    },
    'src_driver': {
        'schema_tabel': 'rental_source.src_driver',
        'bq_query': "SELECT * FROM `multidimensional-modelling.rental_source.src_driver`"
    },
    
    # 4. payment_source (Master)
    'src_payment_method': {
        'schema_tabel': 'payment_source.src_payment_method',
        'bq_query': "SELECT * FROM `multidimensional-modelling.payment_source.src_payment_method`"
    },
    'src_currency': {
        'schema_tabel': 'payment_source.src_currency',
        'bq_query': "SELECT * FROM `multidimensional-modelling.payment_source.src_currency`"
    },

    # ============================================================
    # --- GRUP 2: TABEL TRANSAKSIONAL / ANAK (Antre Menunggu Tabel Induk) ---
    # ============================================================
    
    # 1. flight_source (Transactional)
    'src_booking': {
        'schema_tabel': 'flight_source.src_booking',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_booking`"
    },
    'src_flight_segment': {
        'schema_tabel': 'flight_source.src_flight_segment',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_flight_segment`"
    },
    
    # 2. hotel_source (Transactional)
    'src_room_inventory': {
        'schema_tabel': 'hotel_source.src_room_inventory',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_room_inventory`"
    },
    'src_guest_profile': {
        'schema_tabel': 'hotel_source.src_guest_profile',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_guest_profile`"
    },
    'src_reservation': {
        'schema_tabel': 'hotel_source.src_reservation',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_reservation`"
    },
    'src_hotel_stay': {
        'schema_tabel': 'hotel_source.src_hotel_stay',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_hotel_stay`"
    },
    
    # 3. rental_source (Transactional)
    'src_rental_order': {
        'schema_tabel': 'rental_source.src_rental_order',
        'bq_query': "SELECT * FROM `multidimensional-modelling.rental_source.src_rental_order`"
    },
    'src_rental_trip': {
        'schema_tabel': 'rental_source.src_rental_trip',
        'bq_query': "SELECT * FROM `multidimensional-modelling.rental_source.src_rental_trip`"
    },
    
    # 4. payment_source (Transactional)
    'src_payment_transaction': {
        'schema_tabel': 'payment_source.src_payment_transaction',
        'bq_query': "SELECT * FROM `multidimensional-modelling.payment_source.src_payment_transaction`"
    }
}