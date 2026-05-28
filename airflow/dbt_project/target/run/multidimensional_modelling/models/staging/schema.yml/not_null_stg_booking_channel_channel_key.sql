select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select channel_key
from "warehouse"."main"."stg_booking_channel"
where channel_key is null



      
    ) dbt_internal_test