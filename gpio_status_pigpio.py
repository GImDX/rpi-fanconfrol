#!/usr/bin/env python3
import pigpio
import subprocess

# ========== 显示 pigpiod 连接（放最前） ==========
print("\n🔌 正在连接 pigpiod 的客户端进程（端口 8888）:")
print("-" * 60)

try:
    result = subprocess.run(
        ["sudo", "lsof", "-nPi", "TCP:8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    output = result.stdout.strip()
    if output:
        print(output)
    else:
        print("无活动连接")
except Exception as e:
    print("执行 lsof 失败：", e)

# ========== 连接 pigpiod ==========
pi = pigpio.pi()
if not pi.connected:
    print("\n[错误] 未连接 pigpiod，请先运行：sudo pigpiod")
    exit(1)

# ========== 显示 GPIO 状态 ==========
mode_map = {
    pigpio.INPUT: "IN",
    pigpio.OUTPUT: "OUT",
    pigpio.ALT0: "ALT0",
    pigpio.ALT1: "ALT1",
    pigpio.ALT2: "ALT2",
    pigpio.ALT3: "ALT3",
    pigpio.ALT4: "ALT4",
    pigpio.ALT5: "ALT5"
}

HW_PWM_PINS = {12, 13, 18, 19}

print("\n📟 GPIO 状态（0~27）:")
print(f"{'GPIO':>4} {'Mode':<5} {'Level':<5} {'PWM_Type':<10} {'Freq':>8} {'Duty':>10}")
print("-" * 60)

for gpio in range(0, 28):
    mode = pi.get_mode(gpio)
    level = pi.read(gpio)

    pwm_type = ""
    freq = "-"
    duty = "-"

    if gpio in HW_PWM_PINS and mode == pigpio.ALT0:
        # Hardware PWM detection
        pwm_type = "HARDWARE"
        freq = pi.get_PWM_frequency(gpio)
        duty = pi.get_PWM_dutycycle(gpio)
    else:
        try:
            s_freq = pi.get_PWM_frequency(gpio)
            s_duty = pi.get_PWM_dutycycle(gpio)
            if s_duty > 0:
                pwm_type = "SOFTWARE"
                freq = s_freq
                duty = s_duty
        except pigpio.error:
            pass

    print(f"{gpio:>4} {mode_map.get(mode, '?'):5} {level:^5} {pwm_type:<10} {str(freq):>8} {str(duty):>10}")

pi.stop()
