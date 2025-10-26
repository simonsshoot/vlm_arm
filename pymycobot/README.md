# pymycobot 简明 API 参考

本文档为仓库中 `pymycobot` 驱动代码的简明说明，帮助你快速了解常用函数及其作用。具体实现请参考 `pymycobot/generate.py` 与 `pymycobot/mycobot.py` 源码。

## 总体说明
- 大多数函数最终通过 `_mesg(...)` 将命令打包并通过串口/USB 发送到控制板。
- 常见返回值：有些方法带 `has_reply=True` 会等待并解析控制板返回的数据；无返回的方法通常返回发送结果或 None。
- 单位：关节角度以度/弧度请参考具体实现（库通常以度为单位），笛卡尔坐标以毫米（mm）。

## 常用函数一览

### 连接与电源

- **power_on()**  
  作用：打开与控制板的通信/上电

- **power_off()**  
  作用：关闭与控制板的通信/断电

- **is_power_on() -> int**  
  作用：查询电源状态，返回 1（开）、0（关）、-1（错误）

- **is_controller_connected() -> int**  
  作用：检测是否与控制器连接，返回 1（成功）、0（失败）、-1（错误）

### 舵机与安全

- **release_all_servos(data: int = None)**  
  作用：放松所有关节舵机（断力矩），data=1 时取消阻尼

- **release_servo(servo_id: int, mode: int = None)**  
  参数：servo_id (1-6), mode (可选，1 取消阻尼)  
  作用：释放指定舵机的力矩

- **focus_servo(servo_id: int)**  
  参数：servo_id (1-6)  
  作用：使能指定舵机

- **focus_all_servos()**  
  作用：使能所有舵机

- **joint_brake(joint_id: int)**  
  参数：joint_id (1-6)  
  作用：在运动中制动指定关节，缓冲距离与当前速度相关

### 角度/关节控制（MDI 模式）

- **get_angles() -> list[float]**  
  作用：读取 6 个关节的当前角度值

- **send_angle(id: int, degree: float, speed: int, _async: bool = False)**  
  参数：id (关节编号 1-6), degree (角度值), speed (速度 1-100), _async (是否异步)  
  作用：控制单个关节移动到指定角度

- **send_angles(angles: list[float], speed: int, _async: bool = False)**  
  参数：angles (6 个关节角度列表), speed (速度 1-100), _async (是否异步)  
  作用：一次性发送所有关节角度，机械臂同步移动到目标位置，将角度转换为协议格式并写入串口

- **is_in_position(data: list[float], id: int = 0) -> int**  
  参数：data (角度或坐标列表), id (0=角度, 1=坐标)  
  作用：判断是否到达指定位置，返回 1（是）、0（否）、-1（错误）

- **is_moving() -> int**  
  作用：检测机械臂是否正在运动，返回 0（停止）、1（运动中）、-1（错误）

### 笛卡尔/坐标控制

- **get_coords() -> list[float]**  
  作用：读取末端执行器当前位姿 [x, y, z, rx, ry, rz]

- **send_coord(id: int, coord: float, speed: int, _async: bool = False)**  
  参数：id (坐标轴编号 1-6), coord (坐标值，mm或角度), speed (速度 1-100), _async (是否异步)  
  作用：单轴移动到指定坐标

- **send_coords(coords: list[float], speed: int, mode: int = None, _async: bool = False)**  
  参数：coords ([x(mm), y, z, rx(角度), ry, rz]), speed (速度 1-100), mode (0=角度插补, 1=直线插补), _async (是否异步)  
  作用：发送末端位姿，机械臂移动到目标位置，mode 决定运动轨迹类型

### JOG（点动/手动微调）

- **jog_angle(joint_id: int, direction: int, speed: int, _async: bool = False)**  
  参数：joint_id (1-6), direction (0=减小, 1=增大), speed (速度 1-100), _async (是否异步)  
  作用：点动控制指定关节角度

- **jog_coord(coord_id: int, direction: int, speed: int, _async: bool = False)**  
  参数：coord_id (1-6), direction (0=减小, 1=增大), speed (速度 1-100), _async (是否异步)  
  作用：点动控制指定坐标轴

- **jog_increment(joint_id: int, increment: float, speed: int, _async: bool = False)**  
  参数：joint_id (1-6), increment (增量角度), speed (速度 0-100), _async (是否异步)  
  作用：步进模式，关节移动指定增量

- **pause()**  
  作用：暂停当前运动

- **resume()**  
  作用：恢复暂停的运动

- **stop()**  
  作用：停止运动

- **is_paused() -> int**  
  作用：判断是否暂停，返回 1（暂停）、0（未暂停）、-1（错误）

### 速度/编码器/限制

- **get_speed() -> int**  
  作用：获取当前速度设置

- **set_speed(speed: int)**  
  参数：speed (速度值)  
  作用：设置机械臂运动速度

- **get_encoder(joint_id: int) -> int**  
  参数：joint_id (1-6 或 7 夹爪)  
  作用：获取指定关节的编码器值

