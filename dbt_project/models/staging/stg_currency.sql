SELECT
    currency_code,
    UPPER(currency_name) AS currency_name,
    currency_symbol,
    CAST(usd_exchange_rate AS NUMERIC) AS usd_exchange_rate
FROM airine.src_currency
