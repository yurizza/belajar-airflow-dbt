
  
    
    

    create  table
      "warehouse"."main"."dim_currency__dbt_tmp"
  
    as (
      select
    currency_code,
    currency_name,
    symbol,
    usd_exchange_rate
from "warehouse"."main"."stg_currency"
    );
  
  