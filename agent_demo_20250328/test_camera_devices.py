# test_camera_devices.py
# 测试所有摄像头设备，找到正确的USB摄像头

import cv2
import time

print('=== 测试所有摄像头设备 ===\n')

# 测试 /dev/video0 和 /dev/video1
for i in [0, 1]:
    print(f'\n--- 测试 /dev/video{i} ---')
    
    cap = cv2.VideoCapture(i)
    
    if not cap.isOpened():
        print(f'❌ 无法打开 /dev/video{i}')
        continue
    
    # 获取摄像头属性
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f'✅ 成功打开 /dev/video{i}')
    print(f'   分辨率: {int(width)}x{int(height)}')
    print(f'   帧率: {fps} FPS')
    
    # 尝试读取帧
    print('   预热摄像头...')
    time.sleep(1)
    for _ in range(5):
        cap.read()
        time.sleep(0.1)
    
    ret, frame = cap.read()
    
    if ret and frame is not None:
        print(f'   ✅ 可以读取画面，实际分辨率: {frame.shape[1]}x{frame.shape[0]}')
        
        # 保存测试图片
        filename = f'temp/test_video{i}.jpg'
        cv2.imwrite(filename, frame)
        print(f'   测试图片已保存: {filename}')
        
        # 显示画面
        cv2.imshow(f'Video{i} Test', frame)
        print(f'   按任意键继续测试下一个设备...')
        cv2.waitKey(2000)  # 显示2秒
        cv2.destroyAllWindows()
    else:
        print(f'   ❌ 无法读取画面')
    
    cap.release()

print('\n\n=== 测试完成 ===')
print('请查看 temp/ 目录中的测试图片，确定哪个设备的画面正确')
print('\n建议：')
print('- 如果 test_video0.jpg 画面正常，使用 camera_index=0')
print('- 如果 test_video1.jpg 画面正常，使用 camera_index=1')
print('\n修改方法：')
print('在 vlm_agent_go.py 中修改：')
print('top_view_shot(check=False, camera_index=0)  # 改为正确的索引')
