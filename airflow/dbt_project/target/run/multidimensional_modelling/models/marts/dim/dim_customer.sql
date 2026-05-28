
  
    
    

    create  table
      "warehouse"."main"."dim_customer__dbt_tmp"
  
    as (
      select
    customer_key,
    customer_id,
    first_name,
    last_name,
    gender,
    date_of_birth,
    nationality,
    email,
    phone
from "warehouse"."main"."stg_customer"
    );
  
  