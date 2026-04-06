from mpu6050 import mpu6050
import time


class MPUHandler:
    def __init__(self) -> None:
        try:
            self._sensor = mpu6050(0x68)

        except Exception as e:
            print("[IMU] Init failed: ", e)
            self._sensor = None

    def imu_thread(self, shared, lock, stop_event) -> None:
        while not stop_event.is_set():
            try:
                accel, gyro, _ = self._sensor.get_all_data()

                with lock:
                    shared["ax"] = accel["x"]
                    shared["ay"] = accel["y"]
                    shared["az"] = accel["z"]

                    shared["gx"] = gyro["x"]
                    shared["gy"] = gyro["y"]
                    shared["gz"] = gyro["z"]

            except Exception as e:
                print("[IMU] error: ", e)

        time.sleep(0.01)
