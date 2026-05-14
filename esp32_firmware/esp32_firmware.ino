/**
 * ESP32 ROD 小車 — WiFi 馬達控制韌體
 * 
 * 接線說明（L298N / L9110S 馬達驅動）：
 *   - 左馬達 ENA → GPIO 25,  IN1 → GPIO 26,  IN2 → GPIO 27
 *   - 右馬達 ENB → GPIO 14,  IN3 → GPIO 12,  IN4 → GPIO 13
 * 
 * API:
 *   GET /motor?left=0.5&right=0.5    → 前進
 *   GET /motor?left=-0.5&right=0.5   → 左轉
 *   GET /motor?left=0&right=0        → 停止
 *   GET /status                       → 狀態回報
 */

#include <WiFi.h>
#include <WebServer.h>

// ===== WiFi 設定（改成你的網路） =====
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ===== 馬達 GPIO =====
// 左馬達
#define LEFT_ENA   25   // PWM 速度
#define LEFT_IN1   26   // 方向
#define LEFT_IN2   27   // 方向

// 右馬達
#define RIGHT_ENB  14   // PWM 速度
#define RIGHT_IN3  12   // 方向
#define RIGHT_IN4  13   // 方向

// PWM 參數
#define PWM_FREQ     5000
#define PWM_RES      8     // 8-bit = 0-255
WebServer server(80);

// ===== 馬達控制 (ESP32 core v3.x — ledcWrite 用 pin 而非 channel) =====
void setMotor(int enPin, int in1, int in2, float speed) {
  // speed: -1.0 ~ 1.0（負值 = 反轉）
  int pwm = abs(speed) * 255;
  pwm = constrain(pwm, 0, 255);
  
  if (speed > 0) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  } else if (speed < 0) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  } else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
  }
  ledcWrite(enPin, pwm);
}

// ===== HTTP API =====
void handleMotor() {
  // GET /motor?left=0.5&right=0.5
  float left = server.arg("left").toFloat();
  float right = server.arg("right").toFloat();
  
  left = constrain(left, -1.0, 1.0);
  right = constrain(right, -1.0, 1.0);
  
  setMotor(LEFT_ENA, LEFT_IN1, LEFT_IN2, left);
  setMotor(RIGHT_ENB, RIGHT_IN3, RIGHT_IN4, right);
  
  String response = "{\"left\":" + String(left) + ",\"right\":" + String(right) + "}";
  server.send(200, "application/json", response);
  
  Serial.printf("Motor: L=%.2f R=%.2f\n", left, right);
}

void handleStatus() {
  String json = "{";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"rssi\":" + String(WiFi.RSSI()) + ",";
  json += "\"uptime\":" + String(millis() / 1000);
  json += "}";
  server.send(200, "application/json", json);
}

void handleRoot() {
  String html = "<h1>ESP32 ROD Car</h1>";
  html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
  html += "<p>API: /motor?left=0.5&right=0.5</p>";
  html += "<p><a href='/status'>/status</a></p>";
  server.send(200, "text/html", html);
}

// ===== 初始化 =====
void setup() {
  Serial.begin(115200);
  
  // 馬達腳位
  pinMode(LEFT_IN1, OUTPUT);
  pinMode(LEFT_IN2, OUTPUT);
  pinMode(RIGHT_IN3, OUTPUT);
  pinMode(RIGHT_IN4, OUTPUT);
  
  // PWM (ESP32 core v3.x — ledcAttach 合併 freq+resolution)
  ledcAttach(LEFT_ENA, PWM_FREQ, PWM_RES);
  ledcAttach(RIGHT_ENB, PWM_FREQ, PWM_RES);
  
  // 停止馬達
  setMotor(LEFT_ENA, LEFT_IN1, LEFT_IN2, 0);
  setMotor(RIGHT_ENB, RIGHT_IN3, RIGHT_IN4, 0);
  
  // WiFi
  Serial.printf("Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi failed! Starting AP mode...");
    WiFi.softAP("ESP32-ROD-Car", "12345678");
    Serial.print("AP IP: ");
    Serial.println(WiFi.softAPIP());
  }
  
  // HTTP 路由
  server.on("/", handleRoot);
  server.on("/motor", handleMotor);
  server.on("/status", handleStatus);
  
  server.begin();
  Serial.println("HTTP server started on port 80");
}

void loop() {
  server.handleClient();
  delay(10);
}
