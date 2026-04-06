# ===== IMPORTS =====
from sensors.mpu_handler import MPUHandler
from sensors.gps_handler import GPSHandler
from sensors.rf_handler import RFHandler
from sensors.bmp_handler import BMPHandler
from sensors.motor_handler import StepMotorHandler
from sensors.buzzer_handler import BuzzerHandler
import threading


# ---- setup ----

shared = {}
lock = threading.Lock()
stop_event = threading.Event()

# ---- threads ----

threads = [
    threading.Thread(
        target=MPUHandler().imu_thread, args=(shared, lock, stop_event), daemon=True
    ),
    threading.Thread(
        target=GPSHandler().gps_thread, args=(shared, lock, stop_event), daemon=True
    ),
    threading.Thread(
        target=RFHandler().rf_thread, args=(shared, lock, stop_event), daemon=True
    ),
    threading.Thread(
        target=BMPHandler().bmp_thread, args=(shared, lock, stop_event), daemon=True
    ),
    threading.Thread(
        target=StepMotorHandler().motor_thread, args=(shared, lock, stop_event), daemon=True
    ),
    threading.Thread(
        target=BuzzerHandler().buzzer_thread, args=(shared, lock, stop_event), daemon=True
    ),
]

for t in threads:
    t.start()
try:
    stop_event.wait()
except KeyboardInterrupt:
    print("[main] Stopping...")
    stop_event.set()
