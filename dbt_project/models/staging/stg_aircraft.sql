SELECT
    registration_number,
    aircraft_type,
    manufacturer,
    seat_capacity::int AS seat_capacity,
    operating_airline
FROM airline.src_aircraft