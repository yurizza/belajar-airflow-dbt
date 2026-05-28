select
    stay_id,
    reservation_id,
    cast(actual_checkin_date as date)    as actual_checkin_date,
    cast(actual_nights as integer)       as actual_nights,
    cast(incidental_usd as numeric)      as incidental_usd
from {{ source('hotel_source', 'src_hotel_stay') }}