# utils_llm.py
# 同济子豪兄 2024-5-22
# 调用大语言模型API

print('导入大模型API模块')


import os

import qianfan
def llm_qianfan(PROMPT='你好，你是谁？'):
    '''
    百度智能云千帆大模型平台API
    '''
    
    # 传入 ACCESS_KEY 和 SECRET_KEY
    os.environ["QIANFAN_ACCESS_KEY"] = QIANFAN_ACCESS_KEY
    os.environ["QIANFAN_SECRET_KEY"] = QIANFAN_SECRET_KEY
    
    # 选择大语言模型
    MODEL = "ERNIE-Bot-4"
    # MODEL = "ERNIE Speed"
    # MODEL = "ERNIE-Lite-8K"
    # MODEL = 'ERNIE-Tiny-8K'

    chat_comp = qianfan.ChatCompletion(model=MODEL)
    
    # 输入给大模型
    resp = chat_comp.do(
        messages=[{"role": "user", "content": PROMPT}], 
        top_p=0.8, 
        temperature=0.3, 
        penalty_score=1.0
    )
    
    response = resp["result"]
    return response

import openai
from openai import OpenAI
from API_KEY import *
def llm_yi(message):
    '''
    零一万物大模型API
    '''
    
    API_BASE = "https://api.lingyiwanwu.com/v1"
    API_KEY = YI_KEY

    MODEL = 'yi-large'
    # MODEL = 'yi-medium'
    # MODEL = 'yi-spark'
    
    # 访问大模型API
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    completion = client.chat.completions.create(model=MODEL, messages= message)
    result = completion.choices[0].message.content.strip()
    return result

import requests
import json
import base64
import io
from typing import Optional
from PIL import Image
import numpy as np
API_SECRET_KEY_360 = "fk3468961406.sPA6Fw5yY7kTgIefJ80aX1FphqvnndXV9843ba50"
BASE_URL_360 = "https://api.360.cn/v1/chat/completions"

def llm_360(user_prompt: str, image: Optional[np.ndarray] = None, system_prompt: Optional[str] = None, model_name: str = "gpt-4o") -> str:
    '''
    360大模型API，支持文本和图片输入
    '''
    messages = []
    if system_prompt is not None:
        messages.append({
            "role": "system",
            "content": [
                {"type": "text", "text": system_prompt}
            ]
        })
    user_content = [
        {"type": "text", "text": user_prompt}
    ]
    if image is not None:
        image_pil = Image.fromarray(image)
        buffer = io.BytesIO()
        image_pil.save(buffer, format="PNG")
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_b64}"
            }
        }
        user_content.append(image_content)
    messages.append({
        "role": "user",
        "content": user_content
    })
    payload = json.dumps({
        "model": model_name,
        "messages": messages,
        "temperature": 0.0,
        "stream": False,
        "max_completion_tokens": 1024,
        "user": "andy",
        "content_filter": False,
        "repetition_penalty": 1.05,
    })
    headers = {
        "Authorization": API_SECRET_KEY_360,
        "Content-Type": 'application/json'
    }
    response = requests.post(url=BASE_URL_360, headers=headers, data=payload)
    return response.json()["choices"][0]["message"]["content"].strip()

