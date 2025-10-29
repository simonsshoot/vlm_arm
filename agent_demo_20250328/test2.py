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

def test2():
  print('机械臂归零')
  mc.send_angles([0, 0, 0, 0, 0, 0], 40)
  print('归零时的坐标：')
  print(mc.get_coords())
  time.sleep(2)
  move_to_top_view()
  print('移动到俯视姿态时的坐标：')
  print(mc.get_coords())
  time.sleep(2)
  print('移动到第二个标定点的坐标：')
  mc.send_coords([99.8, -143.7, 319.6, -142.52, -3.55, -119.09])
  print(mc.get_coords())
  time.sleep(2)


if __name__ == "__main__":
    test2()