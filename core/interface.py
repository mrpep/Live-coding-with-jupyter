from .audio_engine import AudioEngine
import threading
import pyaudio

def select_device_ui(device_type='all'):
    player = pyaudio.PyAudio()
    print("Please select an {} device:".format(device_type))
    
    n_hosts = player.get_host_api_count()
    device_counter = 0
    device_dict = {}
    if device_type == 'input':
        default_device = player.get_default_input_device_info()['index']
    elif device_type == 'output':
        default_device = player.get_default_output_device_info()['index']
    else:
        pass
    
    for host_id in range(n_hosts):
        host_info = player.get_host_api_info_by_index(host_id)
        n_host_devices = host_info['deviceCount']
        print(host_info['name']+':')
        for device_id in range(n_host_devices):
            device_info = player.get_device_info_by_host_api_device_index(host_id,device_id)
            if (device_type == 'all') or (device_type == 'input' and device_info['maxInputChannels']>0) or (device_type == 'output' and device_info['maxOutputChannels']>0):
                if device_info['index'] == default_device:
                    print("  -> {}) {}".format(device_counter,device_info['name']))
                    device_dict[''] = device_info['index']
                else:
                    print("     {}) {}".format(device_counter,device_info['name']))
                
                device_dict[str(device_counter)] = device_info['index']
                device_counter += 1
            else:
                pass
            
    selected_device = device_dict[input('',)]
    
    return selected_device

def start_session():
    audio_engine = AudioEngine()
    audio_thread = threading.Thread(target = audio_engine.run, daemon = True)
    
    print("Starting new session")
    select_devices = input("Use default output devices? [(Y)/n)]")
    if select_devices == '':
        out_device = None
    else:
        out_device = select_device_ui(device_type='output')
        
    audio_engine.set_output_device(out_device)
    
    select_devices = input("Use default input devices? [(Y)/n)]")
    if select_devices == '':
        in_device = None
    else:
        in_device = select_device_ui(device_type='input')
    
    audio_engine.set_input_device(in_device)
    
    
    audio_thread.start()
    audio_engine.play()
    
    return audio_engine