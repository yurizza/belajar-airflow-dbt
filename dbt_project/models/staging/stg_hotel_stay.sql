SELECT
    stay_id,
    reservation_id,
    CAST(checkin_date AS DATE) AS checkin_date,
    CAST(checkout_date AS DATE) AS checkout_date,
    number_of_nights::int AS number_of_nights,
    room_charge_usd::numeric AS room_charge_usd,
    extra_charge_usd::numeric AS extra_charge_usd,
    total_bill_usd::numeric AS total_bill_usd
FROM airline.scr_hotel_stay