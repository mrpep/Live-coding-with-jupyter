import numpy as np

class Signal:
    def __init__(self, fs=44100):
        self.params = {}
        self.begin_t = 0       
        self.end_t = None
        self.loop = False
        self.is_playing = True
        self.fs = fs
        self.actual_sample = int(self.begin_t*self.fs)
        
    def set_parameters(self,dict):
        self.params.update(dict)
        
    def get_parameters(self):
        return self.params
        
    def evaluate_parameters(self,t,derivatives=[],integrals=[]):
        evaluated_params = {}
        for param in self.params.keys():
            if type(self.params[param]) not in [str,int,float]:
                evaluated_params[param] = self.params[param].evaluate(t)
            else:
                evaluated_params[param] = self.params[param]
            if param in derivatives:
                if type(self.params[param]) not in [str,int,float]:
                    evaluated_params["{}_delta".format(param)] = self.params[param].get_derivative(t)
                else:
                    evaluated_params["{}_delta".format(param)] = 0
            if param in integrals:
                if type(self.params[param]) not in [str,int,float]:
                    evaluated_params["{}_sum".format(param)] = self.params[param].get_integral(t)
                else:
                    evaluated_params["{}_sum".format(param)] = self.params[param]*t
        
        return evaluated_params
        
    def get_samples(self, buffer_size):
        begin_sample = int(self.begin_t*self.fs)
        if self.end_t is not None:
            end_sample = int(self.end_t*self.fs)
        else:
            end_sample = None
        
        if self.is_playing:  
            if self.end_t is not None and self.actual_sample - end_sample>0:
                self.actual_sample = begin_sample
                
            if self.end_t is not None and self.actual_sample + buffer_size > end_sample:

                remaining_samples = end_sample - self.actual_sample
                new_cycle_samples = buffer_size - remaining_samples
                
                if self.loop:
                    y1 = self.evaluate(np.arange(self.actual_sample,self.actual_sample+remaining_samples)/self.fs)
                    y2 = self.evaluate(np.arange(begin_sample,begin_sample + new_cycle_samples)/self.fs)
                    self.actual_sample = begin_sample + new_cycle_samples
                    y = np.concatenate([y1,y2])
                    #print("{}_1".format(y.shape))
                else:
                    y1 = self.evaluate(np.arange(self.actual_sample,self.actual_sample+remaining_samples)/self.fs)
                    y2 = np.zeros(shape=(new_cycle_samples,))
                    self.actual_sample = begin_sample
                    y = np.concatenate([y1,y2])
                    self.stop()
                    #print(y.shape + '_2')
            else:
                y = self.evaluate(np.arange(self.actual_sample,self.actual_sample+buffer_size)/self.fs)
                self.actual_sample = self.actual_sample + buffer_size
                #print(y.shape + '_3')
        else:
            y = np.zeros(shape=(buffer_size,))
            #print(y.shape + '_4')
        return y
        
    def evaluate(self, t):
        pass
        
    def play(self):
        self.is_playing = True
        
    def stop(self):
        self.is_playing = False

class Oscillator(Signal):
    def __init__(self,name,frequency,amplitude,phase,offset=0,fs=44100,osc_type='sin'):
        super(Oscillator,self).__init__()
        self.params = {'name': name,
                       'frequency':frequency,
                       'amplitude': amplitude,
                       'phase': phase,
                       'offset': offset,
                       'fs': fs,
                       'osc_type': osc_type}
        
        self.last_integration_value = 0
                       
    def evaluate(self,t):
        self.evaluated_params = self.evaluate_parameters(t,integrals=['frequency'])
        phase = 2*np.pi*self.evaluated_params['frequency_sum'] + self.evaluated_params['phase']
        return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*np.sin(phase)
    
    def get_derivative(self,t):
        pass
    
    def get_integral(self,t):
        integral = self.last_integration_value + np.cumsum(self.evaluate(t))/self.params['fs']
        self.last_integration_value = integral[-1]
        
        return integral

                       
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