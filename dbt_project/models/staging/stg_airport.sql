SELECT
    airport_code,
    airport_name,
    city,
    country,
    timezone,
    latitude::float AS latitude,
    longitude::float AS longitude
FROM airline.src_airport