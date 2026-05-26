SELECT
    booking_id,
    customer_id,
    CAST(booking_date AS DATE) AS booking_date,
    UPPER(booking_channel) AS booking_channel,
    fare_basis_code
FROM airline.src_booking