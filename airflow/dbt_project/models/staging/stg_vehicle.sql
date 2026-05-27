select
    vehicle_id,
    plate,
    upper(type_code) as type_code,
    initcap(type_name) as type_name,
    initcap(category) as category,
    initcap(brand) as brand,
    initcap(model) as model,
    cast(seat_capacity as integer) as seat_capacity,
    cast(rate_usd_day as numeric) as rate_usd_day,
    cast(prod_year as integer) as prod_year,
    initcap(status) as status
from {{ source('rental_source','src_vehicle') }}