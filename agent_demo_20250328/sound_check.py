# sound_check.py
# 快速检查语音相关的所有功能：麦克风、录音、扬声器播放声音、语音识别、语音合成
# 同济子豪兄 2024-7-15
# 修改：无麦克风时从文本文件读取输入

from utils_tts import *             # 语音合成模块

# 从文本文件读取输入（替代麦克风录音）
print('从文本文件读取输入')
input_file = 'temp/test_input.txt'
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        speech_result = f.read().strip()
    print(f'读取到的文本：{speech_result}')
except FileNotFoundError:
    print(f'文件 {input_file} 不存在，使用默认文本')
    speech_result = '你好，这是一个测试'

# 语音合成
print('开始语音合成')
tts(TEXT=speech_result,tts_wav_path='temp_newtts.wav',mode='online')

# 播放语音合成音频 - 尝试不同设备
print('\n=== 测试音频播放 ===')
print('1. 尝试 USB 音频设备...')
play_wav('temp/speech_record.wav', device='usb')

print('\n2. 尝试 3.5mm 耳机接口...')
play_wav('temp/speech_record.wav', device='headphone')

print('\n3. 尝试 HDMI 输出...')
play_wav('temp/speech_record.wav', device='hdmi')

print('\n如果听到声音，请记住是哪个设备！')

