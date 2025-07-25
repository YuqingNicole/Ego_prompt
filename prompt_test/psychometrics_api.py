from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import csv
import os

app = FastAPI()

MBTI_KEYS = ["E","I","S","N","T","F","J","P"]
BIG5_KEYS = ["O","C","E","A","N"]

class Psychometrics(BaseModel):
    MBTI: Dict[str, int]
    Big5: Dict[str, int]

# 读取最新一行心理变量数据
def read_latest_psychometrics(csv_file="psychometrics_data.csv"):
    if not os.path.exists(csv_file):
        return {"MBTI": {k: 50 for k in MBTI_KEYS}, "Big5": {k: 50 for k in BIG5_KEYS}}
    with open(csv_file, "r") as f:
        lines = f.readlines()
        if len(lines) <= 1:
            return {"MBTI": {k: 50 for k in MBTI_KEYS}, "Big5": {k: 50 for k in BIG5_KEYS}}
        last = lines[-1].strip().split(",")
        mbti = {k: int(v) for k, v in zip(MBTI_KEYS, last[1:9])}
        big5 = {k: int(v) for k, v in zip(BIG5_KEYS, last[9:])}
        return {"MBTI": mbti, "Big5": big5}

@app.get("/psychometrics", response_model=Psychometrics)
def get_psychometrics():
    """获取最新心理变量数据（MBTI+大五人格）"""
    return read_latest_psychometrics()

@app.get("/psychometrics/mbti")
def get_mbti():
    return read_latest_psychometrics()["MBTI"]

@app.get("/psychometrics/big5")
def get_big5():
    return read_latest_psychometrics()["Big5"]
