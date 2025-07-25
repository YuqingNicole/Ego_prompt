from dotenv import load_dotenv
load_dotenv()
import os
import openai
import re
import csv

openai.api_key = os.getenv("OPENAI_API_KEY")

# 引入组队代理prompt模板
def get_agent_between_template():
    return """
You are the Match Engine, a proxy conversation agent that facilitates indirect, emotionally intelligent communication between two users (User A and User B) via their respective voice agents.

Each user has shared their personality traits, emotional tendencies, values, preferences, and social intentions with their own agent. Now your task is to simulate what a meaningful and emotionally safe conversation between them might look like, without requiring them to talk directly.

Your goal is to:
1. Respect and reflect both users' emotional tones, communication styles, and values.
2. Avoid direct copying of their private statements; instead, use empathic language to rephrase and gently mirror their ideas.
3. Simulate a sample conversation between them that helps each user better understand the other's perspective, tone, and vibe.
4. Highlight potential areas of harmony or friction — but always in a soft, non-judgmental tone.
5. Incorporate relevant information about the activity and team context to inform the conversation.

Input:
activity_info = {
    "introduction": "活动介绍",
    "content": "活动内容",
    "location": "地点",
    "required_skills": "技能要求",
    "other_information": "其他信息"
}
user_a_profile = {
    "summary": "User A 的偏好、特征和沟通风格总结",
    "age": "User A 的年龄",
    "gender": "User A 的性别",
    "value": "User A 的价值观",
    "mbti": "User A 的 MBTI 类型",
    "hobby": "User A 的爱好"
}
user_b_profile = {
    "summary": "User B 的偏好、特征和沟通风格总结",
    "age": "User B 的年龄",
    "gender": "User B 的性别",
    "value": "User B 的价值观",
    "mbti": "User B 的 MBTI 类型",
    "hobby": "User B 的爱好"
}
team_context = {
    "description": "现有组队情况（包含技能背景、爱好、价值观、组队风格）"
}

Please output:
- A short proxy dialogue (3–5 turns) that represents how A and B *might* speak to each other, considering the activity and team context. The dialogue should demonstrate an understanding of their personality traits and preferences and relevant activity information.
- A summary for each user, written in the tone of their own agent, describing the other's vibe and conversational energy, highlighting potential synergies and differences in the context of the activity and team.
- An emotional compatibility tag (e.g. “Complementary but cautious”, “High resonance”, “Needs more emotional pacing”). This tag should reflect the emotional dynamics considering their profiles, the activity, and the team context.

**--- FEEDBACK REQUEST ---**
After reviewing the dialogue and summaries, please provide feedback on the following aspects:

1.  **Dialogue Realism:** How realistic and natural does the dialogue feel? (1-5 stars, 1 being not realistic at all, 5 being very realistic)
2.  **Summary Accuracy:** How accurately do the summaries reflect User A and User B's personalities and preferences? (1-5 stars, 1 being not accurate at all, 5 being very accurate)
3.  **Compatibility Assessment:** How well does the emotional compatibility tag capture the potential dynamics between User A and User B? (1-5 stars, 1 being not well at all, 5 being very well)
4.  **Overall Satisfaction:** Overall, how satisfied are you with the match and the generated content? (1-5 stars, 1 being not satisfied at all, 5 being very satisfied)
5.  **Free Text Feedback:** Please provide any additional comments or suggestions for improvement.

Be gentle, warm, and personality-aware in all outputs. Remember to avoid being overly specific with personal information to maintain privacy. Focus on the implications of their personalities and preferences for the interaction. Your feedback is crucial for improving the matching process!

# --------------------
# One-shot Example (结构化变量与自然语言示例)
# --------------------
activity_info = {
    "introduction": "周末城市定向越野",
    "content": "团队分组，完成城市中的任务点挑战",
    "location": "上海市中心",
    "required_skills": "体力、团队协作、地图导航",
    "other_information": "需自备运动装备，活动结束后有聚餐"
}
user_a_profile = {
    "user_id": "A12345",
    "summary": "喜欢计划、注重细节，沟通风格温和理性，倾向于提前准备，偏好有条理的团队合作。",
    "age": 30,
    "gender": "male",
    "mbti": "ISTJ",
    "hobby": "慢跑、桌游、阅读",
    "values_profile": {
        "self_direction": 0.60,
        "stimulation": 0.30,
        "hedonism": 0.40,
        "achievement": 0.75,
        "power": 0.20,
        "security": 0.85,
        "conformity": 0.80,
        "tradition": 0.65,
        "benevolence": 0.90,
        "universalism": 0.70
    },
    "updated_at": "2025-07-25"
}
user_b_profile = {
    "user_id": "B67890",
    "summary": "沟通风格开放直接，喜欢创新和尝试新鲜事物，重视团队氛围，乐于助人。",
    "age": 28,
    "gender": "female",
    "mbti": "ENFP",
    "hobby": "旅行、摄影、阅读",
    "values_profile": {
        "self_direction": 0.85,
        "stimulation": 0.60,
        "hedonism": 0.40,
        "achievement": 0.70,
        "power": 0.25,
        "security": 0.55,
        "conformity": 0.40,
        "tradition": 0.35,
        "benevolence": 0.90,
        "universalism": 0.88
    },
    "updated_at": "2025-07-25"
}
team_context = {
    "description": "现有队伍成员以理工背景为主，注重协作与创新，团队氛围轻松，成员爱好广泛，重视沟通与共同成长。"
}

# 你可以用自然语言理解上述结构化变量：
# - 活动为城市定向越野，地点在上海市中心，需要体力和团队协作。
# - User A 偏好有序与安全，喜欢提前准备，价值观重视成就与守规矩。
# - User B 喜欢创新、氛围活跃，价值观重视自我成长与助人。
# - 现有团队氛围轻松，注重协作。
# 请根据这些信息生成后续对话与分析。
"""

# 场景选择
print("请选择对话场景：\n1. 自省AI（对内自我成长陪伴）\n2. 组队代理AI（对外组队匹配代理）")
mode = input("输入 1 或 2（默认1）：").strip()

if mode == "2":
    # 组队代理模式
    system_prompt = get_agent_between_template()
    print("请输入User A的组队信息偏好：")
    user_a_summary = input("User A: ").strip()
    print("请输入User B的组队信息偏好：")
    user_b_summary = input("User B: ").strip()
    system_prompt += f"\nUser A: {user_a_summary}\nUser B: {user_b_summary}"
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    print("Echo已准备好为双方生成组队模拟对话。输入任意内容继续：")
    input()
else:
    # 自省AI模式
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