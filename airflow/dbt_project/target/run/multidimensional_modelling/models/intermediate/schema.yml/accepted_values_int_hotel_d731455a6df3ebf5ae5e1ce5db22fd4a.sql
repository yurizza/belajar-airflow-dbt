select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        reservation_status as value_field,
        count(*) as n_records

    from "warehouse"."main"."int_hotel"
    group by reservation_status

)

select *
from all_values
where value_field not in (
    'Booked','Checked_in','Checked_out','Cancelled'
)



      
    ) dbt_internal_test