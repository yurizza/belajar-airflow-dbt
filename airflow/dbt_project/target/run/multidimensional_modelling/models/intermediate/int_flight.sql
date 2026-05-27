
  
  create view "warehouse"."staging"."int_flight__dbt_tmp" as (
    select
    b.booking_id,
    b.customer_key,
    fs.segment_id,
    fs.origin_airport_code,
    fs.destination_airport_code,
    fs.scheduled_departure,
    fs.actual_departure,
    fs.gross_amount_usd,
    ac.aircraft_id,
    ac.registration_number,
    ac.seat_capacity,
    bc.channel_key
from "warehouse"."flight_source"."src_booking" b
join "warehouse"."flight_source"."src_flight_segment" fs on b.booking_id = fs.booking_id
join "warehouse"."flight_source"."src_aircraft" ac on fs.aircraft_id = ac.aircraft_id
join "warehouse"."flight_source"."src_airport" ap on fs.origin_airport_code = ap.airport_code
join "warehouse"."ch_booking_source"."src_book_channel" bc on b.channel_key = bc.channel_key
  );
