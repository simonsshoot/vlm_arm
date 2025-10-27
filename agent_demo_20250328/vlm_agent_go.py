# vlm_agent_go.py
# 基于360视觉大模型的智能机械臂控制程序
# 从txt文件读取指令，使用360 VLM进行物体定位和抓取

print('\n360视觉大模型驱动的智能机械臂！')
print('支持从文件读取指令，自动定位并抓取物体\n')

# 导入常用函数
from utils_robot import *           # 连接机械臂
from utils_vlm import *             # 视觉大模型
from utils_pump import *            # GPIO、吸泵
from utils_led import *             # 控制LED灯颜色
from utils_camera import *
import time

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

def vlm_360_move(PROMPT='桌上有一个小人，移动到该处并用吸泵吸取'):
    '''
    使用360视觉大模型识别图像，吸泵吸取物体
    
    参数:
        PROMPT: 用户指令
    '''
    
    print('\n=== 360视觉大模型识别并抓取物体 ===\n')
    
    ## 第一步：机械臂归零
    print('【第1步】机械臂归零')
    back_zero()
    time.sleep(2)
    
    ## 第二步：给出指令
    print(f'【第2步】指令: {PROMPT}')
    
    ## 第三步：拍摄俯视图
    print('【第3步】拍摄俯视图')
    top_view_shot(check=False,camera_index=0)
    img_path = 'temp/vl_now.jpg'
    
    ## 第四步：调用360视觉大模型识别物体
    print('【第4步】调用360视觉大模型识别物体')
    
    n = 1
    max_retries = 5
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
        print('❌ 多次尝试后仍无法获取大模型结果，任务失败')
        return False
    
    ## 第五步：视觉大模型输出结果后处理和可视化
    print('【第5步】结果可视化')
    try:
        START_X_CENTER, START_Y_CENTER, END_X_CENTER, END_Y_CENTER = post_processing_viz(
            result, img_path, check=False
        )
    except Exception as e:
        print(f'❌ 可视化失败: {e}')
        return False
    
    ## 第六步：手眼标定，将像素坐标转换为机械臂坐标
    print('【第6步】手眼标定，像素坐标转机械臂坐标')
    # 目标物体，机械臂坐标
    TARGET_X_MC, TARGET_Y_MC = eye2hand(START_X_CENTER, START_Y_CENTER)
    print(f'    像素坐标: ({START_X_CENTER}, {START_Y_CENTER})')
    print(f'    机械臂坐标: ({TARGET_X_MC}, {TARGET_Y_MC})')
    
    ## 第七步：移动到目标位置上方
    print('【第7步】移动到目标位置上方')
    HEIGHT_SAFE = 220  # 安全高度
    HEIGHT_GRAB = 90   # 抓取高度
    
    try:
        # 移动到目标上方
        print(f'    移动到 [{TARGET_X_MC}, {TARGET_Y_MC}, {HEIGHT_SAFE}]')
        mc.send_coords([TARGET_X_MC, TARGET_Y_MC, HEIGHT_SAFE, 0, 180, 90], 20, 0)
        time.sleep(4)
        
        ## 第八步：下降并吸取
        print('【第8步】下降并吸取物体')
        
        # 打开吸泵
        print('    打开吸泵')
        pump_on()
        time.sleep(1.5)
        
        # 下降到抓取高度
        print(f'    下降到抓取高度 {HEIGHT_GRAB}mm')
        mc.send_coords([TARGET_X_MC, TARGET_Y_MC, HEIGHT_GRAB, 0, 180, 90], 15, 0)
        time.sleep(4)
        
        # 等待确保吸附
        print('    等待物体吸附稳定...')
        time.sleep(2)
        
        ## 第九步：提升物体
        print('【第9步】提升物体')
        mc.send_coords([TARGET_X_MC, TARGET_Y_MC, HEIGHT_SAFE, 0, 180, 90], 15, 0)
        time.sleep(4)
        
        ## 第十步：归零并释放
        print('【第10步】归零并释放物体')
        back_zero()
        time.sleep(3)
        
        # 关闭吸泵
        print('    关闭吸泵')
        pump_off()
        time.sleep(1)
        
        print('\n✅ 任务完成！\n')
        return True
        
    except Exception as e:
        print(f'❌ 机械臂运动失败: {e}')
        print('    尝试关闭吸泵...')
        try:
            pump_off()
        except:
            pass
        return False
    
    finally:
        # 清理资源
        cv2.destroyAllWindows()

def main():
    '''
    主函数
    '''
    print('=== 360视觉大模型机械臂控制程序 ===\n')
    
    # 初始化
    print('初始化...')
    pump_off()
    
    # 输入方式选择
    print('\n请选择输入方式：')
    print('【1】从文件读取指令 (temp/vlm_instruction.txt)')
    print('【2】键盘输入指令')
    print('【3】使用默认指令')
    
    choice = input('请选择 (直接按Enter默认为1): ').strip()
    
    if choice == '' or choice == '1':
        # 从文件读取
        instruction = read_instruction_from_file('temp/vlm_instruction.txt')
        if instruction is None:
            print('读取指令失败，退出程序')
            return
    elif choice == '2':
        # 键盘输入
        instruction = input('请输入指令: ').strip()
        if not instruction:
            print('指令为空，使用默认指令')
            instruction = '桌上有一个小人，移动到该处并用吸泵吸取'
    elif choice == '3':
        # 默认指令
        instruction = '桌上有一个小人，移动到该处并用吸泵吸取'
        print(f'使用默认指令: {instruction}')
    else:
        print('无效选择，使用默认指令')
        instruction = '桌上有一个小人，移动到该处并用吸泵吸取'
    
    # 执行任务
    print(f'\n开始执行任务...\n')
    success = vlm_360_move(instruction)
    
    if success:
        print('🎉 任务执行成功！')
    else:
        print('⚠️  任务执行失败，请检查错误信息')
    
    # 清理
    print('\n清理资源...')
    GPIO.cleanup()
    cv2.destroyAllWindows()
    # move_to_top_view()
    # check_camera()
    back_zero()

if __name__ == '__main__':
    try:
        main()
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
