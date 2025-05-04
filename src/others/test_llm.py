import use_llm
from use_llm import *

async def run_example():
    # 讀取 use_llm.txt 檔案
    txt_path = Path("use_llm_example.txt")
    if not txt_path.exists():
        print("找不到 use_llm.txt！")
        return

    with open(txt_path, "r", encoding="utf-8") as f:
        request_text = f.read()

    # 呼叫你寫好的 txt_to_json_pipeline
    await txt_to_json_pipeline(request_text)

# 然後記得執行
await run_example()


async def run_example2():

    json_path = Path("txt_to_json.json")
    if not json_path.exists():
        print("找不到 txt_to_json.json")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        request_json = f.read()

    # 呼叫你寫好的 json_to_txt_pipeline
    await json_to_txt_pipeline(json_path)

# 然後記得執行
await run_example2()  # 這個是用 use_llm.txt ➔ 生成 txt_to_json.json
