# IoT Environmental & Energy Telemetry Analytics

Time-series data analytics project processing **17,280 hourly sensor readings** across 4 facility zones (**Server Room A**, **Server Room B**, **RnEST Lab**, **Clinic / Lobby HVAC**) over 180 days using **SQL**, **Python Z-Score Anomaly Detection**, and an interactive **Chart.js Telemetry Dashboard**.

## Business Questions
1. How is energy consumption distributed across facility zones and peak vs. off-peak hours?
2. How many thermal anomalies (`|z| > 2.5`) and SLA temperature breaches occur per zone?
3. What is the estimated cost-saving potential from peak-hour HVAC & workload optimization?

## Key Findings (Verified from `output/iot_metrics.json`)
- **Energy Footprint:** Total consumption reached **57,154.1 kWh** (est. **Rp 82.57M** at PLN commercial tariff), with **Server Room A (18,801.1 kWh)** and **Server Room B (17,096.7 kWh)** accounting for **62.8%** of total power.
- **Peak vs. Off-Peak Load:** Peak-hour (09:00–17:00) average draw is **4.117 kW**—**45.9% higher** than off-peak (**2.822 kW**).
- **Anomaly Detection:** Statistical Z-score monitoring (`|z| > 2.5`) flagged **120 thermal anomalies** and **102 threshold breaches**, with peak spikes reaching **30.62°C** in Server Room A and **31.32°C** in Server Room B.
- **Cost Savings Opportunity:** A 12% peak-hour load optimization yields **Rp 4.62M** in direct 6-month energy savings (~Rp 9.25M annualized).

## Recommendations
1. **Automated Cooling Pre-Chill Before 09:00:** Shift heavy HVAC compressor cycles to off-peak hours to flatten the 4.12 kW daytime spike.
2. **Real-Time Telegram Z-Score Alerts:** Trigger early warnings at `z > 2.0` before server rooms cross the 26.0°C hard threshold.

## How to Run
```bash
python data/generate_data.py
python src/run_analysis.py
```
Open `dashboard.html` in any browser to inspect the interactive charts.
