import pyaudio
import threading
import numpy as np
import utils

class AudioEngine(threading.Thread):
    def __init__(self):
        super(AudioEngine,self).__init__()
        self.fs = 44100
        self.buffer_size = 1024
        self.is_running = True
        self.is_playing = False

        self.sound_list = []
        loop_state = True
        self.i = 0
    
    def add_sound(self,sound):
        self.sound_list.append(sound)
    
    def run(self):
        player = pyaudio.PyAudio()
        stream = player.open(format = pyaudio.paFloat32,channels=1,
                             rate=self.fs, output=True, 
                             frames_per_buffer=self.buffer_size)
        
        while self.is_running:
            if self.is_playing:
                #data = np.zeros((self.buffer_size,))
                #for sound in self.sound_list:
                #    data += sound.get_samples(self.buffer_size)
                
                data = utils.sources_sum(self.sound_list, self.buffer_size)
                data = np.tanh(data.astype(np.float32))
                data = data.tostring()
                stream.write(data)
                
    def stop(self):
        self.is_running = False
        
    def stop_all_sounds(self):
        for sound in self.sound_list:
            sound.stop()
            
    def remove_all_sounds(self):
        self.sound_list = []
        
    def pause(self):
        self.is_playing = False
        
    def play(self):
        self.is_playing = True