
  
    
    

    create  table
      "warehouse"."main"."dim_payment_method__dbt_tmp"
  
    as (
      select
    payment_method_id,
    method_code,
    method_name,
    payment_type,
    provider,
    processing_fee_pct
from "warehouse"."main"."stg_payment_method"
    );
  
  