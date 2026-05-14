# 🤖 AI 倉庫搬運機器人 — 第一個 Embodied AI 作品

## 專案結構

```
ros2_ws/
├── src/my_robot_bringup/          # ROS2 套件
│   ├── my_robot_bringup/
│   │   ├── robot_commander.py     # 基礎 Publisher
│   │   ├── robot_driver.py        # 基礎 Subscriber
│   │   ├── warehouse_robot.py     # 🏭 AI 倉庫機器人（核心）
│   │   └── task_sender.py         # 任務發送器
│   ├── package.xml
│   └── setup.py
├── setup.sh                       # 一鍵安裝腳本
└── README.md
```

## 快速開始

### 1. 環境設定
```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 2. 啟動 AI 倉庫機器人
```bash
# Terminal 1: 啟動機器人大腦
ros2 run my_robot_bringup warehouse_robot

# Terminal 2: 發送任務
ros2 run my_robot_bringup task_sender '去 A 區取貨'
```

### 3. 查看 ROS2 神經系統
```bash
ros2 topic list          # 看到 /cmd_vel, /task_request, /robot_status
ros2 node list           # 看到 warehouse_robot, task_sender
ros2 topic echo /robot_status  # 即時看機器人狀態
```

## 學到的核心概念

| ROS2 概念 | 對應到 Embodied AI | 本專案中的角色 |
|-----------|-------------------|---------------|
| **Node** | 機器人的「器官」 | warehouse_robot, task_sender |
| **Topic** | 機器人的「神經通道」 | /cmd_vel（移動）, /task_request（任務） |
| **Message** | 神經傳遞的「訊號」 | Twist（速度）, String（文字） |
| **Publisher** | 發送訊號 | robot_commander 發送 /cmd_vel |
| **Subscriber** | 接收訊號 | robot_driver 接收 /cmd_vel |

## 進化路線

```
Phase 1 ✅  純 ROS2 指令（Python → /cmd_vel → 機器人移動）
Phase 2     加入 Gazebo 模擬（視覺化 + 物理）
Phase 3     加入 TurtleBot3（真實機器人模型）
Phase 4     加入 AI（LLM 理解自然語言指令）
Phase 5     真實硬體（ESP32 馬達控制）
```

## 指令清單

```bash
# 監聽 topic
ros2 topic echo /cmd_vel

# 手動發送指令
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}" -1

# 查看 topic 頻率
ros2 topic hz /cmd_vel

# 查看 node 資訊
ros2 node info /warehouse_robot

# 圖形化介面（需 GUI）
rqt_graph    # 看 node 之間的連接圖
```
