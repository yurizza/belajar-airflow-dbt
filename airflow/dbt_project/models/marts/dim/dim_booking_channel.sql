select
    channel_key,
    channel_code,
    channel_name,
    channel_type,
    commission_rate_pct,
    booking_fee_usd
from {{ ref('stg_booking_channel') }}