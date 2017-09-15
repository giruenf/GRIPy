# -*- coding: utf-8 -*-
'''
import App
import os 
import json
from collections import OrderedDict
from App.gripy_manager import Manager


class PropertySet(object):
        
  
    
    
class Property(object):
    
    tid = "property"
    _DEFAULTDATA = None    
    
    def __init__(self, data=None, **attributes):
        super(Property, self).__init__(data, **attributes)
        if data is None:
            self._data = {}
            
    @property
    def defaultdata(self):
        if 'defaultdata' not in self.attributes:
            self.attributes['defaultdata'] = self._DEFAULTDATA
        return self.attributes['defaultdata']
    
    @defaultdata.setter
    def defaultdata(self, value):
        self.attributes['defaultdata'] = value
    
    @defaultdata.deleter
    def defaultdata(self, value):
        del self.attributes['defaultdata']
    
        property()
    
    
    
    Property:
        key
        value
        defaultdata
        datatype
        unit
    
    Property:
        key = 'vp'
        value = 4000.0
        _defaultdata = None
        datatype = 
        desc = None
        unit = 'm/s'
        _defaultunit = 'm/s'
    
    
    self._data[uid] = value

    "Density": {
        "RightScale": 2.95, 
        "HistogramLeft": 2.0, 
        "Color": "Red", 
        "LineStyle": "Solid", 
        "Backup": "None", 
        "XplotLogLin": "Lin", 
        "HistogramRight": 3.0, 
        "LogLin": "Lin", 
        "XplotMin": 3.0, 
        "HistogramLogLin": "Lin", 
        "Units": "gm/cc", 
        "LineWidth": 1, 
        "XplotMax": 2.0, 
        "LeftScale": 1.95, 
        "CurveDescription": "BHI LWD Bulk Density (Real Time)"
    }, 

class PropertiesManager(Manager):
    _data = OrderedDict()

    def __init__(self):   
        super(PropertiesManager, self).__init__()

    def getdata(self, uid):
        """
        Return the value of the property associated with the `uid`.
        
        Parameters
        ----------
        uid : uid
            The `Part` unique identificator for which the property value is
            needed.
        
        Returns
        -------
        float or None
            Returns the value assigned to the given `uid`. If no value was
            assigned to it, `defaultdata` is returned instead.
        """
        return self._data.get(uid, self.defaultdata)
    
    def setdata(self, uid, value):
        """
        Assign a property value to a part unique identificator.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the `Part` that will have the `value`
            assigned to.
        value : float
            The value that will be associated with the given `Part`.
        """
        self._data[uid] = value
    
    def deletedata(self, uid):
        """
        Remove the association of a `Part` to a property value.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the `Part` that will have the
            associated property value removed.
        """
        del self._data[uid]




'''


