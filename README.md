# Deye Inverter Prometheus Exporter

A lightweight **Prometheus metrics exporter** for Deye hybrid solar inverters 
using the Solarman V5 local protocol — no cloud, no SolarmanPV account required.

> ✅ **Tested on: Deye SUN-3K-SG04LP1-24-EU-SM1 Hybrid Inverter**  
> **Protocol:** Solarman V5 over local TCP (port 8899)  
> May also work on other Deye/Sunsynk/SolArk hybrid models that share the same register map.

---

## ✨ Features

- **52 Prometheus metrics** — solar, battery, grid, load, inverter temps, time-of-use
- **Zero cloud dependency** — communicates directly with the Wi-Fi data logger on your LAN
- **Secrets in `.env`** — IP and serial number never touch your code
- **Grafana dashboard** — import `grafana/dashboard.json` for an instant visual overview
- **Debug mode** — run once without Prometheus to print all live values

---

## 📁 Project Structure

```
Deye-exporter/
├── .env.example        ← copy to .env and fill in your values
├── .gitignore
├── main.py             ← entry point
├── config.py           ← loads settings from .env
├── decoders.py         ← register decode logic (s16, s32, u32, ...)
├── parameters.py       ← all 52 metric definitions
├── inverter.py         ← PySolarmanV5 client
├── exporter.py         ← Prometheus Gauge setup + polling loop
├── requirements.txt
├── grafana/
│   └── dashboard.json  ← importable Grafana dashboard
└── HA/
    └── deye_hybrid.yaml ← full register map (Home Assistant reference)
```

---

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/YOUR_USERNAME/deye-exporter.git
cd deye-exporter
cp .env.example .env
```

Edit `.env` and fill in your inverter details:

```env
INVERTER_IP=192.168.1.100      # IP of the Solarman Wi-Fi data logger
INVERTER_SERIAL=1234567890     # Serial number shown in the logger web UI
INVERTER_PORT=8899
INVERTER_MB_SLAVE_ID=1
EXPORTER_PORT=9105
POLL_INTERVAL=45
```

> **Finding your serial:** Open `http://<logger-ip>` in a browser (login: `admin`/`admin`),  
> then expand "Device Information" → copy the **Device serial number**.

### 2. Install dependencies

```bash
pip install pysolarmanv5 prometheus_client python-dotenv
```

### 3. Run

**Debug mode** (print all values once):
```bash
python main.py
```

**Exporter mode** (start Prometheus endpoint):
```bash
python main.py --exporter
```

Metrics are available at: `http://localhost:9105/metrics`

---

## 🔧 Run as a systemd Service (Linux)

This lets the exporter start automatically on boot and restart on failure.

### 1. Create a virtual environment

```bash
python3 -m venv /opt/deye-env
```

### 2. Install dependencies into the venv

> ⚠️ Common mistake: running `pip install` while inside an activated venv installs to the **wrong place** when systemd runs the service. Always use the full path to pip.

```bash
/opt/deye-env/bin/pip install -r /root/deye-prometheus/requirements.txt
```

### 3. Set up your `.env`

```bash
cp /root/deye-prometheus/.env.example /root/deye-prometheus/.env
nano /root/deye-prometheus/.env   # fill in your real IP and serial
```

### 4. Create the service file

```bash
nano /etc/systemd/system/deye-exporter.service
```

Paste this:

```ini
[Unit]
Description=Deye Inverter Prometheus Exporter
After=network.target

[Service]
User=root
WorkingDirectory=/root/deye-prometheus
ExecStart=/opt/deye-env/bin/python /root/deye-prometheus/main.py --exporter
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/root/deye-prometheus/.env

[Install]
WantedBy=multi-user.target
```

### 5. Enable and start

```bash
systemctl daemon-reload
systemctl enable deye-exporter   # start on boot
systemctl start deye-exporter
```

### 6. Check logs

```bash
journalctl -u deye-exporter -f
```

You should see:
```
[deye-exporter] Prometheus metrics running on :9105/metrics
[deye-exporter] Exposing 52 gauges — polling every 5s
```

---

## 📊 Prometheus / Grafana Setup

### Prometheus scrape config

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: deye_inverter
    static_configs:
      - targets: ['localhost:9105']
    scrape_interval: 45s
```

### Grafana dashboard

1. Open Grafana → **Dashboards** → **Import**
2. Upload `grafana/dashboard.json`
3. Select your Prometheus datasource
4. Done 🎉

---

## 📈 Exposed Metrics (52 total)

| Group | Count | Examples |
|-------|-------|---------|
| Solar | 9 | `deye_pv1_power`, `deye_daily_production`, `deye_total_production` |
| Battery | 9 | `deye_battery_soc`, `deye_battery_power`, `deye_daily_battery_charge` |
| Grid | 14 | `deye_total_grid_power`, `deye_daily_energy_bought`, `deye_total_energy_sold` |
| Load | 6 | `deye_total_load_power`, `deye_daily_load_consumption` |
| Inverter | 9 | `deye_dc_temperature`, `deye_grid_frequency`, `deye_total_power` |
| Alert | 1 | `deye_alert` (fault bitmask) |
| Time of Use | 25 | `deye_time_of_use_soc_1` … `deye_time_of_use_enable_6` |

> **String-only metrics** (Battery Status, Running Status, Work Mode, etc.) are available in the  
> `HA/deye_hybrid.yaml` for Home Assistant but are not exposed as Prometheus gauges 
> since Prometheus cannot store text values in a Gauge.

---

## 🙏 Credits & Attribution

Register definitions in `HA/deye_hybrid.yaml` and the register mapping used in  
`parameters.py` are adapted from:

**[StephanJoubert/home_assistant_solarman](https://github.com/StephanJoubert/home_assistant_solarman)**  
Licensed under the [Apache License 2.0](https://github.com/StephanJoubert/home_assistant_solarman/blob/main/LICENSE).

The Solarman V5 protocol implementation is provided by:

**[jmccrohan/pysolarmanv5](https://github.com/jmccrohan/pysolarmanv5)**

---

## 📄 License

MIT — do whatever you want, just don't blame me if your battery explodes 🔋
