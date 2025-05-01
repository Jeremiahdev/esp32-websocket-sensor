import asyncio
import logging 
from websockets.legacy.server import serve
import os
import time
from io import BytesIO
from flask import Flask, render_template, send_from_directory, jsonify

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
                  handlers=[logging.StreamHandler()]   )

# Flask Setup
app = Flask(__name__)

# This makes the folder save images
IMAGE_SAVE_DIR = "esp32_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)

# Store last received sensor data
last_sensor_data = {"temperature": None, "humidity": None}

# Serve Web page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/latest-image")
def latest_image():
    """Serve the latest image."""
    try:
        images = sorted(os.listdir(IMAGE_SAVE_DIR), reverse=True)
        if images:
            return send_from_directory(IMAGE_SAVE_DIR, images[0])
    except Exception as e:
        logging.error(f"Error fetching latest image: {e}")
    return "No Image Available", 404

@app.route("/sensor-data")
def get_sensor_data():
    """Serve the last received sensor data."""
    return jsonify(last_sensor_data)   # <-- FIX: use jsonify here

async def handle_client(websocket, path):
    """WebSocket server logic"""
    global last_sensor_data
    logging.info("New client connected")
    
    try:
        async for message in websocket:
            if isinstance(message, int) and len(message) > 5000:
                message = str(message)

            if isinstance(message, (bytes, bytearray)):
                filename = os.path.join(IMAGE_SAVE_DIR, f"image_{int(time.time())}.jpg")
                with open(filename, "wb") as f:
                    f.write(message)
                logging.info(f"Image saved: {filename}")
                await websocket.send("Image received and saved.")

            elif isinstance(message, str):
                logging.debug(f"Received message: {message}")

                # Check if message contains sensor data
                if "temperature=" in message and "humidity=" in message:
                    try:
                        data = dict(item.split("=") for item in message.split(","))
                        temperature = float(data["temperature"])
                        humidity = float(data["humidity"])

                        # Update last sensor data here!
                        last_sensor_data["temperature"] = temperature
                        last_sensor_data["humidity"] = humidity

                        logging.info(f"Received Sensor Data → Temperature: {temperature}°F, Humidity: {humidity}%")
                        await websocket.send("Sensor data received")

                    except Exception as e:
                        logging.error(f"Error parsing sensor data: {e}")
                        await websocket.send("Error parsing data")

                elif message == "ping":
                    response = "pong"
                    await websocket.send(response)

                elif message == "Hello, Server!":
                    response = "Hello, Client!"
                    await websocket.send(response)

                else:
                    response = f"Message received: {message}"
                    logging.debug(f"Sending response: {response}")
                    await websocket.send(response)

            else:
                logging.warning(f"Received unexpected message type: {type(message)}")

    except Exception as e:
        logging.error(f"Error during client connection: {e}")

async def main():
    server_ip = "0.0.0.0"
    port = 8765
    logging.info(f"WebSocket server is running on ws://{server_ip}:{port}")
    async with serve(handle_client, server_ip, port):
        await asyncio.Future()

def run_asyncio_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

if __name__ == "__main__":
    import threading

    # Start WebSocket server in a separate thread
    websocket_thread = threading.Thread(target=run_asyncio_server, daemon=True)
    websocket_thread.start()

    # Run Flask server
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
