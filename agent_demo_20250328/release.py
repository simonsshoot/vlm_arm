from utils_robot import *
import cv2
import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
mc = MyCobot280(PI_PORT, PI_BAUD)  # 修正：改为 mc
mc.set_fresh_mode(0)
import RPi.GPIO as GPIO
# 初始化GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)   

def show_camera():
    cap = cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.5)
    
    print('摄像头已打开，按 q 键退出')
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('无法读取摄像头')
            break
        
        current_angles = mc.get_angles()
        info_frame = frame.copy()

        cv2.putText(info_frame, f'Angles: {[round(a, 1) for a in current_angles]}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 显示画面
        cv2.imshow('Eye2Hand Calibration', info_frame)
        
        # 添加退出机制
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            print('退出程序')
            break
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    show_camera()