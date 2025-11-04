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
mc = MyCobot280("/dev/ttyAMA0", 1000000)
# 设置运动模式为插补
mc.set_fresh_mode(0)

import RPi.GPIO as GPIO
# 初始化GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
# GPIO.output(20, 1)        # 关闭吸泵电磁阀

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
    # mc.send_angles([-62.13, 0, -90, 0, 0, -16.34], 20)
    mc.send_coords([13, -160, 212, 180, 3.31, -135.81], 10)
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
    # calibration_points_im = [
    #     [464, 247],  # 点1
    #     [446, 239],  # 点2
    #     [438, 236],  # 点3
    #     [452, 235],  # 点4
    #     [455, 238],  # 点5
    # ]
    
    # # 对应的机械臂坐标 (mm)
    # calibration_points_mc = [
    #     [26.1, -179.6],   # 点1
    #     [150, -130],      # 点2
    #     [100, -150],      # 点3
    #     [50, -170],       # 点4
    #     [70, -230],       # 点5
    # ]

    calibration_points_im =[
        [395,214],
        [408,246],
        [406,230]
    ]

    calibration_points_mc =[
        [13,-160],
        [100,-100],
        [60,-190]
    ]
    # calibration_points_im = [
    #     [125,302],
    #     [441.4,139]
    # ]
    # calibration_points_mc = [
    #     [-16,-220],
    #     [129,-145]
    # ]
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
    
    # return X_mc, Y_mc
    return 60,-190
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
    
    # GPIO已在utils_pump.py导入时初始化，无需重复初始化
    
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
    # pump_on()
    GPIO.output(20, 0)
    time.sleep(1.5)  # 增加等待时间，确保吸力充分建立
    print("current coords:")
    print(mc.get_coords())
    
    # 吸泵向下吸取物体
    print('    吸泵向下吸取物体')
    print(XY_START[0])
    print(XY_START[1])
    mc.send_coords([XY_START[0], XY_START[1], 100, 0, 180, 90], 30, 0)
    # new add
    GPIO.output(20, 1)
    time.sleep(0.05)
    GPIO.output(21, 0)
    time.sleep(3)
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
    GPIO.output(21, 1)
    time.sleep(0.05)

    # 关闭吸泵
    # pump_off()
    time.sleep(1.5)  
    print("current coords2:")
    print(mc.get_coords())

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def move_fast(X_START, Y_START, X_END, Y_END, HEIGHT=100, SPEED=60):
    '''
    机械臂从一个坐标快速平移到另一个坐标
    
    参数:
        X_START: 起点X坐标 (mm)
        Y_START: 起点Y坐标 (mm)
        X_END: 终点X坐标 (mm)
        Y_END: 终点Y坐标 (mm)
        HEIGHT: 移动高度，默认220mm（安全高度）
        SPEED: 移动速度，默认80（较快）
    '''
    print(f'快速平移: ({X_START},{Y_START}) → ({X_END},{Y_END}), 高度={HEIGHT}mm, 速度={SPEED}')
    
    # 设置运动模式为插补
    mc.set_fresh_mode(0)
    
    # 移动到起点
    print(f'    移动到起点: X={X_START}, Y={Y_START}')
    mc.send_coords([X_START, Y_START, HEIGHT, 0, 180, 90], SPEED, 0)
    time.sleep(2)
    
    # 快速平移到终点
    print(f'    快速平移到终点: X={X_END}, Y={Y_END}')
    mc.send_coords([X_END, Y_END, HEIGHT, 0, 180, 90], SPEED, 0)
    time.sleep(2)
    
    print('    ✓ 快速平移完成')

