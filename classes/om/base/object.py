
from collections import OrderedDict

from classes.base import GripyObject


class OMBaseObject(GripyObject):
    """
    OMBaseObject is the base class for all objects dealt by ObjectManager.
    """
    tid = None
    _TID_FRIENDLY_NAME = None
    
    def _get_tree_object_node_properties(self):
        """Used by TreeController to get the way a object is represented in the
        Tree. General usage is return a dict with object name as main key and
        the object properties are represented as an OrderedDict. Returning None
        will make object invisible in Tree. 
        """
        ret_od = OrderedDict()
        ret_od['name'] = self.name
        
        try:
            for attr, attr_label in self._SHOWN_ATTRIBUTES:
                try:
                    value = self[attr]
                except Exception as e:
                    continue
                if isinstance(value, float):
                    value = "{0:.2f}".format(value)
                elif value is None:
                    value = 'None'               
                ret_od[attr]  = attr_label + ': ' + str(value)  
            
        except AttributeError:
            pass
        return ret_od  
        
    def _is_tree_tid_node_needed(self):
        """Used by TreeController to create or not a tid node as a objects
        from a given class grouper. If tid node is created, the method 
        get_tid_friendly_name will provide it's node label.
        
        """
        return True
    
    def _get_tree_object_friendly_name(self):
        """Returns a name to be used by TreeController as object node label."""
        return self.name
    