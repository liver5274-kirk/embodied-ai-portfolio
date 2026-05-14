#!/bin/bash
# =============================================
# Embodied AI 快速設定腳本
# 一鍵設定 ROS2 + 倉庫機器人專案
# =============================================
set -e

echo "🤖 Embodied AI 環境設定中..."

# === ROS2 環境 ===
if [ -f /opt/ros/jazzy/setup.bash ]; then
    source /opt/ros/jazzy/setup.bash
    echo "✅ ROS2 Jazzy 已安裝"
else
    echo "❌ ROS2 Jazzy 未安裝，請先執行: sudo apt install ros-jazzy-desktop"
    exit 1
fi

# === 建立工作空間 ===
WS=~/ros2_ws
mkdir -p $WS/src

# === 安裝依賴 ===
echo "📦 安裝 Python 依賴..."
sudo apt install -y python3-colcon-common-extensions python3-rosdep 2>/dev/null || true

# === 初始化 rosdep ===
if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then
    sudo rosdep init 2>/dev/null || true
fi
rosdep update 2>/dev/null || true

# === 編譯 ===
echo "🔨 編譯工作空間..."
cd $WS
colcon build --symlink-install 2>&1 | tail -5

echo ""
echo "======================================="
echo "🏆 設定完成！"
echo "======================================="
echo ""
echo "執行方式："
echo "  1. source ~/ros2_ws/install/setup.bash"
echo "  2. ros2 run my_robot_bringup warehouse_robot"
echo "     (另一個 terminal)"
echo "  3. ros2 run my_robot_bringup task_sender '去 A 區取貨'"
echo ""
echo "ROS2 常用指令："
echo "  ros2 topic list          — 查看所有 topic"
echo "  ros2 node list           — 查看所有 node"
echo "  ros2 topic echo /cmd_vel — 監聽移動指令"
echo "  ros2 run turtlesim turtlesim_node — 烏龜範例"
echo ""
