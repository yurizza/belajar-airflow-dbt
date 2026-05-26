SELECT
    ROW_NUMBER() OVER (ORDER BY method_code) AS payment_method_key,
    method_code,
    method_name,
    provider
FROM {{ ref('stg_payment_method') }}