import numpy as np
import re

def sources_sum(sound_list, buffer_size):
    data = np.zeros((buffer_size,))
    for k, sound in sound_list.items():
        data += sound.get_samples(buffer_size)

    return data

def note_to_hz(note):
    note_data = re.match("([ABCDEFG])([#b]*)([0123456789]+)",note)
    notes_dict = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    bemol_dict = {'b':-1,'#':1,'':0}
    note = note_data.groups()[0]
    bemol = note_data.groups()[1]
    octave = int(note_data.groups()[2])

    c5_hz = 440.0*(2.0**(3.0/12.0))
    hz = c5_hz*(2**((notes_dict[note]+bemol_dict[bemol])/12.0+(octave-5)))
    
    return hz
    
def split_by_val(seq,val):
    split_idxs = [0]
    for i,elem in enumerate(seq):
        if elem == val and i != 0:
            split_idxs.append(i)
            if i+1 < len(seq) and seq[i+1] != val:
                split_idxs.append(i+1)
    split_idxs.append(len(seq))
    
    splits = [seq[i:j] for i,j in zip(split_idxs[:-1],split_idxs[1:])]
    
    return splits
    
def recursive_get_duration(sequence, val, duration, p, q):
    splits = split_by_val(sequence,val)
    duration[p:q] = duration[p:q]*len(splits)
    for split in splits:
        q = p + len(split)
        if len(split) > 1:
            duration = recursive_get_duration(split,val+1,duration,p,q)
        p = q
        
    return duration

def get_durations(seq_notes):
    state = 0
    states = []
    for note in seq_notes:
        state = state + note.count('[') 
        states.append(state)
        state = state - note.count(']')
        
    duration = np.ones((len(states),))
    p = 0
    q = len(states)
    val = 0
    duration = recursive_get_duration(states,val,duration,p,q)
    
    return duration
    
def score_to_seq(score):
    #Durations:
    seq_notes = score.split()
    durations = 1.0/get_durations(seq_notes)
    
    #Notes to freq:
    freqs = []
    for raw_note in seq_notes:
        note = raw_note.replace('[','').replace(']','')
        freqs.append(note_to_hz(note))
        
    t = 0
    seq = []
    for i, dur in enumerate(durations):
        note = (t,t+dur,freqs[i])
        t = t + dur
        seq.append(note)
        
    return seq
