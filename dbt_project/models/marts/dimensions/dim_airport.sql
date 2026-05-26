SELECT
    ROW_NUMBER() OVER (ORDER BY airport_code) AS airport_key,
    airport_code,
    airport_name,
    city,
    country,
    timezone,
    latitude,
    longitude
FROM {{ ref('stg_airport') }}