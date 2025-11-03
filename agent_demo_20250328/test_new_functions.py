# test_new_functions.py
# 测试新增的 move_fast 和 pump_drop 函数

from utils_robot import *
from utils_vlm_move import *
import time

print('=' * 60)
print('测试新增函数: move_fast, pump_drop, dance_aggressive')
print('=' * 60)

def test_menu():
    """测试菜单"""
    print('\n请选择要测试的功能:')
    print('1. 测试 dance_aggressive() - 剧烈挑衅舞蹈')
    print('2. 测试 move_fast() - 快速平移 (手动指定坐标)')
    print('3. 测试 pump_drop() - 空中抛物 (手动指定坐标)')
    print('4. 测试 vlm_move_fast() - 使用VLM识别并快速移动')
    print('5. 测试 vlm_pump_drop() - 使用VLM识别并抛物')
    print('6. 综合测试 - 所有功能串联演示')
    print('0. 退出')
    
    choice = input('\n请输入选项 (0-6): ').strip()
    return choice

def test_dance():
    """测试剧烈挑衅舞蹈"""
    print('\n开始测试剧烈挑衅舞蹈...')
    dance_aggressive()

def test_move_fast_manual():
    """测试快速平移 - 手动坐标"""
    print('\n测试快速平移 (手动坐标)')
    print('示例坐标: 起点(100, -100), 终点(200, -200)')
    
    use_default = input('使用默认坐标? (y/n): ').strip().lower()
    
    if use_default == 'y':
        X_START, Y_START = 100, -100
        X_END, Y_END = 200, -200
    else:
        X_START = int(input('起点X坐标: '))
        Y_START = int(input('起点Y坐标: '))
        X_END = int(input('终点X坐标: '))
        Y_END = int(input('终点Y坐标: '))
    
    HEIGHT = int(input('移动高度 (默认220): ') or 220)
    SPEED = int(input('移动速度 (默认80): ') or 80)
    
    move_fast(X_START, Y_START, X_END, Y_END, HEIGHT=HEIGHT, SPEED=SPEED)

def test_pump_drop_manual():
    """测试空中抛物 - 手动坐标"""
    print('\n测试空中抛物 (手动坐标)')
    print('示例坐标: 起点(150, -130), 终点(50, -200)')
    
    use_default = input('使用默认坐标? (y/n): ').strip().lower()
    
    if use_default == 'y':
        XY_START = [150, -130]
        XY_END = [50, -200]
    else:
        x_start = int(input('起点X坐标: '))
        y_start = int(input('起点Y坐标: '))
        x_end = int(input('终点X坐标: '))
        y_end = int(input('终点Y坐标: '))
        XY_START = [x_start, y_start]
        XY_END = [x_end, y_end]
    
    HEIGHT_START = int(input('吸取高度 (默认90): ') or 90)
    HEIGHT_DROP = int(input('抛物高度 (默认180): ') or 180)
    HEIGHT_SAFE = int(input('安全高度 (默认220): ') or 220)
    
    pump_drop(mc, XY_START=XY_START, HEIGHT_START=HEIGHT_START,
              XY_END=XY_END, HEIGHT_DROP=HEIGHT_DROP, HEIGHT_SAFE=HEIGHT_SAFE)

def test_vlm_move_fast_demo():
    """测试 VLM 识别并快速移动"""
    print('\n测试 VLM 识别并快速移动')
    print('示例指令: "从红色方块快速移动到小猪佩奇"')
    
    prompt = input('请输入指令 (按回车使用默认): ').strip()
    if not prompt:
        prompt = '从红色方块快速移动到小猪佩奇'
    
    vlm_move_fast(PROMPT=prompt)

def test_vlm_pump_drop_demo():
    """测试 VLM 识别并空中抛物"""
    print('\n测试 VLM 识别并空中抛物')
    print('示例指令: "把绿色方块抛到篮球上"')
    
    prompt = input('请输入指令 (按回车使用默认): ').strip()
    if not prompt:
        prompt = '把绿色方块抛到篮球上'
    
    vlm_pump_drop(PROMPT=prompt)

def test_comprehensive():
    """综合测试 - 所有功能串联"""
    print('\n开始综合测试 - 展示所有新功能')
    
    print('\n[场景1] 剧烈挑衅舞蹈开场')
    dance_aggressive()
    time.sleep(2)
    
    print('\n[场景2] 快速平移演示')
    move_fast(100, -100, 200, -150, HEIGHT=200, SPEED=100)
    time.sleep(2)
    
    print('\n[场景3] 空中抛物演示')
    pump_drop(mc, XY_START=[200, -150], HEIGHT_START=90,
              XY_END=[80, -200], HEIGHT_DROP=180)
    time.sleep(2)
    
    print('\n[场景4] 胜利舞蹈')
    dance_aggressive()
    
    print('\n✅ 综合测试完成！')

def main():
    """主函数"""
    try:
        while True:
            choice = test_menu()
            
            if choice == '0':
                print('\n退出测试程序')
                break
            elif choice == '1':
                test_dance()
            elif choice == '2':
                test_move_fast_manual()
            elif choice == '3':
                test_pump_drop_manual()
            elif choice == '4':
                test_vlm_move_fast_demo()
            elif choice == '5':
                test_vlm_pump_drop_demo()
            elif choice == '6':
                test_comprehensive()
            else:
                print('❌ 无效选项，请重新选择')
            
            print('\n' + '=' * 60)
            
    except KeyboardInterrupt:
        print('\n\n用户中断')
    except Exception as e:
        print(f'\n❌ 错误: {e}')
        import traceback
        traceback.print_exc()
    finally:
        print('\n测试结束')

if __name__ == '__main__':
    main()
