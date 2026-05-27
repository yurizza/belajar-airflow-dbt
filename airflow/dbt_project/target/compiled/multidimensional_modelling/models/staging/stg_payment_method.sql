select
    cast(payment_method_id as integer) as payment_method_id,
    upper(method_code) as method_code,
    initcap(method_name) as method_name,
    initcap(payment_type) as payment_type,
    initcap(provider) as provider,
    cast(processing_fee_pct as numeric) as processing_fee_pct,
    cast(supports_installment as boolean) as supports_installment
from "data_warehouse"."payment_source"."src_payment_method"