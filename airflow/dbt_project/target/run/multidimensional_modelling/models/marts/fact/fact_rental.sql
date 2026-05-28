
  
    
    

    create  table
      "warehouse"."main"."fact_rental__dbt_tmp"
  
    as (
      -- depends_on: "warehouse"."main"."dim_date"
select
    ro.order_id,
    ro.customer_key,
    ro.reservation_id,
    ro.segment_id,
    ro.vehicle_id,
    ro.driver_id,
    ap.airport_code as pickup_airport,
    ro.order_status,
    -- Measures
    ro.estimated_rate_usd
from "warehouse"."main"."int_rental" ro
join "warehouse"."main"."dim_customer" c on ro.customer_key = c.customer_key
join "warehouse"."main"."dim_vehicle" v on ro.vehicle_id = v.vehicle_id
join "warehouse"."main"."dim_driver" d on ro.driver_id = d.driver_id
left join "warehouse"."main"."dim_airport" ap on ro.pickup_airport = ap.airport_code
    );
  
  