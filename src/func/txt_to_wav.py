# import pyttsx3
# from pathlib import Path

# def txt_to_wav(
#     input_path: str,
#     output_path: str = None,
#     voice_id: str = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-TW_HANHAN_11.0",
#     rate: int = 150,
#     volume: float = 0.9,
#     encoding: str = "utf-8"
# ) -> None:

#     # 設定預設輸出路徑
#     if output_path is None:
#         input_file = Path(input_path)
#         output_path = str(input_file.with_suffix('.wav'))

#     # 確保輸出目錄存在
#     output_file = Path(output_path)
#     output_file.parent.mkdir(parents=True, exist_ok=True)

#     # 初始化語音引擎
#     engine = pyttsx3.init()
    
#     try:
#         # 設定語音參數
#         engine.setProperty('voice', voice_id)
#         engine.setProperty('rate', rate)
#         engine.setProperty('volume', volume)

#         # 讀取文字檔案（加入編碼處理機制）
#         try:
#             with open(input_path, 'r', encoding=encoding) as f:
#                 text = f.read()
#         except UnicodeDecodeError:
#             # 自動嘗試常見中文編碼
#             for codec in ['big5', 'gbk', 'cp950']:
#                 try:
#                     with open(input_path, 'r', encoding=codec) as f:
#                         text = f.read()
#                     break
#                 except UnicodeDecodeError:
#                     continue
#             else:
#                 raise ValueError("無法自動檢測檔案編碼，請手動指定 encoding 參數")

#         # 保存語音檔案
#         engine.save_to_file(text, output_path)
#         engine.runAndWait()
#         print(f"語音檔案已生成：{output_path}")

#     finally:
#         engine.stop()

# # ================== 使用範例 ==================
# if __name__ == "__main__":
#     # 基本用法 (自動檢測編碼)
#     txt_to_wav(
#         input_path=r"C:\MakeNTU_mine\input\test.txt",
#         output_path=r"C:\MakeNTU_mine\output\SB.wav",
#         #encoding="big5"
#     )



#     """
#     UTF-8	現代跨語言標準	.txt, .csv
#     Big5	台灣繁體中文傳統系統	.doc, .txt
#     GBK	中國簡體中文環境	.txt, .log
#     CP950	Windows 繁體中文舊版軟體	.csv, .txt
#     """

#     """
#     將文字檔案轉換為WAV語音檔案

#     Parameters:
#         input_path (str): 輸入文字檔案路徑
#         output_path (str, optional): 輸出語音檔案路徑，預設為輸入檔案同目錄同名.wav
#         voice_id (str): 語音引擎ID，預設為台灣中文語音
#         rate (int): 語速 (預設150，範圍通常50-300)
#         volume (float): 音量 (0.0~1.0，預設0.9)
#         encoding (str): 文字檔案編碼 (預設utf-8)

#     Returns:
#         None

#     Raises:


from gtts import gTTS
from pydub import AudioSegment
import os
from pydub.playback import play

def txt_to_wav(input_path, output_path):
    # Read the input text file (ensure it's UTF-8 encoded)
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    if not text:
        raise ValueError("Input text file is empty.")
    # Generate speech using gTTS
    tts = gTTS(text, lang='zh')
    temp_mp3 = output_path + ".tmp.mp3"
    tts.save(temp_mp3)
    # Convert mp3 to wav using pydub
    sound = AudioSegment.from_mp3(temp_mp3)
    faster_sound=sound.speedup(playback_speed=1.3)
    faster_sound.export(output_path, format="wav")
    os.remove(temp_mp3)
    print(f"Saved WAV file: {output_path}")

# ================== 使用範例 ==================
if __name__ == "__main__":
    # 基本用法 (自動檢測編碼)
    txt_to_wav(
        input_path="/home/mason/Desktop/Make_NTU/v2v/src/func/test.txt",
        output_path="/home/mason/Desktop/Make_NTU/v2v/src/func/test.wav",
        # encoding="big5"
    )

#         FileNotFoundError: 輸入檔案不存在時拋出
#         ValueError: 無法自動檢測編碼時拋出
#     """
'''
pip install pydub
pip install gtts
'''