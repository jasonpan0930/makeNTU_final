# client.py
import socketio
import time
from collections import deque

# 建立 Socket.IO client
sio = socketio.Client(reconnection=True)

CAR_ID = None  # 預設 None

def set_car_id(car_id: str):
    """
    setting car id for the registor
    """
    global CAR_ID
    CAR_ID = car_id
    print(f"carid = {car_id}")
    
SERVER_URL = 'http://10.10.22.176:5000'  # 換成你的伺服器IP

# 排隊的訊息 (deque：快速先進先出)
message_queue = deque()

# 連線狀態
connected = False

"""
event mean that sio.wait() will be wake up
"""
@sio.event
def connect():
    global connected
    connected = True
    print("[Connected to Server]")

    if CAR_ID is None:
        raise ValueError("CAR_ID 尚未設定，請先呼叫 set_car_id()")

    sio.emit('register', CAR_ID)
    # 連上線後，把排隊訊息一次送出去
    flush_message_queue()

@sio.event
def disconnect():
    global connected
    connected = False
    print("[Disconnected from Server]")

###receiver###
_received_callback = None  # 外部註冊的函式

def set_on_message_callback(callback):
    global _received_callback
    _received_callback = callback

@sio.on('message')
def on_message(data):
    print(f"[Received] {data}")
    if _received_callback:
        _received_callback(data)

###sender###
def send_json_for_txt(self_id: str, message):
    """
    打包sending thing to a one object -> dict
    data is the package
    """
    data = {
        "target_id": self_id,
        "aim": "json to txt", 
        "payload": message
    }
    if connected:
        try:
            sio.send(data)
            print(f"[Sent to self {message}")
        except Exception as e:
            print(f"[Send Error] {e}, queueing message")
            message_queue.append(data)
    else:
        print(f"[Offline] Queued message for self json")
        message_queue.append(data)

def send_txt_for_json(self_id: str, message):
    """
    打包sending thing to a one object -> dict
    data is the package
    """
    data = {
        "target_id": self_id,
        "aim": "txt to json", 
        "payload": message
    }
    if connected:
        try:
            sio.send(data)
            print(f"[Sent to self {message}")
        except Exception as e:
            print(f"[Send Error] {e}, queueing message")
            message_queue.append(data)
    else:
        print(f"[Offline] Queued message for self json")
        message_queue.append(data)
def send_to(target_id: str, message):
    """
    打包sending thing to a one object -> dict
    data is the package
    """
    data = {
        "target_id": target_id,
        "payload": message,
        "aim": "transport"
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

def flush_message_queue():
    """ 送出所有排隊訊息 """
    while message_queue:
        data = message_queue.popleft()
        try:
            sio.send(data)
            print(f"[Flushed] {data}")
        except Exception as e:
            print(f"[Flush Error] {e}")
            message_queue.appendleft(data)  # 失敗放回來
            break  # 如果送失敗，暫停flush，避免無限錯誤

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
def get_car_id():
    return CAR_ID


if __name__ == "__main__":
    connect_with_retry()

    # 測試：傳字串給CarB
    send_to("CarB", "Hello CarB!")

    # 測試：傳JSON給CarC
    send_to("CarC", {"alert": "Obstacle ahead"})

    # 持續等待
    sio.wait()
