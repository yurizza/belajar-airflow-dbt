select
    driver_id,
    concat(upper(substring(driver_name, 1, 1)), lower(substring(driver_name, 2))) as driver_name,
    case when gender in ('M','F') then gender else null end as gender,
    license_no,
    upper(license_type) as license_type,
    regexp_replace(languages, '\s+', ' ', 'g') as languages,
    cast(rating as numeric) as rating,
    cast(total_trips as integer) as total_trips,
    cast(is_active as boolean) as is_active,
    cast(joined_date as date) as joined_date
from {{ source('rental_source', 'src_driver') }}