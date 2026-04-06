# InAxon CanSat — Flight Software & Ground Station

Built by the **InAxon team**. This repository contains the full CanSat system: flight software running on a Raspberry Pi Zero, a ground station serial receiver, and a real-time telemetry dashboard.

---

## Repository Structure

```
CansatProject/
├── run.sh                             ← starts the full ground station
├── ground.py                          ← serial receiver: APC220 → CSV + dashboard
├── README.md
│
├── pi_files/pi/                       ← Raspberry Pi Zero flight software
│   ├── cansat.py                      ← main script: spawns all threads
│   └── sensors/
│       ├── mpu_handler.py             ← MPU6050 IMU (accel + gyro)
│       ├── gps_handler.py             ← Adafruit Ultimate GPS (NMEA over UART)
│       ├── bmp_handler.py             ← BMP388 (pressure + temperature)
│       ├── motor_handler.py           ← 28BYJ-48 step motor via ULN2003
│       └── rf_handler.py             ← APC220 RF transmitter (JSON lines)
│
└── InfoDisplay_Dashboard/             ← real-time telemetry dashboard
    ├── main.py                        ← Flask + Socket.IO backend
    ├── .env                           ← HF_KEY (not committed)
    └── static/
        ├── js/
        │   ├── main.js                ← Plotly graphs, socket handling, stats bar
        │   └── axis_analizis.js       ← Three.js 3D orientation viewer
        └── assets/                    ← SD card images dropped here post-mission
```

---

## System Architecture

```
[Pi Zero — pi_files/pi/]
  MPUHandler  ──┐
  GPSHandler  ──┤
  BMPHandler  ──┼──► shared dict ──► RFHandler ──► APC220 ──► (RF link)
  MotorHandler ◄┘  (thread-safe)

[Ground Station]
  (RF link) ──► APC220 ──► ground.py
                              │ validates JSON packets
                              │ logs to ./logs/*.csv
                              │ HTTP POST
                              ▼
                           main.py  (Flask + Socket.IO)
                              │ computes barometric altitude
                              │ computes ISA expected values
                              │ emits new_data via WebSocket
                              ▼
                           Browser Dashboard
                              ├── 4 Plotly graphs (experimental vs ISA)
                              ├── Three.js 3D orientation model
                              ├── Live stats: altitude, coords, data rate
                              ├── AI assistant (Mistral-7B via HuggingFace)
                              └── Image gallery (post-mission, manual load)
```

---

## Hardware

### Flight (Pi Zero)

| Component | Interface | Notes |
|---|---|---|
| Raspberry Pi Zero v1.3 | — | Flight computer |
| MPU6050 | I²C (0x68) | Accelerometer + gyroscope |
| Adafruit Ultimate GPS v3 | UART `/dev/ttyAMA0` | Position |
| BMP388 | I²C | Pressure + temperature |
| APC220 RF module | USB-serial `/dev/ttyUSB0` | Telemetry downlink |
| 28BYJ-48 + ULN2003 | GPIO 17,27,22,23 (BCM) | Attitude correction |
| Pi Camera v2.1 | CSI (15-to-22-pin adapter) | Images to SD card |
| LiPo + PowerBoost 1000C | — | Power |

### Ground

| Component | Interface |
|---|---|
| APC220 RF module | USB-serial `/dev/ttyUSB0` |

---

## Packet Format

The Pi transmits one JSON line per packet at **10 Hz** over the APC220:

```json
{"ax": 0.12, "ay": -0.34, "az": 9.81, "gx": 1.20, "gy": -0.50, "gz": 0.30, "lat": 38.7139, "lon": -9.1334, "alt": 120.5, "tmp": 23.4, "prs": 1001.2}
```

| Field | Unit | Source |
|---|---|---|
| `ax` `ay` `az` | g | MPU6050 accelerometer |
| `gx` `gy` `gz` | °/s | MPU6050 gyroscope |
| `lat` `lon` | ° | GPS |
| `alt` | m | GPS (fallback only) |
| `tmp` | °C | BMP388 |
| `prs` | hPa | BMP388 |

> Altitude shown on the dashboard is computed from `prs` + `tmp` using the hypsometric equation, not from the GPS `alt` field directly.

---

## Computation Split

The Pi is kept intentionally minimal — it only reads sensors and transmits raw values. All heavy computation runs on the ground:

| Computation | Where |
|---|---|
| Barometric altitude | `main.py` — hypsometric equation from `prs` + `tmp` |
| ISA expected temperature | `main.py` — standard atmosphere model |
| ISA expected pressure | `main.py` — standard atmosphere model |
| Roll + pitch (comp. filter) | `axis_analizis.js` — runs in browser |
| Attitude correction | `motor_handler.py` — only exception, must run on Pi |

---

## Ground Station Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Repo root — first time only
uv init --no-workspace

# Dashboard — already initialised
cd InfoDisplay_Dashboard
```

Create `InfoDisplay_Dashboard/.env`:
```
HF_KEY=your_huggingface_token
```

**Running:**
```bash
chmod +x run.sh   # first time only
./run.sh
```

Starts both processes:
- Dashboard → [http://localhost:4000](http://localhost:4000)
- Ground receiver → reads `/dev/ttyUSB0`, logs to `./logs/`

Ctrl+C shuts both down cleanly.

---

## Pi Setup

```bash
# Enable I²C (required for MPU6050 and BMP388)
sudo raspi-config   # Interface Options → I2C → Enable

# Verify sensors are detected after wiring
i2cdetect -y 1     # should show 68 (MPU6050) and 77 (BMP388)

# Install dependencies
pip install mpu6050-raspberrypi pynmea2 pyserial \
    adafruit-blinka adafruit-circuitpython-bmp3xx \
    rpimotorlib --break-system-packages

# Run
cd pi_files/pi
python cansat.py

# Autostart on boot
sudo cp cansat.service /etc/systemd/system/
sudo systemctl enable cansat.service
sudo systemctl start cansat.service
```

---

## Dashboard Pages

| Route | Description |
|---|---|
| `/` | Landing page |
| `/charts` | Main dashboard — graphs, AI assistant, 3D viewer, stats |
| `/axis-analizis` | Full-screen 3D orientation model |
| `/image-display` | Image gallery |

---

## Data Logging

Every received packet is written to a timestamped CSV in `./logs/`:

```
logs/cansat_20260405_142301.csv
```

Columns: `timestamp, ax, ay, az, gx, gy, gz, lat, lon, alt, tmp, prs`

After the mission, copy images from the Pi's SD card into `InfoDisplay_Dashboard/static/assets/` — they appear automatically in the image gallery at `/image-display`.

---

## AI Assistant

The dashboard includes a chat assistant powered by **Mistral-7B** via the HuggingFace inference router. It receives the latest telemetry packet as context on every query, so it can answer questions about current flight data, interpret anomalies, and compare measurements against expected values. Requires `HF_KEY` in `.env`.
