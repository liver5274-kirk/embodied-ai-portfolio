#!/usr/bin/env python3
"""
🏭 AI 倉庫搬運機器人 v2.0 — 接 Gemini 做自然語言理解

概念：
  使用者說「把電子零件搬到包裝區」
      ↓
  Gemini AI 解析意圖 → {from: A, to: C, item: 電子零件}
      ↓
  ROS2 發送 /cmd_vel 導航

執行：
  ros2 run my_robot_bringup warehouse_robot_ai
  ros2 run my_robot_bringup task_sender_ai "把機械零件送去包裝區"
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import time
import json
import urllib.request
import os


# ============ AI 任務解析器（Gemini） ============

class TaskParser:
    """用 Google Gemini 將自然語言轉為機器人指令"""

    ZONES = {
        'A': {'x': 1.0, 'y': 1.0, 'desc': '電子零件區', 'keywords': ['電子', '晶片', 'IC', '電路板', 'A區']},
        'B': {'x': 2.0, 'y': -1.0, 'desc': '機械零件區', 'keywords': ['機械', '馬達', '齒輪', '螺絲', 'B區']},
        'C': {'x': -1.0, 'y': 2.0, 'desc': '包裝材料區', 'keywords': ['包裝', '紙箱', '緩衝', '膠帶', 'C區']},
        'home': {'x': 0.0, 'y': 0.0, 'desc': '基地', 'keywords': ['基地', 'home', '回去', '返回']},
    }

    def __init__(self):
        # 從環境變數讀取 API key
        self.api_key = os.environ.get('GOOGLE_API_KEY', '')
        if not self.api_key:
            # 嘗試從 bashrc 讀取
            import subprocess
            result = subprocess.run(
                ['bash', '-c', 'source ~/.bashrc 2>/dev/null; echo $GOOGLE_API_KEY'],
                capture_output=True, text=True
            )
            self.api_key = result.stdout.strip()

    def parse(self, text: str) -> dict:
        """解析自然語言任務 → {from_zone, to_zone, item}"""
        # 先用關鍵字匹配（快速路徑，不花 API 額度）
        quick = self._keyword_parse(text)
        if quick.get('confidence', 0) > 0.8:
            return quick

        # 關鍵字不夠 → 呼叫 Gemini
        if self.api_key:
            return self._gemini_parse(text)

        # Fallback: 回傳關鍵字結果
        return quick

    def _keyword_parse(self, text: str) -> dict:
        """關鍵字匹配解析"""
        text_upper = text.upper()
        matched = []

        for zone_id, info in self.ZONES.items():
            for kw in info['keywords']:
                if kw.upper() in text_upper:
                    matched.append(zone_id)
                    break

        result = {'from_zone': None, 'to_zone': None, 'item': None, 'confidence': 0}

        if len(matched) >= 2:
            result['from_zone'] = matched[0]
            result['to_zone'] = matched[1]
            result['confidence'] = 0.9
        elif len(matched) == 1:
            # 只有一個區域 → 預設從 home 出發或送回 home
            if '去' in text or '前往' in text or '搬' in text:
                result['from_zone'] = 'home'
                result['to_zone'] = matched[0]
            else:
                result['from_zone'] = matched[0]
                result['to_zone'] = 'home'
            result['confidence'] = 0.6

        return result

    def _gemini_parse(self, text: str) -> dict:
        """用 Gemini 解析任務"""
        prompt = f"""你是倉庫機器人控制系統。解析使用者的自然語言指令，輸出 JSON。

倉庫地圖：
- A區：電子零件區（位置 x=1.0, y=1.0）
- B區：機械零件區（位置 x=2.0, y=-1.0）  
- C區：包裝材料區（位置 x=-1.0, y=2.0）
- home：基地（位置 x=0, y=0）

使用者指令：「{text}」

