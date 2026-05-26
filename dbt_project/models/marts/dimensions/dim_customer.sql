SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    first_name,
    last_name,
    gender,
    nationality,
    email,
    phone
FROM {{ ref('stg_customer') }}
