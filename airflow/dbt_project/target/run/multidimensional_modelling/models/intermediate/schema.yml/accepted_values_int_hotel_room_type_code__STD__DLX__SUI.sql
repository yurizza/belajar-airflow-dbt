select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        room_type_code as value_field,
        count(*) as n_records

    from "warehouse"."main"."int_hotel"
    group by room_type_code

)

select *
from all_values
where value_field not in (
    'STD','DLX','SUI'
)



      
    ) dbt_internal_test