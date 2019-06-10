# -*- coding: utf-8 -*-
"""
DataObject is an "ObjectManager object" [sic] with a Numpy array.
"""

from collections import OrderedDict

import numpy as np
import wx

from classes.om import OMBaseObject
from classes.om import ObjectManager


VALID_INDEXES = {
    'I_LINE': {
            'units': [None],
            'name': 'Iline',
            'desc': ''
    },        
    'X_LINE': {
            'units': [None],
            'name': 'Xline',
            'desc': ''
    },        
    'FREQUENCY': {
            'units': ['Hz'],
            'name': 'Frequency',
            'desc': ''
    },        
    'SCALE': {
            'units': [None],
            'name': 'Scale',
            'desc': ''
    },    
    'OFFSET': {
            'units': ['m', 'ft'],
            'name': 'Offset',
            'desc': ''
    },     
    'MD': {
            'units': ['m', 'ft'],
            'name': 'MD',
            'desc': 'Measured depth'
    },        
    'TVD': {
            'units': ['m', 'ft'],
            'name': 'TVD',
            'desc': 'True vertical depth'
    },        
    'TVDSS': {
            'units': ['m', 'ft'],
            'name': 'TVDSS',
            'desc': 'True vertical depth sub sea'
    },  
    'TWT': {
            'units': ['ms', 's'],
            'name': 'TWT', 
            'desc': 'Two-way time'
    },        
    'TIME': {
            'units': ['ms', 's'],
            'name': 'Time', 
            'desc': 'One-way time'
    },
    'ANGLE': {
            'units': ['deg', 'rad'],
            'name': 'Angle', 
            'desc': 'Angle'            
    },
    'P': {
            'units': ['s/m', 's/km'],
            'name': 'Ray Parameter', 
            'desc': 'P Ray Parameter'            
    }             
}    


def check_data_index(index_type, axis_unit):  
    index_props = VALID_INDEXES.get(index_type)    
    if not index_props:
        raise Exception('Invalid index code. [index_type={}]'.format(index_type))
    if axis_unit not in index_props.get('units'):
        raise Exception('Invalid index unit.')



class DataObject(OMBaseObject):
    tid = None

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['_data'] = {
        'default_value': None,
        'type': np.ndarray      
    }    
    _ATTRIBUTES['unit'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }
    _ATTRIBUTES['datatype'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }           

    def __init__(self, *args, **kwargs):
          
        # TODO: 29/8/2018
        # CHECAR FLAG HIDDEN PARA ATRIBUTO NAO EXIBIDO NO TREE
        # POR EXEMPLO DATA.

        if '_data' not in kwargs:
            if args[0]:
                kwargs['_data'] = args[0]
        super().__init__(**kwargs)      
#        if isinstance(self._data, np.ndarray):
#            self._data.flags.writeable = False




    @property
    def min(self):
        if self._data is None:
            return None
        return np.nanmin(self._data)
        
    
    @property
    def max(self):
        if self._data is None:
            return None
        return np.nanmax(self._data)
    

    @property
    def data(self):
        return self._data


    def _get_max_dimensions(self):
        raise NotImplementedError('Must be implemented by a subclass.')


    def _create_data_index_map(self, *args):
        max_dims = self._get_max_dimensions()
        if len(args) > max_dims:
            msg = 'Exceed number of dimensions [{}] - {}.'.format(max_dims, args)
            raise Exception(msg)
        
#        print('\n\n\n_create_data_index_map')
#        print('args:', args)     
#        print('list(args):', list(args))
#        print('type(args):', type(args))
#        print()
        
        OM = ObjectManager()
        data = []
                
#        i = 0
        
        for di_objs in args:
            
#            i += 1
            
#            print(str(i), di_objs)
            
            if not isinstance(di_objs, list):
                # arg should be a object uid.
                di_objs = [di_objs]
                
            for di_obj in di_objs:
                #print('    Testing: ' + str(di_obj))
                try:
                    # Then, test if object exist this is a valid object uid.
                    obj = OM.get(di_obj)
                    if not obj.tid == 'data_index':
                        raise Exception()
                except:    
                    print('\n\nDEU RUIM:', di_obj)
                    msg = 'Error in objects informed as ' + \
                                            'Data Indexes: {}.'.format(args)
                    raise Exception(msg)
            
            data.append(di_objs)
#            print('data array is Ready!')
       
        
#        print('\nCreating data_index_map:', data)
        di_map = OM.new('data_index_map', max_dims, data)
#        print('Creating data_index_map - OK!!!')
        
        
#        print('\nOM add:', di_map, self.uid)
        try:
            OM.add(di_map, self.uid)
#            print('OM add - OK!!!')
        except Exception as e:    
            print('\nERROR:', e, '\n')
            raise
        



    def get_data_indexes(self, dimension=None):
        """
        """
        OM = ObjectManager()
        data_index_map = OM.list('data_index_map', self.uid)[0]
        data_indexes = data_index_map._get_data_indexes()  
        if dimension is None:
            return data_indexes
        return data_indexes[dimension] 


      

    """


    
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

    def get_state(self):
        state = super(DataTypeObject, self).get_state()
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