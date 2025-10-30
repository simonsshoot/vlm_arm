# agent_go.py
# 同济子豪兄 2024-5-27
# 看懂“图像”、听懂“人话”、指哪打哪的机械臂
# 机械臂+大模型+多模态+语音识别=具身智能体Agent

print('\n听得懂人话、看得懂图像、拎得清动作的具身智能机械臂！')
print('同济子豪兄 2024-5-27 \n')

# 导入常用函数
from utils_asr import *             # 录音+语音识别
from utils_robot import *           # 连接机械臂
from utils_llm import *             # 大语言模型API
from utils_led import *             # 控制LED灯颜色
from utils_camera import *          # 摄像头
from utils_robot import *           # 机械臂运动
from utils_pump import *            # GPIO、吸泵
from utils_vlm_move import *        # 多模态大模型识别图像，吸泵吸取并移动物体
from utils_drag_teaching import *   # 拖动示教
from utils_agent import *           # 智能体Agent编排
from utils_tts import *             # 语音合成模块

# print('播放欢迎词')
pump_off()
# back_zero()
# play_wav('asset/welcome.wav')

message=[]
message.append({"role":"system","content":AGENT_SYS_PROMPT})

def read_order_from_file(file_path='temp/test_input.txt'):
    '''
    从文本文件读取指令
    参数:
        file_path: 文本文件路径
    返回:
        指令字符串
    '''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            order = f.read().strip()
        print(f'从文件读取指令: {order}')
        return order
    except FileNotFoundError:
        print(f'文件不存在: {file_path}，创建默认指令文件')
        default_order = '先归零，再摇头，然后把绿色方块放在篮球上'
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_order)
        return default_order
    except Exception as e:
        print(f'读取文件失败: {e}')
        return None

def read_multi_orders_from_file(file_path='temp/test_input.txt'):
    '''
    从文本文件读取多条指令，每条指令以"；"分割，"END；"表示结束
    参数:
        file_path: 文本文件路径
    返回:
        指令列表
    '''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        print(f'从文件读取多步指令:\n{content}\n')
        
        # 按"；"分割指令
        raw_orders = content.split('；')
        orders = []
        
        for order in raw_orders:
            order = order.strip()
            # 如果遇到END，停止读取
            if order.upper() == 'END' or order == '':
                break
            orders.append(order)
        
        print(f'解析出 {len(orders)} 条指令:')
        for i, order in enumerate(orders, 1):
            print(f'  {i}. {order}')
        print()
        
        return orders
    except FileNotFoundError:
        print(f'文件不存在: {file_path}，创建默认多步指令文件')
        default_content = '先归零；\n摇头；\n把绿色方块放在篮球上；\nEND；'
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(default_content)
        return ['先归零', '摇头', '把绿色方块放在篮球上']
    except Exception as e:
        print(f'读取文件失败: {e}')
        return None

def agent_play():
    '''
    主函数，语音控制机械臂智能体编排动作
    '''
    # 归零
    back_zero()
    
    # print('测试摄像头')
    # check_camera()
    
    # 输入指令
    print('\n请选择输入方式：')
    print('【默认】直接按Enter - 从txt文件读取多步指令 (temp/test_input.txt)')
    print('【数字】输入秒数 - 录音并语音识别')
    print('【k】键盘输入')
    print('【c】测试指令')
    start_record_ok = input('请选择: ').strip()
    
    if start_record_ok == '':
        # 默认从txt文件读取多步指令
        orders = read_multi_orders_from_file('temp/test_input.txt')
        if orders is None or len(orders) == 0:
            raise NameError('从文件读取指令失败或无有效指令，退出')
    elif str.isnumeric(start_record_ok):
        DURATION = int(start_record_ok)
        record(DURATION=DURATION)   # 录音
        order = speech_recognition() # 语音识别
        orders = [order]  # 单条指令也放入列表
    elif start_record_ok == 'k':
        order = input('请输入指令: ')
        orders = [order]  # 单条指令也放入列表
    elif start_record_ok == 'c':
        order = '先归零，再摇头，然后把绿色方块放在篮球上'
        orders = [order]  # 单条指令也放入列表
    else:
        print('无指令，退出')
        raise NameError('无指令，退出')
    
    # 循环执行每条指令
    for idx, order in enumerate(orders, 1):
        print(f'\n{"="*60}')
        print(f'正在执行第 {idx}/{len(orders)} 条指令: {order}')
        print(f'{"="*60}\n')
        
        # 智能体Agent编排动作
        message.append({"role": "user", "content": order})
        # eval() 是 Python 的内置函数，它可以将字符串当作 Python 代码执行。
        plan=agent_plan(message)
        print('agent_plan返回内容:\n', plan)
        agent_plan_output = eval(plan)
        
        print('智能体编排动作如下\n', agent_plan_output)
        # plan_ok = input('是否继续？按c继续，按q退出')
        plan_ok = 'c'
        if plan_ok == 'c':
            response = agent_plan_output['response'] # 获取机器人想对我说的话
            print('开始语音合成')
            tts(response)                     # 语音合成，导出wav音频文件
            play_wav('temp/tts.wav')          # 播放语音合成音频文件
            output_other=''
            for each in agent_plan_output['function']: # 运行智能体规划编排的每个函数
                print('开始执行动作', each)
                ret=eval(each)
                if ret!=None:
                    output_other=ret
        elif plan_ok =='q':
            # exit()
            raise NameError('按q退出')
        agent_plan_output['response']+='.'+ output_other
        message.append({"role":"assistant","content":str(agent_plan_output)})
        
        print(f'\n第 {idx}/{len(orders)} 条指令执行完成\n')
    
    print(f'\n{"="*60}')
    print(f'所有 {len(orders)} 条指令执行完成!')
    print(f'{"="*60}\n')

# agent_play()
if __name__ == '__main__':
    while True:
        agent_play()

