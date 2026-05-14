# ESP32 ROD 小車 — 硬體部署指南

## 硬體需求

| 零件 | 數量 | 用途 |
|------|------|------|
| ESP32 開發板 | 1 | WiFi 馬達控制 |
| L298N 或 L9110S 馬達驅動 | 1 | 驅動 DC 馬達 |
| DC 馬達 + 輪子 | 2 | 差速驅動 |
| 電池盒 (6-12V) | 1 | 供電 |
| 麵包板 + 杜邦線 | 若干 | 接線 |

## 接線圖

```
ESP32                    L298N / L9110S
─────────────────────────────────────────
GPIO 25  ──────────────── ENA (左馬達 PWM)
GPIO 26  ──────────────── IN1 (左馬達方向)
GPIO 27  ──────────────── IN2 (左馬達方向)
GPIO 14  ──────────────── ENB (右馬達 PWM)
GPIO 12  ──────────────── IN3 (右馬達方向)
GPIO 13  ──────────────── IN4 (右馬達方向)

GND     ──────────────── GND
5V/VIN  ──────────────── VCC (可從電池獨立供電)
```

## 步驟 1：安裝 ESP32 開發工具

```bash
# 安裝 arduino-cli
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/

# 安裝 ESP32 核心
arduino-cli config init
arduino-cli core update-index
arduino-cli core install esp32:esp32

# 安裝所需庫
arduino-cli lib install WiFi WebServer
```

## 步驟 2：修改 WiFi 設定

編輯 `esp32_firmware/esp32_rod_car.ino`：

```cpp
const char* WIFI_SSID = "YOUR_WIFI_SSID";      // ← 改這裡
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // ← 改這裡
```

## 步驟 3：燒錄韌體

```bash
# 插上 ESP32（USB 線）
# 查看序列埠
ls /dev/ttyUSB*     # Linux
# 或 COM3, COM4...  # Windows

# 燒錄（把 /dev/ttyUSB0 換成你的埠）
arduino-cli compile --fqbn esp32:esp32:esp32 esp32_firmware/
arduino-cli upload -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 esp32_firmware/

# 查看 Serial Monitor（確認 IP 位址）
arduino-cli monitor -p /dev/ttyUSB0
```

## 步驟 4：測試 ESP32

```bash
# 取得 ESP32 IP（從 Serial Monitor 看到）
# 假設是 192.168.1.100

# 測試 API
curl http://192.168.1.100/status
# → {"ip":"192.168.1.100","rssi":-45,"uptime":120}

# 前進
curl "http://192.168.1.100/motor?left=0.5&right=0.5"

# 左轉
curl "http://192.168.1.100/motor?left=-0.3&right=0.3"

# 停止
curl "http://192.168.1.100/motor?left=0&right=0"
```

## 步驟 5：啟動 ROS2 橋接

```bash
# 載入環境
source ~/ros2_ws/ros2_env.sh

# 啟動橋接器（換成你的 ESP32 IP）
ros2 run esp32_bridge esp32_bridge --ros-args -p esp32_ip:=192.168.1.100

# 另一個 terminal：發送移動指令
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.0}}" -1
```

## 步驟 6：完整 AI 倉庫搬運（真實硬體版）

```bash
# Terminal 1: ESP32 橋接器
ros2 run esp32_bridge esp32_bridge --ros-args -p esp32_ip:=192.168.1.100

# Terminal 2: AI 倉庫機器人
ros2 run my_robot_bringup warehouse_robot_ai

# Terminal 3: 發送自然語言任務
ros2 run my_robot_bringup task_sender_ai "去 A 區取貨"
```

## 故障排除

| 問題 | 解決方案 |
|------|---------|
| ESP32 連不上 WiFi | 確認 SSID/密碼，或用 AP 模式（手機連 ESP32-ROD-Car 熱點） |
| 馬達不動 | 檢查 GPIO 腳位、電源是否足夠（馬達需獨立供電） |
| ROS2 橋接無回應 | ping ESP32 IP，確認同網段 |
| 速度不對 | 調整 `wheel_separation` 和 `wheel_radius` 參數 |
