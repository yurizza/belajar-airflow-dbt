
    
    

with child as (
    select driver_id as from_field
    from "warehouse"."main"."int_rental"
    where driver_id is not null
),

parent as (
    select driver_id as to_field
    from "warehouse"."main"."dim_driver"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


