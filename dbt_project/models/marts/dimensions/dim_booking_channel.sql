SELECT
    ROW_NUMBER() OVER (ORDER BY channel_code) AS booking_channel_key,
    channel_code,
    channel_name
FROM {{ ref('stg_booking') }}