
  
  create view "data_warehouse"."main"."stg_guest_profile__dbt_tmp" as (
    select
    guest_id,
    cast(customer_key as integer) as customer_key,
    upper(preferred_room_type) as preferred_room_type,
    coalesce(special_requests, 'None') as special_requests,
    cast(created_at as date) as created_at
from "data_warehouse"."hotel_source"."src_guest_profile"
  );
