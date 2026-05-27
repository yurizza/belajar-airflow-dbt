select
    airport_code,
    airport_name,
    city,
    country,
    timezone,
    latitude,
    longitude
from {{ ref('stg_airport') }};
