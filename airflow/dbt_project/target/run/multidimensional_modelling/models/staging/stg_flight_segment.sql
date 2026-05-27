
  
  create view "data_warehouse"."main"."stg_flight_segment__dbt_tmp" as (
    select
    cast(segment_id as integer) as segment_id,
    booking_id,
    flight_number,
    origin_airport,
    destination_airport,
    cast(scheduled_departure as timestamp) as scheduled_departure,
    cast(actual_departure as timestamp) as actual_departure,
    initcap(status) as status
from "data_warehouse"."flight_source"."src_flight_segment"
  );
