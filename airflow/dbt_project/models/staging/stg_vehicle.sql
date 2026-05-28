select
    vehicle_id,
    plate,
    upper(type_code) as type_code,
    concat(upper(substring(type_name, 1, 1)), lower(substring(type_name, 2))) as type_name,
    concat(upper(substring(category, 1, 1)), lower(substring(category, 2))) as category,
    concat(upper(substring(brand, 1, 1)), lower(substring(brand, 2))) as brand,
    concat(upper(substring(model, 1, 1)), lower(substring(model, 2))) as model,
    cast(seat_capacity as integer) as seat_capacity,
    cast(rate_usd_day as numeric) as rate_usd_day,
    cast(prod_year as integer) as prod_year,
    concat(upper(substring(status, 1, 1)), lower(substring(status, 2))) as status
from {{ source('rental_source', 'src_vehicle') }}