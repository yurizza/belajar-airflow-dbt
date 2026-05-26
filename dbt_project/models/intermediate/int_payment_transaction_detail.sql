SELECT
    pt.transaction_id,
    pt.customer_id,
    pt.payment_date,
    pt.payment_method,
    pt.currency_code,
    pt.net_amount_usd,
    pt.gross_amount_usd,
    pt.tax_amount_usd,
    pt.refund_amount_usd,
    c.first_name,
    c.last_name,
    pm.method_name,
    curr.currency_name,
    curr.usd_exchange_rate
FROM {{ ref('stg_payment_transaction') }} pt
JOIN {{ ref('stg_customer') }} c 
  ON pt.customer_id = c.customer_id
JOIN {{ ref('stg_payment_method') }} pm 
  ON pt.payment_method = pm.method_code
JOIN {{ ref('stg_currency') }} curr 
  ON pt.currency_code = curr.currency_code