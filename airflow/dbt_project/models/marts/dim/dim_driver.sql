select
    driver_id,
    driver_name,
    gender,
    license_no,
    license_type,
    rating,
    total_trips,
    is_active
from {{ ref('stg_driver') }}