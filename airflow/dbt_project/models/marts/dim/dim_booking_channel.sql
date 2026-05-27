select
    channel_key,
    channel_code,
    channel_name,
    channel_type,
    commission_rate_pct,
    booking_fee_usd,
    typical_lead_days,
    volume_share_pct
from {{ ref('stg_booking_channel') }};
