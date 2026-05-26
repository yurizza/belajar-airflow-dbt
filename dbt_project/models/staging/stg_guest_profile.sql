SELECT
    guest_id,
    customer_key,
    preferred_room_type,
    smoking_preference,
    COALESCE(special_request,'None') AS special_request,
    CAST(created_at AS DATE) AS created_at
FROM airline.src_guest_profile