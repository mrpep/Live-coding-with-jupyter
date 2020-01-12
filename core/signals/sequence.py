import numpy as np
from ..signal import Signal

class Sequence(Signal):
    def __init__(self, sequence):
        super(Sequence,self).__init__()
        self.params = {'sequence': sequence}
        self.max_phase = np.max(np.array(sequence)[:,1])
    
    def generate(self,steps):
        phase = self.get_phase(steps)
        self.phase = phase[-1]
        sequence = np.array(self.params['sequence'])
        sequenced_data = sequence[:,2,np.newaxis]*(np.logical_and(phase>=(sequence[:,0,np.newaxis]),phase<(sequence[:,1,np.newaxis]))).astype(int)
        return np.sum(sequenced_data,axis=0)