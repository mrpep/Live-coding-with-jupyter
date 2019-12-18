from numba import jit
import signals
import numpy as np

def sources_sum(sound_list, buffer_size):
    data = np.zeros((buffer_size,))
    for sound in sound_list:
        data += sound.get_samples(buffer_size)

    return data