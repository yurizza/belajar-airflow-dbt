SELECT
    hotel_id,
    hotel_name,
    brand,
    city,
    star_rating::int AS star_rating,
    total_rooms::int AS total_rooms,
    has_pool::boolean AS has_pool,
    has_gym::boolean AS has_gym,
    CAST(created_at AS DATE) AS created_at,
    CAST(updated_at AS DATE) AS updated_at
FROM airline.src_hotel_property