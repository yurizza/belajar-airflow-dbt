select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        trip_status as value_field,
        count(*) as n_records

    from "warehouse"."main"."int_rental"
    group by trip_status

)

select *
from all_values
where value_field not in (
    'Delayed','Completed','Incident'
)



      
    ) dbt_internal_test