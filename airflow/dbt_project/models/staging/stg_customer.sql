select
    cast(customer_key as integer) as customer_key,
    customer_id,
    concat(upper(substring(first_name, 1, 1)), lower(substring(first_name, 2))) as first_name,
    concat(upper(substring(last_name, 1, 1)), lower(substring(last_name, 2))) as last_name,
    case 
        when gender in ('M','F') then gender
        else null
    end as gender,
    cast(date_of_birth as date) as date_of_birth,
    concat(upper(substring(nationality, 1, 1)), lower(substring(nationality, 2))) as nationality,
    lower(email) as email,
    regexp_replace(phone, '[^0-9]', '', 'g') as phone,
    cast(eff_start_date as date) as eff_start_date,
    cast(nullif(eff_end_date, '') as date) as eff_end_date,
    cast(is_current as boolean) as is_current
from {{ source('customer_source', 'src_customer') }}