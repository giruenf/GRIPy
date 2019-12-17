# -*- coding: utf-8 -*-

from app.gripy_function_manager import FunctionManager
from basic.temp.func import do_STFT, do_CWT

from classes.om import Log
from classes.ui import TrackObjectController


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
