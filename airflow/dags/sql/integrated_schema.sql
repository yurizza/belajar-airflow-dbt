-- ============================================================================
-- INITIALIZATION: Aktifkan Ekstensi UUID & Buat Seluruh Skema Sesuai Gambar
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS customer_source;
CREATE SCHEMA IF NOT EXISTS flight_source;
CREATE SCHEMA IF NOT EXISTS hotel_source;
CREATE SCHEMA IF NOT EXISTS payment_source;

-- ============================================================================
-- 1. GROUP MASTER DATA (Murni Tanpa Constraint)
-- ============================================================================

-- SCHEMA: customer_source -> src_customer
CREATE TABLE IF NOT EXISTS customer_source.src_customer (
    customer_key INT,                  -- Diubah jadi INT biasa (bukan SERIAL PK) agar bisa disuapi langsung dari BQ
    customer_id VARCHAR(100),
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    gender VARCHAR(50),
    date_of_birth DATE,
    nationality VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Index tetap kita pertahankan agar proses dbt query nantinya tetap cepat
CREATE INDEX IF NOT EXISTS idx_customer_email ON customer_source.src_customer(email);
CREATE INDEX IF NOT EXISTS idx_customer_nationality ON customer_source.src_customer(nationality);
CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_source.src_customer(customer_id);


-- SCHEMA: flight_source -> src_airport
CREATE TABLE IF NOT EXISTS flight_source.src_airport (
    airport_code VARCHAR(50),
    airport_name VARCHAR(255),
    city VARCHAR(100),
    country VARCHAR(100),
    timezone VARCHAR(100),
    latitude DECIMAL(12, 7),
    longitude DECIMAL(12, 7),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_airport_city ON flight_source.src_airport(city);
CREATE INDEX IF NOT EXISTS idx_airport_country ON flight_source.src_airport(country);


-- SCHEMA: flight_source -> src_aircraft
CREATE TABLE IF NOT EXISTS flight_source.src_aircraft (
    registration_number VARCHAR(100),
    aircraft_type VARCHAR(100),
    manufacturer VARCHAR(100),
    seat_capacity INT,
    operating_airline VARCHAR(150),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_aircraft_airline ON flight_source.src_aircraft(operating_airline);
CREATE INDEX IF NOT EXISTS idx_aircraft_type ON flight_source.src_aircraft(aircraft_type);


-- SCHEMA: hotel_source -> src_hotel_property
CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_property (
    hotel_id VARCHAR(100),
    hotel_name VARCHAR(255),
    brand VARCHAR(100),
    city VARCHAR(100),
    star_rating INT,
    total_rooms INT,
    has_pool BOOLEAN,
    has_gym BOOLEAN,
    created_at DATE,
    updated_at DATE
);

CREATE INDEX IF NOT EXISTS idx_hotel_brand ON hotel_source.src_hotel_property(brand);
CREATE INDEX IF NOT EXISTS idx_hotel_city ON hotel_source.src_hotel_property(city);
CREATE INDEX IF NOT EXISTS idx_hotel_rating ON hotel_source.src_hotel_property(star_rating);


-- SCHEMA: payment_source -> src_payment_method
CREATE TABLE IF NOT EXISTS payment_source.src_payment_method (
    payment_method_id INT,             -- Diubah jadi INT biasa agar menampung data ID asli dari source
    method_code VARCHAR(100),
    method_name VARCHAR(150),
    payment_type VARCHAR(100),
    provider VARCHAR(100),
    processing_fee_pct DECIMAL(10, 2),
    supports_installment BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_method_type ON payment_source.src_payment_method(payment_type);
CREATE INDEX IF NOT EXISTS idx_payment_method_provider ON payment_source.src_payment_method(provider);


-- SCHEMA: payment_source -> src_currency
CREATE TABLE IF NOT EXISTS payment_source.src_currency (
    currency_code VARCHAR(50),
    currency_name VARCHAR(150),
    currency_symbol VARCHAR(20),
    usd_exchange_rate DECIMAL(18, 5),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_currency_name ON payment_source.src_currency(currency_name);

-- ============================================================================
-- 2. GROUP TRANSACTIONAL & DEPENDENT TABLES (Murni Append-Only Staging)
-- ============================================================================

-- SCHEMA: flight_source -> src_booking
CREATE TABLE IF NOT EXISTS flight_source.src_booking (
    booking_id VARCHAR(100),
    customer_id VARCHAR(100),
    booking_date DATE,
    booking_channel VARCHAR(50),
    fare_basis_code VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_booking_customer ON flight_source.src_booking(customer_id);
CREATE INDEX IF NOT EXISTS idx_booking_date ON flight_source.src_booking(booking_date);
CREATE INDEX IF NOT EXISTS idx_booking_channel ON flight_source.src_booking(booking_channel);


-- SCHEMA: flight_source -> src_flight_segment
CREATE TABLE IF NOT EXISTS flight_source.src_flight_segment (
    segment_id INT,                    -- Diubah jadi INT biasa
    booking_id VARCHAR(100),
    flight_number VARCHAR(100),
    origin_airport VARCHAR(50),
    destination_airport VARCHAR(50),
    scheduled_departure TIMESTAMP,
    actual_departure TIMESTAMP,
    status VARCHAR(100),
    created_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_flight_segment_booking ON flight_source.src_flight_segment(booking_id);
CREATE INDEX IF NOT EXISTS idx_flight_segment_origin ON flight_source.src_flight_segment(origin_airport);
CREATE INDEX IF NOT EXISTS idx_flight_segment_destination ON flight_source.src_flight_segment(destination_airport);
CREATE INDEX IF NOT EXISTS idx_flight_segment_status ON flight_source.src_flight_segment(status);
CREATE INDEX IF NOT EXISTS idx_flight_segment_scheduled ON flight_source.src_flight_segment(scheduled_departure);


-- SCHEMA: hotel_source -> src_room_invent
CREATE TABLE IF NOT EXISTS hotel_source.src_room_invent (
    room_inventory_id INT,             -- Diubah jadi INT biasa
    hotel_id VARCHAR(100),
    room_type_code VARCHAR(50),
    room_type_name VARCHAR(150),
    room_count INT,
    base_rate_usd DECIMAL(14, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_room_inventory_hotel ON hotel_source.src_room_invent(hotel_id);
CREATE INDEX IF NOT EXISTS idx_room_inventory_type ON hotel_source.src_room_invent(room_type_code);


-- SCHEMA: hotel_source -> src_guest_profile
CREATE TABLE IF NOT EXISTS hotel_source.src_guest_profile (
    guest_id VARCHAR(100),
    customer_key INT,
    preferred_room_type VARCHAR(50),
    smoking_preference VARCHAR(100),
    special_request VARCHAR(255),
    created_at DATE,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_guest_profile_key ON hotel_source.src_guest_profile(customer_key);
CREATE INDEX IF NOT EXISTS idx_guest_profile_id ON hotel_source.src_guest_profile(guest_id);


-- SCHEMA: hotel_source -> src_reservation
CREATE TABLE IF NOT EXISTS hotel_source.src_reservation (
    reservation_id VARCHAR(100),
    guest_id VARCHAR(100),
    hotel_id VARCHAR(100),
    booking_date DATE,
    arrival_date DATE,
    departure_date DATE,
    reservation_status VARCHAR(100),
    booking_source VARCHAR(150),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reservation_guest ON hotel_source.src_reservation(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservation_hotel ON hotel_source.src_reservation(hotel_id);
CREATE INDEX IF NOT EXISTS idx_reservation_status ON hotel_source.src_reservation(reservation_status);
CREATE INDEX IF NOT EXISTS idx_reservation_dates ON hotel_source.src_reservation(arrival_date, departure_date);


-- SCHEMA: hotel_source -> src_hotel_stay
CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_stay (
    stay_id INT,                       -- Diubah jadi INT biasa
    reservation_id VARCHAR(100),
    checkin_date DATE,
    checkout_date DATE,
    number_of_nights INT,
    room_charge_usd DECIMAL(14, 2),
    extra_charge_usd DECIMAL(14, 2),
    total_bill_usd DECIMAL(14, 2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hotel_stay_reservation ON hotel_source.src_hotel_stay(reservation_id);
CREATE INDEX IF NOT EXISTS idx_hotel_stay_dates ON hotel_source.src_hotel_stay(checkin_date, checkout_date);


-- SCHEMA: payment_source -> src_payment_transaction
CREATE TABLE IF NOT EXISTS payment_source.src_payment_transaction (
    payment_id VARCHAR(100),
    payment_reference VARCHAR(100),
    invoice_number VARCHAR(100),
    customer_key INT,
    transaction_date DATE,
    transaction_time TIME,
    payment_method_id INT,
    currency_code VARCHAR(50),
    payment_gateway VARCHAR(100),
    payment_status VARCHAR(100),
    gross_amount_usd DECIMAL(16, 2),
    discount_amount_usd DECIMAL(16, 2),
    tax_amount_usd DECIMAL(16, 2),
    net_amount_usd DECIMAL(16, 2),
    refund_amount_usd DECIMAL(16, 2),
    gateway_fee_usd DECIMAL(16, 2),
    installment_months INT,
    source_type VARCHAR(100),
    source_reference VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_transaction_customer ON payment_source.src_payment_transaction(customer_key);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_method ON payment_source.src_payment_transaction(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_currency ON payment_source.src_payment_transaction(currency_code);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_status ON payment_source.src_payment_transaction(payment_status);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_date ON payment_source.src_payment_transaction(transaction_date);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_gateway ON payment_source.src_payment_transaction(payment_gateway);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_source ON payment_source.src_payment_transaction(source_type, source_reference);