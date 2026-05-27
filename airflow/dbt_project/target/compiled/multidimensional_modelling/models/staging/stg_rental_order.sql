select
    order_id,
    cast(customer_key as integer) as customer_key,
    reservation_id,
    segment_id,
    vehicle_id,
    driver_id,
    upper(pickup_airport) as pickup_airport,
    cast(order_date as date) as order_date,
    cast(scheduled_pickup as timestamp) as scheduled_pickup,
    initcap(order_status) as order_status,
    coalesce(special_request, 'None') as special_request,
    cast(estimated_rate_usd as numeric) as estimated_rate_usd
from "data_warehouse"."rental_source"."src_rental_order"