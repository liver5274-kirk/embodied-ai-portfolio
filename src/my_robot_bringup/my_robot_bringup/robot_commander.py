#!/usr/bin/env python3
"""
ROS2 第一課：Publisher（發送者）
發送 /cmd_vel 指令控制機器人移動

概念對應：
  Node    = 這個 Python 程式
  Topic   = /cmd_vel（機器人聽從的移動指令通道）
  Message = Twist（包含線速度 + 角速度）

執行方式（ROS2 裝好後）：
  cd ~/ros2_ws
  colcon build --packages-select my_robot_bringup
  source install/setup.bash
  ros2 run my_robot_bringup robot_commander
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class RobotCommander(Node):
    """倉庫搬運機器人指揮官 — 發送移動指令"""

    def __init__(self):
        super().__init__('robot_commander')  # Node 名稱
        # 建立 Publisher: 往 /cmd_vel topic 發送 Twist 訊息
        self.publisher = self.create_publisher(
            Twist,      # 訊息類型
            '/cmd_vel',  # Topic 名稱
            10,          # Queue size
        )
        self.get_logger().info('🤖 機器人指揮官已上線！')

    def move_forward(self, speed=0.2, duration=2.0):
        """向前移動"""
        msg = Twist()
        msg.linear.x = speed   # 線速度（前進）
        msg.angular.z = 0.0    # 角速度（不轉彎）
        self._publish_for(msg, duration)

    def turn_left(self, speed=0.5, duration=1.57):
        """左轉 90 度"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = speed  # 角速度（左轉）
        self._publish_for(msg, duration)

    def turn_right(self, speed=0.5, duration=1.57):
        """右轉 90 度"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = -speed
        self._publish_for(msg, duration)

    def stop(self):
        """停止"""
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher.publish(msg)
        self.get_logger().info('🛑 停止')

    def _publish_for(self, msg, duration):
        """持續發送指令一段時間"""
        end_time = time.time() + duration
        self.get_logger().info(
            f'📤 發送指令: linear.x={msg.linear.x:.2f}, '
            f'angular.z={msg.angular.z:.2f} ({duration}s)'
        )
        while time.time() < end_time:
            self.publisher.publish(msg)
            time.sleep(0.1)  # 10 Hz

    def go_to_zone(self, zone: str):
        """
        簡易倉庫導航：根據區域名稱移動
        這是「AI 倉庫搬運機器人」的核心邏輯
        """
        zone_map = {
            'A': [('forward', 1.0), ('turn_left', 0.5)],
            'B': [('forward', 2.0), ('turn_right', 0.5)],
            'C': [('turn_right', 0.5), ('forward', 1.5)],
            'home': [('turn_left', 1.0), ('forward', 2.0)],
        }

        if zone not in zone_map:
            self.get_logger().warn(f'⚠️  未知區域: {zone}')
            return

        self.get_logger().info(f'🚀 導航到 {zone} 區...')
        for action, param in zone_map[zone]:
            if action == 'forward':
                self.move_forward(speed=0.2, duration=param)
            elif action == 'turn_left':
                self.turn_left(speed=0.5, duration=param)
            elif action == 'turn_right':
                self.turn_right(speed=0.5, duration=param)
            time.sleep(0.3)  # 指令間隔

        self.stop()
        self.get_logger().info(f'✅ 已到達 {zone} 區！')


def main():
    rclpy.init()
    commander = RobotCommander()

    # ===== 你的倉庫任務 =====
    # 改這行就可以測試不同路徑！
    TARGET_ZONE = 'A'

    commander.get_logger().info(f'🎯 任務: 前往 {TARGET_ZONE} 區取貨')
    commander.go_to_zone(TARGET_ZONE)

    # 任務完成
    commander.get_logger().info('📦 取貨完成！返回 home...')
    commander.go_to_zone('home')

    commander.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
