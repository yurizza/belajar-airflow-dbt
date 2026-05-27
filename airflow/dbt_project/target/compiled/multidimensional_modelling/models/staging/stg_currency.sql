select
    upper(currency_code) as currency_code,
    initcap(currency_name) as currency_name,
    symbol,
    cast(usd_exchange_rate as numeric) as usd_exchange_rate
from "data_warehouse"."payment_source"."src_currency"