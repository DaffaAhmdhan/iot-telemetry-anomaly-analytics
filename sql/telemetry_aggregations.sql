-- ============================================================================
-- IoT Environmental & Energy Telemetry SQL Queries
-- ============================================================================

-- 1. Zone-Level Summary & Threshold Breaches
SELECT
    zone,
    COUNT(*) AS total_readings,
    ROUND(AVG(temperature_c), 2) AS avg_temp_c,
    ROUND(MAX(temperature_c), 2) AS max_temp_c,
    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
    ROUND(SUM(power_kw), 1) AS total_kwh,
    SUM(CASE WHEN temperature_c > temp_threshold_c THEN 1 ELSE 0 END) AS temp_breaches
FROM telemetry
GROUP BY zone
ORDER BY temp_breaches DESC;

-- 2. Peak vs Off-Peak Energy Consumption
SELECT
    CASE WHEN is_peak_hour = 1 THEN 'Peak (09:00-17:00)' ELSE 'Off-Peak' END AS period,
    COUNT(*) AS readings,
    ROUND(AVG(power_kw), 3) AS avg_power_kw,
    ROUND(SUM(power_kw), 1) AS total_kwh
FROM telemetry
GROUP BY is_peak_hour;

-- 3. Hourly Diurnal Profile (24-Hour Cycle)
SELECT
    CAST(strftime('%H', timestamp) AS INTEGER) AS hour_of_day,
    ROUND(AVG(temperature_c), 2) AS avg_temp_c,
    ROUND(AVG(power_kw), 3) AS avg_power_kw
FROM telemetry
GROUP BY hour_of_day
ORDER BY hour_of_day;
