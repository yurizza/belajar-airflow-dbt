
    
    

select
    payment_method_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_payment_method"
where payment_method_id is not null
group by payment_method_id
having count(*) > 1


