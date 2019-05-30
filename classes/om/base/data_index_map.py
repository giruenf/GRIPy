
import copy

from classes.om import OMBaseObject


class DataIndexMap(OMBaseObject):
    tid = 'data_index_map'
#    _TID_FRIENDLY_NAME = 'Data Index Map'
    _READ_ONLY = ['_max_dimensions']
#    _SHOWN_ATTRIBUTES = [
#                            ('dimensions', 'Dimensions'),
#    ]     
    
    
    # TODO: Tornar esta classe _singleton_per_parent
    # pois somente deve ser possivel existir 1 DataIndexMap por DataObject.
    
    
    def __init__(self, max_dimensions, data_indexes_uids_map=[], **attributes):   
        """
        """
        super().__init__(**attributes)
        self._max_dimensions = max_dimensions
         
        # TODO: data_indexes como um array 
        self._data_indexes_uids_map = data_indexes_uids_map
        
        
    @property
    def max_dimensions(self):
        return self._max_dimensions   

    def _get_tree_object_node_properties(self):    
        return None
    
    def _get_data_indexes(self):
        return copy.deepcopy(self._data_indexes_uids_map)


        
        
#    @property
#    def dimensions(self):
#        return len(self._data_indexes_uids_map)      
    
#    @classmethod
#    def _is_tree_tid_node_needed(cls):
#        __doc__ = OMBaseObject._is_tree_tid_node_needed.__doc__
#        return False        

