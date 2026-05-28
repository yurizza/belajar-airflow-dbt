
    
    

select
    stay_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_hotel_stay"
where stay_id is not null
group by stay_id
having count(*) > 1


