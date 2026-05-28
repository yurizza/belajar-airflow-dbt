
  
    
    

    create  table
      "warehouse"."main"."dim_hotel_property__dbt_tmp"
  
    as (
      select
    hotel_id,
    hotel_name,
    brand,
    city,
    star_rating,
    total_rooms
from "warehouse"."main"."stg_hotel_property"
    );
  
  