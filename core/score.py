import re
import numpy as np

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
    split_idxs = []
    for i,elem in enumerate(seq):
        if elem == val:
            split_idxs.append(i)
            if i+1 < len(seq) and seq[i+1] != val:
                split_idxs.append(i+1)
    split_idxs.append(len(seq))
    split_idxs.insert(0,0)
    split_idxs = list(set(split_idxs))
    
    splits = [seq[i:j] for i,j in zip(split_idxs[:-1],split_idxs[1:])]
    
    return splits
    
def recursive_get_duration(sequence, val, duration, p, q, multipliers):
    #print("Calculating durations for level: {}".format(val))
    splits = split_by_val(sequence,val)
    multipliers_subset = np.zeros((len(multipliers)))
    i = p
    #print(splits)
    for split in splits:
        if val in split:
            multipliers_subset[i] = multipliers[i]
            i = i+1
        else:
            multipliers_subset[i] = 1
            i = i+len(split)        
    
    #print(multipliers_subset)
    duration[p:q] = duration[p:q]*np.sum(multipliers_subset)
    #print(duration)
    for split in splits:
        q = p + len(split)
        if len(split) > 1:
            duration = recursive_get_duration(split,val+1,duration,p,q,multipliers)
        p = q
        
    return duration

def get_duration_multipliers(sequence):
    multipliers = []
    for raw_note in sequence:
        note = raw_note.replace('[','').replace(']','')
        note_data = re.match(".*([/*])([.0123456789]*).*",note)
        if note_data:
            op = note_data.groups()[0]
            quantity = note_data.groups()[1]
            if op == '*':
                multipliers.append(float(quantity))
            else:
                multipliers.append(1.0/float(quantity))
        else:
            multipliers.append(1.0)
            
    return multipliers

def get_durations(seq_notes):
    state = 0
    states = []
    for note in seq_notes:
        state = state + note.count('[') 
        states.append(state)
        state = state - note.count(']')
    
    multipliers = np.array(get_duration_multipliers(seq_notes))
    duration = np.ones((len(multipliers),))
    p = 0
    q = len(states)
    val = 0

    duration = recursive_get_duration(states,val,duration/multipliers,p,q,multipliers)
    
    return duration
    
def score_to_seq(score,bar_duration=1.0):
    #Durations:
    seq_notes = score.split()
    durations = bar_duration/get_durations(seq_notes)
    
    #Notes to freq:
    freqs = []
    for raw_note in seq_notes:
        note = raw_note.replace('[','').replace(']','')
        if re.match(".*(X).*",note):
            freqs.append(0.0001)
        else:
            freqs.append(note_to_hz(note))
    t = 0
    seq = []
    for i, dur in enumerate(durations):
        note = (t,t+dur,freqs[i])
        t = t + dur
        seq.append(note)
        
    return seq