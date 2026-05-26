SELECT
    pt.transaction_id,
    dc.customer_key,
    dpm.payment_method_key,
    dcurr.currency_key,
    dd.date_key             AS payment_date_key,
    dt.time_of_day_key,
    pt.gross_amount_usd,
    pt.discount_amount_usd,
    pt.tax_amount_usd,
    pt.net_amount_usd,
    pt.refund_amount_usd,
    pt.gateway_fee_usd,
    pt.loyalty_points_used,
    pt.loyalty_points_earned,
    (pt.net_amount_usd * dcurr.usd_exchange_rate) AS transaction_amount_local
FROM {{ ref('int_payment_transaction_detail') }} pt
JOIN {{ ref('dim_customer') }} dc ON pt.customer_id = dc.customer_id
JOIN {{ ref('dim_payment_method') }} dpm ON pt.payment_method = dpm.method_code
JOIN {{ ref('dim_currency') }} dcurr ON pt.currency_code = dcurr.currency_code
JOIN {{ ref('dim_date') }} dd ON pt.payment_date::date = dd.full_date
JOIN {{ ref('dim_time_of_day') }} dt ON EXTRACT(HOUR FROM pt.payment_date) = dt.hour
