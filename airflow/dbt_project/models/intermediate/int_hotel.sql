with property as (
    select * from {{ ref('stg_hotel_property') }}
),
room as (
    select * from {{ ref('stg_room_inventory') }}
),
stay as (
    select * from {{ ref('stg_hotel_stay') }}
),
reservation as (
    select * from {{ ref('stg_reservation') }}
),
guest as (
    select * from {{ ref('stg_guest_profile') }}
)

select
    hp.hotel_id,
    hp.hotel_name,
    hp.brand,
    hp.city,
    hp.star_rating,
    hp.total_rooms,
    hp.has_pool,
    hp.has_gym,
    ri.room_id,
    ri.room_number,
    ri.room_type_code,
    ri.room_type_name,
    ri.base_rate_usd,
    hs.stay_id,
    hs.checkin_date,
    hs.checkout_date,
    hs.number_of_nights,
    hs.total_bill_usd,
    rs.reservation_id,
    rs.booking_date,
    rs.arrival_date,
    rs.departure_date,
    rs.reservation_status,
    gp.guest_id,
    gp.customer_key,
    gp.preferred_room_type,
    gp.special_request
from property hp
left join room ri on hp.hotel_id = ri.hotel_id
left join stay hs on hp.hotel_id = hs.hotel_id
left join reservation rs on hs.reservation_id = rs.reservation_id
left join guest gp on rs.guest_id = gp.guest_id
