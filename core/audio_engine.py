import pyaudio
import threading
import numpy as np
import utils

class AudioEngine(threading.Thread):
    def __init__(self, fs = 44100, buffer_size = 512):
        super(AudioEngine,self).__init__()
        self.fs = fs
        self.buffer_size = buffer_size
        self.is_running = True
        self.is_playing = False
        self.input_device = None
        self.output_device = None
        self.sound_list = {}
        loop_state = True
        self.i = 0
    
    def set_input_device(self,device):
        self.input_device = device
        
    def set_output_device(self,device):
        self.output_device = device
        
    def add_sound(self,sound,identifier=None):
        self.sound_list[identifier] = sound
    
    def run(self):
        player = pyaudio.PyAudio()
        if self.input_device is None:
            self.input_device = player.get_default_input_device_info()['index']
        if self.output_device is None:
            self.output_device = player.get_default_output_device_info()['index']
        
        stream = player.open(format = pyaudio.paFloat32,channels=1,
                             rate=self.fs, output=True, 
                             frames_per_buffer=self.buffer_size,input_device_index=self.input_device,output_device_index=self.output_device)
        
        while self.is_running:
            if self.is_playing:
                #data = np.zeros((self.buffer_size,))
                #for sound in self.sound_list:
                #    data += sound.get_samples(self.buffer_size)
                
                data = utils.sources_sum(self.sound_list, self.buffer_size)
                data = data.astype(np.float32)
                data = np.tanh(data)
                data = data.tostring()
                stream.write(data)
                
    def stop(self):
        self.is_running = False
        
    def stop_all_sounds(self):
        for sound in self.sound_list:
            sound.stop()
            
    def remove_all_sounds(self):
        self.sound_list = []
        
    def remove_sound(self,identifier):
        self.sound_list.pop(identifier)
        
    def pause(self):
        self.is_playing = False
        
    def play(self):
        self.is_playing = True