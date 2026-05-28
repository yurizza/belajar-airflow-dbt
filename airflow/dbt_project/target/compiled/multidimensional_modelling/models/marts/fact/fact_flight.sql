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
from "warehouse"."main"."int_flight" fs
join "warehouse"."main"."dim_customer" b on fs.customer_key = b.customer_key
join "warehouse"."main"."dim_airport" ap_o on fs.origin_airport_code = ap_o.airport_code
join "warehouse"."main"."dim_airport" ap_d on fs.destination_airport_code = ap_d.airport_code
join "warehouse"."main"."dim_booking_channel" bc on fs.channel_key = bc.channel_key