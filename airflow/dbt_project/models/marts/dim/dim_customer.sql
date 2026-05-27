select
    customer_key,
    customer_id,
    first_name,
    last_name,
    gender,
    date_of_birth,
    nationality,
    email,
    phone,
    is_current
from {{ ref('stg_customer') }};
