select
    guest_id,
    cast(customer_key as integer) as customer_key,
    upper(preferred_room_type) as preferred_room_type,
    initcap(smoking_preference) as smoking_preference,
    coalesce(special_request, 'None') as special_request,
    cast(created_at as date) as created_at
from "warehouse"."hotel_source"."guest_profile"