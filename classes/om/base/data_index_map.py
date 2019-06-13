
import copy
from collections import OrderedDict

from classes.om import OMBaseObject


class DataIndexMap(OMBaseObject):
    tid = 'data_index_map'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['_data'] = {
        'default_value': None,
        'type': list      
    }    
 
    # TODO: Tornar esta classe _singleton_per_parent
    # pois somente deve ser possivel existir 1 DataIndexMap por DataObject.
    
    # TODO: Is this a kind of dummy class?
    def __init__(self, *args, **kwargs):   
        """
        """
        if kwargs.get('_data') is None:    
            if args:
                kwargs['_data'] = args[0]        
        super().__init__(**kwargs)

    def _get_tree_object_node_properties(self):    
        return None
    
    def _get_data_indexes(self):
        return copy.deepcopy(self._data)

   