SELECT
    hs.stay_id,
    dc.customer_key,
    dh.hotel_property_key,
    db.booking_channel_key,
    dd.date_key             AS checkin_date_key,
    hs.nightly_rate_usd,
    hs.extended_room_charge_usd,
    hs.tax_charge_usd,
    hs.extra_charges_usd,
    hs.commission_paid_usd,
    hs.net_revenue_usd,
    hs.total_bill_usd,
    hs.number_of_nights
FROM {{ ref('int_hotel_stay_detail') }} hs
JOIN {{ ref('dim_customer') }} dc ON hs.guest_id = dc.customer_id
JOIN {{ ref('dim_hotel_property') }} dh ON hs.hotel_id = dh.hotel_id
JOIN {{ ref('dim_booking_channel') }} db ON hs.booking_channel = db.channel_code
JOIN {{ ref('dim_date') }} dd ON hs.checkin_date = dd.full_date