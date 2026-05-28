select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select payment_method_id
from "warehouse"."main"."int_payment_transaction"
where payment_method_id is null



      
    ) dbt_internal_test