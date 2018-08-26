# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 13:44:59 2018

@author: Adriano
"""

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
 
    
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        
        
#    """
    def get_z_axis_datatypes(self):
        OM = ObjectManager()
        data_indexes = OM.list('data_index', self.uid)
        zaxis = OrderedDict()
        for z_axis_dt, z_axis_dt_desc in VALID_Z_AXIS_DATATYPES:
            for data_index in data_indexes:
                if data_index.datatype == z_axis_dt and z_axis_dt not in zaxis.values():
                    zaxis[z_axis_dt_desc] = z_axis_dt
#        print ('\n\nget_z_axis_datatypes:', zaxis)            
        return zaxis
#    """
