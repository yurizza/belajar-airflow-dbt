
    
    

select
    driver_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_driver"
where driver_id is not null
group by driver_id
having count(*) > 1


