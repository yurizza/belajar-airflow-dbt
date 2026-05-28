
    
    

select
    room_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_room_inventory"
where room_id is not null
group by room_id
having count(*) > 1


