# -*- coding: utf-8 -*-
"""
DataObject is an "ObjectManager object" [sic] with a Numpy array.
"""

from collections import OrderedDict

import numpy as np
import wx

from classes.om import OMBaseObject



class DataObject(OMBaseObject):
    tid = None

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['unit'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }   
    _ATTRIBUTES['datatype'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }       
    

    def __init__(self, *args, **attributes):
        
        # TODO: 29/8/2018
        # CHECAR FLAG HIDDEN PARA ATRIBUTO NAO EXIBIDO NO TREE
        # POR EXEMPLO DATA.
        
#        print ('\nDataObject.__init__')
#        print (args, attributes)
#        print (self._ATTRIBUTES)
        
        super().__init__(**attributes)
        
        if not args:
            self._data = None
            return
        self._data = args[0]
        
        if isinstance(self._data, np.ndarray):
            self._data.flags.writeable = False


    @property
    def min(self):
#        print ('ENTROU MIN')
        if self._data is None:
#            print ('MIN IS NONE')
            return None
#        print (np.nanmin(self._data))
        return np.nanmin(self._data)
        
    @property
    def max(self):
#        print ('ENTROU MAX')
        if self._data is None:
#            print ('MAX IS NONE')
            return None
#        try:
#            print (np.nanmax(self._data))
#        except Exception as e:
#            print ('ERRAO:', e)
        return np.nanmax(self._data)
    

    @property
    def data(self):
        return self._data

    """

    def get_indexes_set(self):
        OM = ObjectManager()
        indexes_set = OM.list('index_set', self.uid)
        ret = OrderedDict()
        for index_set in indexes_set:
            dis = OM.list('data_index', index_set.uid)
            if not dis:
                ret[index_set.uid] = None
            else:
                ret[index_set.uid] = index_set.get_data_indexes()
        return ret
    
    def get_data_indexes(self, set_name):
        OM = ObjectManager()
        for index_set_uid, inner_ord_dict in self.get_indexes_set().items():
            index_set = OM.get(index_set_uid) 
            if set_name == index_set.name:
                return inner_ord_dict
        return None

    def get_z_axis_indexes_by_type(self, datatype):
        ok = False
        for z_axis_dt, z_axis_dt_desc in VALID_Z_AXIS_DATATYPES:
            if datatype == z_axis_dt:
                ok = True
                break
        if not ok:    
            raise Exception('Invalid datatype={}. Valid values are: {}'.format(datatype, VALID_Z_AXIS_DATATYPES))
        ret_vals = []
        all_data_indexes = self.get_indexes_set().values()   
        for data_indexes in all_data_indexes:
            z_axis_indexes = data_indexes[0]
            for data_index in z_axis_indexes:
                if data_index.datatype == datatype:
                    ret_vals.append(data_index)
        return ret_vals
   
    def get_friendly_indexes_dict(self):
        OM = ObjectManager()
        ret_od = OrderedDict()
        indexes_set = self.get_indexes_set()
        for index_set_uid, indexes_ord_dict in indexes_set.items():
            index_set = OM.get(index_set_uid)
            for dim_idx, data_indexes in indexes_ord_dict.items():
                for data_index in data_indexes:
                    di_friendly_name = data_index.name + '@' + index_set.name
                    ret_od[di_friendly_name] = data_index.uid       
        return ret_od
    
    def get_z_axis_datatypes(self):
        OM = ObjectManager()
        data_indexes_uid = self.get_friendly_indexes_dict().values()
        zaxis = OrderedDict()
        for z_axis_dt, z_axis_dt_desc in VALID_Z_AXIS_DATATYPES:
            for data_index_uid in data_indexes_uid:
                data_index = OM.get(data_index_uid)
                if data_index.datatype == z_axis_dt and z_axis_dt not in zaxis.values():
                    zaxis[z_axis_dt_desc] = z_axis_dt
        return zaxis

    def _getstate(self):
        state = super(DataTypeObject, self)._getstate()
        state.update(data=self._data)
        state.update(self.attributes)
        return state

    def _getparent(self):
        OM = ObjectManager()
        parent_uid = OM._getparentuid(self.uid)
        if not parent_uid:
            return None
        return OM.get(parent_uid)     

    """