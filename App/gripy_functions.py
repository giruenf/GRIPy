# -*- coding: utf-8 -*-

from gripy_function_manager import FunctionManager
from Temp.func import do_STFT, do_CWT
from DT.DataTypes import Log


"""
#FunctionManager.register_function(ab, 'Soma Normal', A, B, a=A)
#@classmethod
#def register_function(cls, func, friendly_name=None,  *args, **kwargs):
"""


def register_app_functions():
    FunctionManager.register_function(do_STFT, "Fourier Transform", Log)
    FunctionManager.register_function(do_CWT, "Wavelet Transform", Log)
