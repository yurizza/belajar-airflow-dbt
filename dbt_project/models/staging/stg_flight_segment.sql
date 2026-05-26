SELECT
    segment_id,
    booking_id,
    flight_number,
    origin_airport,
    destination_airport,
    CAST(scheduled_departure AS TIMESTAMP) AS scheduled_departure,
    CAST(actual_departure AS TIMESTAMP) AS actual_departure,
    INITCAP(status) AS status
FROM airline.src_flight_segment