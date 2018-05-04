# -*- coding: utf-8 -*-
#
# Class for deal with Analytic Signal
# Universidade Estadual do Norte Fluminense - UENF
# Laboratório de Engenharia de Petróleo - LENEP
# Grupo de Inferência em Reservatório - GIR
# Adriano Paulo Laes de Santana
# September 12th, 2017
#
# The following code is based on 
# http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.hilbert.html

import numpy as np
from scipy.signal import hilbert 


class HilbertTransform(object):
    
    def __init__(self, real_signal, sampling):
        self._fs = 1/sampling
        self._analytic_signal =  hilbert(real_signal)           
        self._amplitude_envelope = np.abs(self._analytic_signal)
        self._instantaneous_phase = np.unwrap(np.angle(self._analytic_signal))
        self._instantaneous_frequency = (np.diff(self._instantaneous_phase) / 
                                        (2.0*np.pi) * self._fs)
        self._instantaneous_frequency = np.insert(self._instantaneous_frequency, 0, np.nan)

    @property
    def analytic_signal(self):
        return self._analytic_signal
    
    @analytic_signal.setter
    def analytic_signal(self, value):
        raise Exception('')
    
    @analytic_signal.deleter
    def analytic_signal(self):
        raise Exception('')
        
    @property
    def amplitude_envelope(self):
        return self._amplitude_envelope
    
    @amplitude_envelope.setter
    def amplitude_envelope(self, value):
        raise Exception('')
    
    @amplitude_envelope.deleter
    def amplitude_envelope(self):
        raise Exception('')
        
    @property
    def instantaneous_phase(self):
        return self._instantaneous_phase
    
    @instantaneous_phase.setter
    def instantaneous_phase(self, value):
        raise Exception('')
    
    @instantaneous_phase.deleter
    def instantaneous_phase(self):
        raise Exception('')        
        
    @property
    def instantaneous_frequency(self):
        return self._instantaneous_frequency
    
    @instantaneous_frequency.setter
    def instantaneous_frequency(self, value):
        raise Exception('')
    
    @instantaneous_frequency.deleter
    def instantaneous_frequency(self):
        raise Exception('')            
        
    