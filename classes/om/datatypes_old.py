# -*- coding: utf-8 -*-
"""
DataTypes
=========

`DataTypes` are subtypes of those defined in `OM.Objects` (`GripyObject` and
`ParentObject`) that represent some kind of data in the program data model
(for example, wells, logs and partitions).

Notes
-----
The classes defined in this module are not intended to be directly used.
Instead, they should be registered within `OM.ObjectManager` and used through
its interface. The examples contained here might use the classes directly for
simplicity purposes.

In order to be properly managed by `OM.ObjectManager`, the classes must define
a `tid` of their own.

See Also
--------
OM.Objects : the base classes for the classes defined in this module.
"""



from collections import OrderedDict

import numpy as np
#import wx

from classes.om import DataObject
from classes.om import ObjectManager
#from classes.om import OMBaseObject

#from classes.base import GripyObject

#from app.app_utils import parse_string_to_uid

from basic.colors import COLOR_CYCLE_RGB


from classes.om.welldata_1d import WellData1D




VALID_Z_AXIS_DATATYPES = [('MD', 'Measured Depth'), 
                          ('TVD', 'True Vertical Depth'),
                          ('TVDSS', 'True Vertical Depth Subsea'), 
                          ('TIME', 'One-Way Time'),
                          ('TWT', 'Two-Way Time')
]




        
    
# TODO: verificar se isso abaixo permanecera    
    
class Property(DataObject):
    """
    A property that can be associated with geological layers.
    
    A `Property` can represent any numerical value that can be associated with
    a set of samples (i.e. a set of measurements in a well log) in a well. Its
    value is the same for every sample in each associated set. For example, the
    matrix density can be thought as a property in this context. The set of
    samples corresponding to sandstones might have the value 2.65 g/cm3, and
    the set of samples corresponding to limestones might have the value 2.71
    g/cm3. The set of samples in which a `Property` has the same value is
    represented by a `Part`.
    
    Attributes
    ----------
    data : dict
        A dictionary which keys are parts' unique identificators and values
        are the values of the property the respective layer.
    defaultdata : float or None
        If the data for a `Part` is not defined, this value will be returned
        instead.
    
    See also
    --------
    DataTypes.DataTypes.Part
    DataTypes.DataTypes.Partition
    DataTypes.DataTypes.Well
    
    Examples
    --------
    >>> x = Property(defaultdata = 42)
    >>> x.getdata(partuid)
    42
    >>> x.setdata(partuid, 23)
    >>> x.getdata(partuid)
    23
    """
    
    
    tid = "property"
    _DEFAULTDATA = None    
    
    
    def __init__(self, data=None, **attributes):
        super().__init__(data, **attributes)
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


###############################################################################
###############################################################################
                

class Density(DataObject):
    tid = 'density'

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)

    def get_data_indexes(self):
        OM = ObjectManager()            
        try:
            index_set = OM.list('index_set', self.uid)[0]
            return index_set.get_data_indexes()
        except Exception as e:
            print ('ERROR [Density.get_data_indexes]:', e, '\n')
            raise e


class Seismic(Density):
    tid = 'seismic'
    _FRIENDLY_NAME = 'Seismic'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id')  
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)
                

class WellGather(Density):
    tid = 'gather'
    _FRIENDLY_NAME = 'Gather'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id')  
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)
            

class Scalogram(Density):
    tid = 'scalogram'
    _FRIENDLY_NAME = 'Scalogram'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')                       
    ] 

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)



class GatherScalogram(Scalogram):
    tid = 'gather_scalogram'

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)



class Angle(Density):
    tid = 'angle'
    _FRIENDLY_NAME = 'Angle'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('type', 'Type'),                             
                            ('domain', 'Domain'),    
                            ('unit', 'Units'),
                            ('datum', 'Datum'),
                            ('sample_rate', 'Sample Rate'),
                            ('samples', 'Samples per scale'),
                            #('scales', 'Scales per trace'),
                            ('traces', 'Traces')
    ] 

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)



class Velocity(Density):
    tid = 'velocity'
    _FRIENDLY_NAME = 'Velocity'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('domain', 'Domain'),    
                            ('unit', 'Units'),
                            ('datum', 'Datum'),
                            ('sample_rate', 'Sample Rate'),
                            ('samples', 'Samples per trace'),
                            ('traces', 'Traces')
    ] 

  
    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)


class Spectogram(Density):
    tid = 'spectogram'
    _FRIENDLY_NAME = 'Spectogram'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')                       
    ] 

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)



class GatherSpectogram(Spectogram):
    tid = 'gather_spectogram'
    _FRIENDLY_NAME = 'Spectogram'
    
    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)
        
        
###############################################################################
###############################################################################


class Inversion(DataObject):
    tid = "inversion"
    _FRIENDLY_NAME = 'Inversion'
    
    def __init__(self, **attributes):
        super().__init__(**attributes)


    
class InversionParameter(DataObject):
                                 
    tid = "inversion_parameter"
    _FRIENDLY_NAME = 'Parameter'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Curve Type'),
                            ('unit', 'Units'),
                            ('min', 'Min Value'),
                            ('max', 'Max Value'),
                            ('start', 'Start'),
                            ('end', 'End'),
                            ('step', 'Step'),
    ] 
    
    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)



        



        


class Model1D(Density):
    tid = 'model1d'
    _FRIENDLY_NAME = 'Model'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]

    def __init__(self, data, **attributes):
        super().__init__(data, **attributes)

    def get_index(self):
        #print '\nModel1d.get_index'
        OM = ObjectManager()  
        parent_uid = OM._getparentuid(self.uid)
        parent = OM.get(parent_uid)
        indexes = parent.get_index()
        #
        dis = OM.list('data_index', self.uid)
        if dis:
            for di in dis:
                if di.dimension not in indexes.keys():
                    indexes[di.dimension] = []
                indexes.get(di.dimension).append(di)     
        return indexes     



class ZoneSet(DataObject):
    tid = 'zone_set'
    _FRIENDLY_NAME = 'Zone Sets'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]
    
    def __init__(self, **attributes):
        super().__init__(**attributes)


class Zone(DataObject):
    tid = 'zone'
    _FRIENDLY_NAME = 'Zones'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]
    
    def __init__(self, **attributes):
        if attributes.get('start') is None or attributes.get('end') is None:
            raise Exception('No start or no end.')
        super().__init__(**attributes)
        
    def get_index(self):
        raise Exception()
        
    @property
    def start(self):
        return self.attributes['start']

    @start.setter
    def start(self, value):
        self.attributes['start'] = value

    @start.deleter
    def start(self):
        raise Exception()
        
    @property
    def end(self):
        return self.attributes['end']
           
    @end.setter
    def end(self, value):
        self.attributes['end'] = value        
    
    @end.deleter
    def end(self):
        raise Exception()    
    
    