
    
    

select
    property_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_hotel_property"
where property_id is not null
group by property_id
having count(*) > 1


