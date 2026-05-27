
  
  create view "warehouse"."staging"."stg_aircraft__dbt_tmp" as (
    select
    registration_number,
    aircraft_type,
    manufacturer,
    cast(seat_capacity as integer) as seat_capacity,
    initcap(operating_airline) as operating_airline
from "warehouse"."flight_source"."aircraft"
  );
