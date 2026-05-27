
  
  create view "warehouse"."staging"."stg_payment_transaction__dbt_tmp" as (
    select
    payment_id,
    payment_reference,
    invoice_number,
    cast(customer_key as integer) as customer_key,
    cast(transaction_date as date) as transaction_date,
    cast(transaction_time as time) as transaction_time,
    cast(payment_method_id as integer) as payment_method_id,
    upper(currency_code) as currency_code,
    initcap(payment_gateway) as payment_gateway,
    initcap(payment_status) as payment_status,
    cast(gross_amount_usd as numeric) as gross_amount_usd,
    cast(discount_usd as numeric) as discount_usd,
    cast(tax_usd as numeric) as tax_usd,
    cast(net_amount_usd as numeric) as net_amount_usd,
    cast(refund_amount_usd as numeric) as refund_amount_usd,
    cast(gateway_fee_usd as numeric) as gateway_fee_usd,
    cast(installment_months as integer) as installment_months,
    upper(source_type) as source_type,
    source_reference
from "warehouse"."payment_source"."payment_transaction"
  );
