select
    driver_id,
    driver_name,
    gender,
    license_no,
    license_type,
    languages,
    rating,
    total_trips,
    is_active,
    joined_date
from {{ ref('stg_driver') }};
