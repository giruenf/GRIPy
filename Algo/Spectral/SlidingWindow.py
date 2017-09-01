# -*- coding: utf-8 -*-

import numpy as np

# Based on: http://stackoverflow.com/a/4947453 
# with some adjusts for noverlap

"""
Examples of use:
    
    1-D:
    ====    
    a = np.array(range(100), dtype=np.int)
    b = SlidingWindow(a, 10, 0)   # window_size=10, no overlap
    
    2-D:
    ====      
    a = np.array(range(100), dtype=np.int).reshape((10, 10))
    b = SlidingWindow(a, (4, 4), 2)   # window_size=4 (each dimension), overlap=2
    
    3-D:
    ====      
    a = np.array(range(1000), dtype=np.int).reshape((10, 10, 10))
    b = SlidingWindow(a, (3, 3, 3), 1)  # window_size=3 (each dimension), overlap=1    
    
    
"""

def rolling_window_lastaxis(a, window_size, noverlap):
    if window_size < 1:
       raise ValueError("`window_size` must be at least 1.")
    if window_size > a.shape[-1]:
       raise ValueError("`window_size` is too long.")
    if noverlap is None:
        noverlap = window_size - 1 
    step = window_size - noverlap 
    if noverlap > window_size:
        raise Exception('Overlap cannot be greater than window size.')
    shape = a.shape[:-1] + ((a.shape[-1]-window_size)/step+1, window_size)
    strides =  a.strides[:-1] + (a.strides[-1]*step,) + a.strides[-1:]
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def SlidingWindow(a, window_size, noverlap=None):
    if not hasattr(window_size, '__iter__'):
        return rolling_window_lastaxis(a, window_size, noverlap)
    for i, win in enumerate(window_size):
        if win > 1:
            a = a.swapaxes(i, -1)
            a = rolling_window_lastaxis(a, win, noverlap)
            a = a.swapaxes(-2, i)
    return a

#a = np.array(range(100), dtype=np.int)
#print SlidingWindow(a, 10, 5)   # window_size=10, no overlap