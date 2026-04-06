from RpiMotorLib import RpiMotorLib
import time

PINS = (17, 27, 22, 23)

GZ_THRESHOLD  = 5.0           # deg/s <- ignore below this
STEPS_PER_DEG = 2048 / 360    # half-steps per degree
STEP_DELAY    = 0.002         # seconds between steps
MAX_STEPS     = 20            # cap per correction cycle

class StepMotorHandler:
    def __init__(self) -> None:
        self._motor = RpiMotorLib.BYJMotor("StepMotor", "half")

    def motor_thread(self, shared: dict, lock, stop_event) -> None:
        while not stop_event.is_set():
            with lock:
                gz = shared.get("gz", 0.0)

                if abs(gz) < GZ_THRESHOLD:
                    time.sleep(0.05)
                    continue

                correction_deg = gz * 0.05
                steps = min(int(abs(correction_deg) * STEPS_PER_DEG), MAX_STEPS)
                clockwise = gz < 0

                self._motor.motor_run(PINS, STEP_DELAY, steps, clockwise, False, "half")
        
        self._motor.motor_stop(PINS)
