
  
    
    

    create  table
      "warehouse"."main"."fact_hotel__dbt_tmp"
  
    as (
      -- depends_on: "warehouse"."main"."dim_date"
select
    hs.stay_id,
    r.reservation_id,
    r.guest_id,
    r.hotel_id,
    r.arrival_date as scheduled_checkin_date, 
    hs.actual_checkin_date,
    hs.actual_nights,
    hs.incidental_usd,
    -- Measures / Metrics
    hs.incidental_usd as total_incidental_charges_usd
from "warehouse"."main"."stg_hotel_stay" hs
join "warehouse"."main"."stg_reservation" r on hs.reservation_id = r.reservation_id
    );
  
  