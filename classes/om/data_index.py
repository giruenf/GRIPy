
from collections import OrderedDict

import numpy as np

from classes.om import OMBaseObject
from classes.om import DataObject
from classes.om import ObjectManager


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
    
    
    def __init__(self, *args, **attributes):   

        #print ('\n\nDataIndex:\n', attributes, '\n', args)        

        """
        index = OM.new('data_index', 0, names[i], 
                       sel_curvetypes[i].upper(), units[i].lower(), 
                       data=data[i]
        )
        """

        if not args:
            raise Exception('Args (DataIndex) not found!')

        dim_idx = attributes['dimension']
        
        if dim_idx is None or dim_idx < 0 or not isinstance(dim_idx, int):
            raise Exception('Wrong value for dimension_idx [{}]'.format(
                                                                dim_idx)
            )        

        data = None
        if args:
            data = args[0]
             
        start = attributes.pop('start', None) 
        end = attributes.pop('end', None) 
        step = attributes.pop('step', None)    
            
        if data is None or not isinstance(data, np.ndarray):
            try:
                if end is None:
                    samples = attributes.pop('samples')
                    end = start + step * samples
                data = np.arange(start, end, step)
            except:
                raise Exception('Data values were provided wrongly.')
      
        if start is None:        
            start = data[0]
        if end is None:
            end = data[-1]
        samples = len(data)

        super().__init__(data, start=start, end=end, step=step, 
                                 samples=samples, **attributes
        )
        

    @classmethod
    def _is_tree_tid_node_needed(cls):
        __doc__ = OMBaseObject._is_tree_tid_node_needed.__doc__
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
    








