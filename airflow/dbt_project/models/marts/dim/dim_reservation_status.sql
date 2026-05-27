select
    reservation_id,
    reservation_status,
    booking_source
from {{ ref('stg_reservation') }};
