import serial
import json
import time

APC220_PORT = "/dev/ttyUSB0"
APC220_BAUD = 9600

# Fields sent in every packet
FIELDS = ["ax", "ay", "az", "gx", "gy", "gz", "lat", "lon", "alt", "tmp", "prs"]

class RFHandler:
    def __init__(self) -> None:
        try:
            self._ser = serial.Serial(APC220_PORT, APC220_BAUD, timeout=1)

        except serial.SerialException as e:
            print("[RF] Could not open APC220: ", e)
            return



    def rf_thread(self, shared: dict, lock, stop_event) -> None:
        print("[RF] Transmitting...")

        while not stop_event.is_set():
            with lock:
                packet = {k: shared.get(k) for k in FIELDS}

            line = json.dumps(packet) + "\n"

            try:
                self._ser.write(line.encode("ascii"))

            except serial.SerialException as e:
                print("[RF] Write error: ", e)

            time.sleep(0.1)

        self._ser.close()
        print("[RF] Stopped.")

