select
    b.booking_id,
    b.customer_key,
    fs.segment_id,
    fs.origin_airport_code,
    fs.destination_airport_code,
    fs.scheduled_departure,
    fs.actual_departure,
    fs.gross_amount_usd,
    ac.aircraft_id,
    ac.registration_number,
    ac.seat_capacity,
    bc.channel_key
from {{ ref('stg_booking') }} b
join {{ ref('stg_flight_segment') }} fs on b.booking_id = fs.booking_id
join {{ ref('stg_airport') }} ap on fs.origin_airport_code = ap.airport_code
join {{ ref('stg_book_channel') }} bc on b.channel_key = bc.channel_key
