# -*- coding: utf-8 -*-

from collections import OrderedDict
import numpy as np
import copy

from basic.parms import ParametersManager


class Base(object):
    
    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def _test_inner_instance(self, obj):
        raise NotImplementedError('Must be implemented by subclass.')
        
    @property    
    def data(self):
        return self._data
    
    def append(self, obj):
        self._test_inner_instance(obj)
        self._data.append(obj)
               
    def add(self, index, obj):
        self._test_inner_instance(obj)
        self._data.insert(index, obj)
            
    def get(self, pos):  
        return self._data[pos]
    
    
class IOWells(Base):
    
    def __init__(self):
        super().__init__()

    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWell):
            raise Exception('Object [{}] is not instance of IOWell.'.format(type(obj)))
      

class IOWell(Base):
    
    def __init__(self):
        super().__init__()
        self.infos = None
        
    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWellRun):
            raise Exception('Object [{}] is not instance of IOWellRun.'.format(type(obj)))
      

class IOWellRun(Base):
    
    def __init__(self, name):
        super().__init__()
        self.name =  name
        #self.logs = None

    def _test_inner_instance(self, obj):
        if not isinstance(obj, IOWell):
            msg = 'Object [{}] is not instance of IOWellLog.'.format(type(obj))
            raise Exception(msg)

    def get_depth(self):
        raise NotImplementedError('Must be implemented by subclass.')

    def get_depth_unit(self):
        raise NotImplementedError('Must be implemented by subclass.')
                         
    def get_depth_start(self):
        raise NotImplementedError('Must be implemented by subclass.') 

    def get_depth_end(self):
        raise NotImplementedError('Must be implemented by subclass.')
                     
    def get_logs(self):
        raise NotImplementedError('Must be implemented by subclass.')

                    
            
class IOWellLog(object):
    
    def __init__(self, mnem, unit, data):
        self.mnem = mnem
        self.unit = unit
        self.data = data
        PM = ParametersManager.get()
        try:
            self.datatype = PM.get_datatype_from_mnemonic(self.mnem)
        except:
            self.datatype = None
        try:    
            self.curvetype = PM.get_curvetype_from_mnemonic(self.mnem)
        except:
            self.curvetype = None       
        
    def get_first_occurence_pos(self):
        for idx, boolean in enumerate(np.isnan(self.data)):
            if not boolean:
                return idx
                
    def get_last_occurence_pos(self):
        y = np.isnan(self.data)
        for idx in range(len(y)-1, -1, -1):
            if not y[idx]:
                return idx                



