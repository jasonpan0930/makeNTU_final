import threading
import json

# storing all Socket for connected devices
connected_sockets = []

# connecting 
def connect_bluetooth(target_address: str, port: int = 1):
    """
    Establish a Bluetooth connection and return the socket.
    
    Args:
        target_address (str): The MAC address of the target device.
        port (int): The port to connect to (default is 1). 
    Returns:
        BluetoothSocket: The connected Bluetooth socket.
    """
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))
    print(f"[Bluetooth Connected] Connected to {target_address}")
    connected_sockets.append(sock)
    return sock

# sending string
def send_string(sock, message: str):
    """
    Send a string message over Bluetooth.
    
    Args:
        sock (BluetoothSocket): The connected Bluetooth socket.
        message (str): The string message to send.
    """
    try:
        sock.send(message.encode('utf-8'))
        print(f"[Sent String] {message}")
    except Exception as e:
        print(f"[String Sending Error] {e}")

# sending JSON data
def send_json(sock, json_data: dict):
    """
    Send JSON data over Bluetooth.
    
    Args:
        sock (BluetoothSocket): The connected Bluetooth socket.
        json_data (dict): The dictionary to send as JSON.
    """
    try:
        json_string = json.dumps(json_data)
        sock.send(json_string.encode('utf-8'))
        print(f"[Sent JSON] {json_string}")
    except Exception as e:
        print(f"[JSON Sending Error] {e}")

# send to specific device
def send_to_one(sock, message):
    """
    Send a message to a specific Bluetooth socket (one car).
    
    Args:
        sock (BluetoothSocket): The connected Bluetooth socket.
        message (str or dict): The message to send (string or JSON dictionary).
    """
    try:
        if isinstance(message, dict):  # If the message is a dictionary (JSON)
            send_json(sock, message)
        elif isinstance(message, str):  # If the message is a string
            send_string(sock, message)
        else:
            print("[Error] Invalid message type. Please send a string or dictionary.")
    except Exception as e:
        print(f"[Error sending to one] {e}")

# send to all devices
def broadcast_message(message):
    """
    Send a message to all connected Bluetooth devices (cars).
    
    Args:
        message (str or dict): The message to send (string or JSON dictionary).
    """
    if isinstance(message, str):
        for sock in connected_sockets:
            send_string(sock, message)
    elif isinstance(message, dict):
        for sock in connected_sockets:
            send_json(sock, message)
    else:
        print("[Error] Invalid message type. Please send a string or dictionary.")

# scan and connecting devices around
def scan_and_connect():
    """
    Scan for nearby Bluetooth devices and connect to the first available one.
    """
    print("[Scanning] Scanning for nearby Bluetooth devices...")
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_oui=True, lookup_ucs2=True)
    if not nearby_devices:
        print("[Error] No devices found.")
        return

    print("[Found Devices] Found the following devices:")
    for addr, name in nearby_devices:
        print(f"  {name} - {addr}")

    target_address = input("Please enter the Bluetooth address of the vehicle you want to connect to:").strip()
    if target_address:
        try:
            connect_bluetooth(target_address)
            print(f"[Connected] Successfully connected to {target_address}")
        except Exception as e:
            print(f"[Connection Error] {e}")
    else:
        print("[Error] Invalid address entered.")

# turn off connection
def close_all_connections():
    """
    Close all Bluetooth connections.
    """
    for sock in connected_sockets:
        sock.close()
    print("[System] All connections closed.")

# start waiting for connection
def start_server():
    """
    Start a Bluetooth server to accept incoming connections.
    """
    def listen():
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", 1))  # Port 1 (default)
        server_sock.listen(1)
        print("[Server Started] Listening on port 1...")

        while True:
            try:
                client_sock, address = server_sock.accept()
                print(f"[Incoming Connection] From {address}")
                connected_sockets.append(client_sock)
            except Exception as e:
                print(f"[Server Error] {e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()
    print("[Server Listening] Server started and waiting for connections...")

# main(test)
if __name__ == "__main__":
    start_server()

    while True:
        print("\n---")
        print("[Menu] Command:")
        print(" 1. scan and connecting vehicles around")
        print(" 2. send message to all connected vehicles")
        print(" 3. send message to specific vehicle")
        print(" 4. end")
        choice = input("choice: ").strip()

        if choice == "1":
            scan_and_connect()
        elif choice == "2":
            msg = input("public message:")
            broadcast_message(msg)
        elif choice == "3":
            msg = input("private message:")
            print("[Available Connections] all connected vehicles:")
            for idx, sock in enumerate(connected_sockets):
                print(f"{idx + 1}. {sock.getpeername()[0]}")
            target_idx = int(input("select: ").strip()) - 1
            if 0 <= target_idx < len(connected_sockets):
                send_to_one(connected_sockets[target_idx], msg)
            else:
                print("[selecting error] invalid choice")
        elif choice == "4":
            print("[System] end")
            close_all_connections()
            break
        else:
            print("[input error] please enter 1/2/3/4")
