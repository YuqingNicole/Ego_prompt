import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
csv_file = "psychometrics_data.csv"
df = pd.read_csv(csv_file)

# 绘制MBTI变化曲线
mbti_keys = ["MBTI_E","MBTI_I","MBTI_S","MBTI_N","MBTI_T","MBTI_F","MBTI_J","MBTI_P"]
plt.figure(figsize=(12,6))
for key in mbti_keys:
    plt.plot(df['round'], df[key], label=key)
plt.title('MBTI Variables Over Rounds')
plt.xlabel('Round')
plt.ylabel('Score')
plt.legend()
plt.tight_layout()
plt.savefig('mbti_trend.png')
plt.show()

# 绘制Big Five变化曲线
big5_keys = ["Big5_O","Big5_C","Big5_E","Big5_A","Big5_N"]
plt.figure(figsize=(12,6))
for key in big5_keys:
    plt.plot(df['round'], df[key], label=key)
plt.title('Big Five Variables Over Rounds')
plt.xlabel('Round')
plt.ylabel('Score')
plt.legend()
plt.tight_layout()
plt.savefig('big5_trend.png')
plt.show()
