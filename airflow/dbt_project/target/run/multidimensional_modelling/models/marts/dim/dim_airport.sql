
  
    
    

    create  table
      "warehouse"."main"."dim_airport__dbt_tmp"
  
    as (
      select
    airport_code,
    airport_name,
    city,
    country,
    timezone,
    latitude,
    longitude
from "warehouse"."main"."stg_airport"
    );
  
  