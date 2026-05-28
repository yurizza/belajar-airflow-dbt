
  
    
    

    create  table
      "warehouse"."main"."dim_room_inventory__dbt_tmp"
  
    as (
      select
    room_id,
    hotel_id,
    room_number,
    room_type_code,
    room_type_name,
    base_rate_usd,
    is_active
from "warehouse"."main"."stg_room_inventory"
    );
  
  