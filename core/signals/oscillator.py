import numpy as np
from ..signal import Signal

class Oscillator(Signal):
    def __init__(self, amplitude = 1, frequency = 440, phase_0 = 0, offset = 0, osc_type='sin'):
        super(Oscillator,self).__init__()
        self.parameters = {'frequency':frequency,
                           'phase_0':phase_0,
                           'amplitude':amplitude,
                           'offset':offset,
                           'osc_type':osc_type}
        
        self.phase = phase_0
        self.min_phase = 0
        self.max_phase = 2*np.pi

    def get_frequency(self,steps):
        if isinstance(self.parameters['frequency'],int) or isinstance(self.parameters['frequency'],float):
            return self.parameters['frequency']
        else:
            return self.parameters['frequency'].generate(steps)
        
    def get_offset(self,steps):
        if isinstance(self.parameters['offset'],int) or isinstance(self.parameters['offset'],float):
            return self.parameters['offset']
        else:
            return self.parameters['offset'].generate(steps)
        
    def get_amplitude(self,steps):
        if isinstance(self.parameters['amplitude'],int) or isinstance(self.parameters['amplitude'],float):
            return self.parameters['amplitude']
        else:
            return self.parameters['amplitude'].generate(steps)
        
    def get_phase_increment(self, steps):
        return np.ones(steps)*2*np.pi*self.get_frequency(steps)/self.sr
        
    def generate(self, steps):
        phase = self.get_phase(steps)
        self.phase = phase[-1]
        
        if self.parameters['osc_type'] == 'sin':    
            output = self.get_offset(steps) + self.get_amplitude(steps)*np.sin(phase)
        elif self.parameters['osc_type'] == 'saw':
            output = self.get_offset(steps) + self.get_amplitude(steps)*(1.0 - (phase/np.pi))
        elif self.parameters['osc_type'] == 'square':
            output = self.get_offset(steps) + self.get_amplitude(steps)*(1-2.0*(phase<np.pi))
        elif self.parameters['osc_type'] == 'triangular':
            output = self.get_offset(steps) + self.get_amplitude(steps)*(1.0 - 2.0*np.abs(phase/np.pi - 1.0))
        
        return output