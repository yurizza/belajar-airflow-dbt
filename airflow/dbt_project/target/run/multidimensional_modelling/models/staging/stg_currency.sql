
  
  create view "warehouse"."main"."stg_currency__dbt_tmp" as (
    select
    upper(currency_code) as currency_code,
    concat(upper(substring(currency_name, 1, 1)), lower(substring(currency_name, 2))) as currency_name,
    symbol,
    cast(usd_exchange_rate as numeric) as usd_exchange_rate
from "warehouse"."main"."src_currency"
  );
