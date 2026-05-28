select
    currency_code,
    currency_name,
    symbol,
    usd_exchange_rate
from {{ ref('stg_currency') }}