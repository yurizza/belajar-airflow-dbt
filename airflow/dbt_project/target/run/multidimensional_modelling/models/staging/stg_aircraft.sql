
  
  create view "data_warehouse"."main"."stg_aircraft__dbt_tmp" as (
    select
    registration,
    aircraft_type,
    manufacturer,
    cast(seat_capacity as integer) as seat_capacity,
    initcap(airline) as operating_airline
from "data_warehouse"."flight_source"."src_aircraft"
  );
