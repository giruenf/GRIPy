# -*- coding: utf-8 -*-

from classes.om import OMBaseObject
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
    
    #def __init__(self, data, **attributes):
    def __init__(self, *args, **kwargs):   
        try:
            super().__init__(*args, **kwargs)   
        except Exception as e:
            print ('\n\n\nERRORRRR')
            print (e)
            raise
            
    @classmethod
    def _is_tid_node_needed(cls):
        __doc__ = OMBaseObject._is_tid_node_needed.__doc__
        return False