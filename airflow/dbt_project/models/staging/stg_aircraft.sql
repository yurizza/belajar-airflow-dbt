select
    registration,
    aircraft_type,
    manufacturer,
    cast(seat_capacity as integer) as seat_capacity,
    initcap(airline) as operating_airline
from {{ source('flight_source', 'src_aircraft') }}