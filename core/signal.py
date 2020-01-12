import numpy as np

class Signal():
    def __init__(self,sr=44100):
        self.sr = sr
        self.min_phase = 0
        self.max_phase = None
        self.phase = 0
        
    def get_phase_increment(self,steps):
        return np.ones(steps)/self.sr
    
    def get_phase(self,steps):
        phase = self.phase + np.cumsum(self.get_phase_increment(steps))
        if self.max_phase:
            phase = phase % (self.max_phase - self.min_phase)
            
        return self.min_phase + phase
    
    def loop(self,t0,t1):
        self.min_phase = t0
        self.max_phase = t1
        
    def __mul__(self,other):
        return MultiplySignal(self,other)
    
    def __add__(self,other):
        return AddSignal(self,other)
    
class AddSignal(Signal):
    def __init__(self,a,b):
        super(AddSignal,self).__init__()
        self.a = a
        self.b = b
    def generate(self,steps):
        return self.a.generate(steps) + self.b.generate(steps)
    
class MultiplySignal(Signal):
    def __init__(self,a,b):
        super(MultiplySignal,self).__init__()
        self.a = a
        self.b = b
    def generate(self,steps):
        if not(isinstance(self.b,float) or isinstance(self.b,int)):
            return self.a.generate(steps)*self.b.generate(steps)
        else:
            return self.b*self.a.generate(steps)