
  
    
    

    create  table
      "warehouse"."main"."dim_driver__dbt_tmp"
  
    as (
      select
    driver_id,
    driver_name,
    gender,
    license_no,
    license_type,
    rating,
    total_trips,
    is_active
from "warehouse"."main"."stg_driver"
    );
  
  