- **set_encoder(joint_id: int, encoder: int, speed: int)**  
  参数：joint_id (1-6 或 7), encoder (编码器值), speed (速度 1-100)  
  作用：设置单个关节编码器值

- **get_encoders() -> list[int]**  
  作用：获取所有关节的编码器值列表

- **set_encoders(encoders: list[int], sp: int)**  
  参数：encoders (6 个编码器值), sp (速度 1-100)  
  作用：设置所有关节编码器值

- **get_joint_min_angle(joint_id: int) -> float**  
  参数：joint_id (1-6)  
  作用：获取指定关节的最小运动角度

- **get_joint_max_angle(joint_id: int) -> float**  
  参数：joint_id (1-6)  
  作用：获取指定关节的最大运动角度

### IO 与拓展

- **set_color(r: int, g: int, b: int)**  
  参数：r, g, b (0-255)  
  作用：设置机械臂顶部 LED 灯的 RGB 颜色

- **set_digital_output(pin_no: int, pin_signal: int)**  
  参数：pin_no (引脚编号), pin_signal (0/1)  
  作用：设置数字输出引脚状态

- **get_digital_input(pin_no: int) -> int**  
  参数：pin_no (引脚编号)  
  作用：读取数字输入引脚状态

- **set_gripper_state(flag: int, speed: int, _type_1: int = None)**  
  参数：flag (0=打开, 1=关闭, 10=释放), speed (速度 1-100), _type_1 (夹爪类型：1=自适应, 2=五指, 3=平行, 4=柔性)  
  作用：控制夹爪的开/关状态

- **set_gripper_value(gripper_value: int, speed: int, gripper_type: int = None)**  
  参数：gripper_value (0-100), speed (速度 1-100), gripper_type (夹爪类型)  
  作用：设置夹爪开合程度

- **set_basic_output(pin_no: int, pin_signal: int)**  
  参数：pin_no (引脚编号), pin_signal (0/1)  
  作用：设置基础 IO 输出（M5 版本）

- **get_basic_input(pin_no: int) -> int**  
  参数：pin_no (引脚编号)  
  作用：读取基础 IO 输入（M5 版本）

### 其他工具函数

- **get_error_information() -> int**  
  作用：获取机械臂错误信息，0=无错误，1-6=关节超限，16-19=碰撞保护，32=逆解无解，33-34=线性运动无邻近解

- **get_basic_version() -> str**  
  作用：获取基础固件版本号

- **get_system_version() -> str**  
  作用：获取系统软件版本号

- **set_ssid_pwd(account: str, password: str)**  
  参数：account (WiFi 账号), password (WiFi 密码)  
  作用：设置 WiFi 连接（适用于 M5 或 Seeed 版本）

- **get_ssid_pwd() -> tuple[str, str]**  
  作用：获取当前 WiFi 账号和密码

- **get_tof_distance() -> int**  
  作用：获取 TOF 距离传感器检测的距离（单位：mm，需要外接传感器）

## 插补模式说明（set_fresh_mode）
- set_fresh_mode(0)：角度/关节插补（joint interpolation）
  - 每个关节分别插补到目标角度。优点：实现简单、运动稳定；缺点：末端轨迹不是直线。
- set_fresh_mode(1)：直线/笛卡尔插补（linear Cartesian interpolation）
  - 控制末端沿笛卡尔直线移动，适合抓取/搬运需要直线轨迹的场景；实现需实时逆解，计算量更大。
- 建议：示教和简单点到点动作使用模式 0；需要直线搬运使用模式 1（或在 send_coords 中指定 mode）。

## send_angles / send_coords 内部流程（高层概述）
1. 参数校验与标定函数（calibration_parameters）
2. 将角度/坐标值转换为控制板协议格式（_angle2int / _coord2int）
3. 构造协议帧（命令码 + 数据 + 校验）
4. 通过串口发送字节流（低层 write_bytes / _mesg）
5. 可选等待控制板应答并解析返回值

## 使用示例
```python
from pymycobot.mycobot import MyCobot
from pymycobot import PI_PORT, PI_BAUD

mc = MyCobot(PI_PORT, PI_BAUD)

# 归零
mc.send_angles([0,0,0,0,0,0], 40)

# 单关节移动
mc.send_angle(2, 45, 60)

# 末端移动（笛卡尔）
mc.send_coords([150, -120, 200, 0, 180, 90], 20, mode=1)

# 设置 LED
mc.set_color(255, 0, 0)

# 放松舵机
mc.release_all_servos()
```

## 安全与调试建议
- 重要操作前先 `back_zero()` 或 `release_all_servos()` 以避免意外运动。
- 调试时使用较低速度（speed 值）并在靠近机械臂时保持足够安全距离。
- 如果控制板返回异常码或超时，先检查串口连接、电源与舵机使能状态。

---

如需，我可以为你提取并注释 `pymycobot` 源码中 `send_angles`、`send_coords`、`_mesg` 等函数的具体实现并贴出关键代码片段。回复 “贴实现” 即可。
