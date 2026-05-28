select
    fs.segment_id,
    fs.booking_id,
    fs.flight_number,
    fs.origin_airport as origin_airport_code,
    fs.destination_airport as destination_airport_code,
    sa.airport_name as origin_airport_name,
    aa.airport_name as destination_airport_name,
    fs.scheduled_departure,
    fs.actual_departure,
    fs.status,
    b.customer_key,
    b.booking_channel,
    bc.channel_key
from {{ ref('stg_flight_segment') }} fs
left join {{ ref('stg_airport') }} sa on fs.origin_airport = sa.airport_code
left join {{ ref('stg_airport') }} aa on fs.destination_airport = aa.airport_code
left join {{ ref('stg_booking') }} b on fs.booking_id = b.booking_id
left join {{ ref('stg_booking_channel') }} bc on b.booking_channel = bc.channel_code