select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select currency_code
from "warehouse"."main"."stg_currency"
where currency_code is null



      
    ) dbt_internal_test