select
    upper(currency_code) as currency_code,
    initcap(currency_name) as currency_name,
    symbol,
    cast(usd_exchange_rate as numeric) as usd_exchange_rate
from "warehouse"."payment_source"."currency"