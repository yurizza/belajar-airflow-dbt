select
    ro.order_id,
    ro.customer_key,
    cust.customer_id,
    ro.reservation_id,
    ro.segment_id,
    ro.vehicle_id,
    ro.driver_id,
    d.driver_name,
    ro.pickup_airport,
    ro.order_date,
    ro.scheduled_pickup,
    ro.order_status,
    ro.special_request,
    ro.estimated_rate_usd,
    rt.trip_id,
    rt.actual_pickup,
    rt.actual_dropoff,
    rt.delay_minutes,
    rt.duration_minutes,
    rt.distance_km,
    rt.base_charge_usd,
    rt.surcharge_usd,
    rt.total_charge_usd,
    rt.trip_status,
    rt.driver_rating
from {{ ref('stg_rental_order') }} ro
left join {{ ref('stg_customer') }} cust on ro.customer_key = cust.customer_key
left join {{ ref('stg_driver') }} d on ro.driver_id = d.driver_id
left join {{ ref('stg_rental_trip') }} rt on ro.order_id = rt.order_id