select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with child as (
    select dropoff_hotel as from_field
    from "warehouse"."main"."int_rental"
    where dropoff_hotel is not null
),

parent as (
    select hotel_id as to_field
    from "warehouse"."main"."dim_hotel_property"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



      
    ) dbt_internal_test