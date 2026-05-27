
  
  create view "data_warehouse"."main"."stg_hotel_property__dbt_tmp" as (
    select
    hotel_id,
    initcap(hotel_name) as hotel_name,
    initcap(brand) as brand,
    initcap(city) as city,
    cast(star_rating as integer) as star_rating,
    cast(total_rooms as integer) as total_rooms,
    cast(created_at as date) as created_at,
    cast(updated_at as date) as updated_at
from "data_warehouse"."hotel_source"."src_hotel_property"
  );
