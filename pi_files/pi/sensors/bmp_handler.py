import board
import busio
import adafruit_bmp3xx
import time

class BMPHandler:
    def __init__(self) -> None:
        try:
            self._i2c = busio.I2C(board.SCL, board.SDA)
            self._sensor = adafruit_bmp3xx.BMP3XX_I2C(self._i2c)

            self._sensor.pressure_oversampling = 8
            self._sensor.temperature_oversampling = 2

        except Exception as e:
            print("[BMP] Could not initialize sensor: ", e)
            return

    def bmp_thread(self, shared: dict, lock, stop_event):
        while not stop_event.is_set():
            try:
                with lock:
                    shared["prs"] = round(self._sensor.pressure,    2)   # hPa
                    shared["tmp"] = round(self._sensor.temperature, 2)   # degC

            except Exception as e:
                print("[BMP] Read Error: ", e)

            time.sleep(0.1)
