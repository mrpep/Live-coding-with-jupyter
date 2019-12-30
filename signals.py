import numpy as np
import librosa

class Signal:
    def __init__(self, fs=44100):
        self.params = {}
        self.begin_t = 0       
        self.end_t = None
        self.loop = False
        self.is_playing = True
        self.fs = fs
        self.actual_sample = int(self.begin_t*self.fs)
        self.last_integration_value = 0
        
    def set_parameters(self,dict):
        self.params.update(dict)
        
    def get_parameters(self):
        return self.params
        
    def evaluate_parameters(self,t,derivatives=[],integrals=[]):
        evaluated_params = {}
        for param in self.params.keys():
            if type(self.params[param]) not in [str,int,float,np.ndarray]:
                evaluated_params[param] = self.params[param].evaluate(t)
            else:
                evaluated_params[param] = self.params[param]
            if param in derivatives:
                if type(self.params[param]) not in [str,int,float,np.ndarray]:
                    evaluated_params["{}_delta".format(param)] = self.params[param].get_derivative(t)
                else:
                    evaluated_params["{}_delta".format(param)] = 0
            if param in integrals:
                if type(self.params[param]) not in [str,int,float,np.ndarray]:
                    evaluated_params["{}_sum".format(param)] = self.params[param].get_integral(t)
                else:
                    evaluated_params["{}_sum".format(param)] = self.params[param]*t
        #print(evaluated_params)
        return evaluated_params
        
    def get_samples(self, buffer_size):
        t = np.arange(self.actual_sample, self.actual_sample + buffer_size)/self.fs
        if self.is_playing:  
            y = self.evaluate(t)
        else:
            y = np.zeros(shape=(buffer_size,))
        self.actual_sample = self.actual_sample + buffer_size
        return y
        
    def evaluate(self, t):
        pass
    
    def transform_t(self,t):
        begin_sample = int(self.begin_t*self.fs)
        if self.end_t is not None:
            end_sample = int(self.end_t*self.fs)
        else:
            end_sample = None
            
        if self.loop and end_sample is not None:
            t = t*self.fs
            t = t%(end_sample - begin_sample) + begin_sample
            t = t/self.fs
        return t
        
    def play(self):
        self.is_playing = True
        
    def stop(self):
        self.is_playing = False

    def __mul__(self,other):
        return MultiplyOscillator(self,other)
    
    def __add__(self,other):
        return AddOscillator(self,other)
    
    def get_integral(self,t):
        integral = self.last_integration_value + np.cumsum(self.evaluate(t))/self.fs
        self.last_integration_value = integral[-1]
        
        return integral
    
class MultiplyOscillator(Signal):
    def __init__(self,a,b):
        super(MultiplyOscillator,self).__init__()
        self.a = a
        self.b = b
    def evaluate(self,t):
        if type(self.b) is not (float or int):
            return self.a.evaluate(t)*self.b.evaluate(t)
        else:
            return self.b*self.a.evaluate(t)
    
class AddOscillator(Signal):
    def __init__(self,a,b):
        super(AddOscillator,self).__init__()
        self.a = a
        self.b = b
    def evaluate(self,t):
        return self.a.evaluate(t) + self.b.evaluate(t)
    
class Oscillator(Signal):
    def __init__(self,frequency,amplitude,phase,offset=0,fs=44100,osc_type='sin',duty_cycle=0.5):
        super(Oscillator,self).__init__()
        self.params = {'frequency':frequency,
                       'amplitude': amplitude,
                       'phase': phase,
                       'offset': offset,
                       'fs': fs,
                       'osc_type': osc_type,
                       'duty_cycle': duty_cycle}
        
        self.last_integration_value = 0
                       
    def evaluate(self,t):
        t = self.transform_t(t)
        self.evaluated_params = self.evaluate_parameters(t,integrals=['frequency'])
        if self.evaluated_params['osc_type'] == 'sin':
            phase = 2*np.pi*self.evaluated_params['frequency_sum'] + self.evaluated_params['phase']
            return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*np.sin(phase)
        elif self.evaluated_params['osc_type'] == 'square':
            t = (t*self.fs).astype(int)
            period_samples = np.array((self.fs/self.evaluated_params['frequency']),dtype=int)
            duty_samples = np.array(period_samples*self.evaluated_params['duty_cycle'],dtype=int)
            return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*2*((((t%period_samples)<duty_samples).astype(int))-0.5)
        elif self.evaluated_params['osc_type'] == 'sawtooth':
            t = (t*self.fs).astype(int)
            period_samples = np.array((self.fs/self.evaluated_params['frequency']),dtype=int)
            return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*2*((t%period_samples)/period_samples-0.5)
        elif self.evaluated_params['osc_type'] == 'triangular':
            t = (t*self.fs).astype(int)
            period_samples = np.array((self.fs/self.evaluated_params['frequency']),dtype=int)
            upward_ramp = (t%period_samples)*((t%period_samples)<=(period_samples//2))
            downward_ramp = (period_samples - t%period_samples)*((t%period_samples)>(period_samples//2))
            return self.evaluated_params['offset'] + self.evaluated_params['amplitude']*2*((upward_ramp + downward_ramp)/(period_samples//2)-0.5)
        
    def get_derivative(self,t):
        pass
    


class Sequence(Signal):
    def __init__(self,sequence):
        super(Sequence,self).__init__()
        self.params = {'sequence': sequence}
        
    def evaluate(self,t):
        t = self.transform_t(t)
        self.params['sequence'] = np.array(self.params['sequence'])
        sequenced_data = self.params['sequence'][:,2,np.newaxis]*(np.logical_and(t>=(self.params['sequence'][:,0,np.newaxis]),t<(self.params['sequence'][:,1,np.newaxis]))).astype(int)
        return np.sum(sequenced_data,axis=0)
    
class Sample(Signal):
    def __init__(self,audio_path,fs = 44100):
        super(Sample,self).__init__()
        self.fs = 44100
        self.wavfile, fs = librosa.core.load(audio_path,sr=self.fs)
        
    def evaluate(self,t):
        t = (self.transform_t(t)*self.fs).astype(int)
        y = np.zeros((t.shape[0],))
        print(self.wavfile.shape)
        print(t[t<self.wavfile.shape[0]])
        y[:len(t[t<self.wavfile.shape[0]])] = self.wavfile[t[t<self.wavfile.shape[0]]]
        
        return y
        