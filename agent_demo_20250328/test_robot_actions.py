# test_robot_actions.py
# 测试机械臂各种动作
# 同济子豪兄 2024-5-27

print('\n=== 机械臂动作测试程序 ===\n')

from utils_robot import *
from utils_pump import *
import time

def test_all_actions():
    '''执行所有动作的完整演示'''
    print('\n开始完整动作演示...\n')
    
    # 1. 归零
    print('[1/7] 归零动作')
    back_zero()
    time.sleep(2)
    
    # 2. 摇头
    print('[2/7] 摇头动作')
    head_shake()
    time.sleep(2)
    
    # 3. 点头
    print('[3/7] 点头动作')
    head_nod()
    time.sleep(2)
    
    # 4. 移动到俯视姿态
    print('[4/7] 移动到俯视姿态')
    move_to_top_view()
    time.sleep(2)
    
    # 5. 移动到指定坐标
    print('[5/7] 移动到指定坐标 (150, -130)')
    move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230)
    time.sleep(2)
    
    # 6. 单关节旋转
    print('[6/7] 第6关节旋转')
    single_joint_move(6, 45)
    time.sleep(1)
    single_joint_move(6, -45)
    time.sleep(1)
    single_joint_move(6, 0)
    time.sleep(1)
    
    # 7. 跳舞（最后压轴）
    print('[7/7] 跳舞动作')
    head_dance()
    time.sleep(2)
    
    # 最后归零
    print('演示完成，归零')
    back_zero()
    print('\n✅ 所有动作演示完成！\n')

def main():
    '''主函数'''
    # 初始化：归零和关闭吸泵
    print('初始化机械臂...')
    # pump_off()
    back_zero()
    
    while True:
        choice = input('\n请选择操作 (输入数字或字母): ').strip()
        
        try:
            if choice == '1':
                print('\n执行：归零')
                back_zero()
                
            elif choice == '2':
                print('\n执行：摇头')
                head_shake()
                
            elif choice == '3':
                print('\n执行：跳舞')
                head_dance()
                
            elif choice == '4':
                print('\n执行：点头')
                head_nod()
                
            elif choice == '5':
                print('\n执行：移动到俯视姿态')
                move_to_top_view()
                
            elif choice == '6':
                print('\n执行：俯视拍照')
                check_photo = input('是否需要人工确认拍照？(y/n，默认n): ').strip().lower()
                if check_photo == 'y':
                    top_view_shot(check=True)
                else:
                    top_view_shot(check=False)
                print('拍照完成，图像保存在 temp/vl_now.jpg')
                
            elif choice == '7':
                print('\n执行：移动到指定坐标')
                try:
                    x = int(input('请输入X坐标 (默认150): ') or '150')
                    y = int(input('请输入Y坐标 (默认-130): ') or '-130')
                    h = int(input('请输入高度 (默认230): ') or '230')
                    move_to_coords(X=x, Y=y, HEIGHT_SAFE=h)
                except ValueError:
                    print('输入无效，使用默认值')
                    move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230)
                    
            elif choice == '8':
                print('\n执行：单关节旋转')
                print('关节编号: 1-6')
                try:
                    joint = int(input('请输入关节编号 (1-6): '))
                    if joint < 1 or joint > 6:
                        print('关节编号必须在1-6之间')
                        continue
                    angle = float(input('请输入旋转角度 (-180到180): '))
                    if angle < -180 or angle > 180:
                        print('角度必须在-180到180之间')
                        continue
                    single_joint_move(joint, angle)
                except ValueError:
                    print('输入无效，请输入数字')
                    
            elif choice == '9':
                print('\n执行：放松所有关节')
                confirm = input('⚠️  放松后机械臂会失去动力，确认吗？(y/n): ').strip().lower()
                if confirm == 'y':
                    relax_arms()
                    print('已放松所有关节，可以手动拖动机械臂')
                else:
                    print('已取消')

            elif choice == '10':
                print('\n执行：吸泵测试')
                try:
                    pump_on()
                    time.sleep(5)
                    pump_move(mc, XY_START=[230,-50], HEIGHT_START=90, 
                             XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220)
                    pump_off()
                    print('✅ 测试完成')
                except Exception as e:
                    print(f'❌ 测试失败: {e}')
                    try:
                        pump_off()
                    except:
                        pass

            elif choice=='11':
                angles=print_angles()
                print(f"current angles:{angles}")
            elif choice == '0':
                print('\n执行：所有动作演示')
                confirm = input('这将执行所有动作，需要较长时间，确认吗？(y/n): ').strip().lower()
                if confirm == 'y':
                    test_all_actions()
                else:
                    print('已取消')
                    
            elif choice.lower() == 'q':
                print('\n退出程序...')
                back_zero()
                # pump_off()
                print('已归零并关闭吸泵，再见！')
                break
                
            else:
                print('❌ 无效选择，请重新输入')
                
        except KeyboardInterrupt:
            print('\n\n检测到 Ctrl+C，正在安全退出...')
            back_zero()
            # pump_off()
            print('已归零并关闭吸泵，程序退出。')
            break
            
        except Exception as e:
            print(f'❌ 执行出错: {e}')
            print('尝试归零...')
            try:
                back_zero()
            except:
                print('归零失败，请手动检查机械臂状态')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'\n程序异常: {e}')
        try:
            back_zero()
            pump_off()
        except:
            pass