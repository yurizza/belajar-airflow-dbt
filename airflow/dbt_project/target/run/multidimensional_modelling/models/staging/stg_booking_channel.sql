
  
  create view "warehouse"."main"."stg_booking_channel__dbt_tmp" as (
    select
    cast(channel_key as integer) as channel_key,
    upper(channel_code) as channel_code,
    concat(upper(substring(channel_name, 1, 1)), lower(substring(channel_name, 2))) as channel_name,
    concat(upper(substring(channel_type, 1, 1)), lower(substring(channel_type, 2))) as channel_type,
    cast(commission_rate_pct as numeric) as commission_rate_pct,
    cast(booking_fee_usd as numeric) as booking_fee_usd,
    cast(typical_lead_days as integer) as typical_lead_days,
    cast(volume_share_pct as numeric) as volume_share_pct
from "warehouse"."ch_booking_source"."src_book_channel"
  );
