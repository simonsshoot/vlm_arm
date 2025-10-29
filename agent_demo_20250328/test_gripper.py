# test_gripper.py
# 测试夹爪功能
# 同济子豪兄 2025-10-29

import time
from pymycobot.mycobot280 import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

print('='*50)
print('夹爪功能测试程序')
print('='*50)

# 连接机械臂
print('\n正在连接机械臂...')
mc = MyCobot280(PI_PORT, PI_BAUD)
mc.set_fresh_mode(0)  # 设置运动模式为插补
print('✅ 机械臂连接成功')

def test_basic_gripper():
    """测试1：基本夹爪开关功能"""
    print('\n' + '='*50)
    print('测试1：基本夹爪开关功能')
    print('='*50)
    
    # 检测夹爪类型
    print('\n检测夹爪类型...')
    gripper_type = mc.is_torque_gripper()
    if gripper_type == 40:
        print('✅ 检测到力控夹爪')
        is_torque = 1
    elif gripper_type == 9:
        print('✅ 检测到普通夹爪')
        is_torque = 0
    else:
        print(f'⚠️ 未知夹爪类型: {gripper_type}，使用默认设置')
        is_torque = 0
    
    # 打开夹爪
    print('\n打开夹爪...')
    mc.set_gripper_state(0, 50, _type_1=1, is_torque=is_torque)
    print('夹爪正在打开，等待3秒')
    time.sleep(3)
    
    # 关闭夹爪
    print('\n关闭夹爪...')
    mc.set_gripper_state(1, 50, _type_1=1, is_torque=is_torque)
    print('夹爪正在关闭，等待3秒')
    time.sleep(3)
    
    # 释放夹爪
    print('\n释放夹爪...')
    mc.set_gripper_state(254, 50, _type_1=1, is_torque=is_torque)
    print('夹爪已释放')
    time.sleep(2)
    
    print('✅ 基本夹爪测试完成')

def test_gripper_value():
    """测试2：夹爪精确控制（0-100值）"""
    print('\n' + '='*50)
    print('测试2：夹爪精确控制（0-100值）')
    print('='*50)
    
    # 检测夹爪类型
    gripper_type = mc.is_torque_gripper()
    is_torque = 1 if gripper_type == 40 else 0
    
    # 完全打开 (0)
    print('\n设置夹爪值为 0 (完全打开)...')
    mc.set_gripper_value(0, 50, gripper_type=1, is_torque=is_torque)
    time.sleep(3)
    
    # 半开 (50)
    print('\n设置夹爪值为 50 (半开)...')
    mc.set_gripper_value(50, 50, gripper_type=1, is_torque=is_torque)
    time.sleep(3)
    
    # 完全关闭 (100)
    print('\n设置夹爪值为 100 (完全关闭)...')
    mc.set_gripper_value(100, 50, gripper_type=1, is_torque=is_torque)
    time.sleep(3)
    
    # 回到打开状态
    print('\n设置夹爪值为 0 (完全打开)...')
    mc.set_gripper_value(0, 50, gripper_type=1, is_torque=is_torque)
    time.sleep(3)
    
    print('✅ 夹爪精确控制测试完成')

def test_gripper_cycle():
    """测试3：夹爪循环开关测试"""
    print('\n' + '='*50)
    print('测试3：夹爪循环开关测试（5次）')
    print('='*50)
    
    gripper_type = mc.is_torque_gripper()
    is_torque = 1 if gripper_type == 40 else 0
    
    for i in range(5):
        print(f'\n第 {i+1} 次循环:')
        
        print('  打开夹爪...')
        mc.set_gripper_state(0, 70, _type_1=1, is_torque=is_torque)
        time.sleep(2)
        
        print('  关闭夹爪...')
        mc.set_gripper_state(1, 70, _type_1=1, is_torque=is_torque)
        time.sleep(2)
    
    # 最后释放夹爪
    print('\n释放夹爪...')
    mc.set_gripper_state(254, 50, _type_1=1, is_torque=is_torque)
    
    print('✅ 夹爪循环测试完成')

