from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
from utils_robot import * 
import time
mc = MyCobot280(PI_PORT, PI_BAUD)
# 设置运动模式为插补
mc.set_fresh_mode(0)

import RPi.GPIO as GPIO
GPIO.setwarnings(False)   # 不打印 warning 信息
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.output(20, 1)     

def test3():
    # mc.send_coords([26.1, -179.6, 199.9, 177.68, 0.18, -135.69],50)
    # print("1:\n")
    # time.sleep(4)
    # print(mc.get_coords())
    # mc.send_coords([150.9, -126.8, 199.9, 177.68, 0.18, -135.69],50)
    # time.sleep(4)
    # print(mc.get_coords())
    # print("=============================")
    # pump_move(mc=mc,XY_START=[26.1,-179.6],XY_END=[150.9,-126.8])
    # print("2:\n")
    # time.sleep(4)
    # print(mc.get_coords())
    mc.send_coords([26.1, -179.6, 199.9, 177.68, 0.18, -135.69],50)
    print("1:\n")
    time.sleep(4)
    print(mc.get_coords())
    mc.send_coords([150.9, -126.8, 199.9, 177.68, 0.18, -135.69],50)
    time.sleep(4)
    print(mc.get_coords())
    print("=============================")
    back_zero()
    # mc.send_coords([26.1,-179.6,90,0,180,90],20,0)
    # time.sleep(3)
    # print(mc.get_coords())
    # pump_move(mc=mc,XY_START=[150,-179],XY_END=[26,-179])
    # print("2:\n")
    # time.sleep(4)
    # print(mc.get_coords())

def test2():
  print('机械臂归零')
  mc.send_angles([0, 0, 0, 0, 0, 0], 40)
  # mc.send_coords([52.3, -63.4, 417.9, -93.51, -0.47, -89.96],40)
  time.sleep(3)
  print('归零时的坐标：')
  print(mc.get_coords())
  move_to_top_view()
  time.sleep(5)  # 增加等待时间，确保运动完成
  print('移动到俯视姿态时的坐标：')
  coords = mc.get_coords()
  if coords == -1:
      print('  ⚠️ 获取坐标失败（可能是奇异点），尝试获取关节角度：')
      angles = mc.get_angles()
      print(f'  当前关节角度: {angles}')
  else:
      print(coords)
  print('移动到第二个标定点的坐标：')
  target_coords = [99.8, -143.7, 319.6, -142.52, -3.55, -119.09]
  print(f'  目标坐标: {target_coords}')
  
  # 尝试移动（使用角度插补模式）
  mc.send_coords(target_coords, 50, mode=0)
  time.sleep(5)  # 增加等待时间
  
  # 获取实际到达位置
  actual_coords = mc.get_coords()
  if actual_coords == -1:
      print('  ⚠️ 获取坐标失败，尝试获取关节角度：')
      angles = mc.get_angles()
      print(f'  当前关节角度: {angles}')
  else:
      print(f'  实际坐标: {actual_coords}')
  time.sleep(2)
  move_to_coords(99.8,-143.7)
  actual_coords=mc.get_coords()
  print(actual_coords)

  time.sleep(2)
  mc.send_coords([148.0, -131.0, 223.3, 177.78, 1.8, -91.72],40)
  print(mc.get_coords())
  
  pump_off()
  back_zero()


def test_calibration_coords():
  """测试手眼标定坐标的可达性"""
  print('\n' + '='*60)
  print('测试手眼标定坐标的可达性')
  print('='*60)
  
  # 标定点1: 像素(438,251) -> 机械臂(150.3,-127.5)
  # 标定点2: 像素(444,242) -> 机械臂(99.8,-143.7)
  
  calibration_points = [
      {'name': '标定点1', 'pixel': (438, 251), 'xy': [150.3, -127.5]},
      {'name': '标定点2', 'pixel': (444, 242), 'xy': [99.8, -143.7]}
  ]
  
  HEIGHT_SAFE = 230  # 安全高度
  HEIGHT_LOW = 120    # 抓取高度
  
  for point in calibration_points:
      print(f'\n测试 {point["name"]}:')
      print(f'  像素坐标: {point["pixel"]}')
      print(f'  机械臂 XY: {point["xy"]}')
      
      # 测试安全高度坐标
      safe_coords = [point['xy'][0], point['xy'][1], HEIGHT_SAFE, 0, 180, 90]
      print(f'\n  1️⃣ 测试安全高度坐标: {safe_coords}')
      
      mc.send_coords(safe_coords, 20, mode=0)
      time.sleep(4)
      
      actual = mc.get_coords()
      if actual == -1:
          print('    ❌ 坐标不可达或获取失败')
          angles = mc.get_angles()
          print(f'    当前关节角度: {angles}')
      else:
          print(f'    实际到达: {actual}')
          error_x = abs(actual[0] - safe_coords[0])
          error_y = abs(actual[1] - safe_coords[1])
          error_z = abs(actual[2] - safe_coords[2])
          print(f'    XYZ误差: {error_x:.1f}mm, {error_y:.1f}mm, {error_z:.1f}mm')
          
          if error_x < 10 and error_y < 10 and error_z < 10:
              print('    ✅ 坐标精度良好')
          else:
              print('    ⚠️ 坐标误差较大，可能需要重新标定')
      
      # 测试低位置（抓取高度）
      low_coords = [point['xy'][0], point['xy'][1], HEIGHT_LOW, 0, 180, 90]
      print(f'\n  2️⃣ 测试抓取高度坐标: {low_coords}')
      
      mc.send_coords(low_coords, 15, mode=0)
      time.sleep(4)
      
      actual = mc.get_coords()
      if actual == -1:
          print('    ❌ 坐标不可达或获取失败')
      else:
          print(f'    实际到达: {actual}')
          error_x = abs(actual[0] - low_coords[0])
          error_y = abs(actual[1] - low_coords[1])
          print(f'    XY误差: {error_x:.1f}mm, {error_y:.1f}mm')
      
      # 回到安全高度
      mc.send_coords(safe_coords, 20, mode=0)
      time.sleep(3)
  
  # 归零
  print('\n机械臂归零...')
  mc.send_angles([0, 0, 0, 0, 0, 0], 40)
  time.sleep(3)
  
  print('\n✅ 标定坐标测试完成')


if __name__ == "__main__":
    test3()
    # test_calibration_coords()  # 先测试标定坐标的可达性