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



def main():
  print('开始眼手协调测试程序')
  back_zero()
  time.sleep(2)
  print('移动到俯视姿态')
  move_to_top_view()
  time.sleep(2)
  camera_check()

if __name__=='main':
  main()