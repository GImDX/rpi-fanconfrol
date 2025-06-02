
# PWM Fan Control for Raspberry Pi (pigpio-based)

注意某些树莓派，如4B，调用pigpio，某些频率（11~50kHz）可能没有输出`https://github.com/joan2937/pigpio/issues/517`，使用PWM1（GPIO13）或调高调低频率

树莓派风扇 PWM 控制服务（基于 pigpio），实现以下功能：

- 🌡️ 自动读取风扇转速（通过 TACHO 信号）
- ⚙️ 输出稳定的 25kHz 硬件 PWM 信号控制风扇转速
- 📝 配置文件 `config.txt` 设置初始占空比（PWM_DUTY）
- 📊 实时记录当前 PWM 和 RPM 信息

## 📦 Requirements / 依赖环境

- Raspberry Pi
- `pigpio` library
- `pigpiod` 守护进程（已设置为开机启动）

Install dependencies:

```bash
sudo apt update
sudo apt install pigpio python3-pigpio -y
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## 📁 Project Structure / 项目结构

```
pwm_fan/
├── pwm_fan.py          # 主程序：读取脉冲 + 输出 PWM
├── config.txt          # 配置文件，设置初始 PWM 占空比
├── pwm_fan.service     # systemd 服务文件
├── gpio_status_pigpio.py # 可选，用于调试 GPIO 状态
└── fan_rpm.log         # 运行中输出当前 RPM 与 PWM 状态（自动生成）
```

## ⚙️ Configuration / 配置说明

编辑 `config.txt`：

```ini
PWM_DUTY=65
```

该值为百分比（0~100），用于设置初始 PWM 占空比。

## 🚀 Setup as Service / 设置为服务运行

1. 将服务文件复制到系统目录：

```bash
sudo cp pwm_fan.service /etc/systemd/system/
```

2. 启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable pwm_fan.service
sudo systemctl restart pwm_fan.service
```

3. 查看服务状态：

```bash
sudo systemctl status pwm_fan
```

4. 查看日志输出：

```bash
cat /var/log/fan_pwm.log
```

## 📜 License

MIT License
