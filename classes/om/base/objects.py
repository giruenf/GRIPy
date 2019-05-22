
from collections import OrderedDict

from classes.base import GripyObject


class OMBaseObject(GripyObject):
    """
    OMBaseObject is the base class for all objects dealt by ObjectManager.
    """
    tid = None
    _TID_FRIENDLY_NAME = None
    
    def _get_object_node_properties(self):
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
        
    def _is_tid_node_needed(self):
        """Used by TreeController to create or not a tid node as a objects
        from a given class grouper. If tid node is created, the method 
        get_tid_friendly_name will provide it's node label.
        
        """
        return True

    @classmethod
    def _get_tid_friendly_name(self):
        """In general, classes tids are not adequated to be shown as a
        tid node label. If class _TID_FRIENDLY_NAME is provided, it will be
        used by TreeController as tid node label.
        
        """
        try:
            return self._TID_FRIENDLY_NAME
        except:
            return self.tid

    def _get_object_friendly_name(self):
        """Returns a name to be used by TreeController as object node label."""
        return self.name
    
