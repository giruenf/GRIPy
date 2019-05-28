
from collections import OrderedDict

from classes.om import ObjectManager
from classes.om import OMBaseObject



class CurveSet(OMBaseObject):
    tid = 'curve_set'
#    _FRIENDLY_NAME = 'Curve Set'    
    
    
    def __init__(self, **attributes):
        super().__init__(**attributes)    
        """
        self.attributes = {}
        OM = ObjectManager() 
        vinculated = attrbutes.get('vinculated')
        if vinculated:
            try:
                vinculated_index_set = OM.get(vinculated)
                if vinculated_index_set.tid != self.tid:
                    raise Exception('Wrong tid.')
                self.attributes['name'] = vinculated_index_set.name
                self.attributes['vinculated'] = vinculated
            except:
                raise
        else:        
            self.attributes['name'] = attrbutes.get('name')
            self.attributes['vinculated'] = None
#        OM.subscribe(self._on_OM_add, 'add')
        """    


    @classmethod
    def _is_tree_tid_node_needed(cls):
        __doc__ = OMBaseObject._is_tree_tid_node_needed.__doc__
        return False


                 
    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        OM = ObjectManager()        
        OM.unsubscribe(self._on_OM_add, 'add')
        
        parent_uid = OM._getparentuid(self.uid)
        for obj in OM.list(self.tid, parent_uid):
            if obj is not self and obj.name == self.name:
                raise Exception('Parent object has another son with same name.')

#    @property
#    def name(self):
#        return self.attributes['name']

    @property
    def vinculated(self):
        return self.attributes['vinculated']
  
    
    def get_data_indexes(self):
        OM = ObjectManager() 
        ret_dict = OrderedDict()
        if self.vinculated:
            vinculated_index_set = OM.get(self.vinculated)
            ret_dict = vinculated_index_set.get_data_indexes()
        data_indexes = OM.list('data_index', self.uid)
        if not data_indexes:
            return ret_dict
            
        for data_index in data_indexes:
            if data_index.dimension not in ret_dict.keys():
                ret_dict[data_index.dimension] = []    
            ret_dict.get(data_index.dimension).append(data_index)    
        return ret_dict     


    def get_z_axis_indexes_by_type(self, datatype):
        ok = False
        for z_axis_dt, z_axis_dt_desc in VALID_Z_AXIS_DATATYPES:
            if datatype == z_axis_dt:
                ok = True
                break
        if not ok:    
            raise Exception('Invalid datatype={}. Valid values are: {}'.format(datatype, VALID_Z_AXIS_DATATYPES))
        z_axis_indexes = self.get_data_indexes()[0]
        return [data_index for data_index in z_axis_indexes if data_index.datatype == datatype]


    def get_state(self):
        state = super().get_state()
        state.update(name=self.name)
        state.update(vinculated=self.vinculated)
        return state
     
        
    @classmethod
    def _loadstate(cls, **state):
        OM = ObjectManager()
        try:
            name = state.get('name')
            vinculated = state.get('vinculated')
            index_set = OM.new(cls.tid, name=name, vinculated=vinculated)
        except Exception as e:
            print ('\nERROR:', e, '\n', state)
        return index_set        
