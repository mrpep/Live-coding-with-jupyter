import numpy as np

class Signal:
    def __init__(self, fs=44100):
        self.params = {}
        self.begin_t = 0
        self.t = self.begin_t
        self.end_t = None
        self.loop = False
        self.is_playing = True
        self.fs = fs
        
    def set_parameters(self,dict):
        self.params.update(dict)
        
    def get_parameters(self):
        return self.params
        
    def evaluate_parameters(self,t):
        evaluated_params = {}
        for param in self.params.keys():
            if type(self.params[param]) not in [str,int,float]:
                evaluated_params[param] = self.params[param].evaluate(t)
            else:
                evaluated_params[param] = self.params[param]
        
        return evaluated_params
        
    def get_samples(self, buffer_size):
        if self.is_playing:
            
            if self.end_t is not None and self.t - self.end_t>0:
                self.t = 0
                
            if self.end_t is not None and self.t + buffer_size > self.end_t:
                remaining_samples = self.end_t - self.t
                new_cycle_samples = buffer_size - remaining_samples
                if self.loop:
                    y1 = self.evaluate(np.arange(self.t,self.t+remaining_samples)/self.fs)
                    y2 = self.evaluate(np.arange(self.begin_t,self.begin_t + new_cycle_samples)/self.fs)
                    self.t = self.begin_t + new_cycle_samples
                    y = np.concatenate([y1,y2])
                else:
                    y1 = self.evaluate(np.arange(self.t,self.t+remaining_samples)/self.fs)
                    y2 = np.zeros(shape=(new_cycle_samples,))
                    self.t = self.begin_t
                    y = np.concatenate([y1,y2])
                    self.stop()
            else:
                y = self.evaluate(np.arange(self.t,self.t+buffer_size)/self.fs)
                self.t = self.t + buffer_size
        else:
            y = np.zeros(shape=(buffer_size,))
            
        return y
        
    def evaluate(self, t):
        pass
        
    def play(self):
        self.is_playing = True
        
    def stop(self):
        self.is_playing = False

class Oscillator(Signal):
    def __init__(self,name,freq,amp,phase,offset=0,fs=44100,osc_type='sin'):
        super(Oscillator,self).__init__()
        self.params = {'name': name,
                       'frequency':freq,
                       'amplitude': amp,
                       'phase': phase,
                       'offset': offset,
                       'fs': fs,
                       'osc_type': osc_type}
                       
    def evaluate(self,t):
        self.evaluated_params = self.evaluate_parameters(t)
        return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*np.sin(2*np.pi*self.evaluated_params['frequency']*t + self.evaluated_params['phase'])
                       
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