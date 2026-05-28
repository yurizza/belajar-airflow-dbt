
  
  create view "warehouse"."main"."int_hotel__dbt_tmp" as (
    select
    hp.hotel_id,
    hp.hotel_name,
    hp.brand,
    hp.city,
    hp.star_rating,
    hp.total_rooms,
    r.reservation_id,
    r.customer_key,
    hs.stay_id,
    hs.actual_checkin_date,
    hs.actual_nights,
    hs.incidental_usd
from "warehouse"."main"."stg_hotel_property" hp
left join "warehouse"."main"."stg_reservation" r on hp.hotel_id = r.hotel_id
left join "warehouse"."main"."stg_hotel_stay" hs on r.reservation_id = hs.reservation_id
  );
