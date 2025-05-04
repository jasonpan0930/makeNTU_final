from src.func.record_audio import *
from src.func.record_voice import *
from src.func.txt_to_wav import *
from src.func.use_llm import *
from src.func.wav_to_txt import *
from src.func.all_import import *
from src.func.play_audio import *

from src.server_client.bluetooth_module import *
###connection###
# from src.server_client.client import client
# from src.server_client.server import *
###display###
from src.server_client.screen import *
from PySide6.QtWidgets import *
from src import *
import sys
import time
import threading
import json
import os
import platform


state = "await"
received_queue = []  # 儲存多個收到的 json 訊息
flush_stdin = False  # 控制是否忽略 stdin 輸入

# === 跨平台輸入處理 ===
if platform.system() == "Windows":
    import msvcrt
else:
    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(sys.stdin.fileno())

def is_enter_pressed():
    if platform.system() == "Windows":
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            return key == '\r'
        return False
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            key = sys.stdin.read(1)
            return key == '\n'
        return False

def restore_stdin():
    if platform.system() != "Windows":
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def state_monitor():
    global state, flush_stdin
    while True:
        if not flush_stdin and is_enter_pressed():
            state = "sender"
            flush_stdin = True

        elif received_queue:
            state = "receiver"

        if state == "sender":
            print("[狀態] sender → 執行 sender_start()")
            sender_start()
            state = "await"
            flush_stdin = False

        time.sleep(0.1)

def check_message_correctness(json_path: str) -> bool:
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    correctness = json_data.get("correctness", "none")
    if correctness == "1":
        return True
    else:
        return False
    
def sender_pipeline() -> bool:
    sender_pipeline_part1() # output a json file 
    sender_check=check_message_correctness(json_path='/sender_tmp/sender.json')
    while sender_check!=True:
        sender_resend_pipeline()
        sender_check=check_message_correctness(json_path='/sender_tmp/sender.json')

    # the message format should be correct now

    sender_pipeline_part2() # output a wav file

    sender_pipeline_part3() # output a txt file

    sender_final_check=confirm_pipeline(confirm_msg_path='/sender_tmp/sender_final_confirm.txt')
    # use LLM to convert text to json
    if sender_final_check == "1":
        ###display###
        window.mainScreen_display("輸入正確 --> 傳送")
        txt_to_wav(input_path='/src/basic_text/correct_and_send.txt', output_path='/sender_tmp/correct_and_send.wav')
        play_audio('/sender_tmp/correct_and_send.wav')
        return True
    else:
        ###display###
        window.mainScreen_display("輸入不正確 --> 重新輸入")
        txt_to_wav(input_path='/src/basic_text/resend_2.txt', output_path='/sender_tmp/resend_2.wav')
        play_audio('/sender_tmp/resend_2.wav')
        return False

