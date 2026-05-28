select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select vehicle_id
from "warehouse"."main"."stg_vehicle"
where vehicle_id is null



      
    ) dbt_internal_test