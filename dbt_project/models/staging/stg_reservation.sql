SELECT
    reservation_id,
    guest_id,
    hotel_id,
    CAST(booking_date AS DATE) AS booking_date,
    CAST(arrival_date AS DATE) AS arrival_date,
    CAST(departure_date AS DATE) AS departure_date,
    INITCAP(reservation_status) AS reservation_status,
    booking_source
FROM airline.src_reservation