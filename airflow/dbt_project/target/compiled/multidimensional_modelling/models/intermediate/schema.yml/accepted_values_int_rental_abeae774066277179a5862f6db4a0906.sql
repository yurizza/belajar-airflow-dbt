
    
    

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
    'Ongoing','Completed','Failed'
)


