select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select hotel_id
from "warehouse"."main"."int_hotel"
where hotel_id is null



      
    ) dbt_internal_test