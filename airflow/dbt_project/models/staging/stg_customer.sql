select
    cast(customer_key as integer) as customer_key,
    customer_id,
    initcap(first_name) as first_name,
    initcap(last_name) as last_name,
    case 
        when gender in ('M','F') then gender
        else null
    end as gender,
    cast(date_of_birth as date) as date_of_birth,
    initcap(nationality) as nationality,
    lower(email) as email,
    regexp_replace(phone, '[^0-9]', '', 'g') as phone,  -- bersihkan non-digit
    cast(eff_start_date as date) as eff_start_date,
    cast(nullif(eff_end_date, '') as date) as eff_end_date,
    cast(is_current as boolean) as is_current
from {{ source('customer_source', 'src_customer') }}