#!/usr/bin/env python3
"""
ROS2 第一課：Subscriber（接收者）
接收 /cmd_vel 指令，模擬機器人行為

Node    = robot_driver
Topic   = /cmd_vel（訂閱）
Message = Twist → 解析成實際移動

這是機器人的「神經末梢」— 接收大腦指令執行
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math


class RobotDriver(Node):
    """機器人驅動器 — 接收並執行移動指令"""

    def __init__(self):
        super().__init__('robot_driver')
        # 建立 Subscriber: 聆聽 /cmd_vel topic
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10,
        )
        # 模擬的機器人狀態
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0  # 朝向（弧度）

        self.get_logger().info('🔌 機器人驅動器已啟動，等待指令...')

    def cmd_callback(self, msg: Twist):
        """收到移動指令時觸發"""
        # 更新機器人位置（簡易運動模型）
        dt = 0.1  # 假設 10Hz
        self.x += msg.linear.x * math.cos(self.theta) * dt
        self.y += msg.linear.x * math.sin(self.theta) * dt
        self.theta += msg.angular.z * dt

        # 顯示狀態
        self.get_logger().info(
            f'📍 位置: ({self.x:.2f}, {self.y:.2f})  '
            f'朝向: {math.degrees(self.theta):.0f}°  '
            f'指令: v={msg.linear.x:.2f} ω={msg.angular.z:.2f}'
        )


def main():
    rclpy.init()
    driver = RobotDriver()
    try:
        rclpy.spin(driver)  # 持續聆聽
    except KeyboardInterrupt:
        driver.get_logger().info('👋 機器人驅動器離線')
    finally:
        driver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
