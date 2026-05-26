SELECT
    CAST(date_value AS DATE) AS full_date,
    EXTRACT(YEAR FROM date_value) AS year,
    EXTRACT(MONTH FROM date_value) AS month,
    EXTRACT(DAY FROM date_value) AS day,
    EXTRACT(DOW FROM date_value) AS day_of_week,
    EXTRACT(WEEK FROM date_value) AS week_of_year
FROM UNNEST(GENERATE_DATE_ARRAY('2000-01-01','2030-12-31', INTERVAL 1 DAY)) AS date_value