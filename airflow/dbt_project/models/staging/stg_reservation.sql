select
    reservation_id,
    guest_id,
    hotel_id,
    cast(booking_date as date) as booking_date,
    cast(arrival_date as date) as arrival_date,
    cast(departure_date as date) as departure_date,
    initcap(reservation_status) as reservation_status,
    initcap(booking_source) as booking_source
from {{ source('flight_source', 'src_reservation') }}
