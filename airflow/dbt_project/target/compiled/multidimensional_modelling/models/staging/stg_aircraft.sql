select
    registration,
    aircraft_type,
    manufacturer,
    cast(seat_capacity as integer) as seat_capacity,
    concat(upper(substring(airline, 1, 1)), lower(substring(airline, 2))) as operating_airline
from "warehouse"."flight_source"."src_aircraft"