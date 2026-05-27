select
    airport_code,
    initcap(airport_name) as airport_name,
    initcap(city) as city,
    initcap(country) as country,
    timezone,
    cast(latitude as numeric) as latitude,
    cast(longitude as numeric) as longitude
from "warehouse"."flight_source"."airport"