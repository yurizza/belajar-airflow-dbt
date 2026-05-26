SELECT
    hour AS hour,
    CASE
        WHEN hour BETWEEN 0 AND 5 THEN 'Late Night'
        WHEN hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN hour BETWEEN 12 AND 17 THEN 'Afternoon'
        ELSE 'Evening'
    END AS time_period
FROM UNNEST(GENERATE_ARRAY(0,23)) AS hour