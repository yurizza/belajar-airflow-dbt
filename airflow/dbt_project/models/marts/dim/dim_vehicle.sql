select
    vehicle_id,
    plate,
    type_code,
    type_name,
    category,
    brand,
    model,
    seat_capacity,
    rate_usd_day,
    prod_year,
    status
from {{ ref('stg_vehicle') }}