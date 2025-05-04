# import os
# import whisper
# from pathlib import Path

# def wav_to_txt(
#     input_path: str,
#     output_path: str = None,
#     model_size: str = "base",
#     max_size_mb: int = 200,
#     ffmpeg_path: str = r"C:\ffmpeg\bin",
#     language: str = "zh",
#     initial_prompt: str = "以下是普通話的句子。"
# ) -> str:
   
#     # 設定 FFmpeg 路徑
#     os.environ["PATH"] += os.pathsep + ffmpeg_path

#     # 檢查檔案大小
#     file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
#     if file_size_mb > max_size_mb:
#         raise ValueError(f"音檔過大（{file_size_mb:.1f} MB），建議先分段處理。")

#     # 載入模型
#     model = whisper.load_model(model_size)

#     # 執行語音辨識
#     result = model.transcribe(
#         audio=input_path,
#         language=language,
#         initial_prompt=initial_prompt,
#         verbose=False
#     )

#     # 儲存結果
#     if output_path:
#         output_dir = Path(output_path).parent
#         output_dir.mkdir(parents=True, exist_ok=True)
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(result["text"])

#     return result["text"]


# if __name__ == "__main__":
#     txt = wav_to_txt(
#         input_path=r"C:\MakeNTU_mine\input\test.wav",
#         output_path=r"C:\MakeNTU_mine\output\test.txt",
#         #max_size_mb=500,
#         #language="zh",
#         #initial_prompt="以下是台灣國語的會議錄音，包含專業術語。"
#     )
#     print(f"轉錄完成，辨識結果：{txt}")


#     """
#     將 wav 音檔轉換為文字（支援中文）

#     參數:
#         input_path (str): 輸入音檔路徑
#         output_path (str, optional): 輸出文字檔路徑，預設不儲存
#         model_size (str): Whisper 模型大小 (tiny/base/small/medium/large)
#         max_size_mb (int): 允許處理的最大檔案大小(MB)
#         ffmpeg_path (str): FFmpeg 執行檔路徑
#         language (str): 語音語言代碼 (zh=中文)
#         initial_prompt (str): 強化語境的初始提示

#     回傳:
#         str: 辨識結果文字

#     拋出:
#         ValueError: 音檔過大時拋出錯誤
# <<<<<<< Updated upstream
#     """

import os
import whisper
from pathlib import Path

def wav_to_txt(
    input_path: str,
    output_path: str = None,
    model_size: str = "base",
    max_size_mb: int = 200,
    language: str = "zh",
    initial_prompt: str = """
    以下是普通話的句子。
    其中高機率會有一個車牌號碼
    車牌號碼的格式是三個英文字母+四個數字
    請不要在這七個字符之間加"-"或者空格。
    另外，此對話情境是在車上與它車對話，
    因此對話內容高機率會是行車中的相關內容。
    """
) -> str:

    # 檢查檔案大小
    file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise ValueError(f"音檔過大（{file_size_mb:.1f} MB），建議先分段處理。")

    # 載入模型
    model = whisper.load_model(model_size)

    # 執行語音辨識
    result = model.transcribe(
        audio=input_path,
        language=language,
        initial_prompt=initial_prompt,
        verbose=False
    )

    # 儲存結果
    if output_path:
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

    return result["text"]


# ========== 範例執行 ==========
if __name__ == "__main__":
    txt = wav_to_txt(
        input_path="/home/yourname/input/test.wav",
        output_path="/home/yourname/output/test.txt",
        # language="zh",
        # model_size="small",
        # initial_prompt="以下是台灣國語的會議錄音，包含專業術語。"
    )
    
    print(f"轉錄完成，辨識結果：{txt}")
