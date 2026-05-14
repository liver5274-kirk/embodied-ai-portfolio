#!/bin/bash
# ==========================================
# 🎬 Embodied AI Demo 錄製腳本
# 錄製 AI 倉庫搬運機器人 + TurtleBot3 導航
# 
# 用法: bash demo_record.sh
# 輸出: ~/ros2_ws/demo_output/
# ==========================================
set -e

DEMO_DIR="$HOME/ros2_ws/demo_output"
mkdir -p "$DEMO_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

export PATH="/usr/bin:$HOME/ros2_ws/install/my_robot_bringup/bin:$PATH"
export DISPLAY="${DISPLAY:-:0}"
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/local_setup.bash

# 確保 symlinks
mkdir -p ~/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup
for exe in ~/ros2_ws/install/my_robot_bringup/bin/*; do
    name=$(basename "$exe")
    [ -e "$HOME/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup/$name" ] || \
        ln -sf "../../bin/$name" "$HOME/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup/$name"
done

echo "========================================="
echo "🎬 Embodied AI 作品集 Demo 錄製"
echo "========================================="
echo ""
echo "選擇 Demo 模式："
echo "  1) AI 倉庫搬運機器人（終端機錄影）"
echo "  2) TurtleBot3 Gazebo 導航（螢幕錄影）"
echo "  3) 全部錄製"
echo "  4) 生成作品集 README"
echo ""
read -p "請選擇 [1-4]: " MODE

# ========== Demo 1: AI 倉庫機器人 ==========
demo1_warehouse() {
    echo ""
    echo "🏭 Demo 1: AI 倉庫搬運機器人"
    echo "=============================="
    
    LOGFILE="$DEMO_DIR/warehouse_demo_${TIMESTAMP}.log"
    
    # 啟動機器人（背景）
    ros2 run my_robot_bringup warehouse_robot_ai &
    ROBOT_PID=$!
    sleep 2
    
    echo "" | tee -a "$LOGFILE"
    echo "=== ROS2 神經系統 ===" | tee -a "$LOGFILE"
    ros2 node list 2>&1 | tee -a "$LOGFILE"
    ros2 topic list 2>&1 | tee -a "$LOGFILE"
    
    echo "" | tee -a "$LOGFILE"
    echo "=== Demo 1: 自然語言任務 ===" | tee -a "$LOGFILE"
    
    # 任務 1
    echo "" | tee -a "$LOGFILE"
    echo "📋 任務: 「幫我去 A 區拿電子零件」" | tee -a "$LOGFILE"
    timeout 5 ros2 run my_robot_bringup task_sender_ai "幫我去 A 區拿電子零件" 2>&1 | tee -a "$LOGFILE"
    sleep 2
    
    # 查看狀態
    echo "" | tee -a "$LOGFILE"
    echo "📊 機器人狀態:" | tee -a "$LOGFILE"
    timeout 2 ros2 topic echo /robot_status --once 2>&1 | tee -a "$LOGFILE" || echo "(任務執行中...)" | tee -a "$LOGFILE"
    
    # 任務 2
    echo "" | tee -a "$LOGFILE"
    echo "📋 任務: 「把機械零件從 B 區搬到包裝區 C」" | tee -a "$LOGFILE"
    timeout 10 ros2 run my_robot_bringup task_sender_ai "把機械零件從 B 區搬到包裝區 C" 2>&1 | tee -a "$LOGFILE"
    sleep 2
    
    # 任務 3 - 真正自然語言
    echo "" | tee -a "$LOGFILE"
    echo "📋 任務: 「我需要一些紙箱，可以幫我拿嗎？」" | tee -a "$LOGFILE"
    timeout 10 ros2 run my_robot_bringup task_sender_ai "我需要一些紙箱，可以幫我拿嗎？" 2>&1 | tee -a "$LOGFILE"
    sleep 2
    
    # 清理
    kill $ROBOT_PID 2>/dev/null
    wait $ROBOT_PID 2>/dev/null
    
    echo "" | tee -a "$LOGFILE"
    echo "✅ Demo 1 錄製完成！" | tee -a "$LOGFILE"
    echo "   記錄檔: $LOGFILE" | tee -a "$LOGFILE"
}

# ========== Demo 2: TurtleBot3 Gazebo ==========
demo2_turtlebot3() {
    echo ""
    echo "🐢 Demo 2: TurtleBot3 Gazebo 自主導航"
    echo "======================================"
    
    VIDEOFILE="$DEMO_DIR/turtlebot3_demo_${TIMESTAMP}.mp4"
    LOGFILE="$DEMO_DIR/turtlebot3_demo_${TIMESTAMP}.log"
    
    # 檢查 ffmpeg
    if ! command -v ffmpeg &>/dev/null; then
        echo "⚠️ ffmpeg 未安裝，只記錄 terminal log"
        echo "   安裝: sudo apt install -y ffmpeg"
    fi
    
    export TURTLEBOT3_MODEL=waffle
    
    echo "🚀 啟動 Gazebo 模擬..." | tee -a "$LOGFILE"
    ros2 launch turtlebot3_gazebo empty_world.launch.py &
    GAZEBO_PID=$!
    
    echo "⏳ 等待 Gazebo 初始化（15 秒）..."
    sleep 15
    
    echo "" | tee -a "$LOGFILE"
    echo "=== 機器人神經系統 ===" | tee -a "$LOGFILE"
    ros2 node list 2>&1 | tee -a "$LOGFILE"
    echo "" | tee -a "$LOGFILE"
    ros2 topic list 2>&1 | tee -a "$LOGFILE"
    
    echo "" | tee -a "$LOGFILE"
    echo "=== 傳送移動指令 ===" | tee -a "$LOGFILE"
    for i in 1 2 3; do
        echo "🔄 移動步驟 $i..." | tee -a "$LOGFILE"
        ros2 topic pub --once /cmd_vel geometry_msgs/msg/TwistStamped \
            "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''}, twist: {linear: {x: 0.3}, angular: {z: 0.5}}}" 2>&1 | tee -a "$LOGFILE"
        sleep 1
        
        echo "📍 位置:" | tee -a "$LOGFILE"
        timeout 1 ros2 topic echo /odom --once 2>&1 | grep -A3 position | tee -a "$LOGFILE"
    done
    
    echo "" | tee -a "$LOGFILE"
    echo "=== 感測器數據 ===" | tee -a "$LOGFILE"
    echo "🔍 LiDAR 掃描 (前 3 個值):" | tee -a "$LOGFILE"
    timeout 1 ros2 topic echo /scan --once 2>&1 | grep ranges | head -1 | tee -a "$LOGFILE"
    
    # 清理
    kill $GAZEBO_PID 2>/dev/null
    wait $GAZEBO_PID 2>/dev/null
    
    echo "" | tee -a "$LOGFILE"
    echo "✅ Demo 2 錄製完成！" | tee -a "$LOGFILE"
    echo "   記錄檔: $LOGFILE"
}

# ========== Demo 3: 全部 ==========
demo3_all() {
    demo1_warehouse
    echo ""
    echo "========================================="
    demo2_turtlebot3
}

# ========== 生成作品集 README ==========
demo4_readme() {
    README="$DEMO_DIR/PORTFOLIO.md"
    cat > "$README" << 'EOF'
# 🤖 Embodied AI 作品集 — AI 倉庫搬運機器人

## 專案概述

使用 **ROS2 Jazzy** 開發的 AI 倉庫搬運機器人，支援自然語言指令，在物理模擬器中自主導航與搬運。

```
使用者：「把機械零件從 B 區搬到包裝區」
           ↓
    AI 解析 (Gemini + 關鍵字)
           ↓
    ROS2 /cmd_vel 導航
           ↓
    Gazebo 物理模擬
```

## 技術棧

| 層級 | 技術 |
|------|------|
| 🤖 AI 層 | Google Gemini (LLM) + 關鍵字匹配 |
| 🧠 控制層 | ROS2 Jazzy (Node / Topic / Message) |
| 🏃 模擬層 | Gazebo + TurtleBot3 |
| 🐍 語言 | Python 3.12 |

## 核心概念展示

### ROS2 神經系統
- **Node**: warehouse_robot, task_sender, gazebo
- **Topic**: /cmd_vel (移動), /task_request (任務), /robot_status (狀態)
- **Message**: Twist, String, Odometry, LaserScan

### AI 任務解析
- 自然語言輸入 → 結構化導航指令
- 關鍵字匹配 + Gemini API 雙層解析
- 倉庫區域地圖：A(電子)、B(機械)、C(包裝)、home(基地)

## 執行方式

```bash
# 設定環境
source ~/ros2_ws/ros2_env.sh
export TURTLEBOT3_MODEL=waffle

# AI 倉庫機器人
ros2 run my_robot_bringup warehouse_robot_ai

# 發送自然語言任務
ros2 run my_robot_bringup task_sender_ai "去 A 區取貨，送到 C 區"

# TurtleBot3 Gazebo 模擬
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

## Demo 影片

- [AI 倉庫機器人 Demo](demo_output/)
- [TurtleBot3 導航 Demo](demo_output/)

## 學習歷程

1. Phase 1: PyBullet 機器手臂 Pick & Place
2. Phase 2: ROS2 基礎概念 (Node/Topic/Message)
3. Phase 3: TurtleBot3 Gazebo 模擬
4. Phase 4: AI 自然語言整合
5. 下一步: 真實硬體部署 (ESP32 + 伺服馬達)
EOF

    echo "✅ 作品集 README 已生成: $README"
    cat "$README"
}

# ========== 執行選擇的模式 ==========
case $MODE in
    1) demo1_warehouse ;;
    2) demo2_turtlebot3 ;;
    3) demo3_all ;;
    4) demo4_readme ;;
    *) echo "無效選擇" ;;
esac

echo ""
echo "========================================="
echo "🎉 全部完成！輸出目錄: $DEMO_DIR/"
ls -la "$DEMO_DIR/"
