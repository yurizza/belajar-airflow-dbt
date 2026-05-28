select
    hotel_id,
    hotel_name,
    brand,
    city,
    star_rating,
    total_rooms
from {{ ref('stg_hotel_property') }}