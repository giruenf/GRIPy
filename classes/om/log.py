# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 14:11:52 2018

@author: Adriano
"""

from collections import OrderedDict

from classes.om import DataObject

from classes.om.welldata_1d import WellData1D


class Log(WellData1D):
                                  
    tid = "log"
    _FRIENDLY_NAME = 'Log'
    _SHOWN_ATTRIBUTES = [
                            ('datatype', 'Curve Type'),
                            ('unit', 'Units'),
                            ('min', 'Min Value'),
                            ('max', 'Max Value')
                            #('index_name', 'Index'),
                            #('start', 'Start'),
                            #('end', 'End'),
                            #('step', 'Step'),
    ] 
    
    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)

    @classmethod
    def is_tid_node_needed(cls):
        """For TreeController"""
        return False