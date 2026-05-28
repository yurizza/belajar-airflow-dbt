select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select room_id
from "warehouse"."main"."stg_room_inventory"
where room_id is null



      
    ) dbt_internal_test