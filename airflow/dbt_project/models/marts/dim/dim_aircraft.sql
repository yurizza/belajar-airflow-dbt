select
    registration_number,
    aircraft_type,
    manufacturer,
    seat_capacity,
    operating_airline
from {{ ref('stg_aircraft') }};
