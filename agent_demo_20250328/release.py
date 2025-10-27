from utils_robot import *
import cv2
import time
def show_camera():
    cap=cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.5)
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


if __name__=='__main__':
    show_camera()