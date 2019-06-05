
from collections import OrderedDict

from classes.om import OMBaseObject
from classes.om import DataObject
from classes.om import ObjectManager


class Density(DataObject):
    tid = 'density'

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)


class Seismic(Density):
    tid = 'seismic'
    _TID_FRIENDLY_NAME = 'Seismic'
    
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id')  
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)
        
    def _get_max_dimensions(self):
        return 5
    
        