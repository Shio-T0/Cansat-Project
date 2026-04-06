# InAxon CanSat — Flight Software & Ground Station

Built by the **InAxon team**. This repository contains the full CanSat system: flight software running on a Raspberry Pi Zero, a ground station serial receiver, and a real-time telemetry dashboard.

---

## Repository Structure

```
CansatProject/
├── run.sh                              ← starts the full ground station
├── ground.py                           ← serial receiver: APC220 → CSV + dashboard
├── pyproject.toml                      ← root uv project (Python 3.14)
├── README.md
├── logs/                               ← timestamped CSV logs (auto-created)
│
├── pi_files/                           ← Raspberry Pi Zero flight software
│   ├── cansat.py                       ← main script: spawns all threads
│   └── sensors/
│       ├── mpu_handler.py              ← MPU6050 IMU (accel + gyro)
│       ├── gps_handler.py              ← Adafruit Ultimate GPS (NMEA over UART)
│       ├── bmp_handler.py              ← BMP388 (pressure + temperature)
│       ├── motor_handler.py            ← 28BYJ-48 step motor via ULN2003
│       ├── rf_handler.py               ← APC220 RF transmitter (JSON lines)
│       └── buzzer_handler.py           ← Passive buzzer (startup + Mario recovery)
│
└── InfoDisplay_Dashboard/              ← real-time telemetry dashboard
    ├── main.py                         ← Flask + Socket.IO backend
    ├── consts.py                       ← shared constants (ISA model, port, etc.)
    ├── pyproject.toml                  ← dashboard uv project (Python 3.13)
    ├── .env                            ← HF_KEY (not committed)
    └── static/
        ├── js/
        │   ├── main.js                 ← Plotly graphs, socket handling, stats bar
        │   └── axis_analizis.js        ← Three.js 3D orientation viewer + comp. filter
        ├── css/
        └── assets/                     ← SD card images dropped here post-mission
```

---

## System Architecture

```
[Pi Zero — pi_files/]
  MPUHandler   ──┐
  GPSHandler   ──┤
  BMPHandler   ──┼──► shared dict ──► RFHandler ──► APC220 ──► (RF link)
  MotorHandler ◄─┤  (thread-safe)
  BuzzerHandler◄─┘

[Ground Station]
  (RF link) ──► APC220 ──► ground.py
                              │ parses JSON packets
                              │ logs to ./logs/*.csv
                              │ HTTP POST → /ingest
                              ▼
                           main.py  (Flask + Socket.IO)
                              │ computes barometric altitude
                              │ computes ISA expected values
                              │ emits new_data via WebSocket
                              ▼
                           Browser Dashboard
                              ├── 4 Plotly graphs (experimental vs ISA)
                              ├── Three.js 3D orientation model (comp. filter in browser)
                              ├── Live stats: altitude, coordinates, data rate
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
| BMP388 | I²C (0x77) | Pressure + temperature |
| APC220 RF module | USB-serial `/dev/ttyUSB0` | Telemetry downlink |
| 28BYJ-48 + ULN2003 | GPIO 17,27,22,23 (BCM) | Attitude correction |
| Passive buzzer | GPIO 18 (PWM) | Startup beep + Mario recovery theme |
| Pi Camera v2.1 | CSI (15-to-22-pin adapter) | Images saved to SD card |
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
| `alt` | m | GPS (fallback only — see below) |
| `tmp` | °C | BMP388 |
| `prs` | hPa | BMP388 |

> Altitude on the dashboard is computed from `prs` + `tmp` using the hypsometric equation in `main.py`, not from the GPS `alt` field. GPS altitude is only used as a fallback before the BMP388 is wired.

---

## Computation Split

The Pi is kept intentionally minimal — it only reads sensors, drives the motor, and transmits raw values. All signal processing runs on the ground:

| Computation | Where | Notes |
|---|---|---|
| Barometric altitude | `main.py` | Hypsometric equation from `prs` + `tmp` |
| ISA expected temperature | `main.py` | Standard atmosphere model |
| ISA expected pressure | `main.py` | Standard atmosphere model |
| Roll + pitch | `axis_analizis.js` | Complementary filter runs in browser |
| Attitude correction | `motor_handler.py` | Only exception — must run on Pi |
| Landing detection | `buzzer_handler.py` | Baro + accel fusion, self-contained on Pi |

---

## Ground Station Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
# Repo root — first time only
uv init --no-workspace
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

# Verify sensors detected after wiring
i2cdetect -y 1     # expect: 68 (MPU6050), 77 (BMP388)

# Install dependencies
pip install mpu6050-raspberrypi pynmea2 pyserial \
    adafruit-blinka adafruit-circuitpython-bmp3xx \
    rpimotorlib RPi.GPIO --break-system-packages

# Run manually
cd pi_files
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

## Buzzer Behaviour

| Event | Pattern |
|---|---|
| System boot | Double beep |
| Landing confirmed | Super Mario Bros theme, looping |

Landing is confirmed when both conditions hold simultaneously for 5 seconds: barometric altitude within 30m of launch altitude AND accelerometer magnitude within 0.15g of 1g (stationary). The buzzer computes its own barometric altitude independently from the BMP388 values in the shared buffer — it does not depend on the ground station.

---

## AI Assistant

Powered by **Mistral-7B** via the HuggingFace inference router. On every query it receives the latest telemetry packet as context, so it can answer questions about current flight data, interpret anomalies, and compare measurements against ISA expected values. Requires `HF_KEY` in `InfoDisplay_Dashboard/.env`.

---

## Known Issues

- **`axis_analizis.js`** — `applyIMU` has a duplicate parameter (`gy` appears twice, `gx` missing) causing a `ReferenceError` at runtime. The complementary filter fusion also uses `(ALPHA - 1)` instead of `(1 - ALPHA)`, inverting the accelerometer correction.
- **`ground.py`** — `writeheader` is missing `()` so CSV headers are never written. The `received` counter is never incremented. Several `log.info` / `log.error` calls pass extra args with commas instead of `%s` format strings.
- **`mpu_handler.py`** — `time.sleep(0.01)` is outside the `while` loop, so the IMU runs at full CPU speed with no delay.
- **`motor_handler.py`** — the `threading.Lock` wraps the entire `motor_run` call, blocking IMU and GPS writes for up to 40ms per correction. Only the `gz` read needs the lock.
- **`main.py`** — `generate_data()` is still running as a background task and emitting random `new_data` events that interfere with real data from `/ingest`. It should be removed.
