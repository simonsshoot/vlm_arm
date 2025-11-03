# utils_pump.py
# 同济子豪兄 2024-5-22
# GPIO引脚、吸泵相关函数

print('导入吸泵控制模块')
import RPi.GPIO as GPIO
import time

# 初始化GPIO（参考官方代码）
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
# 初始状态：关闭吸泵（高电平）
GPIO.output(20, 1)
GPIO.output(21, 1)

def pump_on():
    '''
    开启吸泵（参考官方代码）
    GPIO 20 输出低电平 (0) 开启吸泵
    '''
    print('    开启吸泵')
    GPIO.output(20, 0)

def pump_off():
    '''
    关闭吸泵，吸泵放气，释放物体（参考官方代码）
    '''
    print('    关闭吸泵')
    # 1. 关闭吸泵电磁阀（高电平）
    GPIO.output(20, 1)
    time.sleep(0.05)
    
    # 2. 打开泄气阀门放气（低电平）
    GPIO.output(21, 0)
    time.sleep(1)  # 泄气时间延长到1秒，确保完全释放
    
    # 3. 关闭泄气阀门（高电平）
    GPIO.output(21, 1)
    time.sleep(0.05)