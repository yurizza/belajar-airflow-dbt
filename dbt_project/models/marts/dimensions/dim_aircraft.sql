SELECT
    ROW_NUMBER() OVER (ORDER BY registration_number) AS aircraft_key,
    registration_number,
    aircraft_type,
    manufacturer,
    seat_capacity,
    operating_airline
FROM {{ ref('stg_aircraft') }}