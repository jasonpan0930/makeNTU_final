# server.py
from flask import Flask, request
from flask_socketio import SocketIO, emit
import base64
import os
from your_module import txt_to_json_pipeline  # Replace with the real file/module name

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

car_sessions = {}

@socketio.on('register')
def handle_register(car_id):
    print(f"[Register] Car ID: {car_id} -> SID: {request.sid}")
    car_sessions[car_id] = request.sid

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[Disconnected] {request.sid}")
    for car_id, sid in list(car_sessions.items()):
        if sid == request.sid:
            del car_sessions[car_id]
            break

@socketio.on('message')
def handle_message(data):
    print(f"[Received Message] {data}")
    target_id = data.get('target_id')
    payload = data.get('payload')

    if target_id and payload:
        target_sid = car_sessions.get(target_id)
        if target_sid:
            socketio.emit('message', payload, room=target_sid)
            print(f"[Forwarded] to {target_id}")
        else:
            print(f"[Warning] Target {target_id} not connected.")
    else:
        print("[Error] Message missing 'target_id' or 'payload'.")

### New: handle txt upload and return processed JSON ###
@socketio.on("upload_txt")
def handle_upload_txt(data):
    filename = data.get("filename")
    filedata = data.get("filedata")

    if not filename or not filedata:
        emit("processed_json", {"error": "Invalid upload data"})
        return

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    input_path = os.path.join("uploads", filename)
    with open(input_path, "wb") as f:
        f.write(base64.b64decode(filedata))

    output_path = os.path.join("outputs", filename.replace(".txt", ".json"))

    try:
        txt_to_json_pipeline(input_path, output_path)

        with open(output_path, "r") as f:
            json_content = f.read()

        emit("processed_json", {"json_content": json_content}, room=request.sid)
        print(f"[Processed] Sent JSON result for {filename}")
    except Exception as e:
        emit("processed_json", {"error": str(e)}, room=request.sid)
        print(f"[Error processing file] {e}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
