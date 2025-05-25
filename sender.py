import websocket
import json
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your unique identifier (e.g., 'project1_company1_warehouse1_weightScale1')
SENDER_IDENTIFIER = 'project1_company1_warehouse1_weightScale1'
RECEIVER_IDENTIFIER = 'project1_company1_warehouse1_weightScale1'  # Match this with the receiver

def on_open(ws):
    logging.info("Connected to server as sender")
    # Register the sender with its identifier
    ws.send(json.dumps({"type": "register", "identifier": SENDER_IDENTIFIER}))

    # Start sending data in a separate thread
    def send_data():
        try:
            while ws.sock and ws.sock.connected:
                data = {
                    "type": "data",
                    "identifier": RECEIVER_IDENTIFIER,
                    "send-data": 1  # Example data
                }
                ws.send(json.dumps(data))
                logging.info(f"Sent to {RECEIVER_IDENTIFIER}: {data['send-data']}")
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error sending data: {e}")

    threading.Thread(target=send_data, daemon=True).start()

def on_message(ws, message):
    try:
        data = json.loads(message)
        logging.info(f"Received: {data}")
    except json.JSONDecodeError:
        logging.error(f"Invalid message: {message}")

def on_error(ws, error):
    logging.error(f"Error: {error}")

def on_close(ws, close_status_code, close_reason):
    logging.info(f"Disconnected from server: {close_reason} (code: {close_status_code})")

def connect():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "ws://localhost:4000/",  # Update to your server URL (e.g., ws://your-ec2-dns:4000)
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
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