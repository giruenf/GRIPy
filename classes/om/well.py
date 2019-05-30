
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
    _TID_FRIENDLY_NAME = 'Well'
 
    def __init__(self, **attributes):
        super().__init__(**attributes)

    def create_new_curve_set(self, curve_set_name=None):
        OM = ObjectManager()
        existing_csets = OM.list('curve_set', self.uid)
        #
        if curve_set_name:
            for cset in existing_csets: 
                if cset.name == curve_set_name:
                    curve_set_name = None
                    break
        #
        if not curve_set_name:
            curve_set_idx = len(existing_csets) + 1
            curve_set_name = 'Run ' + str(curve_set_idx)
        #    
        curve_set = OM.new('curve_set', name=curve_set_name)
        OM.add(curve_set, self.uid)
        return curve_set

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
        
        
        
        
        
        
        
    def get_curve_sets(self):
        OM = ObjectManager()
        curve_sets = OM.list('curve_set', self.uid)
        return curve_sets

    
    def get_data_indexes(self):
        OM = ObjectManager()
        curve_sets = OM.list('curve_set', self.uid)
        ret = OrderedDict()
        for curve_set in curve_sets:
            dis = OM.list('data_index', curve_set.uid)                 
            ret[curve_set.uid] = dis     
        return ret  

        
    def get_friendly_indexes_dict(self):
        """Used by menu_functions
        """
        OM = ObjectManager()
        ret_od = OrderedDict()
        indexes_set = self.get_data_indexes()  
        for curve_set_uid, data_indexes in indexes_set.items():
            curve_set = OM.get(curve_set_uid)
            for data_index in data_indexes:
                di_friendly_name = data_index.name + '@' + curve_set.name
                ret_od[di_friendly_name] = data_index.uid 
        return ret_od        
                
 
        
        
        
        
        
        
        
        
        
        