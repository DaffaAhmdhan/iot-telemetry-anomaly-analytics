import csv
import math
import os
import random
from datetime import datetime, timedelta

random.seed(2026)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(OUTPUT_DIR, "sensor_telemetry.csv")

ZONES = [
    ("Server Room A", 20.5, 48.0, 4.2, 26.0),
    ("Server Room B", 21.0, 50.0, 3.8, 26.0),
    ("RnEST Lab", 24.5, 58.0, 1.9, 29.0),
    ("Clinic / Lobby HVAC", 23.5, 55.0, 2.7, 28.0),
]


def main():
    start = datetime(2026, 5, 1, 0, 0, 0)
    hours = 24 * 180  # 180 days (~4,320 hours x 4 zones = 17,280 rows)
    rows = []

    for h in range(hours):
        ts = start + timedelta(hours=h)
        hour_of_day = ts.hour
        diurnal = math.sin((hour_of_day - 6) * math.pi / 12.0)

        for zone, base_temp, base_hum, base_kw, temp_thresh in ZONES:
            temp = base_temp + 1.1 * diurnal + random.gauss(0, 0.45)
            hum = base_hum - 3.5 * diurnal + random.gauss(0, 1.8)
            is_peak = 1 if 9 <= hour_of_day <= 17 else 0
            power_kw = base_kw + (0.95 if is_peak else -0.35) + random.gauss(0, 0.22)

            # Inject realistic HVAC / thermal anomalies (~0.7% of readings)
            if random.random() < 0.007:
                temp += random.uniform(5.2, 8.8)
                power_kw += random.uniform(1.8, 3.2)

            rows.append([
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                zone,
                round(temp, 2),
                round(max(20.0, min(90.0, hum)), 2),
                round(max(0.5, power_kw), 3),
                is_peak,
                temp_thresh,
            ])

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "timestamp", "zone", "temperature_c", "humidity_pct",
            "power_kw", "is_peak_hour", "temp_threshold_c"
        ])
        w.writerows(rows)

    print(f"Generated {len(rows)} telemetry rows at {CSV_PATH}")


if __name__ == "__main__":
    main()
