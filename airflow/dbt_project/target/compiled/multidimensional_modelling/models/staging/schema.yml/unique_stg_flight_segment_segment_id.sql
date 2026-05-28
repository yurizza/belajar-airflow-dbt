
    
    

select
    segment_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_flight_segment"
where segment_id is not null
group by segment_id
having count(*) > 1


