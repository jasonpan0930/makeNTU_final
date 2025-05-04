import sounddevice as sd
import soundfile as sf
import numpy as np
import os

'''
# 基本用法（完全等同原程式行為）
record_audio()

# 高階用法（自定義參數）
record_audio(
    filename='meeting_record.wav',
    fs=48000,
    channels=1,
    max_seconds=600
)
'''

def record_audio(
    filename='output.wav',
    fs=44100,
    channels=2,
    max_seconds=300
):
    # make sure the file is exist. if not exist, create it.
    # if not os.path.exists(os.path.dirname(filename)):
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
    #     print(f"目錄 {os.path.dirname(filename)} 已建立")

    folder = os.path.dirname(filename)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"目錄 {folder} 已建立")


    """錄音主函數，按兩次Enter鍵控制錄音起停"""
    frames = []

    def callback(indata, frames_count, time_info, status):
        """音頻輸入回調函數"""
        frames.append(indata.copy())

    def record_until_enter():
        """錄音控制核心邏輯"""
        nonlocal frames
        frames = []
        with sd.InputStream(
            samplerate=fs,
            channels=channels,
            callback=callback
        ):
            input("錄音中...再按一次 Enter 結束錄音：")
        
        audio = np.concatenate(frames, axis=0)
        sf.write(filename, audio, fs)
        print(f"錄音結束，已儲存為 {filename}")

    input("按 Enter 開始錄音：")
    record_until_enter()

if __name__ == "__main__":
    # 保留原始調用方式
    record_audio()