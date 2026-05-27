select
    cast(channel_key as integer) as channel_key,
    upper(channel_code) as channel_code,
    initcap(channel_name) as channel_name,
    initcap(channel_type) as channel_type,
    cast(commission_rate_pct as numeric) as commission_rate_pct,
    cast(booking_fee_usd as numeric) as booking_fee_usd,
    cast(typical_lead_days as integer) as typical_lead_days,
    cast(volume_share_pct as numeric) as volume_share_pct
from "data_warehouse"."ch_booking_source"."src_book_channel"