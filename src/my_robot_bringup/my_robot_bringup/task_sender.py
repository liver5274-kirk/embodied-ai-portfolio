#!/usr/bin/env python3
"""
發送任務給 AI 倉庫機器人
模擬「使用者輸入 → AI 理解 → 機器人執行」
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TaskSender(Node):
    def __init__(self):
        super().__init__('task_sender')
        self.pub = self.create_publisher(String, '/task_request', 10)
        self.get_logger().info('📮 任務發送器就緒')

    def send(self, text: str):
        msg = String()
        msg.data = text
        self.pub.publish(msg)
        self.get_logger().info(f'📤 發送任務: {text}')


def main():
    rclpy.init()
    sender = TaskSender()

    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else '去 A 區取貨'
    sender.send(task)

    # 等一下讓 warehouse_robot 處理
    import time
    time.sleep(5)  # 給機器人時間執行

    sender.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
