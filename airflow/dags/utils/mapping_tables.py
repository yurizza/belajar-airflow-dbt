# airflow/dags/utils/mapping_tables.py

LIST_TABEL_TRAVEL = {
    # --- GRUP 1: TABEL MASTER / INDUK (Wajib Diisi Lebih Dulu) ---
    
    # 1. customer_source
    'src_customer': {
        'schema_tabel': 'customer_source.src_customer',
        'bq_query': "SELECT * FROM `multidimensional-modelling.customer_source.src_customer`"
    },
    
    # 2. flight_source (Master)
    'src_airport': {
        'schema_tabel': 'flight_source.src_airport',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_airport`"
    },
    'src_aircraft': {
        'schema_tabel': 'flight_source.src_aircraft',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_aircraft`"
    },
    
    # 3. hotel_source (Master)
    'src_hotel_propoerty': {
        'schema_tabel': 'hotel_source.src_hotel_property',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_hotel_property`"
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

    # --- GRUP 2: TABEL TRANSAKSIONAL / ANAK (Antre Menunggu Tabel Induk) ---
    
    # flight_source (Transactional)
    'src_booking': {
        'schema_tabel': 'flight_source.src_booking',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_booking`"
    },
    'src_flight_segment': {
        'schema_tabel': 'flight_source.src_flight_segment',
        'bq_query': "SELECT * FROM `multidimensional-modelling.flight_source.src_flight_segment`"
    },
    
    # hotel_source (Transactional)
    'src_room_invent': {
        'schema_tabel': 'hotel_source.src_room_invent',
        'bq_query': "SELECT * FROM `multidimensional-modelling.hotel_source.src_room_invent`"
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
    
    # payment_source (Transactional)
    'src_payment_transaction': {
        'schema_tabel': 'payment_source.src_payment_transaction',
        'bq_query': "SELECT * FROM `multidimensional-modelling.payment_source.src_payment_transaction`"
    }
}