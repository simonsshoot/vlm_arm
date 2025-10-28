# vlm_agent_go.py
# 基于360视觉大模型的智能机械臂控制程序
# 从txt文件读取指令，使用VLM+Agent编排动作

print('\n360视觉大模型 + Agent编排 智能机械臂！')
print('听得懂人话、看得懂图像、拎得清动作\n')

# 导入常用函数
from utils_robot import *           # 连接机械臂
from utils_vlm import *             # 视觉大模型
from utils_pump import *            # GPIO、吸泵
from utils_led import *             # 控制LED灯颜色
from utils_camera import *          # 摄像头
from utils_agent import *           # 智能体Agent编排
from utils_tts import *             # 语音合成
from utils_vlm_move import *        # VLM移动物体
import time

# 初始化对话历史
message = []
message.append({"role": "system", "content": AGENT_SYS_PROMPT})

def read_instruction_from_file(file_path='temp/vlm_instruction.txt'):
    '''
    从文本文件读取指令
    参数:
        file_path: 文本文件路径
    返回:
        指令字符串
    '''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            instruction = f.read().strip()
        print(f'✅ 从文件读取指令: {instruction}')
        return instruction
    except FileNotFoundError:
        print(f'⚠️  文件不存在: {file_path}，创建默认指令文件')
        default_instruction = '桌上有一个小人，移动到该处并用吸泵吸取'
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_instruction)
        return default_instruction
    except Exception as e:
        print(f'❌ 读取文件失败: {e}')
        return None

