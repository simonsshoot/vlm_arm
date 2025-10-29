# test_pump.py
# 吸泵功能测试脚本
# 测试吸泵的开启、关闭、以及吸取物体的完整流程

import time
import RPi.GPIO as GPIO
from utils_pump import pump_on, pump_off
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

def test_pump_basic():
    """
    测试吸泵基本开关功能
    """
    print('\n========== 测试1: 吸泵基本开关 ==========')
    
    # 初始化GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    
    print('开启吸泵...')
    pump_on()
    print('吸泵已开启，等待3秒')
    time.sleep(3)
    
    print('关闭吸泵...')
    pump_off()
    print('吸泵已关闭')
    
    print('✅ 基本开关测试完成\n')

def test_pump_with_movement():
    """
    测试吸泵配合机械臂运动
    模拟吸取物体的完整流程
    """
    print('\n========== 测试2: 吸泵配合机械臂运动 ==========')
    
    # 连接机械臂
    print('连接机械臂...')
    mc = MyCobot280(PI_PORT, PI_BAUD)
    mc.set_fresh_mode(0)  # 插补模式
    
    # 初始化GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    
    # 归零
    print('机械臂归零...')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
    
    # 移动到测试位置上方
    test_x, test_y = 150, -130
    height_safe = 230
    height_low = 90
    
    print(f'移动到测试位置上方 X:{test_x}, Y:{test_y}, Z:{height_safe}')
    mc.send_coords([test_x, test_y, height_safe, 0, 180, 90], 20, 0)
    time.sleep(4)
    
    # 开启吸泵
    print('开启吸泵...')
    pump_on()
    time.sleep(1.5)
    
    # 向下移动吸取
    print(f'向下移动至 Z:{height_low} 吸取物体')
    mc.send_coords([test_x, test_y, height_low, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 等待吸附稳定
    print('等待吸附稳定...')
    time.sleep(2)
    
    # 升起
    print(f'升起至 Z:{height_safe}')
    mc.send_coords([test_x, test_y, height_safe, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 移动到新位置
    target_x, target_y = 100, 220
    print(f'移动到目标位置 X:{target_x}, Y:{target_y}, Z:{height_safe}')
    mc.send_coords([target_x, target_y, height_safe, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 向下放置
    print(f'向下放置至 Z:{height_low}')
    mc.send_coords([target_x, target_y, height_low, 0, 180, 90], 20, 0)
    time.sleep(3)
    
    # 关闭吸泵
    print('关闭吸泵...')
    pump_off()
    time.sleep(1)
    
    # 归零
    print('机械臂归零...')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
    
    print('✅ 吸泵运动测试完成\n')

def test_pump_cycle():
    """
    测试吸泵多次开关循环
    """
    print('\n========== 测试3: 吸泵多次开关循环 ==========')
    
    # 初始化GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)
    
    cycles = 3
    for i in range(cycles):
        print(f'\n第 {i+1}/{cycles} 次循环:')
        print('  开启吸泵')
        pump_on()
        time.sleep(2)
        
        print('  关闭吸泵')
        pump_off()
        time.sleep(1)
    
    print('\n✅ 循环测试完成\n')

def main():
    """
    主测试函数
    """
    print('\n' + '='*50)
    print('吸泵功能测试程序')
    print('='*50)
    
    while True:
        print('\n请选择测试项目:')
        print('1 - 测试吸泵基本开关')
        print('2 - 测试吸泵配合机械臂运动(完整流程)')
        print('3 - 测试吸泵多次开关循环')
        print('0 - 退出')
        
        choice = input('\n请输入选项 (0-3): ').strip()
        
        if choice == '1':
            test_pump_basic()
        elif choice == '2':
            test_pump_with_movement()
        elif choice == '3':
            test_pump_cycle()
        elif choice == '0':
            print('退出测试程序')
            # 确保GPIO清理
            GPIO.cleanup()
            break
        else:
            print('❌ 无效选项，请重新输入')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n程序被用户中断')
        GPIO.cleanup()
    except Exception as e:
        print(f'\n❌ 发生错误: {e}')
        GPIO.cleanup()
