select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select net_amount_usd
from "warehouse"."main"."int_payment_transaction"
where net_amount_usd is null



      
    ) dbt_internal_test