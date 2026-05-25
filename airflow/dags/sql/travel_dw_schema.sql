-- ═══════════════════════════════════════════════════════════════════
--  TRAVEL DATA WAREHOUSE — PostgreSQL DDL
--  Domains: Airline, Hotel, Payment
--  Features: Star schema, SCD Type 1 & 2, cross-domain FK
-- ═══════════════════════════════════════════════════════════════════

-- ───────────────────────────────────────────
--  SCHEMA
-- ───────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS airline;
CREATE SCHEMA IF NOT EXISTS hotel;
CREATE SCHEMA IF NOT EXISTS payment;


-- ═══════════════════════════════════════════════════════════════════
--  SHARED DIMENSIONS  (schema: public)
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE public.dim_date (
    date_key        INTEGER         PRIMARY KEY,
    full_date       DATE            NOT NULL UNIQUE,
    day_of_week     VARCHAR(10)     NOT NULL,
    day_num         SMALLINT        NOT NULL CHECK (day_num BETWEEN 1 AND 7),
    week_num        SMALLINT        NOT NULL CHECK (week_num BETWEEN 1 AND 53),
    month_num       SMALLINT        NOT NULL CHECK (month_num BETWEEN 1 AND 12),
    month_name      VARCHAR(10)     NOT NULL,
    quarter         SMALLINT        NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year            SMALLINT        NOT NULL,
    is_weekend      BOOLEAN         NOT NULL DEFAULT FALSE,
    is_holiday      BOOLEAN         NOT NULL DEFAULT FALSE,
    season          VARCHAR(10)     NOT NULL
);

CREATE TABLE public.dim_time_of_day (
    time_key        INTEGER         PRIMARY KEY,   -- HHMM format e.g. 800 = 08:00
    hour            SMALLINT        NOT NULL CHECK (hour BETWEEN 0 AND 23),
    minute          SMALLINT        NOT NULL CHECK (minute IN (0,15,30,45)),
    time_str        CHAR(5)         NOT NULL,      -- 'HH:MM'
    period_of_day   VARCHAR(10)     NOT NULL,      -- Morning/Afternoon/Evening/Night
    is_peak_hour    BOOLEAN         NOT NULL DEFAULT FALSE
);


-- ═══════════════════════════════════════════════════════════════════
--  AIRLINE DOMAIN
-- ═══════════════════════════════════════════════════════════════════

-- SCD Type 2
CREATE TABLE airline.dim_airport (
    airport_key         SERIAL          PRIMARY KEY,
    airport_code        CHAR(3)         NOT NULL,
    airport_name        VARCHAR(100)    NOT NULL,
    city                VARCHAR(60)     NOT NULL,
    country             VARCHAR(60)     NOT NULL,
    timezone            VARCHAR(40)     NOT NULL,
    latitude            NUMERIC(9,4)    NOT NULL,
    longitude           NUMERIC(9,4)    NOT NULL,
    terminal_count      SMALLINT,
    gate_count          SMALLINT,
    hub_type            VARCHAR(30),
    -- SCD2
    scd_effective_date  DATE            NOT NULL,
    scd_expiry_date     DATE            NOT NULL,
    scd_current_flag    BOOLEAN         NOT NULL DEFAULT TRUE,
    scd_version         SMALLINT        NOT NULL DEFAULT 1,
    CONSTRAINT uq_airport_version UNIQUE (airport_code, scd_version)
);

CREATE TABLE airline.dim_passenger (
    passenger_key           SERIAL          PRIMARY KEY,
    passenger_id            VARCHAR(20)     NOT NULL UNIQUE,
    first_name              VARCHAR(60)     NOT NULL,
    last_name               VARCHAR(60)     NOT NULL,
    gender                  CHAR(1)         NOT NULL CHECK (gender IN ('M','F')),
    date_of_birth           DATE,
    age_group               VARCHAR(10),
    nationality             VARCHAR(40),
    loyalty_tier            VARCHAR(10)     NOT NULL DEFAULT 'None',
    loyalty_miles_balance   INTEGER         NOT NULL DEFAULT 0,
    email                   VARCHAR(120),
    phone_country           VARCHAR(6)
);

