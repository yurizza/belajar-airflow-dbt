
  
  create view "warehouse"."main"."stg_reservation__dbt_tmp" as (
    with source as (
    select 
        reservation_id,
        customer_key,
        guest_id,
        hotel_id,
        segment_id,
        booking_date,
        destination_city,
        checkin_date,   -- Menggunakan kolom asli dari DDL PostgreSQL
        checkout_date,  -- Menggunakan kolom asli dari DDL PostgreSQL
        status as reservation_status -- Menyamakan alias untuk keselarasan model data
    from "warehouse"."main"."src_reservation"
)
select
    reservation_id,
    customer_key,
    guest_id,
    hotel_id,
    segment_id,
    destination_city,
    cast(booking_date as date) as booking_date,
    cast(checkin_date as date) as arrival_date, -- checkin_date di-cast menjadi arrival_date agar tabel mart tidak patah
    cast(checkout_date as date) as checkout_date,
    concat(upper(substring(reservation_status, 1, 1)), lower(substring(reservation_status, 2))) as reservation_status
from source
  );
