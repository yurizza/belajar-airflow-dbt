
    
    

select
    transaction_id as unique_field,
    count(*) as n_records

from "warehouse"."main"."stg_payment_transaction"
where transaction_id is not null
group by transaction_id
having count(*) > 1


