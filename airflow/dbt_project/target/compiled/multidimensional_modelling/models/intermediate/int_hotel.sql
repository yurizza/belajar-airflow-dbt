select
    pt.payment_id,
    pt.customer_key,
    pt.transaction_date,
    pt.gross_amount_usd,
    pt.discount_amount_usd,
    pt.tax_amount_usd,
    pt.net_amount_usd,
    pt.refund_amount_usd,
    pt.gateway_fee_usd,
    pt.installment_months,
    pm.payment_method_id,
    pm.method_code,
    pm.method_name,
    pm.payment_type,
    pm.provider,
    pm.processing_fee_pct,
    pm.supports_installment,
    cur.currency_code,
    cur.usd_exchange_rate
from "warehouse"."payment_source"."src_payment_transaction" pt
join "warehouse"."payment_source"."src_payment_method" pm on pt.payment_method_id = pm.payment_method_id
join "warehouse"."payment_source"."src_currency" cur on pt.currency_code = cur.currency_code