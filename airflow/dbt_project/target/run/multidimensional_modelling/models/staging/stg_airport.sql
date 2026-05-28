
  
  create view "warehouse"."main"."stg_airport__dbt_tmp" as (
    select
    airport_code,
    concat(upper(substring(airport_name, 1, 1)), lower(substring(airport_name, 2))) as airport_name,
    concat(upper(substring(city, 1, 1)), lower(substring(city, 2))) as city,
    concat(upper(substring(country, 1, 1)), lower(substring(country, 2))) as country,
    timezone,
    cast(latitude as numeric) as latitude,
    cast(longitude as numeric) as longitude
from "warehouse"."main"."src_airport"
  );
