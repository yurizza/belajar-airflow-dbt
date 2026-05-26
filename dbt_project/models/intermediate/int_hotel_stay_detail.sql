SELECT
    hs.stay_id,
    hs.reservation_id,
    hs.checkin_date,
    hs.checkout_date,
    hs.number_of_nights,
    hs.total_bill_usd,
    r.guest_id,
    gp.preferred_room_type,
    hp.hotel_name,
    hp.city,
    hp.star_rating
FROM {{ ref('stg_hotel_stay') }} hs
JOIN {{ ref('stg_reservation') }} r 
  ON hs.reservation_id = r.reservation_id
JOIN {{ ref('stg_guest_profile') }} gp 
  ON r.guest_id = gp.guest_id
JOIN {{ ref('stg_hotel_property') }} hp 
  ON r.hotel_id = hp.hotel_id