def vlm_360_locate(PROMPT='桌上有一个小人'):
    '''
    使用360视觉大模型识别图像，返回目标物体的像素坐标和机械臂坐标
    
    参数:
        PROMPT: 用户指令（描述目标物体）
    
    返回:
        dict: {
            'pixel_x': 像素x坐标,
            'pixel_y': 像素y坐标,
            'robot_x': 机械臂x坐标,
            'robot_y': 机械臂y坐标,
            'success': 是否成功
        }
    '''
    
    print(f'\n=== 360视觉大模型定位物体: {PROMPT} ===\n')
    
    ## 第一步：拍摄俯视图
    print('【第1步】拍摄俯视图')
    top_view_shot(check=False, camera_index=0)
    img_path = 'temp/vl_now.jpg'
    
    ## 第二步：调用360视觉大模型识别物体
    print('【第2步】调用360视觉大模型识别物体')
    
    n = 1
    max_retries = 3
    result = None
    
    while n <= max_retries:
        try:
            print(f'    尝试第 {n}/{max_retries} 次访问360视觉大模型...')
            result = vision_360_api(PROMPT, img_path=img_path, vlm_option=0)
            print('    ✅ 360视觉大模型调用成功！')
            print(f'    识别结果: {result}')
            break
        except Exception as e:
            print(f'    ❌ 大模型返回错误: {e}')
            if n < max_retries:
                print(f'    等待2秒后重试...')
                time.sleep(2)
            n += 1
    
    if result is None:
        print('❌ 多次尝试后仍无法获取大模型结果')
        return {'success': False}
    
    ## 第三步：提取起点坐标并可视化
    print('【第3步】提取坐标并可视化')
    try:
        # 读取图像
        img_bgr = cv2.imread(img_path)
        img_h = img_bgr.shape[0]
        img_w = img_bgr.shape[1]
        FACTOR = 999
        
        # 提取起点坐标
        START_NAME = result['start']
        START_X_MIN = int(result['start_xyxy'][0][0] * img_w / FACTOR)
        START_Y_MIN = int(result['start_xyxy'][0][1] * img_h / FACTOR)
        START_X_MAX = int(result['start_xyxy'][1][0] * img_w / FACTOR)
        START_Y_MAX = int(result['start_xyxy'][1][1] * img_h / FACTOR)
        START_X_CENTER = int((START_X_MIN + START_X_MAX) / 2)
        START_Y_CENTER = int((START_Y_MIN + START_Y_MAX) / 2)
        
        print(f'    识别到物体: {START_NAME}')
        print(f'    边界框: ({START_X_MIN}, {START_Y_MIN}) -> ({START_X_MAX}, {START_Y_MAX})')
        print(f'    中心点像素坐标: ({START_X_CENTER}, {START_Y_CENTER})')
        
        # 简单可视化（只画起点）
        img_viz = img_bgr.copy()
        img_viz = cv2.rectangle(img_viz, (START_X_MIN, START_Y_MIN), (START_X_MAX, START_Y_MAX), [0, 0, 255], thickness=3)
        img_viz = cv2.circle(img_viz, [START_X_CENTER, START_Y_CENTER], 6, [0, 0, 255], thickness=-1)
        
        # 写中文物体名称
        from PIL import Image, ImageDraw, ImageFont
        img_rgb = cv2.cvtColor(img_viz, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(img_pil)
        try:
            font = ImageFont.truetype('asset/SimHei.ttf', 32)
        except:
            font = ImageFont.load_default()
        draw.text((START_X_MIN, START_Y_MIN-35), START_NAME, font=font, fill=(255, 0, 0, 1))
        img_viz = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        cv2.imwrite('temp/vl_now_viz.jpg', img_viz)
        print('    保存可视化结果至 temp/vl_now_viz.jpg')
        
    except Exception as e:
        print(f'❌ 坐标提取失败: {e}')
        return {'success': False}
    
    ## 第四步：手眼标定，将像素坐标转换为机械臂坐标
    print('【第4步】手眼标定，像素坐标转机械臂坐标')
    TARGET_X_MC, TARGET_Y_MC = eye2hand(START_X_CENTER, START_Y_CENTER)
    print(f'    像素坐标: ({START_X_CENTER}, {START_Y_CENTER})')
    print(f'    机械臂坐标: ({TARGET_X_MC}, {TARGET_Y_MC})')
    
    return {
        'pixel_x': START_X_CENTER,
        'pixel_y': START_Y_CENTER,
        'robot_x': TARGET_X_MC,
        'robot_y': TARGET_Y_MC,
        'success': True
    }

def vlm_360_move(PROMPT='桌上有一个小人'):
    '''
    使用360视觉大模型识别物体并移动到该位置
    
    参数:
        PROMPT: 用户指令（描述目标物体）
    
    返回:
        成功提示字符串
    '''
    print(f'\n=== 360视觉定位并移动: {PROMPT} ===\n')
    
    # 调用定位函数
    result = vlm_360_locate(PROMPT)
    
    if not result['success']:
        return '❌ 定位失败'
    
    # 提取机械臂坐标
    robot_x = result['robot_x']
    robot_y = result['robot_y']
    
    # 移动到目标位置
    print(f'\n=== 移动到目标位置 ({robot_x}, {robot_y}) ===\n')
    move_to_coords(X=robot_x, Y=robot_y)
    
    return f'✅ 已移动到 ({robot_x}, {robot_y})'

def vlm_agent_play():
    '''
    主函数，使用VLM视觉+Agent编排动作
    '''
    # 归零
    back_zero()
    
    # 输入指令
    print('\n请选择输入方式：')
    print('【默认】直接按Enter - 从txt文件读取 (temp/vlm_instruction.txt)')
    print('【k】键盘输入')
    print('【c】测试指令')
    start_input = input('请选择: ').strip()
    
    if start_input == '':
        # 默认从txt文件读取
        order = read_instruction_from_file('temp/vlm_instruction.txt')
        if order is None:
            raise NameError('从文件读取指令失败，退出')
    elif start_input == 'k':
        order = input('请输入指令: ')
    elif start_input == 'c':
        order = '先归零，再移动到小人的位置，然后摇头'
    else:
        print('无指令，退出')
        raise NameError('无指令，退出')
    
    print(f'\n📝 用户指令: {order}\n')
    
    # 智能体Agent编排动作
    message.append({"role": "user", "content": order})
    agent_plan_output = eval(agent_plan(message, model='360'))
    
    print('🤖 智能体编排动作如下:\n', agent_plan_output)
    
    # 执行编排的动作
    plan_ok = 'c'  # 自动继续
    if plan_ok == 'c':
        response = agent_plan_output['response']  # 获取机器人想说的话
        print(f'\n💬 机器人回复: {response}')
        
        # 语音合成
        try:
            print('🔊 开始语音合成')
            tts(response)
            play_wav('temp/tts.wav')
        except Exception as e:
            print(f'⚠️  语音合成失败: {e}')
        
        output_other = ''
        
        # 执行每个函数
        for each in agent_plan_output['function']:
            print(f'\n▶️  开始执行动作: {each}')
            try:
                ret = eval(each)
                if ret is not None:
                    output_other = str(ret)
                    print(f'    返回结果: {output_other}')
            except Exception as e:
                print(f'❌ 执行失败: {e}')
                continue
    elif plan_ok == 'q':
        raise NameError('按q退出')
    
    # 更新对话历史
    agent_plan_output['response'] += '.' + output_other
    message.append({"role": "assistant", "content": str(agent_plan_output)})
    
    print('\n✅ 任务完成！\n')

if __name__ == '__main__':
    try:
        # 初始化
        print('初始化...')
        pump_off()
        
        # 循环执行任务
        while True:
            vlm_agent_play()
            
    except KeyboardInterrupt:
        print('\n\n检测到 Ctrl+C，正在退出...')
        pump_off()
        GPIO.cleanup()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f'\n程序异常: {e}')
        try:
            pump_off()
            GPIO.cleanup()
            cv2.destroyAllWindows()
        except:
            pass
