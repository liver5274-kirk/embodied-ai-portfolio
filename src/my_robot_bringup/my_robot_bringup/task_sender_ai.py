#!/usr/bin/env python3
"""
AI 任務發送器 — 發送自然語言指令給倉庫機器人
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AITaskSender(Node):
    def __init__(self):
        super().__init__('ai_task_sender')
        self.pub = self.create_publisher(String, '/task_request', 10)
        self.get_logger().info('📮 AI 任務發送器就緒')

    def send(self, text: str):
        msg = String()
        msg.data = text
        self.pub.publish(msg)
        self.get_logger().info(f'📤 發送任務: "{text}"')


def main():
    rclpy.init()
    sender = AITaskSender()

    import sys
    task = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else '把電子零件從A區搬到包裝區'
    sender.send(task)

    import time
    time.sleep(0.5)
    sender.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
