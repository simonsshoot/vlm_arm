# utils_robot.py
# 同济子豪兄 2024-5-22
# 启动并连接机械臂，导入各种工具包

print('导入机械臂连接模块')

from pymycobot.mycobot280 import MyCobot280
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD
import cv2
import numpy as np
import time
from utils_pump import *

# 连接机械臂 (使用 MyCobot280 类以支持 set_fresh_mode)
mc = MyCobot280(PI_PORT, PI_BAUD)
# 设置运动模式为插补
mc.set_fresh_mode(0)

import RPi.GPIO as GPIO
# 初始化GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)        # 关闭吸泵电磁阀

def back_zero():
    '''
    机械臂归零
    '''
    print('机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def relax_arms():
    print('放松机械臂关节')
    mc.release_all_servos()

def head_shake():
    # 左右摆头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(2):
        mc.send_angle(5, 30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30,80)
        time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)

def head_dance():
    # 跳舞
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(1):
        mc.send_angles([(-0.17),(-94.3),118.91,(-39.9),59.32,(-0.52)],80)
        time.sleep(1.2)
        mc.send_angles([67.85,(-3.42),(-116.98),106.52,23.11,(-0.52)],80)
        time.sleep(1.7)
        mc.send_angles([(-38.14),(-115.04),116.63,69.69,3.25,(-11.6)],80)
        time.sleep(1.7)
        mc.send_angles([2.72,(-26.19),140.27,(-110.74),(-6.15),(-11.25)],80)
        time.sleep(1)
        mc.send_angles([0,0,0,0,0,0],80)

def head_nod():
    # 点头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    for count in range(2):
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4,13,70)
        time.sleep(0.5)
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)

def move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230):
    print('移动至指定坐标：X {} Y {}'.format(X, Y))
    mc.send_coords([X, Y, HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)

def single_joint_move(joint_index, angle):
    print('关节 {} 旋转至 {} 度'.format(joint_index, angle))
    mc.send_angle(joint_index, angle, 40)
    time.sleep(2)

def move_to_top_view():
    print('移动至俯视姿态')
    # mc.send_angles([-62.13, 8.96, -87.71, -14.41, 2.54, -16.34], 20)
    mc.send_angles([-62.13, 0, -90, 0, 0, -16.34], 20)
    time.sleep(3)

def top_view_shot(check=False, camera_index=0):
    '''
    拍摄一张图片并保存
    check：是否需要人工看屏幕确认拍照成功，再在键盘上按q键确认继续
    camera_index: 摄像头设备编号 (默认0, USB摄像头通常是0或1)
    '''
    print('    移动至俯视姿态')
    move_to_top_view()
    time.sleep(5)
    
    # 尝试打开摄像头
    print(f'    尝试打开摄像头 /dev/video{camera_index}')
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f'    ❌ 无法打开摄像头 {camera_index}，尝试备用设备')
        camera_index = 1 if camera_index == 0 else 0
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print('    ❌ 所有摄像头都无法打开')
            return
    
    # 设置摄像头参数
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 等待摄像头初始化
    print('    摄像头初始化中...')
    time.sleep(3)
    
    # 预热：读取并丢弃前10帧
    for i in range(10):
        cap.read()
        time.sleep(0.2)
    
    # 读取最终画面
    success, img_bgr = cap.read()
    
    if not success:
        print('    ❌ 摄像头读取失败')
        cap.release()
        return
    
    print(f'    ✅ 成功拍摄，分辨率: {img_bgr.shape[1]}x{img_bgr.shape[0]}')
    
    # 保存图像
    print('    保存至temp/vl_now.jpg')
    cv2.imwrite('temp/vl_now.jpg', img_bgr)

    # 屏幕上展示图像
    cv2.destroyAllWindows()   # 关闭所有opencv窗口
    cv2.imshow('zihao_vlm', img_bgr) 
    check = False
    
    if check:
        print('请确认拍照成功，按c键继续，按q键退出')
        while(True):
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'): # 按c键继续
                break
            if key == ord('q'): # 按q键退出
                # exit()
                cv2.destroyAllWindows()   # 关闭所有opencv窗口
                raise NameError('按q退出')
    else:
        if cv2.waitKey(10) & 0xFF == None:
            pass
        
    # 关闭摄像头
    cap.release()
    # 关闭图像窗口
    # cv2.destroyAllWindows()

