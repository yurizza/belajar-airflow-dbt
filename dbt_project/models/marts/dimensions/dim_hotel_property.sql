SELECT
    ROW_NUMBER() OVER (ORDER BY hotel_id) AS hotel_property_key,
    hotel_id,
    hotel_name,
    brand,
    city,
    star_rating,
    total_rooms,
    has_pool,
    has_gym
FROM {{ ref('stg_hotel_property') }}
