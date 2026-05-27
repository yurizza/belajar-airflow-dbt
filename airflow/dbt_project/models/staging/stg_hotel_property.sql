select
    hotel_id,
    initcap(hotel_name) as hotel_name,
    initcap(brand) as brand,
    initcap(city) as city,
    cast(star_rating as integer) as star_rating,
    cast(total_rooms as integer) as total_rooms,
    cast(has_pool as boolean) as has_pool,
    cast(has_gym as boolean) as has_gym,
    cast(created_at as date) as created_at,
    cast(updated_at as date) as updated_at
from {{ source('hotel_source', 'src_hotel_property') }}