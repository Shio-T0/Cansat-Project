# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pyserial",
#     "requests",
# ]
# ///

import csv
import json
import logging
import serial
import requests
from pathlib import Path
from datetime import datetime
from InfoDisplay_Dashboard.consts import EXP, L, P0

# _____ Consts _____
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
DASHBOART_URL = "http://localhost:4000/ingest"
LOG_DIR = Path("./logs")

# _____ Log _____
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ground")

FIELDS = [
    "timestamp",
    "ax",
    "ay",
    "az",
    "gx",
    "gy",
    "gz",
    "lat",
    "lon",
    "alt",
    "tmp",
    "prs",
]


# ======================
#  Csv Saving
# ======================
class CSVLogger:
    def __init__(self) -> None:
        LOG_DIR.mkdir(exist_ok=True)
        filename = LOG_DIR / f"cansat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._file = open(filename, "w", newline="")
        self._writer = csv.DictWriter(
            self._file, fieldnames=FIELDS, extrasaction="ignore"
        )
        self._writer.writeheader
        log.info("Logging to ", filename)

    def write(self, packet: dict) -> None:
        self._writer.writerow(packet)
        self._file.flush()

    def close(self) -> None:
        self._file.close()


def barometric_altitude(prs_hpa: float, tmp_c: float) -> float:
    """
    Calculates the altitude using pressure: prs_hpa, and temperature: tmp_c.
    """
    T_kelvin = tmp_c + 273.15
    return (T_kelvin / L) * (1 - (prs_hpa / P0) ** (1 / EXP))


# ======================
#  Main
# ======================
def main():
    logger = CSVLogger()

    log.info(f"Opening {SERIAL_PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    except serial.SerialException as e:
        log.error("Could not open serial port: ", e)
        return

    log.info("Listening... Ctrl+C to close")
    received, failed = 0, 0

    try:
        while True:
            try:
                raw = ser.readline().decode("ascii", errors="replace").strip()

            except serial.SerialException as e:
                log.error("Serial read error: ", e)
                continue

            if not raw:
                continue

            try:
                packet = json.loads(raw)
            except json.JSONDecodeError as e:
                failed += 1
                log.error("Could not decode json: ", e)
                continue

            packet["timestamp"] = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log.info(
                "[#%d] alt=%.1fm tmp=%.1f°C lat=%.5f lon=%.5f",
                received,
                packet.get("alt", 0),
                packet.get("tmp", 0),
                packet.get("lat", 0),
                packet.get("lon", 0),
            )

            logger.write(packet)

            try:
                requests.post(DASHBOART_URL, json=packet, timeout=0.5)
            except requests.exceptions.RequestException:
                log.error("Dashboard unreachable")

    except KeyboardInterrupt:
        log.info(f"Stopped. {received} received, {failed} failed")

    finally:
        ser.close()
        logger.close()


if __name__ == "__main__":
    main()
