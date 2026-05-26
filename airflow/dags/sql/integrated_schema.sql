-- ============================================================
-- OLTP SOURCE SCHEMA - PostgreSQL DDL (Idempotent Version)
-- Systems: Flight | Hotel | Car Rental | Payment
-- ============================================================

-- Pembuatan Schema jika belum ada
CREATE SCHEMA IF NOT EXISTS flight_source;
CREATE SCHEMA IF NOT EXISTS hotel_source;
CREATE SCHEMA IF NOT EXISTS rental_source;
CREATE SCHEMA IF NOT EXISTS payment_source;
CREATE SCHEMA IF NOT EXISTS customer_source;
CREATE SCHEMA IF NOT EXISTS ch_booking_source;

-- ============================================================
-- 1. FLIGHT SOURCE SYSTEM
-- ============================================================

CREATE TABLE IF NOT EXISTS flight_source.src_airport (
    airport_code  CHAR(3)        PRIMARY KEY,
    airport_name  VARCHAR(100)   NOT NULL,
    city          VARCHAR(50)    NOT NULL,
    country       VARCHAR(50)    NOT NULL,
    timezone      VARCHAR(50),
    latitude      NUMERIC(9, 6),
    longitude     NUMERIC(9, 6)
);

CREATE TABLE IF NOT EXISTS flight_source.src_aircraft (
    aircraft_id    VARCHAR(10)   PRIMARY KEY,
    registration   VARCHAR(20)   NOT NULL UNIQUE,
    aircraft_type  VARCHAR(50)   NOT NULL,
    manufacturer   VARCHAR(50),
    seat_capacity  SMALLINT,
    airline        VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS customer_source.src_customer (
    customer_key     SERIAL        PRIMARY KEY,
    customer_id      VARCHAR(15)   NOT NULL,
    first_name       VARCHAR(50)   NOT NULL,
    last_name        VARCHAR(50)   NOT NULL,
    gender           CHAR(1)       CHECK (gender IN ('M', 'F')),
    date_of_birth    DATE,
    nationality      VARCHAR(50),
    email            VARCHAR(100),
    phone            VARCHAR(30),
    eff_start_date   DATE          NOT NULL,
    eff_end_date     DATE,
    is_current       SMALLINT      NOT NULL DEFAULT 1 CHECK (is_current IN (0, 1))
);

-- Catatan: PostgreSQL secara bawaan tidak mendukung 'CREATE INDEX IF NOT EXISTS' 
-- digabung dengan nama indeks yang otomatis, namun sintaks di bawah ini valid di Postgres 9.5+.
-- CREATE INDEX IF NOT EXISTS idx_customer_id         ON customer_source.src_customer (customer_id);
-- CREATE INDEX IF NOT EXISTS idx_customer_is_current ON customer_source.src_customer (is_current);

CREATE TABLE IF NOT EXISTS ch_booking_source.src_book_channel (
    channel_key          SERIAL        PRIMARY KEY,
    channel_code         VARCHAR(10)   NOT NULL UNIQUE,
    channel_name         VARCHAR(60)   NOT NULL,
    channel_type         VARCHAR(20),
    commission_rate_pct  NUMERIC(5, 2),
    booking_fee_usd      NUMERIC(8, 2),
    typical_lead_days    SMALLINT,
    volume_share_pct     NUMERIC(5, 2)
);

CREATE TABLE IF NOT EXISTS flight_source.src_booking (
    booking_id       VARCHAR(15)   PRIMARY KEY,
    customer_key     INTEGER       NOT NULL,
    customer_id      VARCHAR(15)   NOT NULL,
    booking_date     DATE          NOT NULL,
    booking_channel  VARCHAR(10)
);

-- CREATE INDEX IF NOT EXISTS idx_booking_customer ON flight_source.src_booking (customer_key);

CREATE TABLE IF NOT EXISTS flight_source.src_flight_segment (
    segment_id               SERIAL        PRIMARY KEY,
    booking_id               VARCHAR(15)   NOT NULL,
    flight_number            VARCHAR(10),
    origin_airport           CHAR(3)       NOT NULL,
    destination_airport      CHAR(3)       NOT NULL,
    scheduled_departure      TIMESTAMP,
    actual_departure         TIMESTAMP,
    scheduled_arrival        TIMESTAMP,
    actual_arrival           TIMESTAMP,
    flight_duration_minutes  SMALLINT,
    delay_minutes            SMALLINT,
    status                   VARCHAR(20)   CHECK (status IN ('Flown','Cancelled','No-Show','Diverted'))
);

-- CREATE INDEX IF NOT EXISTS idx_segment_booking     ON flight_source.src_flight_segment (booking_id);
-- CREATE INDEX IF NOT EXISTS idx_segment_destination ON flight_source.src_flight_segment (destination_airport);


-- ============================================================
-- 2. HOTEL SOURCE SYSTEM
-- ============================================================

CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_property (
    hotel_id        VARCHAR(10)   PRIMARY KEY,
    hotel_name      VARCHAR(100)  NOT NULL,
    brand           VARCHAR(50),
    market_segment  VARCHAR(20),
    city            VARCHAR(50),
    star_rating     SMALLINT      CHECK (star_rating BETWEEN 1 AND 5),
    total_rooms     SMALLINT
);

CREATE TABLE IF NOT EXISTS hotel_source.src_room_inventory (
    room_id         VARCHAR(25)   PRIMARY KEY,
    hotel_id        VARCHAR(10)   NOT NULL,
    room_number     VARCHAR(10),
    room_type_code  CHAR(3),
    room_type_name  VARCHAR(40),
    base_rate_usd   NUMERIC(8, 2),
    is_active       SMALLINT      DEFAULT 1 CHECK (is_active IN (0, 1)) -- Koma gantung di sini sudah dihapus
);

-- CREATE INDEX IF NOT EXISTS idx_room_hotel ON hotel_source.src_room_inventory (hotel_id);

CREATE TABLE IF NOT EXISTS hotel_source.src_guest_profile (
    guest_id              VARCHAR(15)   PRIMARY KEY,
    customer_key          INTEGER       NOT NULL UNIQUE,
    loyalty_tier          VARCHAR(20)   CHECK (loyalty_tier IN ('BLUE','SILVER','GOLD','PLATINUM')),
    preferred_room_type   CHAR(3),
    special_requests      VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS hotel_source.src_reservation (
    reservation_id    VARCHAR(15)   PRIMARY KEY,
    customer_key      INTEGER       NOT NULL,
    guest_id          VARCHAR(15)   NOT NULL,
    hotel_id          VARCHAR(10)   NOT NULL,
    segment_id        INTEGER,
    booking_date      DATE,
    destination_city  VARCHAR(50),
    checkin_date      DATE,
    checkout_date     DATE,
    status            VARCHAR(20)   CHECK (status IN ('Confirmed','Checked-Out','Cancelled','No-Show'))
);

-- CREATE INDEX IF NOT EXISTS idx_reservation_customer ON hotel_source.src_reservation (customer_key);
-- CREATE INDEX IF NOT EXISTS idx_reservation_hotel    ON hotel_source.src_reservation (hotel_id);

CREATE TABLE IF NOT EXISTS hotel_source.src_hotel_stay (
    stay_id               VARCHAR(25)   PRIMARY KEY,
    reservation_id        VARCHAR(15)   NOT NULL UNIQUE,
    actual_checkin_date   DATE,
    actual_nights         SMALLINT,
    incidental_usd        NUMERIC(8, 2) DEFAULT 0.00
);


-- ============================================================
-- 3. CAR RENTAL SOURCE SYSTEM
-- ============================================================

CREATE TABLE IF NOT EXISTS rental_source.src_vehicle (
    vehicle_id     VARCHAR(10)   PRIMARY KEY,
    plate          VARCHAR(20)   NOT NULL UNIQUE,
    type_code      VARCHAR(10),
    type_name      VARCHAR(40),
    category       VARCHAR(20),
    brand          VARCHAR(30),
    model          VARCHAR(30),
    seat_capacity  SMALLINT,
    rate_usd_day   NUMERIC(8, 2),
    prod_year      SMALLINT,
    status         VARCHAR(20)   CHECK (status IN ('Active','Maintenance','Inactive'))
);

CREATE TABLE IF NOT EXISTS rental_source.src_driver (
    driver_id     VARCHAR(10)   PRIMARY KEY,
    driver_name   VARCHAR(100)  NOT NULL,
    gender        CHAR(1)       CHECK (gender IN ('M', 'F')),
    license_no    VARCHAR(30),
    license_type  VARCHAR(5),
    languages     VARCHAR(100),
    rating        NUMERIC(3, 1),
    total_trips   INTEGER       DEFAULT 0,
    is_active     SMALLINT      DEFAULT 1 CHECK (is_active IN (0, 1)),
    joined_date   DATE
);

CREATE TABLE IF NOT EXISTS rental_source.src_rental_order (
    order_id           VARCHAR(15)   PRIMARY KEY,
    customer_key       INTEGER       NOT NULL,
    reservation_id     VARCHAR(15),
    segment_id         INTEGER,
    vehicle_id         VARCHAR(10),
    driver_id          VARCHAR(10),
    pickup_airport     CHAR(3),
    order_date         DATE,
    scheduled_pickup   TIMESTAMP,
    order_status       VARCHAR(20)   CHECK (order_status IN ('Completed','Cancelled','No-Show')),
    booking_source     VARCHAR(30),
    special_request    VARCHAR(100),
    estimated_rate_usd NUMERIC(8, 2)
);

-- CREATE INDEX IF NOT EXISTS idx_order_customer    ON rental_source.src_rental_order (customer_key);
-- CREATE INDEX IF NOT EXISTS idx_order_reservation ON rental_source.src_rental_order (reservation_id);

CREATE TABLE IF NOT EXISTS rental_source.src_rental_trip (
    trip_id            SERIAL        PRIMARY KEY,
    order_id           VARCHAR(15)   NOT NULL UNIQUE,
    actual_pickup      TIMESTAMP,
    actual_dropoff     TIMESTAMP,
    delay_minutes      SMALLINT,
    duration_minutes   SMALLINT,
    distance_km        NUMERIC(7, 1),
    base_charge_usd    NUMERIC(8, 2),
    surcharge_usd      NUMERIC(8, 2),
    total_charge_usd   NUMERIC(8, 2),
    trip_status        VARCHAR(20)   CHECK (trip_status IN ('Completed','Delayed','Incident')),
    driver_rating      NUMERIC(3, 1)
);


-- ============================================================
-- 4. PAYMENT SOURCE SYSTEM
-- ============================================================

CREATE TABLE IF NOT EXISTS payment_source.src_payment_method (
    payment_method_id      SMALLINT      PRIMARY KEY,
    method_code            VARCHAR(15)   NOT NULL UNIQUE,
    method_name            VARCHAR(50)   NOT NULL,
    payment_type           VARCHAR(30),
    provider               VARCHAR(30),
    processing_fee_pct     NUMERIC(5, 2),
    supports_installment   BOOLEAN       DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS payment_source.src_currency (
    currency_code      CHAR(3)       PRIMARY KEY,
    currency_name      VARCHAR(50),
    symbol             VARCHAR(5),
    usd_exchange_rate  NUMERIC(12, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_source.src_payment_transaction (
    payment_id          VARCHAR(15)    PRIMARY KEY,
    payment_reference   UUID           NOT NULL UNIQUE,
    invoice_number      VARCHAR(15)    NOT NULL,
    customer_key        INTEGER        NOT NULL,
    transaction_date    DATE           NOT NULL,
    transaction_time    TIME,
    payment_method_id   SMALLINT       NOT NULL,
    currency_code       CHAR(3)        NOT NULL,
    payment_gateway     VARCHAR(30),
    payment_status      VARCHAR(20)    CHECK (payment_status IN ('Completed','Pending','Failed','Refunded')),
    gross_amount_usd    NUMERIC(12, 2),
    discount_usd        NUMERIC(12, 2) DEFAULT 0.00,
    tax_usd             NUMERIC(12, 2) DEFAULT 0.00,
    net_amount_usd      NUMERIC(12, 2),
    refund_amount_usd   NUMERIC(12, 2) DEFAULT 0.00,
    gateway_fee_usd     NUMERIC(12, 2) DEFAULT 0.00,
    installment_months  SMALLINT       DEFAULT 0,
    source_type         VARCHAR(20)    CHECK (source_type IN ('FLIGHT','HOTEL','CAR_RENTAL')),
    source_reference    VARCHAR(20)    -- booking_id / reservation_id / order_id
);

-- CREATE INDEX IF NOT EXISTS idx_payment_customer ON payment_source.src_payment_transaction (customer_key);
-- CREATE INDEX IF NOT EXISTS idx_payment_status   ON payment_source.src_payment_transaction (payment_status);
-- CREATE INDEX IF NOT EXISTS idx_payment_source   ON payment_source.src_payment_transaction (source_type, source_reference);
-- CREATE INDEX IF NOT EXISTS idx_payment_date     ON payment_source.src_payment_transaction (transaction_date);