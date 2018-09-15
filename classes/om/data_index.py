# -*- coding: utf-8 -*-

from collections import OrderedDict

import numpy as np

from classes.om import OMBaseObject
from classes.om import DataObject
from classes.om import ObjectManager

from classes.om.datatypes_old import check_data_index



# Class for discrete dimensions of Data Objects
class DataIndex(DataObject):
    tid = 'data_index'
    _FRIENDLY_NAME = 'Index'
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['dimension'] = {
        'default_value': -1,
        'type': int       
    }       
    """
    _ATTRIBUTES['start'] = {
        'default_value': -1,
        'type': int       
    }  
    _ATTRIBUTES['end'] = {
        'default_value': -1,
        'type': int       
    }        
    _ATTRIBUTES['step'] = {
        'default_value': None,
        'type': int       
    }  
    _ATTRIBUTES['samples'] = {
        'default_value': None,
        'type': int       
    }   
    """
    
    _SHOWN_ATTRIBUTES = [
                            #('_oid', 'Object Id'),
                            ('dimension', 'Dimension'),
                            ('datatype', 'Type'),
                            ('unit', 'Unit'),
                            ('start', 'Start'),
                            ('end', 'End'),
                            ('step', 'Step'),
                            ('samples', 'Samples')
    ]   
    
    
    def __init__(self, dimension_idx, name, datatype=None, unit=None, **kwargs):   
#    def __init__(self, *args, **kwargs):  

#        print ('\nDataIndex:', dimension_idx, name, datatype, unit, kwargs)        
        #super().__init__(**kwargs)

        if dimension_idx is None or dimension_idx < 0 or not isinstance(dimension_idx, int):
            raise Exception('Wrong value for dimension_idx [{}]'.format(dimension_idx))
        try:    
            check_data_index(datatype, unit)
        except:
            raise        
        data = kwargs.get('data') 
        start = kwargs.get('start') 
        end = kwargs.get('end') 
        step = kwargs.get('step')
        samples = kwargs.get('samples')
        if data is None or not isinstance(data, np.ndarray):
            try:
                end = start + step * samples
                data = np.arange(start, end, step)
            except:
                raise Exception('Data values were provided wrongly.')
      
        if start is None:        
            start = data[0]
        if end is None:
            end = data[-1]
        samples = len(data)

        super().__init__(data, name=name, 
                         datatype=datatype, unit=unit,
                         start=start, end=end, step=step, samples=samples
        )
        self['dimension'] = dimension_idx   
        #"""


    @classmethod
    def _is_tid_node_needed(cls):
        __doc__ = OMBaseObject._is_tid_node_needed.__doc__
        return False

    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        OM = ObjectManager()        
        OM.unsubscribe(self._on_OM_add, 'add')
    
    def get_data_indexes(self):
        ret_dict = OrderedDict()
        ret_dict[0] = [self]
        return ret_dict        


    
    @property
    def start(self):
        try:
#            print ('\nproperty start:', self.data[0])
            return self._data[0]
        except Exception as e:
            print (e)
            raise
#            return None
    
    @property
    def end(self):
        try:
            return self._data[-1]
        except:
            return None

    @property
    def step(self):           
        try:
            return self._data[1] - self._data[0]
        except:
            return None     

    @property
    def samples(self):
        try:
            return len(self._data)
        except:
            return 0  
    
    """
    @classmethod
    def _loadstate(cls, **state):
        OM = ObjectManager()
        try:
            dimension = state.pop('dimension')
            name = state.pop('name')
            datatype = state.pop('datatype')
            unit = state.pop('unit')
            index = OM.new(cls.tid, dimension, name, datatype, unit, **state)
        except Exception as e:
            print ('\nERROR:', e, '\n', state)
        return index
    """







