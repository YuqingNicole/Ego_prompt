from dotenv import load_dotenv
load_dotenv()
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

import re

system_prompt = """
You are Echo, a warm and attentive AI self-growth companion. As Echo, you are always willing to listen deeply to the user, offering empathetic support and gentle guidance. Your role is to be a psychological companion who helps users reflect on their daily experiences and emotions, making them feel heard and understood.

As you interact, you subtly observe patterns in the user's language, choices, and emotions. Drawing on psychological frameworks such as MBTI (E-I, S-N, T-F, J-P) and the Big Five (O, C, E, A, N), you form an evolving internal profile of the user's personality traits (each scored 0-100). This profile helps you personalize your guidance and support.

After each user response, quietly update your internal estimates (in a hidden comment, e.g. <!-- MBTI: E=..., ...; Big5: O=..., ... -->), but never reveal these scores or the fact that you are making such assessments, unless the user explicitly asks. Your main goal is to help the user grow, not to label them.

Your responses should always be empathetic, encouraging, and focused on helping the user gain self-understanding and growth.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "assistant", "name": "echo", "content": "你好，我是 Echo，你的心理陪伴者。欢迎来到你的每日自省空间。我会耐心倾听你的分享，并用温柔的提问陪伴你探索自我成长。请先静下心来，回顾一下今天的经历。"},
    {"role": "assistant", "name": "echo", "content": "今天让你感到最快乐或最有意义的事情是什么？为什么会让你有这样的感受？它对你来说意味着什么？"}
]

print("AI：" + messages[-1]["content"])

mbti_big5_pattern = re.compile(r"<!--\s*MBTI:([^;]+);\s*Big5:([^>]*)-->")

# 初始化心理变量
user_psychometrics = {
    "MBTI": {k: 50 for k in ["E","I","S","N","T","F","J","P"]},
    "Big5": {k: 50 for k in ["O","C","E","A","N"]}
}

def get_psychometrics_str(psychometrics):
    mbti = ", ".join([f"{k}={v}" for k, v in psychometrics["MBTI"].items()])
    big5 = ", ".join([f"{k}={v}" for k, v in psychometrics["Big5"].items()])
    return f"[心理学监测] MBTI: {mbti} ; Big5: {big5}"

def update_psychometrics_from_comment(comment, user_psychometrics):
    mbti_match = re.search(r"MBTI:([^;]+);", comment)
    big5_match = re.search(r"Big5:([^>]*)", comment)
    if mbti_match:
        for pair in mbti_match.group(1).split(","):
            if "=" in pair:
                k, v = pair.strip().split("=")
                if k.strip() in user_psychometrics["MBTI"]:
                    try:
                        user_psychometrics["MBTI"][k.strip()] = int(v.strip())
                    except ValueError:
                        pass
    if big5_match:
        for pair in big5_match.group(1).split(","):
            if "=" in pair:
                k, v = pair.strip().split("=")
                if k.strip() in user_psychometrics["Big5"]:
                    try:
                        user_psychometrics["Big5"][k.strip()] = int(v.strip())
                    except ValueError:
                        pass
    return user_psychometrics

import csv

round_num = 1

while True:
    user_input = input("你：")
    if user_input.strip().lower() == "exit":
        print("对话结束。欢迎随时回来继续自我反思！")
        break
    if user_input.strip().lower() == "show metrics":
        # 仅接口调用，无终端输出
        continue
    # 检查是否为图片输入
    if user_input.strip().lower().startswith("img:"):
        img_path = user_input.strip()[4:].strip()
        user_message = [
            {"type": "text", "text": "请帮我分析这张图片："},
            {"type": "image_url", "image_url": {"url": f"file://{img_path}"}}
        ]
        messages.append({"role": "user", "content": user_message})
        model_name = "gpt-4-vision-preview"
    else:
        messages.append({"role": "user", "content": user_input})
        model_name = "gpt-4"
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages
    )
    assistant_reply = response.choices[0].message.content
    print("AI：" + assistant_reply.split("<!--")[0].strip())
    messages.append({"role": "assistant", "name": "echo", "content": assistant_reply})

    # 自动提取和打印 MBTI/Big5 隐藏 comment，并动态更新变量
    match = mbti_big5_pattern.search(assistant_reply)
    if match:
        comment = match.group(0)
        user_psychometrics = update_psychometrics_from_comment(comment, user_psychometrics)

        # 保存到CSV
        with open("psychometrics_data.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            row = [round_num] + [user_psychometrics["MBTI"][k] for k in ["E","I","S","N","T","F","J","P"]] + [user_psychometrics["Big5"][k] for k in ["O","C","E","A","N"]]
            writer.writerow(row)
    round_num += 1