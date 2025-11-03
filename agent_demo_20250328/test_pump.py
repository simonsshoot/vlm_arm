from pymycobot.mycobot280 import MyCobot280
import time
import RPi.GPIO as GPIO
from utils_robot import *
#输入以上代码导入工程所需要的包

# MyCobot 类初始化需要两个参数：串口号和波特率
# 初始化一个MyCobot对象
# 下面为 树莓派版本创建对象代码
mc = MyCobot280("/dev/ttyAMA0", 1000000)

# 初始化
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
# 开吸泵
GPIO.output(20, 0)

# 等待2秒
time.sleep(2)
# 关吸泵
GPIO.output(20, 1)
time.sleep(0.05)
# 打开泄气阀门
GPIO.output(21, 0)
time.sleep(1)
GPIO.output(21, 1)
time.sleep(0.05)

def test():
  pump_on()
  time.sleep(2)
  pump_off()
  print("==============================")
  time.sleep(1)
  pump_move(mc=mc,XY_START=[150,-139],XY_END=[26,-179])