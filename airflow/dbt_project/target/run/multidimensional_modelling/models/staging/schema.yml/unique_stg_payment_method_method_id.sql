select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    method_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_payment_method"
where method_id is not null
group by method_id
having count(*) > 1



      
    ) dbt_internal_test