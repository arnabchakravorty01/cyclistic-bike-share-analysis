-- Cyclistic Membership Conversion Analysis
-- Assumes a normalized table named cyclistic_rides with fields documented in
-- docs/data_dictionary.md. Syntax is intentionally close to ANSI SQL.

-- 1) Rider mix
SELECT
    member_casual,
    COUNT(*) AS rides,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_rides
FROM cyclistic_rides
GROUP BY member_casual
ORDER BY rides DESC;

-- 2) Weekday vs weekend behavior
SELECT
    member_casual,
    day_type,
    COUNT(*) AS rides,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY member_casual), 2) AS pct_within_segment
FROM cyclistic_rides
GROUP BY member_casual, day_type
ORDER BY member_casual, day_type;

-- 3) Hourly ride-start profile
SELECT
    member_casual,
    hour,
    COUNT(*) AS rides
FROM cyclistic_rides
GROUP BY member_casual, hour
ORDER BY member_casual, hour;

-- 4) Commute-window proxy on weekdays
SELECT
    member_casual,
    SUM(CASE WHEN commute_window THEN 1 ELSE 0 END) AS commute_window_rides,
    SUM(CASE WHEN day_type = 'Weekday' THEN 1 ELSE 0 END) AS weekday_rides,
    ROUND(
        100.0 * SUM(CASE WHEN commute_window THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN day_type = 'Weekday' THEN 1 ELSE 0 END), 0),
        2
    ) AS pct_of_weekday_rides
FROM cyclistic_rides
GROUP BY member_casual;

-- 5) Monthly seasonality
SELECT
    member_casual,
    month,
    COUNT(*) AS rides,
    AVG(ride_duration_min) AS avg_duration_min
FROM cyclistic_rides
GROUP BY member_casual, month
ORDER BY month, member_casual;

-- 6) Same-station behavior
SELECT
    member_casual,
    SUM(CASE WHEN same_station THEN 1 ELSE 0 END) AS same_station_rides,
    COUNT(*) AS rides,
    ROUND(100.0 * SUM(CASE WHEN same_station THEN 1 ELSE 0 END) / COUNT(*), 2) AS same_station_pct
FROM cyclistic_rides
GROUP BY member_casual;

-- 7) High-volume stations with high casual concentration
WITH station_counts AS (
    SELECT
        start_station_name,
        SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END) AS member_rides,
        SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END) AS casual_rides,
        COUNT(*) AS total_rides
    FROM cyclistic_rides
    GROUP BY start_station_name
)
SELECT
    start_station_name,
    member_rides,
    casual_rides,
    total_rides,
    ROUND(100.0 * casual_rides / NULLIF(total_rides, 0), 2) AS casual_share_pct
FROM station_counts
WHERE total_rides >= 5000
ORDER BY casual_share_pct DESC, total_rides DESC
FETCH FIRST 30 ROWS ONLY;

-- 8) Most common routes by rider type
SELECT
    member_casual,
    start_station_name,
    end_station_name,
    COUNT(*) AS rides
FROM cyclistic_rides
GROUP BY member_casual, start_station_name, end_station_name
ORDER BY member_casual, rides DESC;
