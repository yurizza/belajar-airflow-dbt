select
    hotel_id,
    hotel_name,
    brand,
    city,
    star_rating,
    total_rooms,
    has_pool,
    has_gym
from {{ ref('stg_hotel_property') }};
