# utils_tts.py
# 同济子豪兄 2024-5-23
# 语音合成（支持在线和离线两种模式）

print('导入语音合成模块')

import os
import pyaudio
import wave

# 在线语音合成相关导入（可选）
try:
    import appbuilder
    from API_KEY import APPBUILDER_TOKEN
    
    # 设置环境变量（必须在初始化TTS之前）
    os.environ["APPBUILDER_TOKEN"] = APPBUILDER_TOKEN
    
    # 初始化TTS对象
    tts_ab = appbuilder.TTS()
    ONLINE_TTS_AVAILABLE = True
    print('在线TTS模块加载成功')
    print(f'APPBUILDER_TOKEN已设置: {APPBUILDER_TOKEN[:20]}...')
except Exception as e:
    ONLINE_TTS_AVAILABLE = False
    print(f'在线TTS模块加载失败: {e}')
    print('将只能使用离线TTS模式')

def tts_online(TEXT='我是同济子豪兄的麒麟臂', tts_wav_path='temp/tts.wav'):
    '''
    在线语音合成TTS，使用百度PaddleSpeech，生成wav音频文件
    需要有效的APPBUILDER_TOKEN
    '''
    if not ONLINE_TTS_AVAILABLE:
        raise RuntimeError("在线TTS不可用，请检查appbuilder安装和API_KEY配置")
    
    print(f'使用在线TTS合成: {TEXT}')
    inp = appbuilder.Message(content={"text": TEXT})
    out = tts_ab.run(inp, model="paddlespeech-tts", audio_type="wav")
    with open(tts_wav_path, "wb") as f:
        f.write(out.content["audio_binary"])
    print(f"在线TTS语音合成，导出wav音频文件至：{tts_wav_path}")

def tts_offline(TEXT='我是同济子豪兄的麒麟臂', tts_wav_path='temp/tts.wav'):
    '''
    离线语音合成TTS，使用espeak，生成wav音频文件
    需要先安装: sudo apt-get install espeak
    '''
    print(f'使用离线TTS合成: {TEXT}')
    # 使用espeak生成wav文件，-v zh表示中文，-s 150表示语速
    os.system(f'espeak -v zh -s 150 "{TEXT}" --stdout > {tts_wav_path}')
    print(f"离线TTS语音合成，导出wav音频文件至：{tts_wav_path}")

def tts(TEXT='我是同济子豪兄的麒麟臂', tts_wav_path='temp/tts.wav', mode='auto'):
    '''
    语音合成TTS，生成wav音频文件
    参数:
        TEXT: 要合成的文本
        tts_wav_path: 输出wav文件路径
        mode: 合成模式
            - 'online': 强制使用在线模式（百度PaddleSpeech）
            - 'offline': 强制使用离线模式（espeak）
            - 'auto': 自动选择（优先在线，失败则使用离线）
    '''
    if mode == 'online':
        tts_online(TEXT, tts_wav_path)
    elif mode == 'offline':
        tts_offline(TEXT, tts_wav_path)
    elif mode == 'auto':
        if ONLINE_TTS_AVAILABLE:
            try:
                tts_online(TEXT, tts_wav_path)
            except Exception as e:
                print(f'在线TTS失败: {e}')
                print('切换到离线TTS模式')
                tts_offline(TEXT, tts_wav_path)
        else:
            print('在线TTS不可用，使用离线TTS模式')
            tts_offline(TEXT, tts_wav_path)
    else:
        raise ValueError(f"不支持的模式: {mode}，请使用 'online', 'offline' 或 'auto'")

def play_wav(wav_file='asset/welcome.wav', device='usb'):
    '''
    播放wav音频文件
    参数:
        wav_file: wav文件路径
        device: 音频设备，可选值：
            'usb' - USB音频设备 UACDemoV1.0 (card 1, device 0) [默认]
            'hdmi' - HDMI输出 (card 0, device 0)
            'headphone' - 3.5mm耳机接口 (card 2, device 0)
            None - 使用系统默认设备
            或直接指定 'plughw:1,0' 格式
    '''
    # 设备映射（根据实际硬件配置）
    device_map = {
        'hdmi': 'plughw:0,0',        # bcm2835 HDMI 1
        'usb': 'plughw:1,0',          # UACDemoV1.0 (USB Audio)
        'headphone': 'plughw:2,0'     # bcm2835 Headphones
    }
    
    if device is None:
        # 使用系统默认设备
        prompt = 'aplay -t wav {} -q'.format(wav_file)
    elif device in device_map:
        prompt = 'aplay -D {} -t wav {} -q'.format(device_map[device], wav_file)
    else:
        # 直接使用用户指定的设备字符串
        prompt = 'aplay -D {} -t wav {} -q'.format(device, wav_file)
    
    print(f'播放音频: {wav_file} (设备: {device})')
    print(f'执行命令: {prompt}')
    result = os.system(prompt)
    if result != 0:
        print(f'警告: 音频播放命令返回错误码 {result}')
    return result

# def play_wav(wav_file='temp/tts.wav'):
#     '''
#     播放wav文件
#     '''
#     wf = wave.open(wav_file, 'rb')
 
#     # 实例化PyAudio
#     p = pyaudio.PyAudio()
 
#     # 打开流
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True)

#     chunk_size = 1024
#     # 读取数据
#     data = wf.readframes(chunk_size)
 
#     # 播放音频
#     while data != b'':
#         stream.write(data)
#         data = wf.readframes(chunk_size)
 
#     # 停止流，关闭流和PyAudio
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

'''
文本 "你好" 
    ↓
appbuilder.Message 包装
    ↓
发送到百度云端 PaddleSpeech-TTS 模型
    ↓
模型合成语音（选择音色、语速等）
    ↓
返回 WAV 格式音频二进制数据
    ↓
保存为 temp/tts.wav 文件

'''