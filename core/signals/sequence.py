import numpy as np
from ..signal import Signal

class Sequence(Signal):
    def __init__(self, sequence):
        super(Sequence,self).__init__()
        self.parameters = {'sequence': sequence}
        self.max_phase = np.max(np.array(sequence)[:,1])
    
    def generate(self,steps):
        phase = self.get_phase(steps)
        self.phase = phase[-1]
        sequence = np.array(self.parameters['sequence'])
        sequenced_data = sequence[:,2,np.newaxis]*(np.logical_and(phase>=(sequence[:,0,np.newaxis]),phase<(sequence[:,1,np.newaxis]))).astype(int)
        return np.sum(sequenced_data,axis=0)
    
    def __mul__(self,other):
        return MultiplySequence(self,other)
    
    def __rmul__(self,other):
        #Make multiplication conmutative
        return self.__mul__(other)
    
    def __add__(self,other):
        return AddSequence(self,other)
    
class AddSequence(Sequence):
    def __init__(self,a,b):
        super(AddSequence,self).__init__(a.parameters['sequence'])
        sequence_a = np.array(a.parameters['sequence'])
        
        t_break = np.max(sequence_a[:,1])
        sequence_b = np.array(b.parameters['sequence'])
        seq_offset = t_break*np.ones_like(sequence_b)
        seq_offset[:,2] = 0
        sequence_b += seq_offset
        
        sequence = np.concatenate([sequence_a,sequence_b])
        self.parameters = {'sequence': list(map(tuple,sequence))}
        self.max_phase = np.max(np.array(sequence)[:,1])
        
class MultiplySequence(Sequence):
    def __init__(self,a,b):
        super(MultiplySequence,self).__init__(a.parameters['sequence'])
        sequence_a = np.array(a.parameters['sequence'])
        
        t_break = np.max(sequence_a[:,1])
        offset_i = t_break*np.ones_like(sequence_a)
        offset_i[:,2] = 0    
        offset = np.concatenate([i*offset_i for i in range(b)])
        
        sequence = offset + np.tile(sequence_a,(b,1))
        
        self.parameters = {'sequence': list(map(tuple,sequence))}
        self.max_phase = np.max(np.array(sequence)[:,1])
