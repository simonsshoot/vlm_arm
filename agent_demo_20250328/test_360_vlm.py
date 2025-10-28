# test_360_vlm.py
# 测试360视觉大模型的物体定位能力

import cv2
import numpy as np
import base64
import io
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

# 360 API配置
VISION_360_KEY = "fk3468961406.sPA6Fw5yY7kTgIefJ80aX1FphqvnndXV9843ba50"
BASE_URL_360 = "https://api.360.cn/v1/chat/completions"

def call_vlm(
    user_prompt: str,
    image: Optional[np.ndarray] = None,
    system_prompt: Optional[str] = None, 
    model_name: str = "gpt-4o"
) -> str:
    """
    调用360视觉大模型API
    
    参数:
        user_prompt: 用户提示词
        image: 图像数组 (OpenCV BGR格式)
        system_prompt: 系统提示词
        model_name: 模型名称
    
    返回:
        大模型返回的文本内容
    """
    messages = []
    
    # 添加系统提示词
    if system_prompt is not None:
        messages.append({
            "role": "system",
            "content": [
                {"type": "text", "text": system_prompt}
            ]
        })
    
    # 构建用户消息
    user_content = [
        {"type": "text", "text": user_prompt}
    ]

    # 添加图像（如果提供）
    if image is not None:
        # 转换为PIL Image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        
        # 编码为base64
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

    # 构建请求payload
    payload = json.dumps({
        "model": model_name,
        "messages": messages,
        "temperature": 0.0,
        "stream": False,
        "max_completion_tokens": 1024,
        "user": "robot_test",
        "content_filter": False,
        "repetition_penalty": 1.05,
    })

    headers = {
        "Authorization": VISION_360_KEY,
        "Content-Type": 'application/json'
    }
    
    print("📤 发送请求到360大模型...")
    response = requests.post(url=BASE_URL_360, headers=headers, data=payload)
    
    # 解析返回结果
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"].strip()


