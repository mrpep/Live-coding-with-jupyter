import numpy as np

class Oscillator:
    def __init__(self,freq,amp,phase,offset=0,fs=44100,osc_type='sin'):
        self.freq = freq
        self.amp = amp
        self.phase = phase
        self.fs = fs
        self.osc_type = osc_type
        self.i = 0
        self.is_playing = True
        self.offset = offset
        
    def get_samples(self,buffer_size):
        if self.is_playing:
            t = np.arange(self.i,self.i+buffer_size)/self.fs
            if type(self.freq) == Oscillator:
                freq = self.freq.get_samples(buffer_size)
            elif type(self.freq) == Sequencer:
                freq = self.freq.get_samples(buffer_size)
            else:
                freq = self.freq

            if type(self.amp) == Oscillator:
                amp = self.amp.get_samples(buffer_size)
            else:
                amp = self.amp

            if type(self.phase) == Oscillator:
                phase = self.phase.get_samples(buffer_size)
            else:
                phase = self.phase

            if type(self.offset) == Oscillator:
                offset = self.offset.get_samples(buffer_size)
            else:
                offset = self.offset
                
            self.i = self.i + buffer_size
            
            return offset + amp*np.sin(2*np.pi*freq*t + phase)
        else:
            return np.zeros(shape=(buffer_size,))
    
    def set_freq(self,freq):
        self.freq = freq
        
    def set_amp(self,amp):
        self.amp = amp
        
    def set_phase(self,phase):
        self.phase = phase
        
    def play(self):
        self.is_playing = True
    def stop(self):
        self.is_playing = False
        
class Sequencer:
    def __init__(self, bpm=120, instrument=None, fs=44100,measure="4/4"):
        self.instrument = instrument
        self.measure = measure.split("/")
        self.beat_duration = 60.0/bpm
        self.sequences = {}
        self.i = 0
        self.fs = fs
        
    def get_samples(self,buffer_size):
        if self.i + buffer_size < self.sequences['freq'].shape[0]:
            y = self.sequences['freq'][self.i:self.i+buffer_size]
            self.i = self.i + buffer_size
        else:
            offset = buffer_size - (self.sequences['freq'].shape[0] - self.i)
            y = np.concatenate([self.sequences['freq'][self.i:],self.sequences['freq'][:offset]])
            self.i = offset
        return y
    
    def set_sequence(self,parameter,sequence):
        beat_samples = self.beat_duration*self.fs*int(self.measure[0])/int(self.measure[1])
        notes = []
        for note in sequence:
            notes.append(note*np.ones(shape=(int(beat_samples//8),)))
        self.sequences[parameter] = np.concatenate(notes)
        
        
    def set_bpm(self,bpm):
        self.beat_duration = 60.0/bpm
        self.set_sequence('freq',self.sequences['freq'])