# InAxon CanSat — Flight Software & Ground Station

A complete CanSat system built by the **InAxon team**, covering flight software running on a Raspberry Pi Zero, a ground station serial receiver, and a real-time telemetry dashboard.

---

## Repository Structure

```
CansatProject/
├── run.sh                        ← starts the full ground station
├── ground.py                     ← serial receiver: APC220 → CSV + dashboard
│
├── InfoDisplay_Dashboard/        ← real-time telemetry dashboard
│   ├── main.py                   ← Flask + Socket.IO backend
│   └── static/
│       ├── js/
│       │   ├── main.js           ← Plotly graphs, socket handling, stats bar
│       │   └── axis_analizis.js  ← Three.js 3D orientation viewer
│       └── assets/               ← SD card images dropped here post-mission
│
└── cansat/                       ← Pi Zero flight software (to be added)
    └── cansat.py                 ← IMU, GPS, TX threads + step motor control
```

---

## System Architecture

```
[Pi Zero]                         [Ground Station]
  IMU thread  ──┐                   ground.py
  GPS thread  ──┼──► TX thread ──►  - reads APC220 via serial
  Step motor  ◄─┘    (APC220)       - validates JSON packets
                                    - logs to CSV
                                    - POSTs to Flask
                                         │
                                    main.py (Flask + SocketIO)
                                    - /ingest route
                                    - computes ISA expected values
                                    - emits new_data to browser
                                         │
                                    Browser Dashboard
                                    - 4 Plotly graphs (exp vs ISA)
                                    - Three.js 3D orientation model
                                    - Live stats: alt, coords, rate
                                    - AI assistant (Mistral-7B)
                                    - Image gallery (post-mission)
```

---

## Hardware

### Flight (Pi Zero)
| Component | Interface |
|---|---|
| Raspberry Pi Zero v1.3 | — |
| MPU6050 IMU (accel + gyro) | I²C |
| Adafruit Ultimate GPS v3 | UART `/dev/ttyAMA0` |
| APC220 RF module | USB-serial `/dev/ttyUSB0` |
| Step motor | GPIO (attitude correction) |
| Pi Camera v2.1 | CSI (15-to-22-pin adapter) |
| DFRobot pressure sensor | I²C |
| Temperature + humidity sensor | — |
| LiPo + PowerBoost 1000C | — |

### Ground
| Component | Interface |
|---|---|
| APC220 RF module | USB-serial `/dev/ttyUSB0` |

---

## Packet Format

The Pi sends one JSON line per packet at 10 Hz over the APC220:

```json
{"ax": 0.12, "ay": -0.34, "az": 9.81, "gx": 1.20, "gy": -0.50, "gz": 0.30, "lat": 38.7139, "lon": -9.1334, "alt": 120.5, "tmp": 23.4, "prs": 1001.2}
```

| Field | Unit | Source |
|---|---|---|
| `ax` `ay` `az` | g | MPU6050 accelerometer |
| `gx` `gy` `gz` | °/s | MPU6050 gyroscope |
| `lat` `lon` | ° | GPS |
| `alt` | m (above sea level) | GPS |
| `tmp` | °C | temperature sensor |
| `prs` | hPa | pressure sensor |

---

## Ground Station Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# First time only
uv init --no-workspace   # in repo root

cd InfoDisplay_Dashboard
uv init                  # already done — skip if pyproject.toml exists
```

**Running:**

```bash
chmod +x run.sh   # first time only
./run.sh
```

This starts both processes:
- Dashboard → [http://localhost:4000](http://localhost:4000)
- Ground receiver → reads `/dev/ttyUSB0`, logs to `./logs/`

Ctrl+C shuts both down cleanly.

**Environment variables** — create `InfoDisplay_Dashboard/.env`:

```
HF_KEY=your_huggingface_token
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

## Flight Software Setup (Pi Zero)

> Code to be added under `cansat/`

```bash
# On the Pi
pip install mpu6050-raspberrypi pyserial --break-system-packages

# Enable at boot
sudo cp cansat.service /etc/systemd/system/
sudo systemctl enable cansat.service
sudo systemctl start cansat.service
```

---

## Data Logging

Every received packet is written to a timestamped CSV in `./logs/`:

```
logs/cansat_20260405_142301.csv
```

Columns: `timestamp, ax, ay, az, gx, gy, gz, lat, lon, alt, tmp, prs`

After the mission, images from the SD card are copied into `InfoDisplay_Dashboard/static/assets/` and will appear automatically in the image gallery.

---

## Orientation Computation

Roll and pitch are computed on the ground (not the Pi) using a **complementary filter** running in the browser:

```
roll  = 0.98 × (roll  + gx × dt) + 0.02 × atan2(ay, az)
pitch = 0.98 × (pitch + gy × dt) + 0.02 × atan2(-ax, √(ay²+az²))
```

The Pi only sends raw IMU values. This keeps flight software minimal and offloads computation to the ground where resources are unlimited.

---

## AI Assistant

The dashboard includes an AI assistant (Mistral-7B via HuggingFace) that receives the latest telemetry as context and can answer questions about flight data in real time. Requires a HuggingFace API key in `.env`.
