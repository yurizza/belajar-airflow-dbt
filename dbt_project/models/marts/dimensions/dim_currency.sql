SELECT
    ROW_NUMBER() OVER (ORDER BY currency_code) AS currency_key,
    currency_code,
    currency_name,
    currency_symbol,
    usd_exchange_rate
FROM {{ ref('stg_currency') }}
