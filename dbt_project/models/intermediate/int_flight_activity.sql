SELECT
    fs.segment_id,
    fs.booking_id,
    fs.flight_number,
    fs.origin_airport,
    fs.destination_airport,
    fs.scheduled_departure,
    fs.actual_departure,
    b.booking_date,
    c.customer_id,
    a.aircraft_type,
    a.seat_capacity
FROM {{ ref('stg_flight_segment') }} fs
JOIN {{ ref('stg_booking') }} b 
  ON fs.booking_id = b.booking_id
JOIN {{ ref('stg_customer') }} c 
  ON b.customer_id = c.customer_id
JOIN {{ ref('stg_aircraft') }} a 
  ON fs.aircraft_code = a.aircraft_code