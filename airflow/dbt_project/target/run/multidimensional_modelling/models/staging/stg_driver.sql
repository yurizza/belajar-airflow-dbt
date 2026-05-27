
  
  create view "data_warehouse"."main"."stg_driver__dbt_tmp" as (
    select
    driver_id,
    initcap(driver_name) as driver_name,
    case when gender in ('M','F') then gender else null end as gender,
    license_no,
    upper(license_type) as license_type,
    regexp_replace(languages, '\s+', ' ', 'g') as languages, -- bersihkan spasi/tab berlebih
    cast(rating as numeric) as rating,
    cast(total_trips as integer) as total_trips,
    cast(is_active as boolean) as is_active,
    cast(joined_date as date) as joined_date
from "data_warehouse"."rental_source"."src_driver"
  );
