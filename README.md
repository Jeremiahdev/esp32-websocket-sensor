# esp32-websocket-sensor
This project connects an ESP32 device to a Flask server with WebSocket support. It sends DHT11 sensor data (temperature and humidity) and images to the server, which displays them on a webpage.

## Features

- Real-time sensor updates (Temperature and Humidity)
- View the latest ESP32-captured image
- WebSocket communication between ESP32 and Flask server
- Simple and easy-to-use interface

## Prerequisites

Before running this project, make sure you have the following:

- **ESP32** (with the latest firmware installed)
- **DHT11 Sensor** connected to GPIO4 on the ESP32
- **Wi-Fi network** (for connecting both ESP32 and server)
- **Python** installed on your machine

## How to Set Up

### 1. Install Dependencies

Clone the repository and navigate into the project folder. Then, create a `requirements.txt` file that lists the necessary Python libraries:

```bash
pip install -r requirements.txt
