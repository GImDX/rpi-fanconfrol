#!/usr/bin/env python3
import pigpio
import time
import os

with open("/tmp/fan_debug.log", "w") as f:
    f.write("cwd: " + os.getcwd() + "\n")
    f.write("HOME: " + os.environ.get("HOME", "None") + "\n")
    f.write("USER: " + os.environ.get("USER", "None") + "\n")

# === Parameters ===
PWM_GPIO = 12                   # GPIO12: hardware PWM-capable
TACHO_GPIO = 16                 # GPIO16: FAN TACHO input
PWM_FREQ = 25000                # PWM frequency in Hz
PWM_DUTY_DEFAULT = 80           # Fallback duty cycle if config fails (%)
PULSE_MIN_WIDTH_US = 1000       # Minimum valid low-pulse width (us)
FAN_PULSES_PER_REV = 2          # Pulses per fan revolution
PRINT_INTERVAL = 1.0            # Print & log interval in seconds
CONFIG_FILE = "config.txt"
LOG_FILE = "fan_rpm.log"

# === State ===
last_tick = 0
valid_pulse_count = 0
last_rpm_time = time.time()

# === Load PWM duty from config.txt ===
def load_pwm_duty():
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.startswith("PWM_DUTY="):
                    val = float(line.strip().split("=")[1])
                    return max(0, min(100, val))  # Clamp to 0–100%
    except Exception as e:
        print(f"[WARN] Failed to load config.txt: {e}")
    return PWM_DUTY_DEFAULT

# === Initialize pigpio ===
pi = pigpio.pi()
if not pi.connected:
    print("Not connected to pigpio daemon. Run: sudo pigpiod")
    exit(1)

# === Set hardware PWM ===
def set_pwm(duty_percent):
    duty = int(duty_percent * 1_000_000 / 100)
    pi.hardware_PWM(PWM_GPIO, PWM_FREQ, duty)
    print(f"[PWM] Output @ {PWM_FREQ} Hz, Duty = {duty_percent:.1f}%")

# === Callback for TACHO falling edges ===
def tach_callback(gpio, level, tick):
    global last_tick, valid_pulse_count
    if level == 0:
        width = pigpio.tickDiff(last_tick, tick)
        if width >= PULSE_MIN_WIDTH_US:
            valid_pulse_count += 1
        last_tick = tick

# === Main logic ===
def main():
    global valid_pulse_count, last_rpm_time

    pi.set_mode(TACHO_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(TACHO_GPIO, pigpio.PUD_UP)

    current_duty = None
    last_rpm_time = time.time()
    cb = pi.callback(TACHO_GPIO, pigpio.FALLING_EDGE, tach_callback)

    try:
        while True:
            time.sleep(0.1)

            # Load duty dynamically
            new_duty = load_pwm_duty()
            if new_duty != current_duty:
                set_pwm(new_duty)
                current_duty = new_duty

            # RPM print interval
            now = time.time()
            if now - last_rpm_time >= PRINT_INTERVAL:
                rpm = int((valid_pulse_count / (now - last_rpm_time)) * 60 / FAN_PULSES_PER_REV)
                log_line = f"RPM={rpm:5d}  PWM={current_duty:.1f}"
                # print(f"[READ] {log_line}")
                with open(LOG_FILE, "w") as logf:
                    logf.write(log_line + "\n")
                valid_pulse_count = 0
                last_rpm_time = now
    except KeyboardInterrupt:
        print("\n[QUIT] Stopping... Setting PWM = 100%")
        set_pwm(100)
    finally:
        print("\n[STOP] STOP")
        cb.cancel()
        pi.stop()


if __name__ == "__main__":
    main()
