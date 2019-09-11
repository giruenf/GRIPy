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
        if kwargs.get('_data') is None:    
            if args:
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
        """
        args: List of lists of DataIndex uids. 
              
        Examples:
            
            1-D data: [index.uid, owt_index.uid, twt_index.uid]
            
            5-D data: [i_line_index.uid],
                      [x_line_index.uid],
                      [offset_index.uid],
                      [freq_index.uid],
                      [time_index.uid, prof_index.uid]
        """
        max_dims = self._get_max_dimensions()
        if len(args) > max_dims:
            msg = 'Exceed number of dimensions [{}] - {}.'.format(max_dims, args)
            print('\n' + msg)
            raise Exception(msg)
        
        OM = ObjectManager()
        data = []

        for di_objs in args:
            if not isinstance(di_objs, list):
                # arg should be a object uid.
                di_objs = [di_objs]    
            for di_obj in di_objs:
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
            
      
        try:
            di_map = OM.new('data_index_map', data)       
        except Exception as e:  
            msg = 'ERROR DataObject._create_data_index_map: {} - data: {}'.format(e, data)
            print('\n' + msg)
            raise

        if not OM.add(di_map, self.uid):
            msg = 'Cannot add {} to {}.'.format(di_map, self.uid)
            print('\n' + msg)
            raise Exception(msg)
            
        msg = 'Criado {} com sucesso.'.format(di_map)
        #print('\n' + msg)


    def get_data_indexes(self, dimension=None):
        """
        """
        OM = ObjectManager()
        data_index_maps = OM.list('data_index_map', self.uid)
        if not data_index_maps:
            raise Exception('Object without DataIndexMap: {}'.format(self.uid))
        data_index_map = data_index_maps[0]    
        data_indexes = data_index_map._get_data_indexes()  
        if dimension is None:
            return data_indexes
        return data_indexes[dimension] 


