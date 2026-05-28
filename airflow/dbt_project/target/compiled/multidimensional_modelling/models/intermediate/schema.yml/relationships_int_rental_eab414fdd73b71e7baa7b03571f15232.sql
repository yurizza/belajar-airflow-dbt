
    
    

with child as (
    select pickup_airport as from_field
    from "warehouse"."main"."int_rental"
    where pickup_airport is not null
),

parent as (
    select airport_code as to_field
    from "warehouse"."main"."dim_airport"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


