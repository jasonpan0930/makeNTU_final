# only two functions:
# api_txt_to_json(input_path: str, output_path: str)
# api_json_to_txt(input_path: str, output_path: str)

import os
import google.generativeai as genai
import json

myApiKey = 'AIzaSyAqyDuuVe-oB_i0RlJXANWIIGE_gySNzu0'

def api_txt_to_json(input_path: str, output_path: str):
    if os.path.exists(input_path) == False:
        print("input path does not exist")
        return
    txt_to_json_pipeline(input_path, output_path)
    print("already convert to json file")

def api_json_to_txt(input_path: str, output_path: str):
    if os.path.exists(input_path) == False:
        print("input path does not exist")
        return
    json_to_txt_pipeline(input_path, output_path)
    print("already generate txt file")


genai.configure(api_key = myApiKey)
model = genai.GenerativeModel("gemini-1.5-pro")

def gemini_infer(prompt: str, temperature=0.0) -> str:
    response = model.generate_content(prompt, generation_config={
        "temperature": temperature,
        "max_output_tokens": 512,
    })
    return response.text.strip()

def extract_keywords(text: str) -> dict:
    prompt = f"""
        你是一個專門從對話中提取關鍵資訊的 AI。請根據以下規則回傳 JSON 格式的資料：

        規則：
        1. 提取「來自的車牌號碼」、「目標對象車牌號碼」、「使用者想要傳達的訊息」
        2. 若無法判斷任何欄位，correctness = "0"，否則 correctness = "1"
        3. 若車牌號碼中任一超過1組，則 correctness = "0"
        4. 傳達訊息不可僅包含車牌號碼資訊，否則 correctness = "0"
        5. 傳達訊息請用繁體中文。請直接說出他的目的，與目的無關或用於表達心情的字眼不需保留。不得包含不雅字詞，若有則請換成中性用語
        6.輸入的文字高機率包含兩個或兩個以上的車牌號碼
        車牌號碼的格式為三個英文字母+四個數字
        這七個字符中不應該有任何其他符號(例如空格或"-")
        若輸入文字的車牌中有其他符號，請務必幫我忽略
        因此，車牌號碼的格式類似"ABC1234"
        7. 回傳格式如下（不要有其他說明）：
        {{
        "correctness": "1",
        "來自的車牌號碼": "ABC1234",
        "傳給的車牌號碼": "XYZ5678",
        "傳達訊息": "想要超車"
        }}
        8. 有時也會只有單純的對話，沒有任何其他車牌資訊。
        此時請你把該對話內容簡單化後放入"傳達訊息"
        並將傳給的車牌號碼設為空字串("")
        9. 不要有"```json"以及"```"，直接輸出json檔案內容

        以下是使用者輸入：
        {text}
    """


    response = gemini_infer(prompt)

    try:
        return json.loads(response)
    except:
        return {
            "correctness": "0",
            "來自的車牌號碼": "none",
            "傳給的車牌號碼": "none",
            "傳達訊息": "none"
        }

def json_to_sentence(plate: str, message: str) -> str:
    prompt = f"""
    
    現在我們在開車，以下你會拿到旁邊其他車輛想通知你的內容
    其中包含
    你的車牌號碼：車牌號碼
    訊息的來源：車牌號碼（告訴你該訊息是來自那台車）
    以及他要通知你的內容
    請轉成可以有效通知你的駕駛員的口語化繁體中文文字內容

    注意，如果沒有特別說是在廣播，則該訊息就是單純地傳給你的
    也就是說，如果訊息說前方的車好慢想超車
    則請你直接通知駕駛員：XXX想跟你說他想超車

    -----------------
    訊息來源的車牌號碼：{plate}
    訊息：{message}
    -----------------
    請用簡短但自然的方式說出來，像是對駕駛說話，不要用條列式。
    """
    return gemini_infer(prompt)

def confirm_meaning_is_correct(text: str) -> int:
    prompt = f"""
    以下是一段話，請判斷它是否表示「正確」的意思。
    如果是正確的意思，請只回覆 1；若不是，請只回覆 0。
    不准有其他文字，僅回覆 1 或 0。

    {text}
    """
    reply = gemini_infer(prompt)
    return 1 if "1" in reply else 0

def txt_to_json_pipeline(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        request = f.read()
    result = extract_keywords(request)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

def json_to_txt_pipeline(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    result = json_to_sentence(json_data["來自的車牌號碼"], json_data["傳達訊息"])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

def confirm_pipeline(confirm_msg_path: str) -> str:
    with open(confirm_msg_path, "r", encoding="utf-8") as f:
        confirm_msg = f.read()
    return str(confirm_meaning_is_correct(confirm_msg))


    
def check_end(message: str) -> str:
    prompt = f"""
        你的任務是判斷一段車與車之間的對話是否應該繼續。請根據**最後一句回覆**來決定，判斷規則如下：

        1. 若句子中包含終結語句，代表對話已結束，回傳 "End"：
        - 常見終結語句包括：感謝、先這樣、沒事了、結束對話、好、收到、抱歉、下次聊、再聯絡

        2. 若句中包含常見疑問詞，代表對話尚未結束，回傳 "Conti"：
        - 常見疑問詞包括：為什麼、如何、哪裡、誰、什麼、怎麼

        3. 若句子為祈使語氣（請求對方執行某動作），回傳 "Conti"：
        - 祈使語氣範例：靠邊停讓我超車、記得開大燈、開快一點

        4. 回覆格式僅能為以下其一（不加任何其他說明）：
        - "Conti"
        - "End"

        請根據下方兩台車之間的對話進行判斷，格式如下，每句以 "\n[車牌號碼]：" 分隔：

        ------------
        {message}
        ------------
    """
    ans = gemini_infer(prompt).strip()
    print("ans:", ans)
    return ans



if __name__ == "__main__":
    # 基本用法 (自動檢測編碼)
    junk = """[ABC-1234]：那條巷子可以左轉嗎？  
    [XYZ-5678]: 我不確定耶，你要不要問前面的車看看？
    [ABC-1234]: 好滴
"""
    check_end(junk)