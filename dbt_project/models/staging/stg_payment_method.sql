SELECT
    payment_method_id,
    method_code,
    INITCAP(method_name) AS method_name,
    provider,
    CAST(created_at AS DATE) AS created_at,
    CAST(updated_at AS DATE) AS updated_at
FROM airline.src_payment_method
