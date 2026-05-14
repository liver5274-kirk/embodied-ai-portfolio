#!/bin/bash
# ==========================================
# ROS2 Jazzy 啟動包裝腳本
# 解決 Python 3.11 (Hermes venv) vs 3.12 (ROS2) 衝突
# ==========================================
# 使用方式:
#   source ros2_env.sh              # 設定環境
#   ros2 run turtlesim turtlesim_node  # 跑任何 ROS2 指令
# ==========================================

# 強制使用系統 Python 3.12（不是 Hermes venv 的 3.11）
export PATH="/usr/bin:$PATH"
export DISPLAY="${DISPLAY:-:0}"

# ROS2 環境
source /opt/ros/jazzy/setup.bash

# 工作空間（如果有）
if [ -f ~/ros2_ws/install/local_setup.bash ]; then
    source ~/ros2_ws/install/local_setup.bash
fi

# Python 路徑修正（確保我們的套件能找到）
export PYTHONPATH="$HOME/ros2_ws/src/my_robot_bringup:$PYTHONPATH"

# 修復 ament_python symlinks（讓 ros2 run 找得到執行檔）
if [ -d "$HOME/ros2_ws/install/my_robot_bringup/bin" ]; then
    mkdir -p "$HOME/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup"
    for exe in "$HOME/ros2_ws/install/my_robot_bringup/bin/"*; do
        name=$(basename "$exe")
        [ -e "$HOME/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup/$name" ] || \
            ln -sf "../../bin/$name" "$HOME/ros2_ws/install/my_robot_bringup/lib/my_robot_bringup/$name"
    done
fi

echo "🤖 ROS2 Jazzy 環境已載入"
echo "   Python: $(/usr/bin/python3.12 --version)"
echo "   DISPLAY: $DISPLAY"
echo ""
echo "試試看:"
echo "  ros2 run turtlesim turtlesim_node"
echo "  ros2 topic list"
echo "  ros2 node list"
