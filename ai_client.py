# ai_client.py
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 从环境变量获取 API Key
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量")

# 使用旧版通用域名（不需要 Workspace ID）
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 创建客户端
client = OpenAI(api_key=api_key, base_url=base_url)

def get_qwen_response(prompt: str, system_prompt: str = None) -> str:
    """调用通义千问模型获取回复"""
    if system_prompt is None:
        system_prompt = "你是一个游戏助手，回答关于阿尔比恩OL的问题，提供清晰、有用的建议。"

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"通义千问 API 调用失败: {e}")
        return f"⚠️ AI服务暂时不可用，请稍后再试。错误：{e}"