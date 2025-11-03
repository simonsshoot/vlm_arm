"""
手眼标定测试脚本
用于验证和执行完整的手眼标定流程

使用步骤:
1. 将ArUco标定板放置在机械臂工作区内
2. 运行此脚本,按提示操作
3. 标定完成后,会保存校准矩阵到EyesInHand_matrix.json
4. 可以直接测试标定效果

依赖:
- camera_params.npz (相机内参文件)
- marker_utils.py (ArUco标记检测工具)
- 已安装opencv-python, opencv-contrib-python, numpy
"""

import sys
import os
import cv2
import numpy as np
import json
from pymycobot.mycobot import MyCobot
import time

# 添加路径以导入工具模块
current_dir = os.path.dirname(os.path.abspath(__file__))
calibration_dir = os.path.join(os.path.dirname(current_dir), 'mycobot_280', 'camera_calibration')
sys.path.insert(0, calibration_dir)

try:
    from marker_utils import detect_marker_center
except ImportError:
    print("警告: marker_utils.py 未找到,将使用简化版检测")
    detect_marker_center = None


class EyeInHandCalibration:
    """手眼标定类 (Eye-in-Hand模式)"""
    
    def __init__(self, robot_port="COM3", camera_index=0):
        """
        初始化标定系统
        
        Args:
            robot_port: 机械臂串口,如"COM3"或"/dev/ttyAMA0"
            camera_index: 摄像头索引,默认0
        """
        self.robot_port = robot_port
        self.camera_index = camera_index
        self.mc = None
        self.cap = None
        
        # 标定点存储
        self.pixel_points = []  # 像素坐标 [[u1,v1], [u2,v2], ...]
        self.robot_coords = []  # 机械臂坐标 [[x1,y1,z1], [x2,y2,z1], ...]
        
        # 相机内参
        self.camera_matrix = None
        self.dist_coeffs = None
        
        print("=" * 60)
        print("手眼标定系统初始化")
        print("=" * 60)
    
    def init_robot(self):
        """初始化机械臂"""
        print("\n[1] 正在连接机械臂...")
        try:
            self.mc = MyCobot(self.robot_port, 115200)
            time.sleep(1)
            
            # 检查连接
            angles = self.mc.get_angles()
            if angles is None or len(angles) != 6:
                raise Exception("机械臂连接失败")
            
            print(f"    ✓ 机械臂已连接: {self.robot_port}")
            print(f"    当前角度: {[round(a, 1) for a in angles]}")
            return True
            
        except Exception as e:
            print(f"    ✗ 机械臂连接失败: {e}")
            return False
    
    def init_camera(self):
        """初始化相机"""
        print("\n[2] 正在初始化相机...")
        
        try:
            # 尝试打开相机
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise Exception(f"无法打开相机 {self.camera_index}")
            
            # 设置分辨率
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # 预热相机
            for _ in range(10):
                self.cap.read()
            
            # 测试读取
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("相机读取失败")
            
            print(f"    ✓ 相机已就绪: 索引 {self.camera_index}")
            print(f"    分辨率: {frame.shape[1]}x{frame.shape[0]}")
            
            # 加载相机内参
            self.load_camera_params()
            
            return True
            
        except Exception as e:
            print(f"    ✗ 相机初始化失败: {e}")
            if self.cap:
                self.cap.release()
            return False
    
    def load_camera_params(self):
        """加载相机内参"""
        # 尝试多个可能的路径
        possible_paths = [
            os.path.join(calibration_dir, 'camera_params.npz'),
            os.path.join(os.path.dirname(current_dir), 'mycobot_280', 'config', 'camera_params.npz'),
            os.path.join(current_dir, 'camera_params.npz')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    data = np.load(path)
                    self.camera_matrix = data['mtx']
                    self.dist_coeffs = data['dist']
                    print(f"    ✓ 已加载相机内参: {path}")
                    return True
                except Exception as e:
                    print(f"    警告: 加载相机内参失败: {e}")
        
        print("    警告: 未找到相机内参文件,将使用简化标定")
        return False
    
    def capture_calibration_point(self, point_index, show_window=True):
        """
        采集一个标定点
        
        Args:
            point_index: 标定点序号 (1, 2, 3, ...)
            show_window: 是否显示预览窗口
            
        Returns:
            成功返回True,失败返回False
        """
        print(f"\n[采集标定点 {point_index}]")
        print("  请将机械臂移动到标定位置,确保相机可以看到ArUco标记")
        input("  准备就绪后按 Enter 继续...")
        
        # 获取当前机械臂坐标
        coords = self.mc.get_coords()
        if coords is None or len(coords) < 3:
            print("  ✗ 无法获取机械臂坐标")
            return False
        
        robot_x, robot_y, robot_z = coords[:3]
        print(f"  机械臂坐标: X={robot_x:.1f}, Y={robot_y:.1f}, Z={robot_z:.1f}")
        
        # 拍摄图像
        time.sleep(0.5)  # 等待稳定
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("  ✗ 相机读取失败")
            return False
        
        # 检测ArUco标记中心
        pixel_u, pixel_v = self.detect_marker_in_frame(frame)
        
        if pixel_u is None:
            print("  ✗ 未检测到ArUco标记")
            if show_window:
                cv2.imshow("Calibration - No Marker", frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
            return False
        
        print(f"  标记中心: U={pixel_u}, V={pixel_v}")
        
        # 保存标定点
        self.pixel_points.append([pixel_u, pixel_v])
        self.robot_coords.append([robot_x, robot_y, robot_z])
        
        # 显示标记
        if show_window:
            cv2.circle(frame, (int(pixel_u), int(pixel_v)), 10, (0, 255, 0), 2)
            cv2.putText(frame, f"Point {point_index}", (int(pixel_u)+15, int(pixel_v)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow(f"Calibration Point {point_index}", frame)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()
        
        print(f"  ✓ 标定点 {point_index} 采集成功")
        return True
    
    def detect_marker_in_frame(self, frame):
        """
        在图像中检测ArUco标记中心
        
        Args:
            frame: 输入图像
            
        Returns:
            (u, v) 像素坐标,未检测到返回 (None, None)
        """
        # 使用marker_utils如果可用
        if detect_marker_center is not None:
            try:
                center = detect_marker_center(frame, self.camera_matrix, self.dist_coeffs)
                if center is not None:
                    return int(center[0]), int(center[1])
            except Exception as e:
                print(f"  警告: marker_utils检测失败: {e}")
        
        # 备用检测方法: OpenCV ArUco
        try:
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
            
            if ids is not None and len(corners) > 0:
                # 使用第一个检测到的标记
                corner = corners[0][0]
                center_u = np.mean(corner[:, 0])
                center_v = np.mean(corner[:, 1])
                return int(center_u), int(center_v)
        except Exception as e:
            print(f"  警告: ArUco检测失败: {e}")
        
        return None, None
    
    def compute_calibration_matrix(self):
        """计算手眼标定矩阵"""
        print("\n[3] 正在计算标定矩阵...")
        
        if len(self.pixel_points) < 3:
            print("  ✗ 标定点不足,至少需要3个点")
            return False
        
        print(f"  采集的标定点数量: {len(self.pixel_points)}")
        
        # 构建线性方程组求解变换矩阵
        # 对于每个标定点: [x_robot, y_robot] = M * [u_pixel, v_pixel, 1]
        
        A = []
        b_x = []
        b_y = []
        
        for (u, v), (x, y, z) in zip(self.pixel_points, self.robot_coords):
            A.append([u, v, 1])
            b_x.append(x)
            b_y.append(y)
        
        A = np.array(A)
        b_x = np.array(b_x)
        b_y = np.array(b_y)
        
        # 最小二乘法求解
        try:
            # 求解 X = M_x * [u, v, 1]
            M_x, residuals_x, rank_x, s_x = np.linalg.lstsq(A, b_x, rcond=None)
            # 求解 Y = M_y * [u, v, 1]
            M_y, residuals_y, rank_y, s_y = np.linalg.lstsq(A, b_y, rcond=None)
            
            print(f"  ✓ 标定矩阵计算完成")
            print(f"    X方向残差: {residuals_x[0] if len(residuals_x) > 0 else 'N/A'}")
            print(f"    Y方向残差: {residuals_y[0] if len(residuals_y) > 0 else 'N/A'}")
            
            # 保存标定结果
            calibration_data = {
                "M_x": M_x.tolist(),
                "M_y": M_y.tolist(),
                "pixel_points": self.pixel_points,
                "robot_coords": self.robot_coords,
                "num_points": len(self.pixel_points),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到JSON文件
            output_path = os.path.join(current_dir, 'EyesInHand_matrix.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(calibration_data, f, indent=2)
            
            print(f"  ✓ 标定矩阵已保存: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"  ✗ 标定计算失败: {e}")
            return False
    
    def test_calibration(self):
        """测试标定效果"""
        print("\n[4] 测试标定效果...")
        print("  将机械臂移动到测试位置")
        input("  准备就绪后按 Enter 继续...")
        
        # 获取当前坐标
        coords = self.mc.get_coords()
        if coords is None:
            print("  ✗ 无法获取机械臂坐标")
            return
        
        actual_x, actual_y, actual_z = coords[:3]
        print(f"  实际坐标: X={actual_x:.1f}, Y={actual_y:.1f}, Z={actual_z:.1f}")
        
        # 拍摄图像
        ret, frame = self.cap.read()
        if not ret:
            print("  ✗ 相机读取失败")
            return
        
        # 检测标记
        pixel_u, pixel_v = self.detect_marker_in_frame(frame)
        
        if pixel_u is None:
            print("  ✗ 未检测到ArUco标记")
            return
        
        print(f"  检测到标记: U={pixel_u}, V={pixel_v}")
        
        # 使用标定矩阵计算预测坐标
        try:
            # 加载标定矩阵
            calib_path = os.path.join(current_dir, 'EyesInHand_matrix.json')
            with open(calib_path, 'r') as f:
                calib_data = json.load(f)
            
            M_x = np.array(calib_data['M_x'])
            M_y = np.array(calib_data['M_y'])
            
            # 计算预测坐标
            pixel_vec = np.array([pixel_u, pixel_v, 1])
            predicted_x = np.dot(M_x, pixel_vec)
            predicted_y = np.dot(M_y, pixel_vec)
            
            print(f"  预测坐标: X={predicted_x:.1f}, Y={predicted_y:.1f}")
            
            # 计算误差
            error_x = abs(predicted_x - actual_x)
            error_y = abs(predicted_y - actual_y)
            error_total = np.sqrt(error_x**2 + error_y**2)
            
            print(f"  误差: ΔX={error_x:.1f}mm, ΔY={error_y:.1f}mm, 总误差={error_total:.1f}mm")
            
            if error_total < 10:
                print("  ✓ 标定效果很好 (误差<10mm)")
            elif error_total < 20:
                print("  ⚠ 标定效果一般 (误差<20mm)")
            else:
                print("  ✗ 标定效果较差,建议重新标定")
            
        except Exception as e:
            print(f"  ✗ 测试失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("\n资源已释放")


def main():
    """主函数"""
    print("=" * 60)
    print("手眼标定向导 (Eye-in-Hand)")
    print("=" * 60)
    
    # 参数配置
    robot_port = input("\n请输入机械臂串口 (默认COM3): ").strip() or "COM3"
    camera_index = input("请输入相机索引 (默认0): ").strip()
    camera_index = int(camera_index) if camera_index else 0
    
    # 创建标定对象
    calibrator = EyeInHandCalibration(robot_port, camera_index)
    
    try:
        # 初始化
        if not calibrator.init_robot():
            print("\n程序终止: 机械臂初始化失败")
            return
        
        if not calibrator.init_camera():
            print("\n程序终止: 相机初始化失败")
            return
        
        # 标定流程说明
        print("\n" + "=" * 60)
        print("标定流程说明:")
        print("1. 在机械臂工作区放置ArUco标定板")
        print("2. 移动机械臂到不同位置(至少3个,建议5-9个)")
        print("3. 每个位置确保相机能看到标定板")
        print("4. 建议采集点均匀分布在工作区内")
        print("=" * 60)
        
        # 询问采集点数量
        num_points = input("\n请输入要采集的标定点数量 (建议5-9个): ").strip()
        num_points = int(num_points) if num_points else 5
        
        # 采集标定点
        for i in range(1, num_points + 1):
            success = calibrator.capture_calibration_point(i)
            if not success:
                retry = input("  采集失败,是否重试? (y/n): ").strip().lower()
                if retry == 'y':
                    i -= 1  # 重试当前点
                    continue
                else:
                    break
        
        # 计算标定矩阵
        if len(calibrator.pixel_points) >= 3:
            if calibrator.compute_calibration_matrix():
                # 测试标定
                test = input("\n是否进行标定测试? (y/n): ").strip().lower()
                if test == 'y':
                    calibrator.test_calibration()
        else:
            print("\n标定点不足,无法完成标定")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        calibrator.cleanup()
    
    print("\n标定完成!")


if __name__ == "__main__":
    main()
