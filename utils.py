import numpy as np
import re

def sources_sum(sound_list, buffer_size):
    data = np.zeros((buffer_size,))
    for k, sound in sound_list.items():
        data += sound.generate(buffer_size)

    return data