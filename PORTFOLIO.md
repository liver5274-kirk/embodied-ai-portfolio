# 🤖 Embodied AI 作品集 — AI 倉庫搬運機器人

> **一句話總結**：用自然語言指揮機器人在 3D 模擬世界中自主導航搬貨 — ROS2 + Gemini AI + Gazebo 完整整合

---

## 📋 專案總覽

| 項目 | 內容 |
|------|------|
| **專案類型** | Embodied AI / Robotics / LLM 整合 |
| **開發時間** | 2026.05（2 天快速原型） |
| **技術棧** | ROS2 Jazzy + Python 3.12 + Google Gemini + Gazebo |
| **原始碼** | [github.com/liver5274-kirk/embodied-ai-portfolio](https://github.com/liver5274-kirk/embodied-ai-portfolio) |
| **Demo 影片** | `bash demo_record.sh`（一鍵錄製） |

---

## 🎯 這個專案解決什麼問題？

傳統倉庫機器人需要**工程師寫死導航路徑**，任何變動都要重新編程。

這個專案展示：**任何人都能用自然語言指揮機器人**，AI 自動理解意圖並轉換為 ROS2 導航指令。

```
「把機械零件從 B 區搬到包裝區」
「我需要一些紙箱」
「幫我去 A 區拿電子零件」
         ↓
   AI 理解意圖 → 結構化指令 → 機器人執行
```

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────┐
│                    使用者輸入（自然語言）                    │
│            「把機械零件搬到包裝材料區」                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   🧠 AI 層（雙層解析）                      │
│  ┌─────────────────┐    ┌──────────────────────┐        │
│  │ 關鍵字匹配 (0ms)  │ ←→ │ Google Gemini API    │        │
│  │ 機械→B, 包裝→C   │    │ 複雜語意理解 + 推理   │        │
│  └─────────────────┘    └──────────────────────┘        │
│              輸出: {from: "B", to: "C", item: "機械零件"} │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  🧠 ROS2 控制層                           │
│                                                         │
│  /task_request (String) ──→ warehouse_robot_ai (Node)   │
│                                  │                      │
│                           /cmd_vel (Twist)               │
│                                  │                      │
│                                  ▼                      │
│  /robot_status (String) ←──  機器人移動                  │
│                                                         │
│  其他 Topic: /odom, /scan, /imu, /camera, /tf           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  🏃 模擬 / 硬體層                          │
│                                                         │
│  ┌──────────────────┐   ┌──────────────────┐            │
│  │ Gazebo + TB3     │   │ ESP32 ROD 小車    │            │
│  │ (物理模擬)        │   │ (真實硬體)         │            │
│  └──────────────────┘   └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技術棧

### 核心框架
| 技術 | 版本 | 用途 |
|------|------|------|
| **ROS2** | Jazzy Jalisco | 機器人作業系統（Node / Topic / Message） |
| **Python** | 3.12 | 主要開發語言 |
| **Gazebo** | Ionic (Ignition) | 3D 物理模擬 |
| **Google Gemini** | 2.0 Flash | 自然語言理解 |
| **Ubuntu** | 24.04 LTS (WSL2) | 開發環境 |

### 關鍵依賴
```
rclpy          — ROS2 Python 客戶端
geometry_msgs  — Twist（速度指令）
std_msgs       — String（任務/狀態）
nav_msgs       — Odometry（里程計）
sensor_msgs    — LaserScan, Imu, Image
turtlebot3_*   — 機器人模型與模擬
```

---

## 📂 專案結構

```
embodied-ai-portfolio/
├── PORTFOLIO.md                   ← 這份文件
├── README.md                      ← 快速開始指南
│
├── ros2_env.sh                    ← 一鍵載入 ROS2 環境
├── run_warehouse.sh               ← 一鍵啟動倉庫機器人
├── demo_record.sh                 ← 一鍵錄製 Demo
├── setup.sh                       ← 自動安裝腳本
│
├── phase1_robot_arm.py            ← Phase 1: PyBullet 機器手臂
│
├── demo_output/                   ← Demo 影片與記錄
│
└── src/my_robot_bringup/          ← ROS2 套件
    ├── package.xml
    ├── setup.py
    └── my_robot_bringup/
        ├── warehouse_robot.py     ← 倉庫機器人 v1（基礎）
        ├── warehouse_robot_ai.py  ← AI 版（Gemini 整合）
        ├── task_sender.py         ← 任務發送器 v1
        ├── task_sender_ai.py      ← AI 任務發送器
        ├── robot_commander.py     ← Publisher 範例
        └── robot_driver.py        ← Subscriber 範例
```

---

## 🧪 核心概念展示

### 1. ROS2 神經系統

Embodied AI 的核心是機器人如何「感知→思考→行動」。ROS2 用三個概念實現：

| 概念 | 說明 | 本專案實例 |
|------|------|-----------|
| **Node** | 獨立運行的程式（機器人的器官） | `warehouse_robot_ai`, `task_sender_ai`, `gazebo` |
| **Topic** | Node 之間的通訊通道（神經元） | `/cmd_vel`（移動）, `/task_request`（任務） |
| **Message** | 通道傳遞的資料格式（神經訊號） | `Twist`（速度）, `String`（文字）, `LaserScan` |

```
[task_sender_ai]        [warehouse_robot_ai]         [gazebo]
      │                        │                         │
      │── /task_request ──────→│                         │
      │   (String)             │── /cmd_vel ────────────→│
      │                        │   (Twist)               │
      │                        │←── /odom ───────────────│
      │                        │   (Odometry)            │
      │←── /robot_status ──────│                         │
      │    (String)            │←── /scan ───────────────│
      │                        │   (LaserScan)           │
```

### 2. AI 任務解析（雙層設計）

```python
class TaskParser:
    def parse(self, text: str) -> dict:
        # Layer 1: 關鍵字匹配（0ms, 0 API cost）
        quick = self._keyword_parse(text)
        if quick['confidence'] > 0.8:
            return quick  # 「機械零件→B區」直接命中

        # Layer 2: Gemini API（複雜語意）
        return self._gemini_parse(text)
        # 「我需要一些紙箱」→ 推理出 C 區（包裝區）
```

**為什麼雙層？**
- 關鍵字匹配：零延遲、零成本、處理 80% 的常見指令
- Gemini API：處理「我需要紙箱」、「幫我拿東西」等模糊指令
- 容錯設計：API 失敗時自動降級為關鍵字匹配

### 3. 逆向運動學 (Inverse Kinematics)

Phase 1 展示了機器手臂的核心數學：給定目標座標 → 計算每個關節要轉多少度。

```python
# 給定: 方塊在 (1.0, 0.3, 0.65)
# 計算: 7 個關節各要轉幾度
HOME_POSE  = [0, -0.4, 0, -2.0, 0, 1.5, 0]     # 站立
GRASP_POSE = [0, -1.0, 0, -2.6, 0, 1.0, 1.0]    # 抓取
PLACE_POSE = [0.8, -0.8, 0.3, -2.4, 0.4, 1.0, 0.5]  # 放置
```

---

## 🚀 快速開始

### 環境需求
- Ubuntu 24.04（或 WSL2 + WSLg）
- ROS2 Jazzy Desktop
- Python 3.12
- 選用：Google Gemini API Key

### 一鍵啟動

```bash
# 1. 複製專案
git clone https://github.com/liver5274-kirk/embodied-ai-portfolio.git
cd embodied-ai-portfolio

# 2. 安裝依賴
sudo apt install -y ros-jazzy-desktop ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-gazebo

# 3. 編譯
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install

# 4. 載入環境
source ros2_env.sh
```

### 執行 Demo

```bash
# === Demo A: AI 倉庫機器人 ===
# Terminal 1
ros2 run my_robot_bringup warehouse_robot_ai

# Terminal 2
ros2 run my_robot_bringup task_sender_ai "把機械零件搬到包裝材料區"

# === Demo B: TurtleBot3 模擬 ===
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo empty_world.launch.py

# === Demo C: PyBullet 機器手臂 ===
python3 phase1_robot_arm.py
```

### 錄製 Demo 影片
```bash
bash demo_record.sh   # 互動式選單
```

---

## 🎬 Demo 展示

### Demo A：AI 倉庫搬運機器人
```
輸入: 「把機械零件搬到包裝材料區」
AI 解析: from=B(機械), to=C(包裝), confidence=90%
執行:
  1. home → B 區取貨 (導航距離 2.2m)
  2. B 區 → C 區送貨 (導航距離 3.0m)
  3. C 區 → home 返回 (導航距離 2.2m)
輸出: /robot_status 即時回報每一步
```

### Demo B：TurtleBot3 自主導航
```
啟動: Gazebo 3D 模擬 + TurtleBot3 waffle 模型
感測器: LiDAR 360° 雷射掃描 + IMU + RGB 相機
控制: /cmd_vel (TwistStamped) 移動指令
監控: /odom 即時位置, /scan 障礙物距離
```

### Demo C：機器手臂 Pick & Place
```
模擬: Franka Panda 7-DOF 機械手臂
任務: 從桌上抓取方塊 → 移動到目標位置 → 放下
輸出: 7 張關鍵幀 PNG 圖片
```

---

## 📈 學習歷程

| 階段 | 內容 | 學到什麼 | 花費 |
|------|------|---------|------|
| **Phase 1** | PyBullet 機器手臂 | 運動學、自由度、物理模擬 | NT$0 |
| **Phase 2** | ROS2 基礎 | Node / Topic / Message 神經系統 | NT$0 |
| **Phase 3** | TurtleBot3 + Gazebo | 3D 模擬、感測器、導航 | NT$0 |
| **Phase 4** | Gemini AI 整合 | LLM + 機器人、雙層解析架構 | NT$0 (免費額度) |
| **Phase 5** | ESP32 真實硬體 | 實體機器人控制（進行中） | NT$500 |
| **Phase 6** | Isaac Sim 高階模擬 | GPU 加速、數位孿生（規劃中） | — |

---

## 💼 潛在應用場景

| 場景 | 如何應用本專案 |
|------|---------------|
| 🏭 智慧倉儲 | 自然語言指揮 AGV 搬貨 |
| 🏥 醫院物流 | 「把藥品送到 3 樓護理站」 |
| 🏨 飯店服務 | 「送毛巾到 502 房」 |
| 🎓 教育訓練 | ROS2 + AI 教學平台 |
| 🔬 研究原型 | 快速驗證 Embodied AI 概念 |

---

## 🔜 下一步計畫

- [ ] ESP32 ROD 小車真實硬體部署
- [ ] 加入 SLAM 即時地圖建構
- [ ] Web 前端（Streamlit）遠端控制
- [ ] 多機器人協作（多 Node 通訊）
- [ ] Isaac Sim 高精度模擬遷移

---

## 📞 聯絡方式

- **GitHub**: [liver5274-kirk](https://github.com/liver5274-kirk)
- **專案位置**: [embodied-ai-portfolio](https://github.com/liver5274-kirk/embodied-ai-portfolio)

---

*Built with ROS2 Jazzy, Google Gemini, Gazebo, and PyBullet. May 2026.*
