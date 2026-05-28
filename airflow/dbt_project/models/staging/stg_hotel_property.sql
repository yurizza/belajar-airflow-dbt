select
    hotel_id,
    concat(upper(substring(hotel_name, 1, 1)), lower(substring(hotel_name, 2))) as hotel_name,
    concat(upper(substring(brand, 1, 1)), lower(substring(brand, 2))) as brand,
    concat(upper(substring(city, 1, 1)), lower(substring(city, 2))) as city,
    cast(star_rating as integer) as star_rating,
    cast(total_rooms as integer) as total_rooms,
    cast(created_at as date) as created_at,
    cast(updated_at as date) as updated_at
from {{ source('hotel_source', 'src_hotel_property') }}