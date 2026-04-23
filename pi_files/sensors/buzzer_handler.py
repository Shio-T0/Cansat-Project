import RPi.GPIO as GPIO
import time

BUZZER_PIN = 21

LAND_ALT_RANGE = 30
LAND_ACCEL_TOL = 0.15
LAND_CONFIRM_SEC = 5.0
ALT_CALIBRATION_SAMPLES = 10

# Barometric altitude consts
T0, P0, L, EXP = 288.15, 1013.25, 0.0065, 5.2561


class BuzzerHandler:
    def __init__(self) -> None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        self._pwm = GPIO.PWM(BUZZER_PIN, 440)
        self._launch_alt = None
        self._land_since = None
        self._landed = False
        self._alt_samples = []

    def _tone_on(self, freq: int):
        self._pwm.ChangeFrequency(freq)
        self._pwm.start(50)

    def _tone_off(self):
        self._pwm.stop()

    def _beep(self, duration: float, freq: int = 2000):
        self._tone_on(freq)
        time.sleep(duration)
        self._tone_off()

    def startup_beep(self):
        """Double beep for system boot"""
        self._beep(0.1, 2000)
        time.sleep(0.1)
        self._beep(0.1, 2000)

    def _baro_alt(self, prs: float, tmp: float) -> float:
        T = tmp + 273.15
        return (T / L) * (1 - (prs / P0) ** (1 / EXP))

    def _calibrate(self, alt: float) -> bool:
        self._alt_samples.append(alt)
        if len(self._alt_samples) >= ALT_CALIBRATION_SAMPLES:
            self._launch_alt = sum(self._alt_samples) / len(self._alt_samples)
            print(f"[BUZZER] Launch altitude calibrated: {self._launch_alt:.1f}m")
            return True
        return False

    def _check_landing(self, shared: dict) -> bool:
        prs = shared.get("prs")
        tmp = shared.get("tmp")
        ax = shared.get("ax", 0.0)
        ay = shared.get("ay", 0.0)
        az = shared.get("az", 0.0)

        if prs is None or tmp is None or self._launch_alt is None:
            return False

        alt = self._baro_alt(prs, tmp)
        baro_ok = abs(alt - self._launch_alt) < LAND_ALT_RANGE
        total_g = (ax**2 + ay**2 + az**2) ** 0.5
        accel_ok = abs(total_g - 1.0) < LAND_ACCEL_TOL

        if baro_ok and accel_ok:
            if self._land_since is None:
                self._land_since = time.time()
            elif time.time() - self._land_since >= LAND_CONFIRM_SEC:
                return True
        else:
            self._land_since = None

        return False

    # Main thread
    def buzzer_thread(self, shared: dict, lock, stop_event) -> None:
        self.startup_beep()

        try:
            while not stop_event.is_set():
                with lock:
                    snapshot = dict(shared)

                if self._launch_alt is None:
                    prs = snapshot.get("prs")
                    tmp = snapshot.get("tmp")
                    if prs is not None and tmp is not None:
                        self._calibrate(self._baro_alt(prs, tmp))

                    time.sleep(0.5)
                    continue

                # Recovery phase
                if self._landed:
                    self._mario_cycle(stop_event)
                    continue

                if self._check_landing(snapshot):
                    print("[BUZZER] Landing confirmed -> I'tsa mE, Mário! ¯\\_(ツ)_/¯")
                    self._landed = True

                time.sleep(0.5)

        finally:
            self._tone_off()
            GPIO.cleanup(BUZZER_PIN)
            print("[BUZZER] Cleaned up 👍️")
