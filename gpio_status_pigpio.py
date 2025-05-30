#!/usr/bin/env python3
import pigpio
import subprocess

# ========== GPIO Alternate Functions 映射 ==========
gpio_alt_functions = {
    0:  ["SDA0", "SA5", "PCLK", "SPI3.CEO_N", "TXD2", "SDA6"],
    1:  ["SCL0", "SA4", "DE", "SPI3.MISO", "RXD2", "SCL6"],
    2:  ["SDA1", "SA3", "LCD_VSYN", "SPI3.MOSI", "CTS2", "SDA3"],
    3:  ["SCL1", "SA2", "LCD_HSYN", "SPI3.SCLK", "RTS2", "SCL3"],
    4:  ["GPCLK0", "SA1", "DPI_D0", "SPI4.CEO_N", "TXD3", "SDA3"],
    5:  ["GPCLK1", "SA0", "DPI_D1", "SPI4.MISO", "RXD3", "SCL3"],
    6:  ["GPCLK2", "SOE_N", "DPI_D2", "SPI4.MOSI", "CTS3", "SDA4"],
    7:  ["SPI0.CE1_N", "SWE_N", "DPI_D3", "SPI4.SCLK", "RTS3", "SCL4"],
    8:  ["SPI0.CE0_N", "SD0", "DPI_D4", "-", "TXD4", "SDA4"],
    9:  ["SPI0.MISO", "SD1", "DPI_D5", "-", "RXD4", "SCL4"],
    10: ["SPI0.MOSI", "SD2", "DPI_D6", "-", "CTS4", "SDA5"],
    11: ["SPI0.SCLK", "SD3", "DPI_D7", "-", "RTS4", "SCL5"],
    12: ["PWM0", "SD4", "DPI_D8", "SPI5.CEO_N", "TXD5", "SDA5"],
    13: ["PWM1", "SD5", "DPI_D9", "SPI5.MISO", "RXD5", "SCL5"],
    14: ["TXD0", "SD6", "DPI_D10", "SPI5.MOSI", "CTS5", "TXD1"],
    15: ["RXD0", "SD7", "DPI_D11", "SPI5.SCLK", "RTS5", "RXD1"],
    16: ["FL0", "SD8", "DPI_D12", "CTS0", "SPI1.CE2_N", "CTS1"],
    17: ["FL1", "SD9", "DPI_D13", "RTS0", "SPI1.CE1_N", "RTS1"],
    18: ["PCM.CLK", "SD10", "DPI_D14", "SPI6.CEO_N", "SPI6.CEO_N", "PWM0"],
    19: ["PCM.FS", "SD11", "DPI_D15", "SPI6.MISO", "SPI1.MISO", "PWM1"],
    20: ["PCM.DIN", "SD12", "DPI_D16", "SPI6.MOSI", "SPI1.MOSI", "GPCLK0"],
    21: ["PCM.DOUT", "SD13", "DPI_D17", "SPI6.SCLK", "SPI1.SCLK", "GPCLK1"],
    22: ["SD0.CLK", "SD14", "DPI_D18", "SD1.CLK", "ARM.TRST", "SDA6"],
    23: ["SD0.CMD", "SD15", "DPI_D19", "SD1.CMD", "ARM.RTCK", "SCL6"],
    24: ["SD0.DAT0", "SD16", "DPI_D20", "SD1.DAT0", "ARM.TDO", "SPI3.CEI_N"],
    25: ["SD0.DAT1", "SD17", "DPI_D21", "SD1.DAT1", "ARM.TCK", "SPI4.CEI_N"],
    26: ["SD0.DAT2", "TE0", "DPI_D22", "SD1.DAT2", "ARM.TDI", "SPI5.CEO_N"],
    27: ["SD0.DAT3", "TE1", "DPI_D23", "SD1.DAT3", "ARM.TMS", "SPI6.CEI_N"],
}



# ========== 正确的硬件 PWM 检测模式 ==========
hw_pwm_modes = {
    12: pigpio.ALT0,  # PWM0
    13: pigpio.ALT0,  # PWM1
    18: pigpio.ALT5,  # PWM0
    19: pigpio.ALT5   # PWM1
}

# ========== 显示 pigpiod 连接（放最前） ==========
print("\n🔌 正在连接 pigpiod 的客户端进程（端口 8888）:")
print("-" * 114)

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

print("\n📟 GPIO 状态（0~27）:")
print(f"{'GPIO':>4} {'Mode':<4} {'Level':<5} {'PWM_Type':<8} {'Freq':>8} {'Duty':>10}  {'ALT0':<10} {'ALT1':<10} {'ALT2':<10} {'ALT3':<10} {'ALT4':<10} {'ALT5'}")
print("-" * 114)

for gpio in range(0, 28):
    mode = pi.get_mode(gpio)
    level = pi.read(gpio)

    pwm_type = ""
    freq = "-"
    duty = "-"

    # 正确判断硬件 PWM：gpio+mode 对应才算
    if gpio in hw_pwm_modes and mode == hw_pwm_modes[gpio]:
        pwm_type = "HARDWARE"
        try:
            freq = pi.get_PWM_frequency(gpio)
            duty = pi.get_PWM_dutycycle(gpio)
        except pigpio.error:
            pass  # 有可能虽然模式匹配但实际未启用
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

    alt = gpio_alt_functions.get(gpio, ["-"] * 6)
    print(f"{gpio:>4} {mode_map.get(mode, '?'):4} {level:^5} {pwm_type:<8} {str(freq):>8} {str(duty):>10}  {alt[0]:<10} {alt[1]:<10} {alt[2]:<10} {alt[3]:<10} {alt[4]:<10} {alt[5]}")

pi.stop()
