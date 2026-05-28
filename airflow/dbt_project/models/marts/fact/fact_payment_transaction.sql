-- depends_on: {{ ref('dim_date') }}
select
    pt.payment_id,
    pt.customer_key,
    pt.transaction_date,
    pt.transaction_time,
    pt.payment_method_id,
    pt.currency_code,
    -- Measures (Duplikasi kolom yang sama sudah dihapus)
    pt.gross_amount_usd,
    pt.discount_usd,
    pt.tax_usd,
    pt.net_amount_usd,
    pt.refund_amount_usd,
    pt.gateway_fee_usd,
    pt.installment_months,
    pt.net_amount_usd * cur.usd_exchange_rate as transaction_amount_local
from {{ ref('int_payment_transaction') }} pt
join {{ ref('dim_customer') }} c on pt.customer_key = c.customer_key
join {{ ref('dim_payment_method') }} pm on pt.payment_method_id = pm.payment_method_id
join {{ ref('dim_currency') }} cur on pt.currency_code = cur.currency_code