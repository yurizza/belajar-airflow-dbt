
    
    

select
    method_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_payment_method"
where method_id is not null
group by method_id
having count(*) > 1