def print_angles():
    cur_angles=mc.get_angles()
    return cur_angles

def eye2hand(X_im=160, Y_im=120):
    '''
    输入目标点在图像中的像素坐标，转换为机械臂坐标（多点标定版本）
    
    使用5个标定点进行线性插值，提高精度
    
    标定数据（像素 -> 机械臂坐标 mm）：
    点1: (464, 247) -> (26.1, -179.6)
    点2: (446, 239) -> (150, -130)
    点3: (438, 236) -> (100, -150)
    点4: (452, 235) -> (50, -170)
    点5: (455, 238) -> (70, -230)
    '''
    
    # 所有标定点数据（像素坐标）
    calibration_points_im = [
        [464, 247],  # 点1
        [446, 239],  # 点2
        [438, 236],  # 点3
        [452, 235],  # 点4
        [455, 238],  # 点5
    ]
    
    # 对应的机械臂坐标 (mm)
    calibration_points_mc = [
        [26.1, -179.6],   # 点1
        [150, -130],      # 点2
        [100, -150],      # 点3
        [50, -170],       # 点4
        [70, -230],       # 点5
    ]
    
    # 分离 X 和 Y 坐标
    X_cali_im = [pt[0] for pt in calibration_points_im]  # [464, 446, 438, 452, 455]
    Y_cali_im = [pt[1] for pt in calibration_points_im]  # [247, 239, 236, 235, 238]
    
    X_cali_mc = [pt[0] for pt in calibration_points_mc]  # [26.1, 150, 100, 50, 70]
    Y_cali_mc = [pt[1] for pt in calibration_points_mc]  # [-179.6, -130, -150, -170, -230]
    
    # 对 X 坐标进行排序（np.interp 要求递增）
    X_sorted_indices = np.argsort(X_cali_im)
    X_cali_im_sorted = [X_cali_im[i] for i in X_sorted_indices]
    X_cali_mc_sorted = [X_cali_mc[i] for i in X_sorted_indices]
    
    # 对 Y 坐标进行排序
    Y_sorted_indices = np.argsort(Y_cali_im)
    Y_cali_im_sorted = [Y_cali_im[i] for i in Y_sorted_indices]
    Y_cali_mc_sorted = [Y_cali_mc[i] for i in Y_sorted_indices]
    
    # X 线性插值
    X_mc = int(np.interp(X_im, X_cali_im_sorted, X_cali_mc_sorted))
    
    # Y 线性插值
    Y_mc = int(np.interp(Y_im, Y_cali_im_sorted, Y_cali_mc_sorted))
    
    return X_mc, Y_mc

# 吸泵吸取并移动物体
def pump_move(mc, XY_START=[230,-50], HEIGHT_START=90, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220):

    '''
    用吸泵，将物体从起点吸取移动至终点

    mc：机械臂实例
    XY_START：起点机械臂坐标
    HEIGHT_START：起点高度，方块用90，药盒子用70
    XY_END：终点机械臂坐标
    HEIGHT_END：终点高度
    HEIGHT_SAFE：搬运途中安全高度
    '''
    
    # 初始化GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)
    GPIO.setup(21, GPIO.OUT)

    # 设置运动模式为插补
    mc.set_fresh_mode(0)
    
    # # 机械臂归零
    # print('    机械臂归零')
    # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    # time.sleep(4)
    
    # 吸泵移动至物体上方
    print('    吸泵移动至物体上方')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)

    # 开启吸泵
    pump_on()
    time.sleep(1.5)  # 增加等待时间，确保吸力充分建立
    print("current coords:")
    print(mc.get_coords())
    
    # 吸泵向下吸取物体
    print('    吸泵向下吸取物体')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0], XY_START[1], 120, 0, 180, 90], 20, 0)
    time.sleep(4)
    print(mc.get_coords())
    
    # 额外等待，确保物体被牢固吸住
    print('    确保物体吸附稳定...')
    # mc.send_coords([150,-126,90,0,180,90],20,0)

    time.sleep(1.5)

    # 升起物体
    print('    升起物体')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(4)

    # 搬运物体至目标上方
    print('    搬运物体至目标上方')
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(4)

    # 向下放下物体
    print('    向下放下物体')
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_END, 0, 180, 90], 20, 0)
    time.sleep(3)

    # 关闭吸泵
    pump_off()
    time.sleep(1.5)  
    print("current coords2:")
    print(mc.get_coords())

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
