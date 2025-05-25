import websocket
import json
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def on_open(ws):
    logging.info("Connected to server as sender")
    ws.send(json.dumps({"type": "sender"}))
    
    # Start sending data in a separate thread
    def send_data():
        try:
            while ws.sock and ws.sock.connected:
                data = {"type": "data", "send-data": 1}
                ws.send(json.dumps(data))
                logging.info(f"Sent: {data['send-data']}")
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error sending data: {e}")
    
    threading.Thread(target=send_data, daemon=True).start()

def on_message(ws, message):
    logging.info(f"Received: {message}")

def on_error(ws, error):
    logging.error(f"Error: {error}")

def on_close(ws, close_status_code, close_reason):
    logging.info(f"Disconnected from server: {close_reason} (code: {close_status_code})")

def connect():
    while True:
        try:
            ws = websocket.WebSocketApp("wss://weight-scale-nodejs.onrender.com/",
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            ws.run_forever()
        except Exception as e:
            logging.error(f"Connection failed: {e}")
        logging.info("Attempting to reconnect in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    try:
        connect()
    except KeyboardInterrupt:
        logging.info("Shutting down sender")