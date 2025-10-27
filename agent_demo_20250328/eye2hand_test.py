from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils_robot import *
from camera_check import *

mc = MyCobot280(PI_PORT, PI_BAUD)
mc.set_fresh_mode(0)
import RPi.GPIO as GPIO
# 初始化GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)   

def eye2hand_calibration():
    """
    手眼标定函数：实时显示摄像头画面，同时可以控制机械臂移动
    
    键盘操作：
    - 1-6: 选择要控制的关节 (1=关节1, 2=关节2, ..., 6=关节6)
    - +数字: 增加角度 (如 +5, +10)
    - -数字: 减少角度 (如 -5, -10)
    - r: 记录当前位置的坐标和角度
    - z: 归零
    - s: 保存当前画面
    - q: 退出
    """
    print('\n=== 手眼标定程序 ===')
    print('键盘操作说明：')
    print('  1-6: 选择关节')
    print('  +数字: 增加角度 (如 +5, +10)')
    print('  -数字: 减少角度 (如 -5, -10)')
    print('  r: 记录当前位置')
    print('  z: 归零')
    print('  s: 保存画面')
    print('  q: 退出\n')
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.5)
    
    selected_joint = 1  # 默认选择关节1
    calibration_points = []  # 存储标定点
    input_buffer = ""  # 用于存储输入的数字
    
    while True:
        # 读取摄像头画面
        ret, frame = cap.read()
        if not ret:
            print('无法读取摄像头')
            break
        
        # 获取当前机械臂角度
        current_angles = mc.get_angles()
        
        # 在画面上显示信息
        info_frame = frame.copy()
        cv2.putText(info_frame, f'Selected Joint: {selected_joint}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(info_frame, f'Angles: {[round(a, 1) for a in current_angles]}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(info_frame, f'Points recorded: {len(calibration_points)}', (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        if input_buffer:
            cv2.putText(info_frame, f'Input: {input_buffer}', (10, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # 显示画面
        cv2.imshow('Eye2Hand Calibration', info_frame)
        
        # 键盘控制
        key = cv2.waitKey(10) & 0xFF
        
        # 选择关节
        if key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
            selected_joint = int(chr(key))
            print(f'选择关节 {selected_joint}')
            input_buffer = ""
        
        # 数字输入 (0-9)
        elif key >= ord('0') and key <= ord('9'):
            input_buffer += chr(key)
            print(f'输入: {input_buffer}')
        
        # 加号 - 增加角度
        elif key == ord('=') or key == ord('+'):
            if input_buffer:
                try:
                    angle_change = float(input_buffer)
                    current_angle = current_angles[selected_joint - 1]
                    new_angle = current_angle + angle_change
                    mc.send_angle(selected_joint, new_angle, 30)
                    print(f'关节 {selected_joint}: {current_angle:.1f}° -> {new_angle:.1f}° (+{angle_change}°)')
                    input_buffer = ""
                    time.sleep(0.1)
                except ValueError:
                    print('输入无效')
                    input_buffer = ""
            else:
                print('请先输入角度值，如: 5 然后按 +')
        
        # 减号 - 减少角度
        elif key == ord('-') or key == ord('_'):
            if input_buffer:
                try:
                    angle_change = float(input_buffer)
                    current_angle = current_angles[selected_joint - 1]
                    new_angle = current_angle - angle_change
                    mc.send_angle(selected_joint, new_angle, 30)
                    print(f'关节 {selected_joint}: {current_angle:.1f}° -> {new_angle:.1f}° (-{angle_change}°)')
                    input_buffer = ""
                    time.sleep(0.1)
                except ValueError:
                    print('输入无效')
                    input_buffer = ""
            else:
                print('请先输入角度值，如: 5 然后按 -')
        
        # 清除输入缓冲
        elif key == 27:  # ESC键
            input_buffer = ""
            print('清除输入')
        
        # 归零
        elif key == ord('z'):
            print('归零中...')
            back_zero()
        
        # 记录标定点
        elif key == ord('r'):
            coords = mc.get_coords()
            point_info = {
                'angles': current_angles.copy(),
                'coords': coords,
                'timestamp': time.time()
            }
            calibration_points.append(point_info)
            print(f'\n✅ 记录标定点 #{len(calibration_points)}:')
            print(f'   角度: {[round(a, 1) for a in current_angles]}')
            print(f'   坐标: {coords}\n')
        
        # 保存画面
        elif key == ord('s'):
            filename = f'temp/calibration_{int(time.time())}.jpg'
            cv2.imwrite(filename, frame)
            print(f'画面已保存: {filename}')
        
        # 退出
        elif key == ord('q'):
            print('\n退出标定程序')
            break
    
    # 清理
    cap.release()
    cv2.destroyAllWindows()
    
    # 显示所有标定点
    if calibration_points:
        print(f'\n=== 共记录 {len(calibration_points)} 个标定点 ===')
        for i, point in enumerate(calibration_points, 1):
            print(f'标定点 {i}:')
            print(f'  角度: {[round(a, 1) for a in point["angles"]]}')
            print(f'  坐标: {point["coords"]}\n')
    
    return calibration_points

def main():
    print('开始眼手协调测试程序')
    back_zero()
    time.sleep(2)
    print('移动到俯视姿态')
    move_to_top_view()
    
    # LED变蓝是机械臂的错误指示（逆运动学无解）
    print('移动到标定起始位置')
    move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230)
    
    # 使用新的手眼标定函数
    calibration_points = eye2hand_calibration()

if __name__=='__main__':
    main()