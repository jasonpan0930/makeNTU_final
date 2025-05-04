import sys
import time
import threading
import json
import os
import platform
import keyboard
import select
import termios
import tty


from src.func.record_audio import *
from src.func.record_voice import *
from src.func.txt_to_wav import * 
from src.func.wav_to_txt import *
from src.func.all_import import *
from src.func.play_audio import *
###connection###
from src.server_client.client import *
from src.server_client.server import *
###display###
from src.server_client.screen import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
###API###
from src.func.api import *

holding: bool = False
partner = ""
history_str = ""

"""
export QT_QPA_PLATFORM=offscreen

"""


receive_or_not = False

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

def is_tab_pressed():
    if platform.system() == "Windows":
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            return key == '\t'
        return False
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            key = sys.stdin.read(1)
            return key == '\t'
        return False

def restore_stdin():
    if platform.system() != "Windows":
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def state_monitor():
    global state, flush_stdin, receive_or_not
    while True:
        if not flush_stdin and is_tab_pressed():
            state = "sender"
            flush_stdin = True

        elif receive_or_not:
            state = "receiver"


        if state == "sender":
            print("[狀態] sender → 執行 sender_start()")
            sender_start()
            state = "await"
            flush_stdin = False

        elif state == "receiver":
            print(f"[狀態] receiver → 處理 ")
            receiver_start()
            state = "await"
            receive_or_not = False


        time.sleep(0.1)

def receiver_start():
    global history_str
    global holding
    global partner
    if os.path.exists('receiver_tmp/received.json') == False:
        print('no received json in receiver_tmp/received.json')
        return
    
    # 2. 讀取 received.json 的內容
    with open('receiver_tmp/received.json', "r", encoding="utf-8") as json_file:
        data = json.load(json_file)


    sender = data.get("來自的車牌號碼")
    if holding and sender != partner:
        receive = {
            "correctness": "-1",
            "來自的車牌號碼": data.get("傳給的車牌號碼"),
            "傳給的車牌號碼": data.get("來自的車牌號碼"),
            "傳達訊息": "busy"
        }
        send_to(receive.get("傳給的車牌號碼"), receive)
    else:
        if data.get("correctness") == "-1":
            if data.get("傳達訊息") == "busy":
                message = "接受方正在與它車溝通"
                holding = False
                partner = ""
        else:
            if not holding:
                holding = True
                partner = data.get("來自的車牌號碼")
                history_str = f'[{partner}]: {data.get("傳達訊息")}\n'
            else:
                history_str += f'[{partner}]: {data.get("傳達訊息")}\n'
            # 3. 取得 "傳達訊息" 的內容
            message = data.get("傳達訊息", "")  # 如果 key 不存在，回傳空字串
            if data.get("correctness") == "-2":
                message += "\n階段性溝通結束"
                holding = False
                partner = ""
                history_str = ""
                print("disholding")
        window.mainScreen_display(message)

        # 4. 將訊息寫入 received.txt
        with open('receiver_tmp/received.txt', "w", encoding="utf-8") as txt_file:
            txt_file.write(message)
        # convert text to voice
        txt_to_wav(input_path='receiver_tmp/received.txt', output_path='receiver_tmp/received.wav')
        # play the audio
        play_audio('receiver_tmp/received.wav')
        # wait for receiver to confirm
        print("history")
        print(history_str)



