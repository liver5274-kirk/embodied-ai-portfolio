#!/usr/bin/env python3
"""
ESP32 ROD 小車橋接器 — ROS2 ↔ ESP32 WiFi
訂閱 /cmd_vel → 轉換為 ESP32 HTTP API 呼叫

執行:
  ros2 run esp32_bridge esp32_bridge --ros-args -p esp32_ip:=192.168.1.100
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import urllib.request
import json
import math


class ESP32Bridge(Node):
    """將 ROS2 /cmd_vel 指令橋接到 ESP32 小車"""

    def __init__(self):
        super().__init__('esp32_bridge')

        # 宣告參數
        self.declare_parameter('esp32_ip', '192.168.4.1')  # 預設 AP 模式
        self.declare_parameter('wheel_separation', 0.15)    # 輪距 (m)
        self.declare_parameter('wheel_radius', 0.03)        # 輪半徑 (m)
        self.declare_parameter('max_linear_speed', 0.5)     # 最大線速度
        self.declare_parameter('max_angular_speed', 1.5)    # 最大角速度

        self.esp32_ip = self.get_parameter('esp32_ip').value
        self.wheel_sep = self.get_parameter('wheel_separation').value
        self.wheel_rad = self.get_parameter('wheel_radius').value
        self.max_linear = self.get_parameter('max_linear_speed').value
        self.max_angular = self.get_parameter('max_angular_speed').value

        # Subscriber: /cmd_vel
        self.sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10,
        )

        self.get_logger().info(f'🔌 ESP32 橋接器啟動 → http://{self.esp32_ip}/motor')

    def cmd_callback(self, msg: Twist):
        """收到 /cmd_vel 指令 → 換算左右輪速度 → HTTP 發送"""
        # 差速驅動運動學（逆向）
        # v = 線速度, ω = 角速度
        v = msg.linear.x
        omega = msg.angular.z

        # 限制範圍
        v = max(-self.max_linear, min(self.max_linear, v))
        omega = max(-self.max_angular, min(self.max_angular, omega))

        # 左右輪速度 (rad/s → 常規化為 -1~1)
        v_left = (v - omega * self.wheel_sep / 2.0) / self.wheel_rad
        v_right = (v + omega * self.wheel_sep / 2.0) / self.wheel_rad

        # 常規化到 -1.0 ~ 1.0
        max_speed = max(abs(v_left), abs(v_right), 1.0)
        left_norm = v_left / max_speed
        right_norm = v_right / max_speed

        # 發送 HTTP 請求
        url = f'http://{self.esp32_ip}/motor?left={left_norm:.2f}&right={right_norm:.2f}'
        try:
            urllib.request.urlopen(url, timeout=1.0)
            self.get_logger().debug(
                f'📤 cmd_vel → L={left_norm:.2f} R={right_norm:.2f}'
            )
        except Exception as e:
            self.get_logger().warn(f'⚠️ ESP32 無回應: {e}')


def main():
    rclpy.init()
    bridge = ESP32Bridge()
    try:
        rclpy.spin(bridge)
    except KeyboardInterrupt:
        print('\n👋 ESP32 橋接器關閉')
    finally:
        bridge.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
