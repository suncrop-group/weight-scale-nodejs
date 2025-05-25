import websocket
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your unique identifier (must match the sender's RECEIVER_IDENTIFIER)
RECEIVER_IDENTIFIER = 'project1_company1_warehouse1_weightScale1'

def on_open(ws):
    logging.info("Connected to server as receiver")
    # Register the receiver with its identifier
    ws.send(json.dumps({"type": "register", "identifier": RECEIVER_IDENTIFIER}))

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data["type"] == "data":
            logging.info(f"Received data: {data['send-data']}")
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
        logging.info("Shutting down receiver")