# -*- coding: utf-8 -*-

import numpy as np
import scipy
from SlidingWindow import SlidingWindow
#from scipy.signal import minimum_phase
from scipy import signal# import stft


def get_complex_polar_coords(number, deg=False):
    return np.absolute(number), np.angle(number, deg)


def get_complex_from_polar_coords(mod, angle, deg=False):
    if deg:
        angle = np.radians(angle)
    try:
        ret = [mod[idx] * np.complex(np.cos(ang), np.sin(ang)) for idx, ang in enumerate(angle)]   
    except TypeError:
        ret = mod * np.complex(np.cos(angle), np.sin(angle))
    return ret


def phase_rotation(value, angle_inc, deg=True):
    mod , angle = get_complex_polar_coords(value, deg)
    angle += angle_inc
    return get_complex_from_polar_coords(mod, angle, deg)


def frequency_phase_rotation(values, angle, deg=False):
    window_size = 64
    noverlap = 32
    window = signal.hann(window_size, sym=False)
    if not signal.check_COLA(window, len(window), noverlap):
        raise Exception('check_COLA failed.')
    f, t, Zxx = signal.stft(values, window=window, nperseg=window_size, 
                       noverlap=noverlap
    )
    Zxx_rotated = np.zeros(Zxx.shape, dtype=np.complex)
    for freq_idx in range(Zxx.shape[0]): # Loop over all frequencies
        Zxx_rotated[freq_idx] = phase_rotation(Zxx[freq_idx], angle, deg)
    t, x = signal.istft(Zxx_rotated, window=window, nperseg=window_size, 
                        noverlap=noverlap
    )
    return t, x
    

def _in1d_with_tolerance(A, B, tol=1e-05):
    return (np.abs(A[:,None] - B) < tol).any(1)


# Time in milliseconds
def get_synthetic_ricker(fp, time_peak=0.0, time=None):
    start = -10.0
    step = 0.001
    end = start * (-1.0)
    t = np.arange(start, end+step, step)        
    factor = (np.pi * fp * t) ** 2
    y = np.array((1 - 2. * factor) * np.exp(-factor))
    t = t + time_peak
    if time is None:        
        return t, y
    else:
        vec = _in1d_with_tolerance(t, time)
        return time, y[vec]
   
    
"""    
def get_synthetic_ricker(fp, time_peak=0.0, time=None, min_phase=True):    
    data = _get_synthetic_ricker(fp, time_peak, time)[1]
    if not min_phase:
        return data
    data = minimum_phase(data, method='homomorphic')
    step = time[1]-time[0]
    min_phase_time = np.arange(time[0], time[0] + step*2*len(data), step*2)
    data = np.interp(time, min_phase_time+time_peak, data)
    return data
"""                
                
                