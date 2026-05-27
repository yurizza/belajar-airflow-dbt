
  
  create view "warehouse"."staging"."stg_room_inventory__dbt_tmp" as (
    select
    room_id,
    hotel_id,
    cast(room_number as integer) as room_number,
    upper(room_type_code) as room_type_code,
    initcap(room_type_name) as room_type_name,
    cast(base_rate_usd as numeric) as base_rate_usd,
    cast(is_active as boolean) as is_active
from "warehouse"."hotel_source"."room_inventory"
  );
