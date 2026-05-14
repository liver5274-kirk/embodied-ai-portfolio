#!/bin/bash
# ==========================================
# AI 倉庫搬運機器人 — 一鍵啟動腳本
# ==========================================
# 用法:
#   Terminal 1: bash run_warehouse.sh
#   Terminal 2: bash run_warehouse.sh send "去 A 區取貨"
# ==========================================
set -e

# 強制使用系統 Python 3.12（ROS2 Jazzy 需要）
export PATH="/usr/bin:$HOME/ros2_ws/install/my_robot_bringup/bin:$PATH"
export DISPLAY="${DISPLAY:-:0}"

# ROS2 環境
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/local_setup.bash

# 確保 Python 找得到我們的套件
SITE_PACKAGES="$HOME/ros2_ws/install/my_robot_bringup/lib/python3.12/site-packages"
export PYTHONPATH="$SITE_PACKAGES:$HOME/ros2_ws/build/my_robot_bringup:$PYTHONPATH"

if [ "$1" = "send" ]; then
    # === 任務發送模式 ===
    TASK="${2:-去 A 區取貨}"
    echo "📤 發送任務: $TASK"
    /usr/bin/python3.12 -c "
import sys
sys.path.insert(0, '$HOME/ros2_ws/build/my_robot_bringup')
import rclpy
from my_robot_bringup.task_sender import TaskSender

rclpy.init()
sender = TaskSender()
sender.send('$TASK')
import time; time.sleep(0.5)
sender.destroy_node()
rclpy.shutdown()
print('✅ 任務已發送！')
"
elif [ "$1" = "cmd" ]; then
    # === 直接發送移動指令 ===
    echo "🚀 發送 /cmd_vel 指令..."
    ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}"
else
    # === 機器人模式（持續聆聽任務） ===
    echo "🏭 AI 倉庫搬運機器人啟動中..."
    echo "   可用指令: ros2 topic echo /robot_status"
    echo "   發送任務: bash run_warehouse.sh send '去 B 區取貨'"
    echo ""
    /usr/bin/python3.12 -c "
import sys
sys.path.insert(0, '$HOME/ros2_ws/build/my_robot_bringup')
import rclpy
from my_robot_bringup.warehouse_robot import main
try:
    main()
except KeyboardInterrupt:
    print('\n👋 倉庫機器人關閉')
"
fi
