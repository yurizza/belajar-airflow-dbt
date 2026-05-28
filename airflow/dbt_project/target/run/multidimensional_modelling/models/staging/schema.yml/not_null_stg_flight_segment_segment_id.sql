select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select segment_id
from "warehouse"."main"."stg_flight_segment"
where segment_id is null



      
    ) dbt_internal_test