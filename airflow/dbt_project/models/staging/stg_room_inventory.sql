select
    room_id,
    hotel_id,
    cast(room_number as integer) as room_number,
    upper(room_type_code) as room_type_code,
    concat(upper(substring(room_type_name, 1, 1)), lower(substring(room_type_name, 2))) as room_type_name,
    cast(base_rate_usd as numeric) as base_rate_usd,
    cast(is_active as boolean) as is_active
from {{ source('hotel_source', 'src_room_inventory') }}