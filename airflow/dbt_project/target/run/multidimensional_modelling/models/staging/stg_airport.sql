
  
  create view "data_warehouse"."main"."stg_airport__dbt_tmp" as (
    select
    airport_code,
    initcap(airport_name) as airport_name,
    initcap(city) as city,
    initcap(country) as country,
    timezone,
    cast(latitude as numeric) as latitude,
    cast(longitude as numeric) as longitude
from "data_warehouse"."flight_source"."src_airport"
  );
