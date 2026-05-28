select
    booking_id,
    cast(customer_key as integer) as customer_key,
    customer_id,
    cast(booking_date as date) as booking_date,
    upper(booking_channel) as booking_channel
from "warehouse"."flight_source"."src_booking"