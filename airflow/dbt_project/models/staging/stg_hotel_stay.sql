select
    stay_id,
    reservation_id,
    cast(checkin_date as date) as checkin_date,
    cast(checkout_date as date) as checkout_date,
    cast(number_of_nights as integer) as number_of_nights,
    cast(room_charge_usd as numeric) as room_charge_usd,
    cast(extra_charge_usd as numeric) as extra_charge_usd,
    cast(total_bill_usd as numeric) as total_bill_usd
from {{ source('hotel_source', 'src_hotel_stay') }}