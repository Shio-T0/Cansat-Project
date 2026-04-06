import serial
import pynmea2
import time


GPS_PORT = "/dev/ttyAMA0"
GPS_BAUD = 9600

class GPSHandler:
    def __init__(self) -> None:
        try:
            self._ser = serial.Serial(GPS_PORT, GPS_BAUD, timeout=2)
        except serial.SerialException as e:
            print("[GPS] could not open port: ", e)
            return

    def gps_thread(self, shared: dict, lock, stop_event) -> None:
        while not stop_event.is_set():
            try:
                raw = self._ser.readline().decode("ascii", errors="replace").strip()

                if not raw.startswith("$"):
                    continue

                msg = pynmea2.parse(raw)

                if isinstance(msg, pynmea2.GGA):
                    if msg.gps_qual and msg.gps_qual > 0:
                        with lock:
                            shared["lat"] = round(msg.latitude,  6)
                            shared["lon"] = round(msg.longitude, 6)
                            shared["alt"] = round(msg.altitude,  1)

            except pynmea2.ParseError:
                pass

            except serial.SerialException as e:
                print("[GPS] Serial error: ", e)
                time.sleep(1)

    
        self._ser.close()