-- SCD Type 2
CREATE TABLE airline.dim_passenger_profile (
    profile_key                 SERIAL          PRIMARY KEY,
    passenger_id                VARCHAR(20)     NOT NULL,
    frequent_flyer_num          VARCHAR(20),
    preferred_seat              VARCHAR(20),
    preferred_meal              VARCHAR(20),
    special_assistance          VARCHAR(10),
    marketing_consent           BOOLEAN         DEFAULT FALSE,
    lifetime_segments_flown     INTEGER         DEFAULT 0,
    lifetime_miles_earned       INTEGER         DEFAULT 0,
    customer_segment            VARCHAR(30),
    -- SCD2
    scd_effective_date          DATE            NOT NULL,
    scd_expiry_date             DATE            NOT NULL,
    scd_current_flag            BOOLEAN         NOT NULL DEFAULT TRUE,
    scd_version                 SMALLINT        NOT NULL DEFAULT 1,
    CONSTRAINT fk_profile_passenger FOREIGN KEY (passenger_id)
        REFERENCES airline.dim_passenger (passenger_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE airline.dim_aircraft (
    aircraft_key            SERIAL          PRIMARY KEY,
    registration_number     VARCHAR(10)     NOT NULL UNIQUE,
    aircraft_type_code      VARCHAR(6)      NOT NULL,
    aircraft_type_name      VARCHAR(50)     NOT NULL,
    manufacturer            VARCHAR(30),
    body_type               VARCHAR(15),
    seat_capacity           SMALLINT,
    year_manufactured       SMALLINT,
    operating_airline       VARCHAR(60),
    engine_type             VARCHAR(15),
    max_range_km            INTEGER,
    fuel_capacity_liters    INTEGER,
    in_service              BOOLEAN         DEFAULT TRUE
);

CREATE TABLE airline.dim_class_of_service (
    class_key               SERIAL          PRIMARY KEY,
    service_code            CHAR(1)         NOT NULL,
    service_name            VARCHAR(30)     NOT NULL,
    airline                 VARCHAR(60)     NOT NULL,
    cabin_width_cm          SMALLINT,
    seat_pitch_cm           SMALLINT,
    baggage_allowance_kg    SMALLINT,
    lounge_access           BOOLEAN         DEFAULT FALSE,
    priority_boarding       BOOLEAN         DEFAULT FALSE,
    meal_included           BOOLEAN         DEFAULT FALSE,
    seat_share_pct          NUMERIC(5,2),
    fare_multiplier         NUMERIC(5,2)
);

CREATE TABLE airline.dim_fare_basis (
    fare_key                SERIAL          PRIMARY KEY,
    fare_basis_code         VARCHAR(10)     NOT NULL UNIQUE,
    fare_name               VARCHAR(40)     NOT NULL,
    cabin_code              CHAR(1)         NOT NULL,
    fare_multiplier         NUMERIC(5,2),
    is_refundable           BOOLEAN         DEFAULT FALSE,
    is_changeable           BOOLEAN         DEFAULT FALSE,
    advance_purchase_days   SMALLINT        DEFAULT 0,
    minimum_stay_days       SMALLINT        DEFAULT 0,
    blackout_periods        BOOLEAN         DEFAULT FALSE
);

CREATE TABLE airline.dim_booking_channel (
    channel_key             SERIAL          PRIMARY KEY,
    channel_code            VARCHAR(5)      NOT NULL UNIQUE,
    channel_name            VARCHAR(40)     NOT NULL,
    channel_type            VARCHAR(10)     NOT NULL,
    commission_rate_pct     NUMERIC(5,2)    DEFAULT 0,
    booking_fee_usd         NUMERIC(8,2)    DEFAULT 0,
    typical_lead_days       SMALLINT,
    volume_share_pct        NUMERIC(5,2)
);

-- FACT
CREATE TABLE airline.fact_segment_flight_activity (
    segment_key                         BIGINT          PRIMARY KEY,
    -- Time FKs
    scheduled_departure_date_key        INTEGER         NOT NULL,
    scheduled_departure_time_key        INTEGER         NOT NULL,
    actual_departure_date_key           INTEGER         NOT NULL,
    actual_departure_time_key           INTEGER         NOT NULL,
    -- Dimension FKs
    passenger_key                       INTEGER         NOT NULL,
    passenger_profile_key               INTEGER         NOT NULL,
    segment_origin_airport_key          INTEGER         NOT NULL,
    segment_destination_airport_key     INTEGER         NOT NULL,
    aircraft_key                        INTEGER         NOT NULL,
    class_of_service_key                INTEGER         NOT NULL,
    fare_basis_key                      INTEGER         NOT NULL,
    booking_channel_key                 INTEGER         NOT NULL,
    -- Degenerate dimensions
    confirmation_number                 VARCHAR(20),
    ticket_number                       VARCHAR(20),
    segment_sequence_number             SMALLINT,
    flight_number                       VARCHAR(8),
    -- Measures
    base_fare_revenue_usd               NUMERIC(12,2),
    passenger_facility_charges_usd      NUMERIC(8,2),
    airport_tax_usd                     NUMERIC(8,2),
    government_tax_usd                  NUMERIC(8,2),
    baggage_charges_usd                 NUMERIC(8,2),
    upgrade_fees_usd                    NUMERIC(8,2),
    transaction_fees_usd                NUMERIC(8,2),
    total_revenue_usd                   NUMERIC(12,2),
    segment_miles_flown                 INTEGER,
    segment_miles_earned                INTEGER,
    delay_minutes                       INTEGER         DEFAULT 0,
    seat_capacity                       SMALLINT,
    flight_status                       VARCHAR(15),
    load_factor_pct                     NUMERIC(5,1),
    -- Constraints
    CONSTRAINT fk_fact_air_sched_dep_date   FOREIGN KEY (scheduled_departure_date_key)   REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_fact_air_sched_dep_time   FOREIGN KEY (scheduled_departure_time_key)   REFERENCES public.dim_time_of_day (time_key),
    CONSTRAINT fk_fact_air_act_dep_date     FOREIGN KEY (actual_departure_date_key)      REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_fact_air_act_dep_time     FOREIGN KEY (actual_departure_time_key)      REFERENCES public.dim_time_of_day (time_key),
    CONSTRAINT fk_fact_air_passenger        FOREIGN KEY (passenger_key)                 REFERENCES airline.dim_passenger (passenger_key),
    CONSTRAINT fk_fact_air_profile          FOREIGN KEY (passenger_profile_key)         REFERENCES airline.dim_passenger_profile (profile_key),
    CONSTRAINT fk_fact_air_origin           FOREIGN KEY (segment_origin_airport_key)    REFERENCES airline.dim_airport (airport_key),
    CONSTRAINT fk_fact_air_destination      FOREIGN KEY (segment_destination_airport_key) REFERENCES airline.dim_airport (airport_key),
    CONSTRAINT fk_fact_air_aircraft         FOREIGN KEY (aircraft_key)                  REFERENCES airline.dim_aircraft (aircraft_key),
    CONSTRAINT fk_fact_air_class            FOREIGN KEY (class_of_service_key)          REFERENCES airline.dim_class_of_service (class_key),
    CONSTRAINT fk_fact_air_fare             FOREIGN KEY (fare_basis_key)                REFERENCES airline.dim_fare_basis (fare_key),
    CONSTRAINT fk_fact_air_channel         FOREIGN KEY (booking_channel_key)            REFERENCES airline.dim_booking_channel (channel_key)
);


-- ═══════════════════════════════════════════════════════════════════
--  HOTEL DOMAIN
-- ═══════════════════════════════════════════════════════════════════

-- SCD Type 2
CREATE TABLE hotel.dim_hotel_property (
    hotel_property_key      SERIAL          PRIMARY KEY,
    hotel_id                VARCHAR(10)     NOT NULL,
    hotel_name              VARCHAR(100)    NOT NULL,
    brand                   VARCHAR(40)     NOT NULL,
    category                VARCHAR(20),
    star_rating             SMALLINT        CHECK (star_rating BETWEEN 1 AND 5),
    city                    VARCHAR(60)     NOT NULL,
    country                 VARCHAR(60)     NOT NULL,
    currency                CHAR(3)         NOT NULL,
    local_tax_rate          NUMERIC(6,4),
    latitude                NUMERIC(9,4),
    longitude               NUMERIC(9,4),
    total_rooms             SMALLINT,
    has_pool                BOOLEAN         DEFAULT FALSE,
    has_gym                 BOOLEAN         DEFAULT FALSE,
    has_spa                 BOOLEAN         DEFAULT FALSE,
    price_range_low_usd     NUMERIC(10,2),
    price_range_high_usd    NUMERIC(10,2),
    -- SCD2
    scd_effective_date      DATE            NOT NULL,
    scd_expiry_date         DATE            NOT NULL,
    scd_current_flag        BOOLEAN         NOT NULL DEFAULT TRUE,
    scd_version             SMALLINT        NOT NULL DEFAULT 1
);

-- SCD Type 1 (overwrite)
CREATE TABLE hotel.dim_customer (
    customer_key            INTEGER         PRIMARY KEY,  -- same as passenger_key
    passenger_key_ref       INTEGER         NOT NULL,
    customer_id             VARCHAR(20)     NOT NULL UNIQUE,
    first_name              VARCHAR(60)     NOT NULL,
    last_name               VARCHAR(60)     NOT NULL,
    gender                  CHAR(1)         CHECK (gender IN ('M','F')),
    nationality             VARCHAR(40),
    age_group               VARCHAR(10),
    loyalty_tier            VARCHAR(10),
    hotel_loyalty_num       VARCHAR(20),
    hotel_loyalty_tier      VARCHAR(10),
    preferred_room_type     VARCHAR(5),
    smoking_preference      VARCHAR(15),
    travel_purpose          VARCHAR(20),
    email                   VARCHAR(120),
    last_updated            DATE,
    CONSTRAINT fk_hotel_cust_passenger FOREIGN KEY (passenger_key_ref)
        REFERENCES airline.dim_passenger (passenger_key)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE hotel.dim_booking_channel (
    booking_channel_key     SERIAL          PRIMARY KEY,
    channel_code            VARCHAR(5)      NOT NULL UNIQUE,
    channel_name            VARCHAR(40)     NOT NULL,
    channel_type            VARCHAR(10)     NOT NULL,
    commission_rate_pct     NUMERIC(5,2)    DEFAULT 0,
    instant_confirm         BOOLEAN         DEFAULT FALSE,
    cancellation_policy     VARCHAR(15),
    volume_share_pct        NUMERIC(5,2),
    avg_lead_days           SMALLINT
);

-- FACT
CREATE TABLE hotel.fact_hotel_stay (
    hotel_stay_key              BIGINT          PRIMARY KEY,
    -- Time FKs
    reservation_date_key        INTEGER         NOT NULL,
    arrival_date_key            INTEGER         NOT NULL,
    departure_date_key          INTEGER         NOT NULL,
    -- Dimension FKs
    customer_key                INTEGER         NOT NULL,
    hotel_property_key          INTEGER         NOT NULL,
    booking_channel_key         INTEGER         NOT NULL,
    -- Degenerate dimensions
    confirmation_number         VARCHAR(20),
    ticket_number               VARCHAR(20),
    number_of_nights            SMALLINT        NOT NULL DEFAULT 1,
    room_type_code              CHAR(3),
    room_type_name              VARCHAR(30),
    -- Measures
    nightly_rate_usd            NUMERIC(10,2),
    extended_room_charge_usd    NUMERIC(12,2),
    tax_charge_usd              NUMERIC(10,2),
    extra_charges_usd           NUMERIC(10,2)   DEFAULT 0,
    commission_paid_usd         NUMERIC(10,2)   DEFAULT 0,
    net_revenue_usd             NUMERIC(12,2),
    total_bill_usd              NUMERIC(12,2),
    reservation_status          VARCHAR(15),
    lead_time_days              SMALLINT        DEFAULT 0,
    linked_flight_segment       BOOLEAN         DEFAULT FALSE,
    -- Constraints
    CONSTRAINT fk_fact_hotel_res_date    FOREIGN KEY (reservation_date_key) REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_fact_hotel_arr_date    FOREIGN KEY (arrival_date_key)     REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_fact_hotel_dep_date    FOREIGN KEY (departure_date_key)   REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_fact_hotel_customer    FOREIGN KEY (customer_key)         REFERENCES hotel.dim_customer (customer_key),
    CONSTRAINT fk_fact_hotel_property    FOREIGN KEY (hotel_property_key)   REFERENCES hotel.dim_hotel_property (hotel_property_key),
    CONSTRAINT fk_fact_hotel_channel     FOREIGN KEY (booking_channel_key)  REFERENCES hotel.dim_booking_channel (booking_channel_key)
);


-- ═══════════════════════════════════════════════════════════════════
--  PAYMENT DOMAIN
-- ═══════════════════════════════════════════════════════════════════

-- SCD Type 2
CREATE TABLE payment.dim_payment_method (
    payment_method_key          SERIAL          PRIMARY KEY,
    method_code                 VARCHAR(15)     NOT NULL,
    method_name                 VARCHAR(40)     NOT NULL,
    payment_type                VARCHAR(20)     NOT NULL,
    provider                    VARCHAR(20),
    card_brand                  VARCHAR(15),
    is_digital_wallet           BOOLEAN         DEFAULT FALSE,
    processing_fee_pct          NUMERIC(6,3),
    volume_share_pct            NUMERIC(5,2),
    supports_installment        BOOLEAN         DEFAULT FALSE,
    max_installment_months      SMALLINT        DEFAULT 0,
    supports_refund             BOOLEAN         DEFAULT TRUE,
    daily_limit_usd             NUMERIC(12,2),
    -- SCD2
    scd_effective_date          DATE            NOT NULL,
    scd_expiry_date             DATE            NOT NULL,
    scd_current_flag            BOOLEAN         NOT NULL DEFAULT TRUE,
    scd_version                 SMALLINT        NOT NULL DEFAULT 1,
    CONSTRAINT uq_pay_method_version UNIQUE (method_code, scd_version)
);

CREATE TABLE payment.dim_currency (
    currency_key            SERIAL          PRIMARY KEY,
    currency_code           CHAR(3)         NOT NULL UNIQUE,
    currency_name           VARCHAR(40)     NOT NULL,
    currency_symbol         VARCHAR(5),
    usd_exchange_rate       NUMERIC(12,4)   NOT NULL,
    rate_effective_date     DATE,
    is_base_currency        BOOLEAN         DEFAULT FALSE,
    region                  VARCHAR(20)
);

-- FACT
CREATE TABLE payment.fact_payment_transaction (
    payment_key                 BIGINT          PRIMARY KEY,
    -- Time FKs
    payment_date_key            INTEGER         NOT NULL,
    payment_time_key            INTEGER         NOT NULL,
    -- Dimension FKs
    customer_key                INTEGER         NOT NULL,
    payment_method_key          INTEGER         NOT NULL,
    currency_key                INTEGER         NOT NULL,
    -- Cross-domain FKs (nullable — one or the other)
    flight_segment_key          BIGINT,
    hotel_stay_key              BIGINT,
    -- Degenerate dimensions
    payment_reference           VARCHAR(20),
    invoice_number              VARCHAR(30),
    payment_status              VARCHAR(20),
    payment_gateway             VARCHAR(15),
    installment_months          SMALLINT        DEFAULT 0,
    transaction_source          VARCHAR(10),
    -- Measures
    gross_amount_usd            NUMERIC(12,2),
    discount_amount_usd         NUMERIC(10,2)   DEFAULT 0,
    tax_amount_usd              NUMERIC(10,2)   DEFAULT 0,
    net_amount_usd              NUMERIC(12,2),
    refund_amount_usd           NUMERIC(12,2)   DEFAULT 0,
    gateway_fee_usd             NUMERIC(10,2)   DEFAULT 0,
    loyalty_points_used         INTEGER         DEFAULT 0,
    loyalty_points_earned       INTEGER         DEFAULT 0,
    transaction_amount_local    NUMERIC(14,2),
    source_reference_num        VARCHAR(20),
    -- Constraints
    CONSTRAINT fk_pay_date          FOREIGN KEY (payment_date_key)      REFERENCES public.dim_date (date_key),
    CONSTRAINT fk_pay_time          FOREIGN KEY (payment_time_key)      REFERENCES public.dim_time_of_day (time_key),
    CONSTRAINT fk_pay_customer      FOREIGN KEY (customer_key)          REFERENCES hotel.dim_customer (customer_key),
    CONSTRAINT fk_pay_method        FOREIGN KEY (payment_method_key)    REFERENCES payment.dim_payment_method (payment_method_key),
    CONSTRAINT fk_pay_currency      FOREIGN KEY (currency_key)          REFERENCES payment.dim_currency (currency_key),
    CONSTRAINT fk_pay_flight        FOREIGN KEY (flight_segment_key)    REFERENCES airline.fact_segment_flight_activity (segment_key),
    CONSTRAINT fk_pay_hotel         FOREIGN KEY (hotel_stay_key)        REFERENCES hotel.fact_hotel_stay (hotel_stay_key),
    CONSTRAINT chk_pay_source CHECK (
        (flight_segment_key IS NOT NULL AND hotel_stay_key IS NULL) OR
        (flight_segment_key IS NULL AND hotel_stay_key IS NOT NULL) OR
        (flight_segment_key IS NULL AND hotel_stay_key IS NULL)
    )
);


-- ═══════════════════════════════════════════════════════════════════
--  INDEXES
-- ═══════════════════════════════════════════════════════════════════

CREATE INDEX idx_airport_code         ON airline.dim_airport (airport_code, scd_current_flag);
CREATE INDEX idx_airport_current      ON airline.dim_airport (scd_current_flag) WHERE scd_current_flag = TRUE;

CREATE INDEX idx_profile_pax          ON airline.dim_passenger_profile (passenger_id, scd_current_flag);
CREATE INDEX idx_profile_current      ON airline.dim_passenger_profile (scd_current_flag) WHERE scd_current_flag = TRUE;

CREATE INDEX idx_fact_air_dates       ON airline.fact_segment_flight_activity (scheduled_departure_date_key);
CREATE INDEX idx_fact_air_pax         ON airline.fact_segment_flight_activity (passenger_key);
CREATE INDEX idx_fact_air_route       ON airline.fact_segment_flight_activity (segment_origin_airport_key, segment_destination_airport_key);
CREATE INDEX idx_fact_air_status      ON airline.fact_segment_flight_activity (flight_status);

CREATE INDEX idx_hotel_prop_current   ON hotel.dim_hotel_property (scd_current_flag) WHERE scd_current_flag = TRUE;
CREATE INDEX idx_hotel_prop_city      ON hotel.dim_hotel_property (city, scd_current_flag);

CREATE INDEX idx_fact_hotel_arr       ON hotel.fact_hotel_stay (arrival_date_key);
CREATE INDEX idx_fact_hotel_cust      ON hotel.fact_hotel_stay (customer_key);
CREATE INDEX idx_fact_hotel_status    ON hotel.fact_hotel_stay (reservation_status);

CREATE INDEX idx_pay_method_current   ON payment.dim_payment_method (scd_current_flag) WHERE scd_current_flag = TRUE;

CREATE INDEX idx_fact_pay_date        ON payment.fact_payment_transaction (payment_date_key);
CREATE INDEX idx_fact_pay_customer    ON payment.fact_payment_transaction (customer_key);
CREATE INDEX idx_fact_pay_status      ON payment.fact_payment_transaction (payment_status);
CREATE INDEX idx_fact_pay_gateway     ON payment.fact_payment_transaction (payment_gateway);
CREATE INDEX idx_fact_pay_flight      ON payment.fact_payment_transaction (flight_segment_key) WHERE flight_segment_key IS NOT NULL;
CREATE INDEX idx_fact_pay_hotel       ON payment.fact_payment_transaction (hotel_stay_key)     WHERE hotel_stay_key IS NOT NULL;

