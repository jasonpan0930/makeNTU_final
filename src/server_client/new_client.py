# client.py
import socketio
import time
from collections import deque
import base64
import os

# 建立 Socket.IO client
sio = socketio.Client(reconnection=True)

CAR_ID = None  # 預設 None
SERVER_URL = 'http://10.10.5.7:5000'  # 換成你的伺服器 IP

# 訊息排隊
message_queue = deque()
connected = False

def set_car_id(car_id: str):
    global CAR_ID
    CAR_ID = car_id

@sio.event
def connect():
    global connected
    connected = True
    print("[Connected to Server]")

    if CAR_ID is None:
        raise ValueError("CAR_ID 尚未設定，請先呼叫 set_car_id()")

    sio.emit('register', CAR_ID)
    flush_message_queue()

@sio.event
def disconnect():
    global connected
    connected = False
    print("[Disconnected from Server]")

### Receiver for messages ###
_received_callback = None

def set_on_message_callback(callback):
    global _received_callback
    _received_callback = callback

@sio.on('message')
def on_message(data):
    print(f"[Received] {data}")
    if _received_callback:
        _received_callback(data)

### New: Receive processed JSON result ###
@sio.on("processed_json")
def on_processed_json(data):
    if "error" in data:
        print("[Server Error]", data["error"])
        return

    with open("result.json", "w") as f:
        f.write(data["json_content"])
    print("✅ Received and saved JSON as result.json")

### Sender ###
def send_to(target_id: str, message):
    data = {
        "target_id": target_id,
        "payload": message
    }
    if connected:
        try:
            sio.send(data)
            print(f"[Sent to {target_id}] {message}")
        except Exception as e:
            print(f"[Send Error] {e}, queueing message")
            message_queue.append(data)
    else:
        print(f"[Offline] Queued message for {target_id}")
        message_queue.append(data)

def send_to_server_for_json(message):
    if connected:
        try:
            sio.send(message)
            print(f"[Sent to Server] {message}")
        except Exception as e:
            print(f"[Send Error] {e}, queueing message")
            message_queue.append(message)
    else:
        print("[Offline] Queued message for server")
        message_queue.append(message)

def flush_message_queue():
    while message_queue:
        data = message_queue.popleft()
        try:
            sio.send(data)
            print(f"[Flushed] {data}")
        except Exception as e:
            print(f"[Flush Error] {e}")
            message_queue.appendleft(data)
            break

def connect_with_retry():
    while True:
        try:
            print(f"[Connecting] Connecting to {SERVER_URL}...")
            sio.connect(SERVER_URL)
            print("[Connected] Success!")
            break
        except Exception as e:
            print(f"[Connect Failed] {e}")
            print("[Retry] Waiting 3 seconds...")
            time.sleep(3)

### New: Send txt file to server ###
def send_txt_file_to_server(txt_path):
    if not os.path.exists(txt_path):
        print("[Error] File not found:", txt_path)
        return

    with open(txt_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')

    data = {
        "filename": os.path.basename(txt_path),
        "filedata": encoded
    }
    sio.emit("upload_txt", data)
    print("[Sent txt file to server]")

### Run ###
if __name__ == "__main__":
    connect_with_retry()
    set_car_id("CarA")

    # Send .txt file
    send_txt_file_to_server("example.txt")

    sio.wait()
