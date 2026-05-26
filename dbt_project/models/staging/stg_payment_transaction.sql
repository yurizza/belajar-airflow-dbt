SELECT
    transaction_id,
    customer_id,
    CAST(payment_date AS DATE) AS payment_date,
    payment_method,
    currency_code,
    gross_amount_usd::numeric AS gross_amount_usd,
    discount_amount_usd::numeric AS discount_amount_usd,
    tax_amount_usd::numeric AS tax_amount_usd,
    net_amount_usd::numeric AS net_amount_usd,
    refund_amount_usd::numeric AS refund_amount_usd,
    gateway_fee_usd::numeric AS gateway_fee_usd,
    loyalty_points_used::int AS loyalty_points_used,
    loyalty_points_earned::int AS loyalty_points_earned,
    transaction_amount_local::numeric AS transaction_amount_local
FROM airline.src_payment_transaction
