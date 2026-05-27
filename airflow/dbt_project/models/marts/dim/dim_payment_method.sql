select
    payment_method_id,
    method_code,
    method_name,
    payment_type,
    provider,
    processing_fee_pct,
    supports_installment
from {{ ref('stg_payment_method') }};
