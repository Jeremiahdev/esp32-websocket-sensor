#include <WiFi.h>
#include <WebSocketsClient.h>
#include <DHT.h>

#define DHTPIN 4       // GPIO4 for DHT11 data pin
#define DHTTYPE DHT11

const char* ssid = "****************";    // Your WiFi name
const char* password = "******************"; // Your WiFi password
const char* wsServer = "********************";    // Your computer/server IP
const int wsPort = 8765;                   // Must match your Python server port

WebSocketsClient webSocket;
DHT dht(DHTPIN, DHTTYPE);

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_CONNECTED:
            Serial.println("[WebSocket] Connected!");
            break;
        case WStype_DISCONNECTED:
            Serial.println("[WebSocket] Disconnected!");
            break;
        case WStype_TEXT:
            Serial.printf("[WebSocket] Server says: %s\n", payload);
            break;
        case WStype_PONG:
            Serial.println("[WebSocket] Pong received!");
            break;
        default:
            break;
    }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  dht.begin();

  // Initialize WebSocket
  webSocket.begin(wsServer, wsPort, "/");
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();

  static unsigned long lastSendTime = 0;
  static unsigned long lastPingTime = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastSendTime > 5000) { // Every 5 seconds
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (!isnan(temperature) && !isnan(humidity)) {
      float temperatureF = (temperature * 1.8) + 32; // Convert to Fahrenheit

      //  Send simple "key=value" format to match Python server
      String sensorData = "temperature=" + String(temperatureF) + ",humidity=" + String(humidity);

      Serial.println("Sending: " + sensorData);
      webSocket.sendTXT(sensorData);

      lastSendTime = currentMillis;
    } else {
      Serial.println("Failed to read from DHT11 sensor!");
    }
  }

  if (currentMillis - lastPingTime > 10000) {  // Ping every 10 seconds
    webSocket.sendPing();
    lastPingTime = currentMillis;
  }
}
