# from playsound import playsound

# def play_audio(wav_path: str, block: bool = True):
   
#     playsound(wav_path, block=block)

# # 範例用法
# if __name__ == "__main__":
#     play_audio(r"C:\MakeNTU_mine\output\test.wav")
    
    
    
#     """
#     播放 WAV 音檔

#     參數:
#         wav_path (str): .wav 檔案的完整路徑
#         block (bool): 是否阻塞主執行緒直到音檔播放結束，預設 True

#     注意:
#         - 請確保 wav_path 為正確的檔案路徑，並使用雙反斜線或 raw string。
#         - 若路徑錯誤會拋出 FileNotFoundError。
#         - 若需非阻塞播放（背景播放），可設 block=False（playsound 1.3.0 以上支援）。
#   """
import simpleaudio as sa

def play_audio(wav_path: str, block: bool = True):
    try:
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        if block:
            play_obj.wait_done()
    except FileNotFoundError:
        print(f"File not found: {wav_path}")
    except Exception as e:
        print(f"Error playing audio: {e}")

# 範例用法
if __name__ == "__main__":
    play_audio("/home/mason/Desktop/Make_NTU/v2v/src/func/test.wav")  # Linux 路徑格式
