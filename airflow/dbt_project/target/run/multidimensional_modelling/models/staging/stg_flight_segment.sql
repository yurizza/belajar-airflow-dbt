
  
  create view "warehouse"."main"."stg_flight_segment__dbt_tmp" as (
    select
    cast(segment_id as integer) as segment_id,
    booking_id,
    flight_number,
    origin_airport,
    destination_airport,
    cast(scheduled_departure as timestamp) as scheduled_departure,
    cast(actual_departure as timestamp) as actual_departure,
    concat(upper(substring(status, 1, 1)), lower(substring(status, 2))) as status
from "warehouse"."flight_source"."src_flight_segment"
  );
