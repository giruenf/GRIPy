# -*- coding: utf-8 -*-

from app.gripy_function_manager import FunctionManager
from basic.temp.func import do_STFT, do_CWT

from classes.om import Log
from ui.mvc_classes.track_object import TrackObjectController

#from datatypes.DataTypes import Log


"""
#FunctionManager.register_function(ab, 'Soma Normal', A, B, a=A)
#@classmethod
#def register_function(cls, func, friendly_name=None,  *args, **kwargs):
"""


def register_app_functions():
    FunctionManager.register_function(do_STFT, 
                                      "Fourier Transform", 
                                      Log, 
                                      toc=TrackObjectController
    )
    FunctionManager.register_function(do_CWT, 
                                      "Wavelet Transform", 
                                      Log, 
                                      toc=TrackObjectController
    )

