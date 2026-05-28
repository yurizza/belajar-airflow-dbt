
  
  create view "warehouse"."main"."stg_rental_trip__dbt_tmp" as (
    select
    cast(trip_id as integer) as trip_id,
    order_id,
    cast(actual_pickup as timestamp) as actual_pickup,
    cast(actual_dropoff as timestamp) as actual_dropoff,
    cast(delay_minutes as integer) as delay_minutes,
    cast(duration_minutes as integer) as duration_minutes,
    cast(distance_km as numeric) as distance_km,
    cast(base_charge_usd as numeric) as base_charge_usd,
    cast(surcharge_usd as numeric) as surcharge_usd,
    cast(total_charge_usd as numeric) as total_charge_usd,
    concat(upper(substring(trip_status, 1, 1)), lower(substring(trip_status, 2))) as trip_status,
    cast(driver_rating as numeric) as driver_rating
from "warehouse"."main"."src_rental_trip"
  );
