
  
  create view "data_warehouse"."main"."dim_date__dbt_tmp" as (
    with dates as (
    select d::date as full_date
    from range(date '2020-01-01', date '2030-12-31', interval 1 day) t(d)
)
select
    cast(strftime(full_date, '%Y%m%d') as integer) as date_key,
    full_date,
    strftime(full_date, '%A') as day_of_week,
    cast(strftime(full_date, '%w') as integer) as day_number_in_week,
    cast(strftime(full_date, '%d') as integer) as day_number_in_month,
    cast(strftime(full_date, '%W') as integer) as week_number_in_year,
    cast(strftime(full_date, '%m') as integer) as month_number,
    strftime(full_date, '%B') as month_name,
    case 
        when cast(strftime(full_date, '%m') as integer) in (1,2,3) then 'Q1'
        when cast(strftime(full_date, '%m') as integer) in (4,5,6) then 'Q2'
        when cast(strftime(full_date, '%m') as integer) in (7,8,9) then 'Q3'
        else 'Q4'
    end as quarter,
    cast(strftime(full_date, '%Y') as integer) as year
from dates;
  );
