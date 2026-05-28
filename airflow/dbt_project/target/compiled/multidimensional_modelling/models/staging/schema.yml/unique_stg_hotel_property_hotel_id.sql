
    
    

select
    hotel_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_hotel_property"
where hotel_id is not null
group by hotel_id
having count(*) > 1