def sender_pipeline_part1():
    # detect user's voice
    record_audio(filename='/sender_tmp/sender.wav', fs=44100, channels=2, max_seconds=300)  # record audio

    # convert voice to text
    wav_to_txt(input_path='/sender_tmp/sender.wav', output_path='/sender_tmp/sender.txt')
    
    ###    display txt on main screen      ###
    with open('/sender_tmp/sender.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
    # use LLM to convert text to json
    txt_to_json_pipeline(input_path='/sender_tmp/sender.txt', output_path='/sender_tmp/sender.json')

def sender_resend_pipeline():

    # tell sender not clear
    txt_to_wav(input_path='/src/basic_text/resend_1.txt', output_path='/sender_tmp/resend_1.wav')
    
    ###  play audio and display resend_1.txt###
    play_audio('/sender_tmp/resend_1.wav')
    with open('/sender_tmp/resend_1.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
    # detect user's voice
    record_audio(filename='/sender_tmp/sender.wav', fs=44100, channels=2, max_seconds=300)  # record audio 

    # convert voice to text
    wav_to_txt(input_path='/sender_tmp/sender.wav', output_path='/sender_tmp/sender.txt')

    # use LLM to convert text to json
    txt_to_json_pipeline(input_path='/sender_tmp/sender.txt', output_path='/sender_tmp/sender.json') 


def sender_pipeline_part2():
    
    # use LLM to convert json to text
    json_to_txt_pipeline(input_path='/sender_tmp/sender.json', output_path='/sender_tmp/sender_notyet_confirm.txt')

    ###  display on main screen  ###
    with open('/sender_tmp/sender_notyet_confirm.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
    # convert text to voice
    txt_to_wav(input_path='/sender_tmp/sender_notyet_confirm.txt', output_path='/sender_tmp/let_sender_confirm.wav')


def sender_pipeline_part3():
    # play the audio
    with open('/src/basic_text/send_check.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
        play_audio('/sender_tmp/sender_notyet_confirm.wav')
    # play the audio
    play_audio('/sender_tmp/let_sender_confirm.wav')

    # wait for sender to confirm
    record_audio(filename='/sender_tmp/sender_final_confirm.wav', fs=44100, channels=2, max_seconds=300)  # record audio

    # convert voice to text
    wav_to_txt(input_path='/sender_tmp/sender_final_confirm.wav', output_path='/sender_tmp/sender_final_confirm.txt')


###receive handle###
def handle_incoming(data):
    print(f"[Main got message] {data}")
    # 指定儲存的目錄和檔案名稱
    directory = "receiver_tmp"
    filename = "received.json"
    filepath = os.path.join(directory, filename)
    receiver_start()

    # 將 json_data 寫入檔案
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    ### there should call a function to do sth

def receiver_pipeline() -> bool:

    # convert json to text
    json_to_txt_pipeline(input_path='/receiver_tmp/received.json', output_path='/receiver_tmp/received.txt')
    # convert text to voice
    txt_to_wav(input_path='/receiver_tmp/received.txt', output_path='/receiver_tmp/received.wav')
    # play the audio
    play_audio('/receiver_tmp/received.wav')
    # wait for receiver to confirm
    receiver_pipeline_part1() # record and output a json file
    
    receiver_check=check_message_correctness(json_path='/receiver_tmp/receiver.json')
    while receiver_check!=True:
        receiver_resend_pipeline()
        receiver_check=check_message_correctness(json_path='/receiver_tmp/receiver.json')

    receiver_pipeline_part2() # output a wav file

    receiver_pipeline_part3() # output a txt file

    receiver_final_check=confirm_pipeline(confirm_msg_path='/reciever_tmp/receiver_final_confirm.txt')
    # use LLM to convert text to json
    if receiver_final_check == "1":    ### display: 輸入正確-->傳送 or 輸入不正確--> 重新輸入 ###
        ###display###
        window.mainScreen_display('輸入正確-->傳送')
        return True
    else:
        ###display###
        window.mainScreen_display('輸入不正確--> 重新輸入')
        txt_to_wav(input_path='/src/basic_text/resend_2.txt', output_path='/reiceiver_tmp/resend_2.wav')
        play_audio('/receiver_tmp/resend_2.wav')
        return False

def receiver_pipeline_part1():

    # detect user's voice   
    record_audio(filename='/receiver_tmp/receiver.wav', fs=44100, channels=2, max_seconds=300)  # record audio

    # convert voice to text
    wav_to_txt(input_path='/receiver_tmp/receiver.wav', output_path='/receiver_tmp/receiver.txt')
    ###    display txt on main screen      ###
    with open('/receiver_tmp/receiver.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
    # use LLM to convert text to json
    txt_to_json_pipeline(input_path='/receiver_tmp/receiver.txt', output_path='/receiver_tmp/receiver.json')

def receiver_resend_pipeline():
    # tell sender not clear
    txt_to_wav(input_path='/src/basic_text/resend_1.txt', output_path='/receiver_tmp/resend_1.wav')
    
    ###  play audio and display resend_1.txt###
    play_audio('/receiver_tmp/resend_1.wav')

    # detect user's voice
    record_audio(filename='/receiver_tmp/receiver.wav', fs=44100, channels=2, max_seconds=300)  # record audio 

    # convert voice to text
    wav_to_txt(input_path='/receiver_tmp/receiver.wav', output_path='/receiver_tmp/receiver.txt')

    # use LLM to convert text to json
    txt_to_json_pipeline(input_path='/receiver_tmp/receiver.txt', output_path='/receiver_tmp/receiver.json') 
    # use LLM to convert json to text

def receiver_pipeline_part2():
    # use LLM to convert json to text
    json_to_txt_pipeline(input_path='/receiver_tmp/receiver.json', output_path='/receiver_tmp/receiver_notyet_confirm.txt')

    ###  display on main screen  ###
    with open('/receiver_tmp/receiver_notyet_confirm.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        window.mainScreen_display(content)
    # convert text to voice
    txt_to_wav(input_path='/receiver_tmp/receiver_notyet_confirm.txt', output_path='/receiver_tmp/let_receiver_confirm.wav')

def receiver_pipeline_part3():
    # play the audio
    play_audio('/receiver_tmp/let_receiver_confirm.wav')

    # wait for receiver to confirm
    record_audio(filename='/receiver_tmp/receiver_final_confirm.wav', fs=44100, channels=2, max_seconds=300)  # record audio

    # convert voice to text
    wav_to_txt(input_path='/receiver_tmp/receiver_final_confirm.wav', output_path='/receiver_tmp/receiver_final_confirm.txt')

def sender_start():

    sender_check=sender_pipeline()
    while sender_check!=True:
        sender_check=sender_pipeline()
    with open('/sender_tmp/sender.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        to_car_ID=json_data.get("傳給的車牌號碼", "none")
        send_to(to_car_ID, json_data) # send the message to the receiver
    client.sio.wait()

def receiver_start():
    # record from which car ID
    receiver_check=receiver_pipeline()
    while receiver_check!=True:
        receiver_check=receiver_pipeline()
    with open('/receiver_tmp/received.json', 'r', encoding='utf-8') as f:
        received_json_data = json.load(f)
        from_car_ID=received_json_data.get("來自的車牌號碼", "none")
        with open('/receiver_tmp/receiver.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            send_to(from_car_ID, json_data) # send the message to the sender
    client.sio.wait()

if __name__== "__main_":
    ##set CarID
    client.set_car_id(input('your car ID: '))
    ##設定receiver function註冊
    client.set_on_message_callback(handle_incoming)
    ##接上server
    client.connect_with_retry()

    ###   display   ###
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    threading.Thread(target=state_monitor, daemon=True).start()
    
    client.sio.wait()
    sys.exit(app.exec()) #關螢幕等於關機