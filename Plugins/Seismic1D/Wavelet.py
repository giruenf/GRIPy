# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager
from DT.DataTypes import GenericDataType
import numpy as np

class Wavelet(GenericDataType):
    tid = 'wlet'

    def __init__(self, data, **attributes):
        super(Wavelet, self).__init__(data, **attributes)
        self._data.flags.writeable = False

    @property
    def ns(self):
        return len(self._data)

ObjectManager.registertype(Wavelet)