請輸出純 JSON（不要 markdown）：
{{"from_zone": "A", "to_zone": "C", "item": "電子零件", "confidence": 0.9}}"""

        try:
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}'
            data = json.dumps({
                'contents': [{'parts': [{'text': prompt}]}],
                'generationConfig': {'temperature': 0.0, 'maxOutputTokens': 100}
            }).encode()
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read())

            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            # 清理 markdown
            ai_text = ai_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(ai_text)
            parsed['confidence'] = parsed.get('confidence', 0.8)
            return parsed
        except Exception as e:
            print(f'⚠️ Gemini API 錯誤: {e}，使用關鍵字備援')
            return self._keyword_parse(text)


# ============ AI 倉庫機器人 ============

class AIWarehouseRobot(Node):
    """
    AI 倉庫搬運機器人 — 接 Gemini 理解自然語言
    """

    def __init__(self):
        super().__init__('ai_warehouse_robot')

        # Subscriber: 聽取自然語言任務
        self.task_sub = self.create_subscription(
            String, '/task_request', self.on_task_received, 10
        )

        # Publisher: 移動指令
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Publisher: 狀態回報
        self.status_pub = self.create_publisher(String, '/robot_status', 10)

        # AI 任務解析器
        self.parser = TaskParser()

        # 機器人狀態
        self.current_zone = 'home'
        self.current_pos = {'x': 0.0, 'y': 0.0}
        self.has_package = False

        self.get_logger().info('🤖 AI 倉庫搬運機器人 v2.0 已啟動！')
        self.get_logger().info(f'   Gemini API: {"已連接" if self.parser.api_key else "離線模式（關鍵字匹配）"}')
        self.get_logger().info(f'   已知區域: {list(self.parser.ZONES.keys())}')

    def on_task_received(self, msg: String):
        """收到自然語言任務"""
        task = msg.data
        self.get_logger().info(f'📋 收到任務: "{task}"')

        # === 🤖 AI 解析任務 ===
        plan = self.parser.parse(task)
        self.get_logger().info(
            f'🧠 AI 解析: from={plan["from_zone"]} → to={plan["to_zone"]}'
            f'  item={plan.get("item","?")} confidence={plan.get("confidence",0):.0%}'
        )

        from_zone = plan.get('from_zone')
        to_zone = plan.get('to_zone')

        if not from_zone or not to_zone:
            self._report(f'⚠️ 無法理解任務: "{task}"')
            return

        if from_zone not in self.parser.ZONES or to_zone not in self.parser.ZONES:
            self._report(f'⚠️ 未知區域: {from_zone} 或 {to_zone}')
            return

        # === 執行任務 ===
        from_info = self.parser.ZONES[from_zone]
        to_info = self.parser.ZONES[to_zone]

        self._report(f'🚀 前往 {from_zone} 區（{from_info["desc"]}）取貨')
        self._navigate_to(from_zone)

        self._report(f'📦 在 {from_zone} 區取得 {plan.get("item", "物品")}')
        self.has_package = True

        self._report(f'🚛 運送到 {to_zone} 區（{to_info["desc"]}）')
        self._navigate_to(to_zone)

        self._report(f'📦 已送達！')
        self.has_package = False

        self._report(f'🏠 返回基地')
        self._navigate_to('home')
        self._report(f'✅ 任務完成！')

    def _navigate_to(self, zone: str):
        """導航到目標區域"""
        import math
        target = self.parser.ZONES[zone]
        dx = target['x'] - self.current_pos['x']
        dy = target['y'] - self.current_pos['y']
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)

        self.get_logger().info(
            f'   🧭 導航到 {zone}: 距離={distance:.2f}m, 角度={math.degrees(target_angle):.0f}°'
        )

        # 轉向
        self._rotate(target_angle)
        # 前進
        self._move_forward(distance)

        self.current_pos = {'x': target['x'], 'y': target['y']}
        self.current_zone = zone

    def _rotate(self, angle: float, speed: float = 0.5):
        duration = abs(angle) / speed
        msg = Twist(); msg.angular.z = speed if angle > 0 else -speed
        end = time.time() + duration
        while time.time() < end:
            self.cmd_pub.publish(msg); time.sleep(0.1)
        self.cmd_pub.publish(Twist())

    def _move_forward(self, distance: float, speed: float = 0.2):
        duration = distance / speed
        msg = Twist(); msg.linear.x = speed
        end = time.time() + duration
        while time.time() < end:
            self.cmd_pub.publish(msg); time.sleep(0.1)
        self.cmd_pub.publish(Twist())

    def _report(self, message: str):
        msg = String(); msg.data = message
        self.status_pub.publish(msg)
        self.get_logger().info(f'📢 {message}')


def main():
    rclpy.init()
    robot = AIWarehouseRobot()
    try:
        rclpy.spin(robot)
    except KeyboardInterrupt:
        print('\n👋 AI 倉庫機器人關閉')
    finally:
        robot.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
