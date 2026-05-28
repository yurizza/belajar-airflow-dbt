select distinct
    md5(reservation_status) as reservation_status_key,
    reservation_status
from {{ ref('stg_reservation') }}
where reservation_status is not null