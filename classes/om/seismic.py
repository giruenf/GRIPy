
from collections import OrderedDict

from classes.om import OMBaseObject
from classes.om import DataObject
from classes.om import ObjectManager


class Density(DataObject):
    tid = 'density'

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)

    def get_data_indexes(self):
        OM = ObjectManager()            
        try:
            index_set = OM.list('index_set', self.uid)[0]
            return index_set.get_data_indexes()
        except Exception as e:
            print ('ERROR [Density.get_data_indexes]:', e, '\n')
            raise e



class Seismic(Density):
    tid = 'seismic'
    _TID_FRIENDLY_NAME = 'Seismic'
    
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id')  
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)
        
        
    @classmethod
    def _is_tree_tid_node_needed(cls):
        __doc__ = OMBaseObject._is_tree_tid_node_needed.__doc__
        return False

    def _get_max_dimensions(self):
        return 4
    
        