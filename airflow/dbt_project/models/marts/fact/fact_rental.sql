select
    ro.order_id,
    ro.customer_key,
    rt.trip_id,
    rt.actual_pickup_date,
    rt.actual_dropoff_date,
    v.vehicle_id,
    d.driver_id,
    ap.airport_code as pickup_airport,
    hp.hotel_id as dropoff_hotel,
    ro.order_status,
    rt.trip_status,
    -- Measures
    ro.estimated_rate_usd,
    ro.base_charge_usd,
    ro.surcharge_usd,
    ro.total_charge_usd,
    rt.distance_km,
    rt.trip_duration_minutes,
    rt.pickup_delay_minutes,
    rt.driver_rating
from {{ ref('int_rental') }} ro
join {{ ref('dim_customer') }} c on ro.customer_key = c.customer_key
join {{ ref('dim_vehicle') }} v on ro.vehicle_id = v.vehicle_id
join {{ ref('dim_driver') }} d on rt.driver_id = d.driver_id
left join {{ ref('dim_airport') }} ap on ro.pickup_airport = ap.airport_code
left join {{ ref('dim_hotel_property') }} hp on rt.dropoff_hotel = hp.hotel_id;
