# simulator.py
import time
import csv
import math
import random
from pathlib import Path

FILE_PATH = Path("telemetry.csv")

def main():
    # Create file with header if not exists
    new_file = not FILE_PATH.exists()
    with FILE_PATH.open("a", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["t", "altitude", "temperature", "accel"])

        t0 = time.time()
        while True:
            t = time.time() - t0  # seconds

            # Fake altitude profile: goes up then down
            altitude = 100 * math.sin(t / 10.0) + 200  # just some curve

            # Fake temperature
            temperature = 20 + 2 * math.sin(t / 30.0) + random.uniform(-0.2, 0.2)

            # Fake accel magnitude
            accel = 1.0 + 0.1 * math.sin(t / 5.0) + random.uniform(-0.05, 0.05)

            writer.writerow([f"{t:.2f}", f"{altitude:.2f}", f"{temperature:.2f}", f"{accel:.3f}"])
            f.flush()

            time.sleep(0.5)  # sample every 0.5s

if __name__ == "__main__":
    main()
