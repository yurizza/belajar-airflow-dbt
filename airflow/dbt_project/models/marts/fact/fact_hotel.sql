select
    hs.stay_id,
    r.reservation_id,
    gp.guest_id,
    hp.hotel_id,
    ri.room_id,
    hs.checkin_date,
    hs.checkout_date,
    hs.number_of_nights,
    hs.room_charge_usd,
    hs.extra_charge_usd,
    hs.total_bill_usd,
    -- Measures
    hs.room_charge_usd as base_rate_usd,
    hs.number_of_nights as actual_nights,
    hs.extra_charge_usd as total_incidental_charges_usd,
    hs.total_bill_usd as total_accommodation_bill_usd
from {{ ref('stg_hotel_stay') }} hs
join {{ ref('stg_reservation') }} r on hs.reservation_id = r.reservation_id
join {{ ref('stg_guest_profile') }} gp on r.guest_id = gp.guest_id
join {{ ref('dim_hotel_property') }} hp on r.hotel_id = hp.hotel_id
join {{ ref('dim_room_inventory') }} ri on hs.stay_id = ri.room_id;