def visualize_result(img_bgr, result_dict, output_path='temp/test_vl_viz.jpg'):
    """
    可视化检测结果
    
    参数:
        img_bgr: 原始图像 (BGR格式)
        result_dict: 大模型返回的字典，包含物体信息
        output_path: 输出图像路径
    """
    img_h, img_w = img_bgr.shape[:2]
    FACTOR = 999
    
    img_viz = img_bgr.copy()
    
    # 加载中文字体
    try:
        font = ImageFont.truetype('asset/SimHei.ttf', 32)
    except:
        font = ImageFont.load_default()
    
    # 处理起点物体
    if 'start' in result_dict and result_dict['start_xyxy'] is not None:
        start_name = result_dict['start']
        start_x_min = int(result_dict['start_xyxy'][0][0] * img_w / FACTOR)
        start_y_min = int(result_dict['start_xyxy'][0][1] * img_h / FACTOR)
        start_x_max = int(result_dict['start_xyxy'][1][0] * img_w / FACTOR)
        start_y_max = int(result_dict['start_xyxy'][1][1] * img_h / FACTOR)
        start_x_center = int((start_x_min + start_x_max) / 2)
        start_y_center = int((start_y_min + start_y_max) / 2)
        
        # 画框和中心点
        cv2.rectangle(img_viz, (start_x_min, start_y_min), (start_x_max, start_y_max), 
                     [0, 0, 255], thickness=3)
        cv2.circle(img_viz, [start_x_center, start_y_center], 6, [0, 0, 255], thickness=-1)
        
        # 写物体名称
        img_rgb = cv2.cvtColor(img_viz, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(img_pil)
        draw.text((start_x_min, start_y_min - 35), start_name, font=font, fill=(255, 0, 0, 1))
        img_viz = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        print(f"  ✅ 起点物体: {start_name}")
        print(f"     边界框: ({start_x_min}, {start_y_min}) -> ({start_x_max}, {start_y_max})")
        print(f"     中心点: ({start_x_center}, {start_y_center})")
    
    # 处理终点物体（如果有）
    if 'end' in result_dict and result_dict['end'] is not None:
        end_name = result_dict['end']
        end_x_min = int(result_dict['end_xyxy'][0][0] * img_w / FACTOR)
        end_y_min = int(result_dict['end_xyxy'][0][1] * img_h / FACTOR)
        end_x_max = int(result_dict['end_xyxy'][1][0] * img_w / FACTOR)
        end_y_max = int(result_dict['end_xyxy'][1][1] * img_h / FACTOR)
        end_x_center = int((end_x_min + end_x_max) / 2)
        end_y_center = int((end_y_min + end_y_max) / 2)
        
        # 画框和中心点
        cv2.rectangle(img_viz, (end_x_min, end_y_min), (end_x_max, end_y_max), 
                     [255, 0, 0], thickness=3)
        cv2.circle(img_viz, [end_x_center, end_y_center], 6, [255, 0, 0], thickness=-1)
        
        # 写物体名称
        img_rgb = cv2.cvtColor(img_viz, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(img_pil)
        draw.text((end_x_min, end_y_min - 35), end_name, font=font, fill=(0, 0, 255, 1))
        img_viz = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        print(f"  ✅ 终点物体: {end_name}")
        print(f"     边界框: ({end_x_min}, {end_y_min}) -> ({end_x_max}, {end_y_max})")
        print(f"     中心点: ({end_x_center}, {end_y_center})")
    
    # 保存可视化结果
    cv2.imwrite(output_path, img_viz)
    print(f"\n💾 可视化结果已保存至: {output_path}")
    
    # 显示图像
    cv2.imshow('360 VLM Test', img_viz)
    print("按任意键关闭窗口...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_object_detection(img_path='temp/test_vl.jpg'):
    """
    测试物体检测功能
    """
    print("=" * 60)
    print("🔍 测试360视觉大模型物体定位功能")
    print("=" * 60)
    
    # 读取图像
    print(f"\n📷 读取图像: {img_path}")
    img_bgr = cv2.imread(img_path)
    
    if img_bgr is None:
        print(f"❌ 无法读取图像: {img_path}")
        return
    
    print(f"✅ 图像尺寸: {img_bgr.shape[1]}x{img_bgr.shape[0]}")
    
    # 系统提示词
    system_prompt = '''
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
    
    # 测试1: 识别单个物体
    print("\n" + "=" * 60)
    print("📋 测试1: 识别肠溶胶囊药品盒子")
    print("=" * 60)
    user_prompt_1 = "桌上有一个肠溶胶囊药品盒子"
    
    response_1 = call_vlm(
        user_prompt=system_prompt + "\n我现在的指令是：" + user_prompt_1,
        image=img_bgr,
        model_name="gpt-4o"
    )
    
    print(f"\n📝 大模型原始返回:\n{response_1}")
    
    # 解析JSON
    try:
        # 清理Markdown代码块
        content = response_1.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        if content.endswith('```'):
            content = content.rsplit('\n', 1)[0] if '\n' in content else content[:-3]
        content = content.strip()
        
        result_1 = json.loads(content)
        print(f"\n✅ 解析成功:")
        print(json.dumps(result_1, ensure_ascii=False, indent=2))
        
        # 可视化
        visualize_result(img_bgr, result_1, 'temp/test_vl_viz_1.jpg')
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
    
    # 测试2: 识别两个物体
    print("\n" + "=" * 60)
    print("📋 测试2: 把笔放在药品盒子上")
    print("=" * 60)
    user_prompt_2 = "把笔放在肠溶胶囊药品盒子上"
    
    response_2 = call_vlm(
        user_prompt=system_prompt + "\n我现在的指令是：" + user_prompt_2,
        image=img_bgr,
        model_name="gpt-4o"
    )
    
    print(f"\n📝 大模型原始返回:\n{response_2}")
    
    # 解析JSON
    try:
        # 清理Markdown代码块
        content = response_2.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1] if '\n' in content else content[3:]
        if content.endswith('```'):
            content = content.rsplit('\n', 1)[0] if '\n' in content else content[:-3]
        content = content.strip()
        
        result_2 = json.loads(content)
        print(f"\n✅ 解析成功:")
        print(json.dumps(result_2, ensure_ascii=False, indent=2))
        
        # 可视化
        visualize_result(img_bgr, result_2, 'temp/test_vl_viz_2.jpg')
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
    
    # 测试3: 直接要求检测所有物体
    print("\n" + "=" * 60)
    print("📋 测试3: 自由检测所有物体")
    print("=" * 60)
    user_prompt_3 = "请识别图中所有物体，并返回它们的名称和边界框坐标"
    
    response_3 = call_vlm(
        user_prompt=user_prompt_3,
        image=img_bgr,
        model_name="gpt-4o"
    )
    
    print(f"\n📝 大模型返回:\n{response_3}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_object_detection('temp/test_vl.jpg')
