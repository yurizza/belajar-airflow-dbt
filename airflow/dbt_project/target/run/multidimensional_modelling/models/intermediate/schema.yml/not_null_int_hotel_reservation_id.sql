select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select reservation_id
from "warehouse"."main"."int_hotel"
where reservation_id is null



      
    ) dbt_internal_test