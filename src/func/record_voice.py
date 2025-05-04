import sounddevice as sd
import soundfile as sf
import numpy as np
import threading

fs = 44100
channels = 2
max_seconds = 300  # 最長錄音時間（例如5分鐘）

frames = []

def callback(indata, frames_count, time_info, status):
    frames.append(indata.copy())

def record_until_enter():
    global frames
    frames = []
    with sd.InputStream(samplerate=fs, channels=channels, callback=callback):
        input("錄音中...再按一次 Enter 結束錄音：")
    # 錄音結束
    audio = np.concatenate(frames, axis=0)
    sf.write('output.wav', audio, fs)
    print("錄音結束，已儲存為 output.wav")

if __name__ == "__main__":
    input("按 Enter 開始錄音：")
    # 啟動錄音，直到再次按下 Enter
    record_until_enter()
