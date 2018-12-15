
from collections import OrderedDict

from classes.om import ObjectManager
from classes.om import OMBaseObject

VALID_Z_AXIS_DATATYPES = [('MD', 'Measured Depth'), 
                          ('TVD', 'True Vertical Depth'),
                          ('TVDSS', 'True Vertical Depth Subsea'), 
                          ('TIME', 'One-Way Time'),
                          ('TWT', 'Two-Way Time')
]

class Well(OMBaseObject):
    tid = "well"
    _FRIENDLY_NAME = 'Well'
 
    def __init__(self, **attributes):
        super().__init__(**attributes)

    def get_z_axis_datatypes(self, inverted=False):
        """Returns a dict with valid Z axis data types for this Well. Dict key
        will be a long description for the data type (e.g. 'Measured Depth') 
        and value will be a short identification (e.g. 'MD'). Returned dict 
        will contain information from all DataIndex objects that are children 
        of this Well.
        """
        OM = ObjectManager()
        z_axis = OrderedDict()    
        data_indexes = OM.list('data_index', self.uid, True)
        
        for z_axis_dt, z_axis_dt_desc in VALID_Z_AXIS_DATATYPES:
            for data_index in data_indexes:
                if (data_index.datatype == z_axis_dt) and \
                                            z_axis_dt not in z_axis.values():
                    z_axis[z_axis_dt] = z_axis_dt_desc      
        if not inverted:            
            return z_axis
        return OrderedDict(zip(z_axis.values(), z_axis.keys()))

    def get_z_axis_datatype_range(self, datatype):
        """Given a Well index datatype (e.g. `MD`), returns a tuple with its 
        minimal and maximum values, considering all occurences.
        """
        min_ = 100000
        max_ = -1
        OM = ObjectManager()
        data_indexes = OM.list('data_index', self.uid, True)
        for data_index in data_indexes:
            if data_index.datatype == datatype:
                if data_index.start < min_:
                    min_ = data_index.start
                if data_index.end > max_:
                    max_ = data_index.end   
        return (min_, max_)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        