# test_qwen_vlm.py
# 测试Qwen VL API的返回内容

import cv2
import base64
from openai import OpenAI

# Qwen API配置
Qwen_KEY = "sk-1a68ae54b3fd424f91d0979d7b67b491"

# 测试图像
img_path = 'temp/test_vl.jpg'  # 或者 'temp/vl_now.jpg'

# 系统提示词
SYSTEM_PROMPT = '''
我即将说一句给机械臂的指令，你帮我从这句话中提取出起始物体和终止物体，并从这张图中分别找到这两个物体左上角和右下角的像素坐标，输出json数据结构。

例如，如果我的指令是：请帮我把红色方块放在房子简笔画上。
你输出这样的格式：
{
 "start":"红色方块",
 "start_xyxy":[[102,505],[324,860]],
 "end":"房子简笔画",
 "end_xyxy":[[300,150],[476,310]]
}

只回复json本身即可，不要回复其它内容
'''

PROMPT = "把笔放在肠溶胶囊药品盒子上"

print("=" * 60)
print("测试Qwen VL API")
print("=" * 60)

# 读取并编码图像
print(f"\n读取图像: {img_path}")
with open(img_path, 'rb') as image_file:
    image = 'data:image/jpeg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')

# 创建客户端
client = OpenAI(
    api_key=Qwen_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 调用API
print(f"\n调用Qwen VL API...")
print(f"指令: {PROMPT}")

completion = client.chat.completions.create(
    model="qwen-vl-max-2024-11-19",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT + "\n我现在的指令是：" + PROMPT
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image
                    }
                }
            ]
        },
    ]
)

# 获取原始返回内容
raw_content = completion.choices[0].message.content.strip()

print("\n" + "=" * 60)
print("原始返回内容:")
print("=" * 60)
print(raw_content)
print("=" * 60)

# 尝试解析
print("\n尝试解析...")

# 方法1: 直接eval
try:
    result = eval(raw_content)
    print("✅ eval() 成功")
    print(result)
except Exception as e:
    print(f"❌ eval() 失败: {e}")
    
    # 方法2: 清理Markdown后eval
    try:
        import json
        content = raw_content.strip()
        
        # 移除Markdown代码块
        if content.startswith('```'):
            content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        if content.endswith('```'):
            content = content.rsplit('\n', 1)[0] if '\n' in content else content[:-3]
        content = content.strip()
        
        print(f"\n清理后的内容:\n{content}")
        
        # 尝试JSON解析
        result = json.loads(content)
        print("✅ json.loads() 成功")
        print(result)
    except Exception as e2:
        print(f"❌ json.loads() 失败: {e2}")
        
        # 尝试eval
        try:
            result = eval(content)
            print("✅ eval(清理后) 成功")
            print(result)
        except Exception as e3:
            print(f"❌ eval(清理后) 失败: {e3}")

print("\n测试完成！")
