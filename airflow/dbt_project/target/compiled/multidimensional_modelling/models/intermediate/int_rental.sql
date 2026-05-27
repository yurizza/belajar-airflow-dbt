select
    ro.order_id,
    ro.customer_key,
    ro.scheduled_pickup_date,
    rt.trip_id,
    rt.actual_pickup_date,
    rt.actual_dropoff_date,
    rt.distance_km,
    rt.trip_duration_minutes,
    rt.pickup_delay_minutes,
    rt.driver_rating,
    v.vehicle_id,
    v.type_name,
    v.brand,
    v.model,
    d.driver_id,
    d.driver_name,
    ap.airport_code as pickup_airport,
    hp.hotel_id as dropoff_hotel,
    ro.status as order_status,
    rt.status as trip_status,
    ro.estimated_rate_usd,
    ro.base_charge_usd,
    ro.surcharge_usd,
    ro.total_charge_usd
from "warehouse"."rental_source"."src_rental_order" ro
join "warehouse"."rental_source"."src_rental_trip" rt on ro.order_id = rt.order_id
join "warehouse"."rental_source"."src_vehicle" v on ro.vehicle_id = v.vehicle_id
join "warehouse"."rental_source"."src_driver" d on rt.driver_id = d.driver_id
left join "warehouse"."flight_source"."src_airport" ap on ro.pickup_airport_code = ap.airport_code
left join "warehouse"."hotel_source"."src_hotel_property" hp on rt.dropoff_hotel_id = hp.hotel_id