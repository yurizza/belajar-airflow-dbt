select
    hp.hotel_id,
    hp.hotel_name,
    hp.brand,
    hp.city,
    hp.star_rating,
    hp.total_rooms,
    r.reservation_id,
    r.customer_key,
    hs.stay_id,
    hs.actual_checkin_date,
    hs.actual_nights,
    hs.incidental_usd
from {{ ref('stg_hotel_property') }} hp
left join {{ ref('stg_reservation') }} r on hp.hotel_id = r.hotel_id
left join {{ ref('stg_hotel_stay') }} hs on r.reservation_id = hs.reservation_id