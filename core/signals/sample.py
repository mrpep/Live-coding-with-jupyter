from ..signal import Signal

import numpy as np
import librosa

class Sample(Signal):
    def __init__(self,audio_path):
        super(Sample,self).__init__()
        self.parameters = {'audio_path':audio_path}
        self.wavfile, sr = librosa.core.load(audio_path,sr=self.sr)
        self.max_phase = self.wavfile.shape[0]/self.sr
    
    def get_phase(self,steps):
        phase = self.phase + np.arange(1,steps+1)
        if self.max_phase:
            phase = phase % ((self.max_phase - self.min_phase)*self.sr)
            
        return (self.min_phase*self.sr + phase).astype(int)
    
    def generate(self,steps):
        phase = self.get_phase(steps)
        self.phase = phase[-1]
        
        output = self.wavfile[phase]
        
        return output