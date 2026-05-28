select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with child as (
    select origin_airport_code as from_field
    from "warehouse"."main"."int_flight"
    where origin_airport_code is not null
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



      
    ) dbt_internal_test