def dance_aggressive():
    '''
    剧烈挑衅舞蹈 - 快速、大幅度、带攻击性的动作
    '''
    print('开始剧烈挑衅舞蹈！')
    
    mc.send_angles([0, -20, 30, 0, -10, 0], 60)
    time.sleep(0.8)
    
    for _ in range(3):
        mc.send_angles([40, -30, 50, -20, 20, 60], 100)
        time.sleep(0.4)
        mc.send_angles([-40, -30, 50, -20, 20, -60], 100)
        time.sleep(0.4)

    for _ in range(2):
        mc.send_angles([0, -80, 90, -10, 40, 0], 90)
        time.sleep(0.5)
        mc.send_angles([0, 10, -40, 30, -50, 0], 90)
        time.sleep(0.5)
    
    mc.send_angles([0, -40, 60, -20, 30, 0], 80)
    time.sleep(0.6)
    mc.send_angles([90, -60, 80, -20, 50, 90], 100)
    time.sleep(0.6)
    mc.send_angles([180, -40, 60, -20, 30, 180], 100)
    time.sleep(0.6)
    mc.send_angles([270, -60, 80, -20, 50, 270], 100)
    time.sleep(0.6)
    mc.send_angles([360, -40, 60, -20, 30, 0], 100)
    time.sleep(0.6)
    
    for _ in range(6):
        mc.send_angles([10, -45, 70, -25, 35, 15], 120)
        time.sleep(0.25)
        mc.send_angles([-10, -35, 50, -15, 25, -15], 120)
        time.sleep(0.25)
    for _ in range(2):
        mc.send_angles([0, -90, 120, -30, 60, 0], 100)
        time.sleep(0.5)
        mc.send_angles([0, 20, -80, 60, -40, 0], 100)
        time.sleep(0.5)
    
    mc.send_angles([0, -50, 70, -20, 40, 0], 60)
    time.sleep(1)
    
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(2)
    
    print('✓ 剧烈挑衅舞蹈完成！') 

def pump_drop(mc, XY_START=[150, -130], HEIGHT_START=90, XY_END=[50, -200], HEIGHT_DROP=180, HEIGHT_SAFE=220):
    '''
    从指定坐标吸取物品，移到另一坐标，在空中抛下（不降落直接关闭气泵）
    
    参数:
        mc: 机械臂实例
        XY_START: 起点机械臂坐标 [X, Y]
        HEIGHT_START: 起点吸取高度，方块用90，药盒子用70
        XY_END: 终点机械臂坐标 [X, Y]
        HEIGHT_DROP: 抛物高度（在这个高度关闭气泵），默认180mm
        HEIGHT_SAFE: 搬运途中安全高度，默认220mm
    '''
    print(f'开始抛物操作: ({XY_START[0]},{XY_START[1]}) → 空中抛至 ({XY_END[0]},{XY_END[1]})')
    
    # 设置运动模式为插补
    mc.set_fresh_mode(0)
    
    # 1. 吸泵移动至物体上方
    print('     移动到物体上方')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)
    
    # 2. 吸泵向下吸取物体
    print(f'   下降吸取物体 (高度={HEIGHT_START}mm)')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 25, 0)

    print('    开启吸泵')
    # pump_on()
    GPIO.output(20, 0)
    time.sleep(2)
    # 关吸泵
    GPIO.output(20, 1)
    time.sleep(0.05)
    GPIO.output(21, 0)
    time.sleep(3)
    
    # 额外等待，确保物体被牢固吸住
    print('    确保物体吸附稳定...')
    time.sleep(1.5)

    # 4. 升起物体到安全高度
    print(f'   升起物体到安全高度 ({HEIGHT_SAFE}mm)')
    mc.send_coords([XY_START[0], XY_START[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(4)

    # 5. 搬运物体至目标上方
    print(f'   搬运至目标上方 ({XY_END[0]},{XY_END[1]})')
    mc.send_coords([XY_END[0], XY_END[1], HEIGHT_SAFE, 0, 180, 90], 15, 0)
    time.sleep(4)

    # 6. 下降到抛物高度并立即关闭气泵（空中抛物）
    # print(f'    下降到抛物高度 ({HEIGHT_DROP}mm) 并抛下物体！')
    # mc.send_coords([XY_END[0], XY_END[1], HEIGHT_DROP, 0, 180, 90], 20, 0)
    # time.sleep(2)
    
    # ⚠️ 关键：在空中关闭吸泵，物体自由落体
    print('    ⚠️  空中释放物体！')
    # pump_off()
    GPIO.output(21, 1)
    time.sleep(1)
    
    print('    当前坐标:')
    print(mc.get_coords())

    # 机械臂归零
    print('    机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
    
    print('✓ 抛物操作完成！')
