import csv
import json
import math
import os
import sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "sensor_telemetry.csv")
DB_PATH = os.path.join(BASE_DIR, "output", "iot_telemetry.db")
JSON_PATH = os.path.join(BASE_DIR, "output", "iot_metrics.json")

TARIFF_IDR_PER_KWH = 1444.70


def main():
    os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS telemetry;")
    cur.execute("""
        CREATE TABLE telemetry (
            timestamp TEXT NOT NULL,
            zone TEXT NOT NULL,
            temperature_c REAL NOT NULL,
            humidity_pct REAL NOT NULL,
            power_kw REAL NOT NULL,
            is_peak_hour INTEGER NOT NULL,
            temp_threshold_c REAL NOT NULL
        );
    """)

    rows = []
    zone_temps = defaultdict(list)
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = float(r["temperature_c"])
            z = r["zone"]
            zone_temps[z].append((r["timestamp"], t, float(r["power_kw"])))
            rows.append((
                r["timestamp"], z, t, float(r["humidity_pct"]),
                float(r["power_kw"]), int(r["is_peak_hour"]), float(r["temp_threshold_c"])
            ))

    cur.executemany("INSERT INTO telemetry VALUES (?, ?, ?, ?, ?, ?, ?);", rows)
    conn.commit()

    conn.row_factory = sqlite3.Row
    zone_summary = [dict(r) for r in conn.execute("""
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
    """).fetchall()]

    peak_split = [dict(r) for r in conn.execute("""
        SELECT
            CASE WHEN is_peak_hour = 1 THEN 'Peak (09:00-17:00)' ELSE 'Off-Peak' END AS period,
            COUNT(*) AS readings,
            ROUND(AVG(power_kw), 3) AS avg_power_kw,
            ROUND(SUM(power_kw), 1) AS total_kwh
        FROM telemetry
        GROUP BY is_peak_hour;
    """).fetchall()]

    hourly_profile = [dict(r) for r in conn.execute("""
        SELECT
            CAST(strftime('%H', timestamp) AS INTEGER) AS hour_of_day,
            ROUND(AVG(temperature_c), 2) AS avg_temp_c,
            ROUND(AVG(power_kw), 3) AS avg_power_kw
        FROM telemetry
        GROUP BY hour_of_day
        ORDER BY hour_of_day;
    """).fetchall()]

    # Z-score anomaly detection per zone (|z| > 2.5)
    anomaly_summary = []
    total_anomalies = 0
    for z, series in zone_temps.items():
        vals = [x[1] for x in series]
        mean_t = sum(vals) / len(vals)
        std_t = math.sqrt(sum((v - mean_t) ** 2 for v in vals) / len(vals))
        anomalies = [x for x in series if std_t > 0 and abs(x[1] - mean_t) / std_t > 2.5]
        total_anomalies += len(anomalies)
        anomaly_summary.append({
            "zone": z,
            "mean_temp_c": round(mean_t, 2),
            "std_temp_c": round(std_t, 2),
            "z_score_anomalies": len(anomalies),
            "anomaly_rate_pct": round(100.0 * len(anomalies) / len(series), 2),
        })

    total_kwh = sum(z["total_kwh"] for z in zone_summary)
    est_cost_idr = round(total_kwh * TARIFF_IDR_PER_KWH)
    peak_kwh = next(p["total_kwh"] for p in peak_split if p["period"].startswith("Peak"))
    potential_savings_idr = round(peak_kwh * 0.12 * TARIFF_IDR_PER_KWH)  # 12% peak load shift/optimization

    output = {
        "total_readings": len(rows),
        "total_kwh": round(total_kwh, 1),
        "estimated_energy_cost_idr": est_cost_idr,
        "potential_peak_savings_idr": potential_savings_idr,
        "total_z_anomalies": total_anomalies,
        "zone_summary": zone_summary,
        "peak_split": peak_split,
        "hourly_profile": hourly_profile,
        "anomaly_summary": anomaly_summary,
    }

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    conn.close()
    print(json.dumps({
        "total_readings": output["total_readings"],
        "total_kwh": output["total_kwh"],
        "estimated_energy_cost_idr": output["estimated_energy_cost_idr"],
        "potential_peak_savings_idr": output["potential_peak_savings_idr"],
        "total_z_anomalies": output["total_z_anomalies"],
        "zone_summary": zone_summary,
    }, indent=2))


if __name__ == "__main__":
    main()
