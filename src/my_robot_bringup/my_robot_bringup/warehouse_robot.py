#!/usr/bin/env python3
"""
ROS2 第三課：AI 倉庫搬運機器人 — 整合 Node + Topic + 任務邏輯

這個 Node 結合了 Publisher + Subscriber：
  1. 聆聽 /task_request（人類輸入的任務）
  2. 判斷目標區域
  3. 發送 /cmd_vel 移動指令
  4. 聆聽 /robot_status 確認到達

這是你第一個 Embodied AI 作品的核心邏輯！
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import time


class WarehouseRobot(Node):
    """
    AI 倉庫搬運機器人

    Subscribers:  /task_request (String) — 接收任務
    Publishers:   /cmd_vel (Twist) — 發送移動指令
                  /robot_status (String) — 回報狀態
    """

    def __init__(self):
        super().__init__('warehouse_robot')

        # === Subscriber: 聽取任務 ===
        self.task_sub = self.create_subscription(
            String,
            '/task_request',
            self.on_task_received,
            10,
        )

        # === Publisher: 發送移動指令 ===
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # === Publisher: 回報狀態 ===
        self.status_pub = self.create_publisher(String, '/robot_status', 10)

        # === 倉庫地圖 ===
        self.zones = {
            'A': {'x': 1.0, 'y': 1.0, 'desc': '電子零件區'},
            'B': {'x': 2.0, 'y': -1.0, 'desc': '機械零件區'},
            'C': {'x': -1.0, 'y': 2.0, 'desc': '包裝材料區'},
            'home': {'x': 0.0, 'y': 0.0, 'desc': '基地'},
        }

        # 機器人狀態
        self.current_pos = {'x': 0.0, 'y': 0.0}
        self.current_zone = 'home'
        self.has_package = False

        self.get_logger().info('🏭 AI 倉庫搬運機器人已啟動！')
        self.get_logger().info(f'   已知區域: {list(self.zones.keys())}')

    def on_task_received(self, msg: String):
        """收到任務指令（例如「去 A 區取貨」）"""
        task = msg.data
        self.get_logger().info(f'📋 收到任務: {task}')

        # === AI 判斷邏輯（簡易版，之後可換 LLM） ===
        target_zone = self._parse_task(task)
        if target_zone is None:
            self._report(f'無法理解任務: {task}')
            return

        if target_zone not in self.zones:
            self._report(f'未知區域: {target_zone}')
            return

        # === 執行任務 ===
        self._report(f'🚀 前往 {target_zone} 區（{self.zones[target_zone]["desc"]}）')
        self._navigate_to(target_zone)
        self._report(f'📦 在 {target_zone} 區取貨完成')
        self.has_package = True

        # 返回 home
        self._report(f'🏠 返回基地...')
        self._navigate_to('home')
        self._report(f'✅ 任務完成！貨物已送達基地')

    def _parse_task(self, task: str) -> str:
        """簡易任務解析（之後可用 LLM 取代）"""
        task_upper = task.upper()
        for zone in self.zones:
            if zone in task_upper:
                return zone
        # 關鍵字匹配
        kw_map = {
            '電子': 'A', '零件': 'A', '晶片': 'A',
            '機械': 'B', '馬達': 'B', '齒輪': 'B',
            '包裝': 'C', '紙箱': 'C', '材料': 'C',
        }
        for kw, zone in kw_map.items():
            if kw in task:
                return zone
        return None

    def _navigate_to(self, zone: str):
        """導航到目標區域（簡易版 — 之後可換路徑規劃）"""
        target = self.zones[zone]
        dx = target['x'] - self.current_pos['x']
        dy = target['y'] - self.current_pos['y']

        # 計算方向和距離
        import math
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)

        self.get_logger().info(
            f'   🧭 導航: 距離={distance:.2f}m, 角度={math.degrees(target_angle):.0f}°'
        )

        # 轉向目標
        self._rotate(target_angle)

        # 前進
        self._move_forward(distance)

        # 更新位置
        self.current_pos = {'x': target['x'], 'y': target['y']}
        self.current_zone = zone

    def _rotate(self, target_angle: float, speed: float = 0.5):
        """原地旋轉到目標角度"""
        duration = abs(target_angle) / speed
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = speed if target_angle > 0 else -speed

        end = time.time() + duration
        while time.time() < end:
            self.cmd_pub.publish(msg)
            time.sleep(0.1)

        # 停止
        msg.angular.z = 0.0
        self.cmd_pub.publish(msg)

    def _move_forward(self, distance: float, speed: float = 0.2):
        """直線前進"""
        duration = distance / speed
        msg = Twist()
        msg.linear.x = speed
        msg.angular.z = 0.0

        end = time.time() + duration
        while time.time() < end:
            self.cmd_pub.publish(msg)
            time.sleep(0.1)

        # 停止
        msg.linear.x = 0.0
        self.cmd_pub.publish(msg)

    def _report(self, message: str):
        """回報狀態"""
        msg = String()
        msg.data = message
        self.status_pub.publish(msg)
        self.get_logger().info(f'📢 {message}')


def main():
    rclpy.init()
    robot = WarehouseRobot()
    try:
        rclpy.spin(robot)
    except KeyboardInterrupt:
        print('\n👋 倉庫機器人關閉')
    finally:
        robot.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