def sender_start():
    global history_str
    global holding
    global partner
    record_audio(filename='sender_tmp/sender.wav', fs=44100, channels=2, max_seconds=300)
    wav_to_txt(input_path='sender_tmp/sender.wav', output_path='sender_tmp/sender.txt')
    
    #tested while record_audio fucked up
        # with open('sender_tmp/sender.txt', 'r', encoding='utf-8') as f:
        #     content = f.read()
        #     print("[Transcript] sender.txt內容如下：")
        #     print(content)

        # with open('sender_tmp/sender.txt', 'w', encoding='utf-8') as f:
        #     content = "我是ANK1234,想要超車你GCC3456 "
        #     f.write(content) 

    with open('sender_tmp/sender.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print("[Transcript] sender.txt內容如下：")
            print(content)
    with open("sender_tmp/sender.txt", "a", encoding="utf-8") as file:
        file.write(f"。我的車牌號碼是{get_car_id()}")  # 自動寫到檔案末尾

    api_txt_to_json( input_path= 'sender_tmp/sender.txt', output_path= 'sender_tmp/sender.json')

    with open('sender_tmp/sender.json', 'r', encoding='utf-8') as f:
        sender_data = json.load(f)
        #auto take in receiver
        if holding and sender_data.get("傳給的車牌號碼") == "":
            sender_data["傳給的車牌號碼"] = partner
            sender_data["correctness"] = "1"

        if holding and sender_data.get("傳給的車牌號碼") != partner:
            error_message = "接收者錯誤"
            with open('sender_tmp/error_message.txt', 'w', encoding='utf-8') as f:
                f.write(error_message)
            txt_to_wav(input_path='sender_tmp/error_message.txt', output_path='sender_tmp/error_message.wav')
            play_audio('sender_tmp/error_message.wav')
            sender_start()
            return
        correctness = sender_data.get("correctness", 0)  # 若沒這欄位則預設為 0
    print("correctness: ", correctness)
    print(sender_data)
    with open("sender_tmp/sender.json", "w", encoding="utf-8") as f:
        json.dump(sender_data, f, ensure_ascii=False, indent=4)  # 格式化写入


    #correctness = 1
    if correctness == '1':
        api_json_to_txt(input_path='sender_tmp/sender.json', output_path='sender_tmp/check.txt')
        #my_check.txt =  "  "+check.txt
        with open('sender_tmp/sender.json', 'r', encoding='utf-8') as f:
            sender_data = json.load(f)
            target_id = sender_data.get("傳給的車牌號碼", "未知車牌")

        # 讀 check.txt 內容
        with open('sender_tmp/check.txt', 'r', encoding='utf-8') as f:
            check_content = f.read().strip()

        # 合併內容
        final_text = f"目標車輛是 {target_id} ，你想傳送的內容是：{check_content}"
        window.mainScreen_display(f"You:{target_id}\n{check_content}")

        # 寫入 my_check.txt
        with open('sender_tmp/my_check.txt', 'w', encoding='utf-8') as f:
            f.write(final_text)

        txt_to_wav(input_path='sender_tmp/my_check.txt', output_path='sender_tmp/my_check.wav')
        
        play_audio('sender_tmp/my_check.wav')

        ####
        user_choice = wait_for_user_input(timeout=10)

        if user_choice == "restart":
            print("[Info] 使用者選擇重錄或超時未操作，重新開始錄音。")
            sender_start()
            return  # 終止當前流程，避免繼續往下執行
        elif user_choice == "dont_send_and_quit":
            print("[Info] 使用者選擇離開並不送出。")
            temp_data = {
                "correctness": "-2",
                "來自的車牌號碼": "",
                "傳給的車牌號碼": "",
                "傳達訊息": ""
            }
            send_to(target_id, temp_data)
            holding = False
            partner = ""
            return
        else:
            print("[Info] 使用者確認內容，繼續傳送。")
        ###

        #check finish
            

        # 讀取 sender.json 的內容
        with open('sender_tmp/sender.json', "r", encoding="utf-8") as json_file:
            load_json = json.load(json_file)
            target_id = load_json.get("傳給的車牌號碼")
        # 讀取 check.txt 訊息內容
        with open('sender_tmp/check.txt', 'r', encoding='utf-8') as f:
            message = f.read()
        # modify "傳達訊息" in sender.json
        load_json["傳達訊息"] = message
        if holding == False:
            holding = True
            partner = target_id

        # check conti or end
        if holding == True:
            history_str += f"[{get_car_id()}]: {message}\n"
            keep_holding = check_end(history_str)
            if keep_holding == "End":
                holding = 0
                partner = ""
                history_str = ""
                load_json["correctness"] = "-2"
                print("disholding")
                
        # 傳送
        if target_id:
            send_to(target_id, load_json)
            print("sent!")
            print("history")
            print(history_str)
        else:
            print("[Error] 找不到車牌號碼")
    

    #correctness = 0
    elif correctness == '0' : 
        print("record again")
        sender_start()
        return  # 終止當前流程，避免繼續往下執行

 
def wait_for_user_input(timeout=10):
    print(f"[請在 {timeout} 秒內按空白鍵確認，或直接 Enter 取消]")
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        start = time.time()
        buffer = ""
        while time.time() - start < timeout:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                ch = sys.stdin.read(1)
                if ch == '\n':
                    print("[Enter] 被取消，重錄。")
                    return "restart"
                elif ch == '\x1b':
                    print("[ESC] 離開並不送出。")
                    return "dont_send_and_quit"
                elif ch == ' ':
                    print("[空白鍵] 確認，繼續執行。")
                    return "continue"
                else:
                    buffer += ch
        print("[Timeout] 沒有輸入，重錄。")
        return "restart"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)



def handle_incoming(data):
    '''
    data = dict: {"correctness":, "來自的車牌號碼":, "傳給的車牌號碼":, "傳達訊息":}
    '''
    ###   display   ###
    if data.get("來自的車牌號碼") == "server":
        ##from server -> screen manage
        inform = data.get("傳達訊息")  #(car_id, "delete") or (car_id, "add") or (online_cars, "include")
        if inform[1] == "add":
            window.plate_manager.add_plate(inform[0])
        elif inform[1] == "delete":
            window.plate_manager.delete_plate(inform[0])
        elif inform[1] == "include": # online_cars is a list of str
            online_cars = inform[0]
            for car in online_cars:
                window.plate_manager.add_plate(car) 

    else:
        global receive_or_not
        receive_or_not = True
        print(f"[Main got message] {data}")

        ### display ###
        window.plate_manager.move_plate_to_top(data.get("來自的車牌號碼"))
        # 指定儲存的目錄和檔案名稱
        directory = "receiver_tmp"
        filename = "received.json"
        filepath = os.path.join(directory, filename)
        
        # 將 json_data 寫入檔案
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        ### there should call a function to do sth

def tell_me_all_cars():
    online_cars= get_online_cars()
    online_cars = [cid for cid in online_cars if cid != get_car_id()]
    print(f"[Main] 目前在線的車輛有：{online_cars}")
    with open('online_cars.txt', 'w', encoding='utf-8') as f:
        f.write("目前在線的車輛有：\n")
        for car in online_cars:
            f.write(f"{car}\n")
    play_audio('online_cars.txt')

if __name__== "__main__":
    ##set CarID
    carID = input('your car ID: ')
    set_car_id(carID)

    ###   display first   ###
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()


    ##設定receiver function註冊
    set_on_message_callback(handle_incoming)
    ##接上server
    connect_with_retry()

    threading.Thread(target=state_monitor, daemon=True).start()
    threading.Thread(target=sio.wait, daemon=True).start()

    # try:
    
    #關螢幕等於關機
    sys.exit(app.exec())