def test_gripper_with_movement():
    """测试4：夹爪配合机械臂移动"""
    print('\n' + '='*50)
    print('测试4：夹爪配合机械臂移动')
    print('请在坐标 [200, -50] 附近放置一个可抓取的物体')
    print('='*50)
    
    input('\n准备好后，按回车键继续...')
    
    gripper_type = mc.is_torque_gripper()
    is_torque = 1 if gripper_type == 40 else 0
    
    # 机械臂归零
    print('\n机械臂归零...')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
    
    # 打开夹爪准备抓取
    print('\n打开夹爪...')
    mc.set_gripper_state(0, 50, _type_1=1, is_torque=is_torque)
    time.sleep(3)
    
    # 移动到物体上方
    print('\n移动到物体上方...')
    mc.send_coords([200, -50, 200, 0, 180, 90], 20, 0)
    time.sleep(4)
    
    # 向下移动接近物体
    print('\n向下移动接近物体...')
    mc.send_coords([200, -50, 100, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 关闭夹爪抓取
    print('\n关闭夹爪抓取物体...')
    mc.set_gripper_state(1, 50, _type_1=1, is_torque=is_torque)
    time.sleep(3)
    
    # 检查夹爪是否在移动
    print('\n检查夹爪状态...')
    is_moving = mc.is_gripper_moving()
    if is_moving == 1:
        print('  夹爪正在移动...')
        time.sleep(2)
    elif is_moving == 0:
        print('  夹爪已停止')
    
    # 获取夹爪当前值
    gripper_value = mc.get_gripper_value(gripper_type=1)
    print(f'  当前夹爪值: {gripper_value}')
    
    # 向上抬起物体
    print('\n向上抬起物体...')
    mc.send_coords([200, -50, 200, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 移动到新位置
    print('\n移动到目标位置...')
    mc.send_coords([150, -150, 200, 0, 180, 90], 15, 0)
    time.sleep(4)
    
    # 向下放置
    print('\n向下放置...')
    mc.send_coords([150, -150, 100, 0, 180, 90], 20, 0)
    time.sleep(3)
    
    # 打开夹爪释放物体
    print('\n打开夹爪释放物体...')
    mc.set_gripper_state(0, 50, _type_1=1, is_torque=is_torque)
    time.sleep(2)
    
    # 机械臂归零
    print('\n机械臂归零...')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)
    
    print('✅ 夹爪配合移动测试完成')

def test_gripper_speed():
    """测试5：不同速度下的夹爪控制"""
    print('\n' + '='*50)
    print('测试5：不同速度下的夹爪控制')
    print('='*50)
    
    gripper_type = mc.is_torque_gripper()
    is_torque = 1 if gripper_type == 40 else 0
    
    speeds = [30, 50, 70, 100]
    
    for speed in speeds:
        print(f'\n使用速度 {speed} 测试:')
        
        print(f'  以速度 {speed} 打开夹爪...')
        mc.set_gripper_state(0, speed, _type_1=1, is_torque=is_torque)
        time.sleep(3)
        
        print(f'  以速度 {speed} 关闭夹爪...')
        mc.set_gripper_state(1, speed, _type_1=1, is_torque=is_torque)
        time.sleep(3)
    
    # 最后释放
    mc.set_gripper_state(254, 50, _type_1=1, is_torque=is_torque)
    
    print('✅ 不同速度测试完成')

def test_gripper_torque():
    """测试6：力控夹爪扭矩设置（仅适用于自适应夹爪）"""
    print('\n' + '='*50)
    print('测试6：力控夹爪扭矩设置')
    print('='*50)
    
    gripper_type = mc.is_torque_gripper()
    
    if gripper_type != 40:
        print('⚠️ 当前夹爪不是力控夹爪，跳过此测试')
        return
    
    print('✅ 检测到力控夹爪')
    
    # 获取当前扭矩
    current_torque = mc.get_HTS_gripper_torque()
    print(f'\n当前扭矩值: {current_torque}')
    
    # 设置不同扭矩值进行测试
    torque_values = [150, 300, 500, 700]
    
    for torque in torque_values:
        print(f'\n设置扭矩为 {torque}...')
        result = mc.set_HTS_gripper_torque(torque)
        if result == 1:
            print(f'  ✅ 扭矩设置成功')
        else:
            print(f'  ❌ 扭矩设置失败')
        
        # 验证设置
        actual_torque = mc.get_HTS_gripper_torque()
        print(f'  实际扭矩值: {actual_torque}')
        
        # 测试抓取
        print(f'  以扭矩 {torque} 测试抓取...')
        mc.set_gripper_state(1, 50, _type_1=1, is_torque=1)
        time.sleep(3)
        
        mc.set_gripper_state(0, 50, _type_1=1, is_torque=1)
        time.sleep(2)
    
    # 恢复原扭矩
    if current_torque:
        print(f'\n恢复原扭矩值 {current_torque}...')
        mc.set_HTS_gripper_torque(current_torque)
    
    print('✅ 扭矩测试完成')

def test_gripper_protection():
    """测试7：夹爪保护电流设置"""
    print('\n' + '='*50)
    print('测试7：夹爪保护电流设置')
    print('='*50)
    
    # 获取当前保护电流
    current_protection = mc.get_gripper_protect_current()
    print(f'\n当前保护电流: {current_protection} mA')
    
    # 设置保护电流（范围 1-500）
    new_protection = 300
    print(f'\n设置保护电流为 {new_protection} mA...')
    mc.set_gripper_protect_current(new_protection)
    time.sleep(1)
    
    # 验证设置
    actual_protection = mc.get_gripper_protect_current()
    print(f'实际保护电流: {actual_protection} mA')
    
    # 恢复原保护电流
    if current_protection:
        print(f'\n恢复原保护电流 {current_protection} mA...')
        mc.set_gripper_protect_current(current_protection)
    
    print('✅ 保护电流测试完成')

def main():
    """主测试函数"""
    print('\n请选择要执行的测试:')
    print('1 - 基本夹爪开关功能')
    print('2 - 夹爪精确控制（0-100值）')
    print('3 - 夹爪循环开关测试')
    print('4 - 夹爪配合机械臂移动')
    print('5 - 不同速度下的夹爪控制')
    print('6 - 力控夹爪扭矩设置（仅自适应夹爪）')
    print('7 - 夹爪保护电流设置')
    print('8 - 全部测试（按顺序执行）')
    print('0 - 退出')
    
    choice = input('\n请输入选项 (0-8): ').strip()
    
    try:
        if choice == '1':
            test_basic_gripper()
        elif choice == '2':
            test_gripper_value()
        elif choice == '3':
            test_gripper_cycle()
        elif choice == '4':
            test_gripper_with_movement()
        elif choice == '5':
            test_gripper_speed()
        elif choice == '6':
            test_gripper_torque()
        elif choice == '7':
            test_gripper_protection()
        elif choice == '8':
            print('\n开始执行全部测试...')
            test_basic_gripper()
            input('\n按回车继续下一个测试...')
            
            test_gripper_value()
            input('\n按回车继续下一个测试...')
            
            test_gripper_cycle()
            input('\n按回车继续下一个测试...')
            
            test_gripper_speed()
            input('\n按回车继续下一个测试...')
            
            test_gripper_torque()
            input('\n按回车继续下一个测试...')
            
            test_gripper_protection()
            input('\n按回车继续下一个测试...')
            
            test_gripper_with_movement()
            
            print('\n' + '='*50)
            print('✅ 所有测试完成！')
            print('='*50)
        elif choice == '0':
            print('退出测试程序')
        else:
            print('❌ 无效选项，请重新运行程序')
    
    except KeyboardInterrupt:
        print('\n\n测试被用户中断')
        # 释放夹爪
        try:
            mc.set_gripper_state(254, 50, _type_1=1, is_torque=0)
        except:
            pass
        # 机械臂归零
        try:
            mc.send_angles([0, 0, 0, 0, 0, 0], 40)
        except:
            pass
    
    except Exception as e:
        print(f'\n❌ 测试过程中出现错误: {e}')
        # 释放夹爪
        try:
            mc.set_gripper_state(254, 50, _type_1=1, is_torque=0)
        except:
            pass
        # 机械臂归零
        try:
            mc.send_angles([0, 0, 0, 0, 0, 0], 40)
        except:
            pass
    
    finally:
        print('\n程序结束')

if __name__ == '__main__':
    main()
