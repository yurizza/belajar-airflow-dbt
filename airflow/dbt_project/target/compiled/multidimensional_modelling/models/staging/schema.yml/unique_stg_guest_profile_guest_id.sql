
    
    

select
    guest_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_guest_profile"
where guest_id is not null
group by guest_id
having count(*) > 1


