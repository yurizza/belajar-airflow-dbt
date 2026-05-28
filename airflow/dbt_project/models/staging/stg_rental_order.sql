select
    order_id,
    cast(customer_key as integer) as customer_key,
    reservation_id,
    segment_id,
    vehicle_id,
    driver_id,
    upper(pickup_airport) as pickup_airport,
    cast(order_date as date) as order_date,
    scheduled_pickup as scheduled_pickup,
    concat(upper(substring(order_status, 1, 1)), lower(substring(order_status, 2))) as order_status,
    coalesce(special_request, 'None') as special_request,
    cast(estimated_rate_usd as numeric) as estimated_rate_usd
from {{ source('rental_source', 'src_rental_order') }}