"""
手眼标定结果测试脚本
用于快速验证标定矩阵的准确性

功能:
1. 加载已保存的标定矩阵
2. 实时显示相机图像和预测坐标
3. 对比实际机械臂坐标和预测坐标的误差
"""

import sys
import os
import cv2
import numpy as np
import json
from pymycobot.mycobot import MyCobot
import time

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
calibration_dir = os.path.join(os.path.dirname(current_dir), 'mycobot_280', 'camera_calibration')
sys.path.insert(0, calibration_dir)

try:
    from marker_utils import detect_marker_center
except ImportError:
    detect_marker_center = None


def detect_aruco_marker(frame, camera_matrix=None, dist_coeffs=None):
    """检测ArUco标记中心"""
    # 优先使用marker_utils
    if detect_marker_center is not None:
        try:
            center = detect_marker_center(frame, camera_matrix, dist_coeffs)
            if center is not None:
                return int(center[0]), int(center[1])
        except:
            pass
    
    # 备用方法
    try:
        aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        
        if ids is not None and len(corners) > 0:
            corner = corners[0][0]
            center_u = np.mean(corner[:, 0])
            center_v = np.mean(corner[:, 1])
            return int(center_u), int(center_v)
    except:
        pass
    
    return None, None


def pixel_to_robot_coords(pixel_u, pixel_v, M_x, M_y):
    """将像素坐标转换为机械臂坐标"""
    pixel_vec = np.array([pixel_u, pixel_v, 1])
    robot_x = np.dot(M_x, pixel_vec)
    robot_y = np.dot(M_y, pixel_vec)
    return robot_x, robot_y


def main():
    print("=" * 60)
    print("手眼标定结果测试")
    print("=" * 60)
    
    # 加载标定矩阵
    calib_path = os.path.join(current_dir, 'EyesInHand_matrix.json')
    
    if not os.path.exists(calib_path):
        print(f"\n错误: 未找到标定文件 {calib_path}")
        print("请先运行 test_eye2hand_calibration.py 完成标定")
        return
    
    try:
        with open(calib_path, 'r') as f:
            calib_data = json.load(f)
        
        M_x = np.array(calib_data['M_x'])
        M_y = np.array(calib_data['M_y'])
        
        print(f"\n✓ 已加载标定矩阵")
        print(f"  标定时间: {calib_data.get('timestamp', 'Unknown')}")
        print(f"  标定点数: {calib_data.get('num_points', 'Unknown')}")
        
    except Exception as e:
        print(f"\n错误: 加载标定文件失败 - {e}")
        return
    
    # 连接机械臂
    robot_port = input("\n请输入机械臂串口 (默认COM3): ").strip() or "COM3"
    
    try:
        print(f"\n正在连接机械臂 {robot_port}...")
        mc = MyCobot(robot_port, 115200)
        time.sleep(1)
        
        angles = mc.get_angles()
        if angles is None:
            raise Exception("机械臂连接失败")
        
        print("✓ 机械臂已连接")
        
    except Exception as e:
        print(f"✗ 机械臂连接失败: {e}")
        return
    
    # 打开相机
    camera_index = input("请输入相机索引 (默认0): ").strip()
    camera_index = int(camera_index) if camera_index else 0
    
    try:
        print(f"\n正在打开相机 {camera_index}...")
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            raise Exception("相机打开失败")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 预热
        for _ in range(10):
            cap.read()
        
        print("✓ 相机已就绪")
        
    except Exception as e:
        print(f"✗ 相机打开失败: {e}")
        return
    
    # 实时测试
    print("\n" + "=" * 60)
    print("实时测试模式")
    print("说明:")
    print("- 移动机械臂到不同位置")
    print("- 确保相机能看到ArUco标记")
    print("- 窗口显示预测坐标和实际坐标的对比")
    print("- 按 'q' 退出, 按 's' 截图保存")
    print("=" * 60)
    
    try:
        while True:
            # 读取图像
            ret, frame = cap.read()
            if not ret:
                print("相机读取失败")
                break
            
            # 检测ArUco标记
            pixel_u, pixel_v = detect_aruco_marker(frame)
            
            # 获取机械臂坐标
            coords = mc.get_coords()
            
            if pixel_u is not None and coords is not None:
                # 预测坐标
                pred_x, pred_y = pixel_to_robot_coords(pixel_u, pixel_v, M_x, M_y)
                
                # 实际坐标
                actual_x, actual_y, actual_z = coords[:3]
                
                # 计算误差
                error_x = abs(pred_x - actual_x)
                error_y = abs(pred_y - actual_y)
                error_total = np.sqrt(error_x**2 + error_y**2)
                
                # 绘制标记中心
                cv2.circle(frame, (pixel_u, pixel_v), 8, (0, 255, 0), -1)
                cv2.circle(frame, (pixel_u, pixel_v), 15, (0, 255, 0), 2)
                
                # 显示信息
                info_y = 30
                cv2.putText(frame, f"Pixel: ({pixel_u}, {pixel_v})", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                info_y += 30
                
                cv2.putText(frame, f"Predicted: X={pred_x:.1f}, Y={pred_y:.1f}", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                info_y += 30
                
                cv2.putText(frame, f"Actual:    X={actual_x:.1f}, Y={actual_y:.1f}, Z={actual_z:.1f}", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                info_y += 30
                
                # 误差显示 (颜色根据误差大小变化)
                color = (0, 255, 0) if error_total < 10 else (0, 165, 255) if error_total < 20 else (0, 0, 255)
                cv2.putText(frame, f"Error: X={error_x:.1f}, Y={error_y:.1f}, Total={error_total:.1f}mm", 
                           (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
            else:
                # 未检测到标记
                cv2.putText(frame, "No ArUco marker detected", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            # 显示图像
            cv2.imshow("Calibration Test (Press 'q' to quit, 's' to save)", frame)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 保存截图
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(current_dir, 'temp', f'calib_test_{timestamp}.jpg')
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                cv2.imwrite(save_path, frame)
                print(f"\n截图已保存: {save_path}")
    
    except KeyboardInterrupt:
        print("\n用户中断")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n测试结束")


if __name__ == "__main__":
    main()
