SELECT
    customer_id,
    first_name,
    last_name,
    CASE WHEN gender = 'M' THEN 'Male'
         WHEN gender = 'F' THEN 'Female'
         ELSE gender END AS gender,
    CAST(date_of_birth AS DATE) AS date_of_birth,
    nationality,
    LOWER(email) AS email,
    REGEXP_REPLACE(phone, '(\d{3})(\d{3})(\d{4})', '\1-\2-\3') AS phone
FROM airline.src_customer;