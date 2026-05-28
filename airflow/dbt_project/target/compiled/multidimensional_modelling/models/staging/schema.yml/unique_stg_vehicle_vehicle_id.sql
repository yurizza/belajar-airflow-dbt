
    
    

select
    vehicle_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_vehicle"
where vehicle_id is not null
group by vehicle_id
having count(*) > 1


