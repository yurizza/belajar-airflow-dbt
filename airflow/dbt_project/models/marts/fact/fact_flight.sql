-- depends_on: {{ ref('dim_date') }}
select
    fs.segment_id,
    fs.booking_id,
    b.customer_key,
    fs.origin_airport_code,
    fs.destination_airport_code,
    fs.scheduled_departure,
    fs.actual_departure,
    bc.channel_key,
    -- Measures / Metrik kualitatif
    datediff('minute', fs.scheduled_departure, fs.actual_departure) as actual_departure_delay_minutes,
    1 as segment_count
from {{ ref('int_flight') }} fs
join {{ ref('dim_customer') }} b on fs.customer_key = b.customer_key
join {{ ref('dim_airport') }} ap_o on fs.origin_airport_code = ap_o.airport_code
join {{ ref('dim_airport') }} ap_d on fs.destination_airport_code = ap_d.airport_code
join {{ ref('dim_booking_channel') }} bc on fs.channel_key = bc.channel_key