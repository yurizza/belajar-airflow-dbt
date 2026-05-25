-- ============================================================================
-- INITIALIZATION: Aktifkan Ekstensi UUID & Buat Seluruh Skema Sesuai Gambar
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS customer_source;
CREATE SCHEMA IF NOT EXISTS flight_source;
CREATE SCHEMA IF NOT EXISTS hotel_source;
CREATE SCHEMA IF NOT EXISTS payment_source;

-- ============================================================================
-- 1. GROUP MASTER DATA (Wajib Dibuat Paling Awal)
-- ============================================================================

-- SCHEMA: customer_source -> src_customer
CREATE TABLE IF NOT EXISTS customer_source.src_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    date_of_birth DATE NOT NULL,
    nationality VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_email ON customer_source.src_customer(email);
CREATE INDEX IF NOT EXISTS idx_customer_nationality ON customer_source.src_customer(nationality);
CREATE INDEX IF NOT EXISTS idx_customer_id ON customer_source.src_customer(customer_id);

COMMENT ON TABLE customer_source.src_customer IS 'Shared customer master table for flight and hotel bookings';


-- SCHEMA: flight_source -> src_airport
CREATE TABLE IF NOT EXISTS flight_source.src_airport (
    airport_code VARCHAR(3) PRIMARY KEY,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_airport_city ON flight_source.src_airport(city);
CREATE INDEX IF NOT EXISTS idx_airport_country ON flight_source.src_airport(country);

COMMENT ON TABLE flight_source.src_airport IS 'Master data for airports worldwide';


-- SCHEMA: flight_source -> src_aircraft
CREATE TABLE IF NOT EXISTS flight_source.src_aircraft (
    registration_number VARCHAR(20) PRIMARY KEY,
    aircraft_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(50) NOT NULL,
    seat_capacity INT NOT NULL CHECK (seat_capacity > 0),
    operating_airline VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_aircraft_airline ON flight_source.src_aircraft(operating_airline);
CREATE INDEX IF NOT EXISTS idx_aircraft_type ON flight_source.src_aircraft(aircraft_type);

COMMENT ON TABLE flight_source.src_aircraft IS 'Master data for aircraft fleet';


-- SCHEMA: hotel_source -> src_hotel_propoerty (Disamakan dengan typo di gambar dbeaver kamu)
CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_propoerty (
    hotel_id VARCHAR(20) PRIMARY KEY,
    hotel_name VARCHAR(150) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    star_rating INT NOT NULL CHECK (star_rating BETWEEN 1 AND 5),
    total_rooms INT NOT NULL CHECK (total_rooms > 0),
    has_pool BOOLEAN DEFAULT FALSE,
    has_gym BOOLEAN DEFAULT FALSE,
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    CONSTRAINT ck_hotel_dates CHECK (updated_at >= created_at)
);

CREATE INDEX IF NOT EXISTS idx_hotel_brand ON hotel_source.src_hotel_propoerty(brand);
CREATE INDEX IF NOT EXISTS idx_hotel_city ON hotel_source.src_hotel_propoerty(city);
CREATE INDEX IF NOT EXISTS idx_hotel_rating ON hotel_source.src_hotel_propoerty(star_rating);

COMMENT ON TABLE hotel_source.src_hotel_propoerty IS 'Master data for hotel properties';


-- SCHEMA: payment_source -> src_payment_method
CREATE TABLE IF NOT EXISTS payment_source.src_payment_method (
    payment_method_id SERIAL PRIMARY KEY,
    method_code VARCHAR(20) UNIQUE NOT NULL,
    method_name VARCHAR(100) NOT NULL,
    payment_type VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    processing_fee_pct DECIMAL(5, 2) NOT NULL CHECK (processing_fee_pct >= 0 AND processing_fee_pct <= 10),
    supports_installment BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_payment_type CHECK (
        payment_type IN ('Credit Card', 'Debit Card', 'E-Wallet', 'Transfer', 'BNPL')
    )
);

CREATE INDEX IF NOT EXISTS idx_payment_method_type ON payment_source.src_payment_method(payment_type);
CREATE INDEX IF NOT EXISTS idx_payment_method_provider ON payment_source.src_payment_method(provider);

COMMENT ON TABLE payment_source.src_payment_method IS 'Master data for payment methods and providers';


-- SCHEMA: payment_source -> src_currency
CREATE TABLE IF NOT EXISTS payment_source.src_currency (
    currency_code VARCHAR(3) PRIMARY KEY,
    currency_name VARCHAR(50) NOT NULL UNIQUE,
    currency_symbol VARCHAR(5),
    usd_exchange_rate DECIMAL(10, 5) NOT NULL CHECK (usd_exchange_rate > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_currency_name ON payment_source.src_currency(currency_name);

COMMENT ON TABLE payment_source.src_currency IS 'Currency reference and USD exchange rates';


-- ============================================================================
-- 2. GROUP TRANSACTIONAL & DEPENDENT TABLES (Mengikat Relasi Lintas Skema)
-- ============================================================================

-- SCHEMA: flight_source -> src_booking
CREATE TABLE IF NOT EXISTS flight_source.src_booking (
    booking_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    booking_date DATE NOT NULL,
    booking_channel VARCHAR(10) NOT NULL,
    fare_basis_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer_source.src_customer(customer_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_booking_channel CHECK (
        booking_channel IN ('WEB', 'MOB', 'OTA', 'GDS', 'CTR', 'AGT')
    )
);

CREATE INDEX IF NOT EXISTS idx_booking_customer ON flight_source.src_booking(customer_id);
CREATE INDEX IF NOT EXISTS idx_booking_date ON flight_source.src_booking(booking_date);
CREATE INDEX IF NOT EXISTS idx_booking_channel ON flight_source.src_booking(booking_channel);

COMMENT ON TABLE flight_source.src_booking IS 'Flight booking transactions';


-- SCHEMA: flight_source -> src_flight_segment
CREATE TABLE IF NOT EXISTS flight_source.src_flight_segment (
    segment_id SERIAL PRIMARY KEY,
    booking_id VARCHAR(20) NOT NULL,
    flight_number VARCHAR(20) NOT NULL,
    origin_airport VARCHAR(3) NOT NULL,
    destination_airport VARCHAR(3) NOT NULL,
    scheduled_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES flight_source.src_booking(booking_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (origin_airport) REFERENCES flight_source.src_airport(airport_code)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (destination_airport) REFERENCES flight_source.src_airport(airport_code)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_flight_status CHECK (
        status IN ('Flown', 'Cancelled', 'No-Show', 'Diverted')
    ),
    CONSTRAINT ck_flight_dates CHECK (
        actual_departure IS NULL OR actual_departure >= scheduled_departure
    )
);

CREATE INDEX IF NOT EXISTS idx_flight_segment_booking ON flight_source.src_flight_segment(booking_id);
CREATE INDEX IF NOT EXISTS idx_flight_segment_origin ON flight_source.src_flight_segment(origin_airport);
CREATE INDEX IF NOT EXISTS idx_flight_segment_destination ON flight_source.src_flight_segment(destination_airport);
CREATE INDEX IF NOT EXISTS idx_flight_segment_status ON flight_source.src_flight_segment(status);
CREATE INDEX IF NOT EXISTS idx_flight_segment_scheduled ON flight_source.src_flight_segment(scheduled_departure);

COMMENT ON TABLE flight_source.src_flight_segment IS 'Individual flight legs within a booking';


-- SCHEMA: hotel_source -> src_room_invent (Disamakan dengan nama potong di gambar kamu)
CREATE TABLE IF NOT EXISTS hotel_source.src_room_invent (
    room_inventory_id SERIAL PRIMARY KEY,
    hotel_id VARCHAR(20) NOT NULL,
    room_type_code VARCHAR(10) NOT NULL,
    room_type_name VARCHAR(50) NOT NULL,
    room_count INT NOT NULL CHECK (room_count > 0),
    base_rate_usd DECIMAL(10, 2) NOT NULL CHECK (base_rate_usd > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotel_source.src_hotel_propoerty(hotel_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE(hotel_id, room_type_code)
);

CREATE INDEX IF NOT EXISTS idx_room_inventory_hotel ON hotel_source.src_room_invent(hotel_id);
CREATE INDEX IF NOT EXISTS idx_room_inventory_type ON hotel_source.src_room_invent(room_type_code);

COMMENT ON TABLE hotel_source.src_room_invent IS 'Room type inventory for each hotel';


-- SCHEMA: hotel_source -> src_guest_profile
CREATE TABLE IF NOT EXISTS hotel_source.src_guest_profile (
    guest_id VARCHAR(20) PRIMARY KEY,
    customer_key INT NOT NULL,
    preferred_room_type VARCHAR(10),
    smoking_preference VARCHAR(20) NOT NULL,
    special_request VARCHAR(100),
    created_at DATE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES customer_source.src_customer(customer_key)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_smoking CHECK (
        smoking_preference IN ('Non-Smoking', 'Smoking')
    ),
    CONSTRAINT ck_preferred_room CHECK (
        preferred_room_type IN ('STD', 'SUP', 'DLX', 'EXC', 'SUT', 'FAM') 
        OR preferred_room_type IS NULL
    )
);

CREATE INDEX IF NOT EXISTS idx_guest_profile_key ON hotel_source.src_guest_profile(customer_key);
CREATE INDEX IF NOT EXISTS idx_guest_profile_id ON hotel_source.src_guest_profile(guest_id);

COMMENT ON TABLE hotel_source.src_guest_profile IS 'Guest preferences linked to shared customer master';


-- SCHEMA: hotel_source -> src_reservation
CREATE TABLE IF NOT EXISTS hotel_source.src_reservation (
    reservation_id VARCHAR(20) PRIMARY KEY,
    guest_id VARCHAR(20) NOT NULL,
    hotel_id VARCHAR(20) NOT NULL,
    booking_date DATE NOT NULL,
    arrival_date DATE NOT NULL,
    departure_date DATE NOT NULL,
    reservation_status VARCHAR(20) NOT NULL,
    booking_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES hotel_source.src_guest_profile(guest_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (hotel_id) REFERENCES hotel_source.src_hotel_propoerty(hotel_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_reservation_status CHECK (
        reservation_status IN ('Confirmed', 'Cancelled', 'No Show')
    ),
    CONSTRAINT ck_date_order CHECK (
        arrival_date < departure_date AND booking_date <= arrival_date
    )
);

CREATE INDEX IF NOT EXISTS idx_reservation_guest ON hotel_source.src_reservation(guest_id);
CREATE INDEX IF NOT EXISTS idx_reservation_hotel ON hotel_source.src_reservation(hotel_id);
CREATE INDEX IF NOT EXISTS idx_reservation_status ON hotel_source.src_reservation(reservation_status);
CREATE INDEX IF NOT EXISTS idx_reservation_dates ON hotel_source.src_reservation(arrival_date, departure_date);

COMMENT ON TABLE hotel_source.src_reservation IS 'Hotel reservations and booking lifecycle';


-- SCHEMA: hotel_source -> src_hotel_stay
CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_stay (
    stay_id SERIAL PRIMARY KEY,
    reservation_id VARCHAR(20) NOT NULL,
    checkin_date DATE NOT NULL,
    checkout_date DATE NOT NULL,
    number_of_nights INT NOT NULL CHECK (number_of_nights > 0),
    room_charge_usd DECIMAL(10, 2) NOT NULL CHECK (room_charge_usd >= 0),
    extra_charge_usd DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (extra_charge_usd >= 0),
    total_bill_usd DECIMAL(10, 2) NOT NULL CHECK (total_bill_usd >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES hotel_source.src_reservation(reservation_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT ck_stay_dates CHECK (checkin_date < checkout_date),
    CONSTRAINT ck_total_bill CHECK (
        total_bill_usd = room_charge_usd + extra_charge_usd
    )
);

CREATE INDEX IF NOT EXISTS idx_hotel_stay_reservation ON hotel_source.src_hotel_stay(reservation_id);
CREATE INDEX IF NOT EXISTS idx_hotel_stay_dates ON hotel_source.src_hotel_stay(checkin_date, checkout_date);

COMMENT ON TABLE hotel_source.src_hotel_stay IS 'Actual hotel stays with billing details';


-- SCHEMA: payment_source -> src_payment_transaction
CREATE TABLE IF NOT EXISTS payment_source.src_payment_transaction (
    payment_id VARCHAR(20) PRIMARY KEY,
    payment_reference UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(20) UNIQUE NOT NULL,
    customer_key INT NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    payment_method_id INT NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    payment_gateway VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    gross_amount_usd DECIMAL(12, 2) NOT NULL CHECK (gross_amount_usd > 0),
    discount_amount_usd DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (discount_amount_usd >= 0),
    tax_amount_usd DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (tax_amount_usd >= 0),
    net_amount_usd DECIMAL(12, 2) NOT NULL CHECK (net_amount_usd > 0),
    refund_amount_usd DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (refund_amount_usd >= 0),
    gateway_fee_usd DECIMAL(12, 2) NOT NULL DEFAULT 0 CHECK (gateway_fee_usd >= 0),
    installment_months INT DEFAULT 0 CHECK (installment_months >= 0 AND installment_months <= 36),
    source_type VARCHAR(20) NOT NULL,
    source_reference VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_key) REFERENCES customer_source.src_customer(customer_key)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_source.src_payment_method(payment_method_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (currency_code) REFERENCES payment_source.src_currency(currency_code)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_payment_status CHECK (
        payment_status IN ('Completed', 'Pending', 'Failed', 'Refunded')
    ),
    CONSTRAINT ck_source_type CHECK (
        source_type IN ('FLIGHT', 'HOTEL')
    ),
    CONSTRAINT ck_refund_limit CHECK (
        refund_amount_usd <= net_amount_usd
    ),
    CONSTRAINT ck_net_calculation CHECK (
        net_amount_usd = ROUND((gross_amount_usd - discount_amount_usd + tax_amount_usd)::numeric, 2)
    )
);

CREATE INDEX IF NOT EXISTS idx_payment_transaction_customer ON payment_source.src_payment_transaction(customer_key);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_method ON payment_source.src_payment_transaction(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_currency ON payment_source.src_payment_transaction(currency_code);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_status ON payment_source.src_payment_transaction(payment_status);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_date ON payment_source.src_payment_transaction(transaction_date);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_gateway ON payment_source.src_payment_transaction(payment_gateway);
CREATE INDEX IF NOT EXISTS idx_payment_transaction_source ON payment_source.src_payment_transaction(source_type, source_reference);

COMMENT ON TABLE payment_source.src_payment_transaction IS 'Payment transactions for both flight and hotel bookings';