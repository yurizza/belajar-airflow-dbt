
  
    
    

    create  table
      "warehouse"."main"."dim_aircraft__dbt_tmp"
  
    as (
      select
    registration_number,
    aircraft_type,
    manufacturer,
    seat_capacity,
    operating_airline
from "warehouse"."main"."stg_aircraft";
    );
  
  