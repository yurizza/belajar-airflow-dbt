-- models/staging/hotel/stg_room_inventory.sql

with source as (
    select * from {{ source('travel_raw', 'src_room_inventory') }}
),

renamed as (
    select
        room_inventory_id,
        hotel_id,
        upper(trim(room_type_code))     as room_type_code,
        trim(room_type_name)            as room_type_name,
        room_count,
        round(base_rate_usd::numeric, 2) as base_rate_usd

    from source
    where room_inventory_id is not null
)

select * from renamed
