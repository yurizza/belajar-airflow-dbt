
  
  create view "warehouse"."main"."stg_payment_method__dbt_tmp" as (
    select
    cast(payment_method_id as integer) as payment_method_id,
    upper(method_code) as method_code,
    concat(upper(substring(method_name, 1, 1)), lower(substring(method_name, 2))) as method_name,
    concat(upper(substring(payment_type, 1, 1)), lower(substring(payment_type, 2))) as payment_type,
    concat(upper(substring(provider, 1, 1)), lower(substring(provider, 2))) as provider,
    cast(processing_fee_pct as numeric) as processing_fee_pct,
    cast(supports_installment as boolean) as supports_installment
from "warehouse"."payment_source"."src_payment_method"
  );
