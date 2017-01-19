# -*- coding: utf-8 -*-
"""
DataTypes
=========

`DataTypes` are subtypes of those defined in `OM.Objects` (`GenericObject` and
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


from OM.Objects import GenericObject, ParentObject
#from OM.Manager import ObjectManager

from Basic.Colors import COLOR_CYCLE_RGB

import numpy as np




class GenericDataType(GenericObject):
    """
    The most basic data type, only has name and data.
    
    The first argument of the constructor is the data the object is
    representing. All other arguments must be passed as keyword arguments and
    will be stored in the `attributes` attribute.
    
    Parameters
    ----------
    data : any appropriate type
        The data itself that the object represents.
        
    Attributes
    ----------
    data : any appropriate type
        The data itself that the object represents.
    name : str
        The name of the object. Obtained from `attributes`. If `attributes`
        doesn't have a key ``'name'``, a string representation of the object's
        `uid` will be assigned to it.
    attributes : dict
        A dictionary containing all of a `GenericDataType` attributes other
        than `data`. The keys are the attributes names and the values are the
        attributes themselves. Some special attributes may have a `property`
        related to it, e.g. `name`.
    
    Examples
    --------
    >>> class NamedDataType(GenericObject):
    >>>     pass
    >>> x = NamedDataType([23, 42], foo='bar', name='ObjName')
    >>> x.data
    [23, 42]
    >>> x.name
    'ObjName'
    >>> x.foo
    AttributeError: 'NamedDataType' object has no attribute 'foo'
    >>> x.attributes
    {'foo': 'bar', 'name': 'ObjName'}
    >>> x.attributes['foo']
    'bar'
    """
    
    def __init__(self, data, **attributes):
        super(GenericDataType, self).__init__()
        self._data = data
        self.attributes = attributes

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        msg = "Cannot set object data."
        raise TypeError(msg)

    @data.deleter
    def data(self):
        msg = "Cannot delete object data."
        raise TypeError(msg)
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
    
    def _getstate(self):
        state = super(GenericDataType, self)._getstate()
        state.update(self.attributes, data=self._data)
        return state


        
        
class DataTypeUnitMixin(object):
    """
    A "mix-in" for data types that need an exposed unit attribute.
    
    Attributes
    ----------
    unit : str
        The unit of the object. Obtained from `attributes`. If `attributes`
        doesn't have a key ``'unit'``, an empty string will be assigned to it.
    
    Examples
    --------
    >>> class NameUnitDataType(GenericDataType, DataTypeUnitMixin):
    >>>     pass
    >>> x = NameUnitDataType([1, 2, 3], name="Foo", unit="Bar")
    >>> x.name
    "Foo"
    >>> x.unit
    "Bar"
    """
    
    @property
    def unit(self):
        if 'unit' not in self.attributes:
            self.attributes['unit'] = ''
        return self.attributes['unit']
    
    @unit.setter
    def unit(self, value):
        self.attributes['unit'] = value
    
    @unit.deleter
    def unit(self):
        del self.attributes['unit']


class DataTypeCurveMixin(object):
    """
    A "mix-in" for data types that need an exposed curvetype attribute.
    
    Attributes
    ----------
    curvetype : str
        The curve type of the object. Obtained from `attributes`. If `attributes`
        doesn't have a key ``'curvetype'``, an empty string will be assigned to it.
    
    Examples
    --------
    >>> class NameCurveDataType(GenericDataType, DataTypeCurveMixin):
    >>>     pass
    >>> x = NameCurveDataType([1, 2, 3], name="Foo", curvetype="Bar")
    >>> x.name
    "Foo"
    >>> x.curvetype
    "Bar"
    """
    
    @property
    def curvetype(self):
        if 'curvetype' not in self.attributes:
            self.attributes['curvetype'] = ''
        return self.attributes['curvetype']
    
    @curvetype.setter
    def curvetype(self, value):
        self.attributes['curvetype'] = value
    
    @curvetype.deleter
    def curvetype(self):
        del self.attributes['curvetype']



class DataTypeMinMaxMixin(object):
    """    
    TODO: COMPLETAR ISSO!!!    
    """

    @property
    def min(self):
        if self.attributes.get('min') is None:
            self.min(np.nanmin(self._data))
        return self.attributes['min']
        
    @min.setter
    def min(self, value):
        self.attributes['min'] = value

    @min.deleter
    def min(self):
        del self.attributes['min']
           
    @property
    def max(self):
        if self.attributes.get('max') is None:
            self.min(np.nanmax(self._data))
        return self.attributes.get('max')

    @max.setter
    def max(self, value):
        self.attributes['max'] = value

    @max.deleter
    def max(self):
        del self.attributes['max']
       
        

        
        
class DataTypeIndexMixin(object):
    """
    A "mix-in" for data types that need an exposed index attribute (in general 
    time or depth).
    
    Attributes
    ----------
    index : IndexCurve

    
    TODO: COMPLETAR ISSO!!!
    
    """
    
    _ACCEPT_MULTIPLE_INDEXES = False

    
    @property
    def index(self):
        if 'index' not in self.attributes:
            self.attributes['index'] = []           
        return self.attributes['index']

    
    @index.setter
    def index(self, value):
        if isinstance(value, IndexCurve) and not self._ACCEPT_MULTIPLE_INDEXES: 
            self.attributes['index'] = value
        if isinstance(value, list) and self._ACCEPT_MULTIPLE_INDEXES: 
            self.attributes['index'] = value     
    
    @index.deleter
    def index(self):
        del self.attributes['index']        
        

        
class DataTypeIndexUidMixin(object):
   
    """
    
    TODO: COMPLETAR ISSO!!!
    
    """
        
    @property
    def index_uid(self):
        return self.attributes.get('index_uid')
    
        
    @index_uid.setter
    def index_uid(self, value):
        msg = "Cannot set object index_uid."
        raise TypeError(msg)

    
    @index_uid.deleter
    def index_uid(self):
        msg = "Cannot delete object index_uid."
        raise TypeError(msg)
        
        
        
'''        
class Depth(GenericDataType, DataTypeUnitMixin, DataTypeCurveMixin):
    """
    The depth measurements of a well log.
    
    In a well log, the `Depth` can be viewed as an array of depth values where
    the logging tool measurements were taken. The depth is usually associated
    with one or many logs (i.e. a set of measures obtained by the logging tool,
    for example the set of NPHI measures) and their array data are alligned.
    
    In a LAS file, for example, the depth is always the first curve. On most
    of the traditional well log plots, the depth is the y-axis and the logs
    occupy the x-axis of the tracks.

    Attributes
    ----------
    data : numpy.ndarray
        An array containing the depth values of each available measurement of a
        well log.
    
    See Also
    --------
    DataTypes.DataTypes.Log
    DataTypes.DataTypes.Well
    """
    
    tid = "depth"
    
    def __init__(self, data, **attributes):
        super(Depth, self).__init__(data, **attributes)
        self._data.flags.writeable = False
'''
 
        
       
        
        
class Log(GenericDataType, DataTypeUnitMixin, DataTypeCurveMixin, DataTypeMinMaxMixin, DataTypeIndexUidMixin):
    """
    The values of a particular measurement along a well.
    
    In a well log, the `Log` can be viewed as an array of the measurements made
    by a logging tool. The `Log` is usually associated with a depth, that
    provides the locations where each measurement was taken.
    
    On most of the traditional well log plots, the logs take the x-axis of the
    different tracks, while the depth is placed in the y-axis.
    
    Logs are not necessarily the result of a well loging operation. They can
    be obtained from operations between existing logs, for example.

    Attributes
    ----------
    data : numpy.ndarray
        An array containing the values of a particular property along a well.
    
    See Also
    --------
    DataTypes.DataTypes.Depth
    DataTypes.DataTypes.Well
    """
    
    tid = "log"
    _OM_TREE_PARENT_LABEL = 'Log'
    _OM_TREE_ATTR_SHOWN = [('curvetype', 'Curve Type'),
                           ('unit', 'Units'),
                           ('min', 'Min Value'),
                           ('max', 'Max Value'),
                           ('index_uid', 'Index Uid')
    ] 
    
    def __init__(self, data, **attributes):
        super(Log, self).__init__(data, **attributes)
        self._data.flags.writeable = False
        
        self.min = np.nanmin(self._data)
        self.max = np.nanmax(self._data)


        

        
class Property(GenericDataType, DataTypeUnitMixin, DataTypeCurveMixin):
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


class Part(GenericDataType, DataTypeCurveMixin):
    """
    A set of samples belonging to a well log.
    
    Attributes
    ----------
    data : np.ndarray
        An array of floats or booleans. This array must have dimensions
        compatible with the pertinent `Depth`. If a float array, each of its
        values indicates the probability (0 being no chance and 1 being
        absolute certainty) the sample belonging to the `Part`. In the boolean
        case, each value denotes whether or not the sample belong to the
        `Part`.
    color : tuple
        The color associated with the `Part`. It is a tuple of 3 ints, each of
        them varying between 0 and 255.
    code : int
        The numeric code associated with the `Part`. If not given, a unique
        value will be assigned to it.
    
    See also
    --------
    DataTypes.DataTypes.Property
    DataTypes.DataTypes.Partition
    DataTypes.DataTypes.Well
    """
    tid = "part"
    _NOCODESTART = 1000
    _DEFAULTCOLORS = COLOR_CYCLE_RGB
    _OM_TREE_PARENT_LABEL = 'Part'
    
    @GenericDataType.name.getter
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{:g}'.format(self.code)
        return self.attributes['name']
    
    @property
    def code(self):
        if 'code' not in self.attributes:
            self.attributes['code'] = self._NOCODESTART + self.uid[1]
        return self.attributes['code']
    
    @code.setter
    def code(self, value):
        self.attributes['code'] = value
    
    @code.deleter
    def code(self):
        del self.attributes['code']
    
    @property
    def color(self):
        if 'color' not in self.attributes:
            self.attributes['color'] = self._DEFAULTCOLORS[self.oid % len(self._DEFAULTCOLORS)]
        return self.attributes['color']
    
    @color.setter
    def color(self, value):
        self.attributes['color'] = value
    
    @color.deleter
    def color(self):
        del self.attributes['color']


class Partition(ParentObject, DataTypeCurveMixin, DataTypeIndexUidMixin):
    """
    A partitioning of well log samples.
    
    From the mathematics definition a partition of a set is "a grouping of the
    set's elements into non-empty subsets, in such a way that every element is
    included in **one and only one** of the subsets". [1]_
    
    In the well log case, a `Partition` is a division of the well log in
    subsets. Each subset is represented by a `Part`, and each sample of the
    well log can belong to only one subset (i.e. only one `Part`) in the same
    `Partition` (note that a sample can belong to other parts in different
    partitions). A practical example of a partition is the result of a facies
    classification process. A certain lithology is equivalent to a `Part`, and
    each sample of the well log can be associated with only one lithology.
    
    A `Partition` can also have associated properties (see `Property`).
    
    Attributes
    ----------
    name : str
        The name of the `Partition`. If no name is assigned to it, a string
        representation of its unique identificator (`uid`) will be used.
    
    References
    ----------
    .. [1] Partition of a set:
    https://en.wikipedia.org/wiki/Partition_of_a_set    
    
    See also
    --------
    DataTypes.DataTypes.Property
    DataTypes.DataTypes.Part
    DataTypes.DataTypes.Well
    """
    tid = "partition"
    _OM_TREE_PARENT_LABEL = 'Partition'
    _OM_TREE_ATTR_SHOWN = [('curvetype', 'Curve Type'),
                           ('index_uid', 'Index Uid')
    ] 
    def __init__(self, **attributes):
        super(Partition, self).__init__()
        self.attributes = attributes
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
    
    def getdata(self, asbool=True):
        """
        Return a matrix which lines are the data from the `Partition` parts.
        
        Parameters
        ----------
        asbool : bool, optional
            Whether to return a boolean matrix. This parameter makes no
            difference if the parts' `data` is already boolean. In the
            case where the parts' `data` represent a probability of belonging
            to that part, the part with largest probability will be set to
            `True` and the others to `False`, for each sample. For example,
            if a column of the matrix is ``[0.6, 0.3, 0.1]`` with `asbool` set
            to `False` will be transformed into ``[True, False, False]`` if
            `asbool` is set to `True`.
        
        Returns
        -------
        np.ndarray
            A matrix which lines are the parts' `data`. In other words,
            ``pttn.getdata(False)[0]`` is the same as
            ``pttn.list('part')[0].data``, where ``pttn`` is a `Partition`
            instance. The parameters `asbool`, which defaults to `True`,
            controls the `dtype` of the matrix.
        """
        data = np.vstack(part.data for part in self.list('part'))
        if data.dtype == bool or asbool == False:
            return data
        else:
            bdata = np.zeros_like(data, dtype=bool)
            bdata.T[np.arange(bdata.shape[1]), np.argmax(data, axis=0)] = True
            return bdata

    def getaslog(self, propuid=None):
        """
        Return a log representation of the partition or one of its properties.
        
        Parameters
        ----------
        propuid : uid, optional
            The unique identificator of the property which values will be
            returned. If this parameter is not provided, a representation
            of the partition itself is returned.
        
        Returns
        -------
        np.ndarray
            A log representation of the partition or one of its properties. The
            samples belonging to a particular `Part` will have a value equal to
            the property `data` in that `Part`, or to the `Part` `code` in the
            case `propuid` is not given.
        """
        if propuid is None:
            values = [part.code for part in self.list('part')]
            null = -1
        else:
            prop = self.get(propuid)
            values = [prop.getdata(part.uid) for part in self.list('part')]
            null = np.nan
        return self._getaslog(values, self.getdata(), null)

    @staticmethod
    def _getaslog(values, data, null):
        """
        Auxiliar method used by `getaslog`.
        
        Basically, this method performs a matrix multiplication between
        `values` and `data`.
        
        Parameters
        ----------
        values : array-like
            A one-dimensional array with length equal to the number of lines
            of `data`.
        data : np.ndarray
            A boolean matrix. The number of lines of the matrix must be equal
            to the lenght of `values`. Each column of the matrix must have one
            and only one `True` value.
        null : int or float
            The representation of invalid or non-existent data.
        
        Returns
        -------
        np.ndarray
            The matrix multiplication of `values` and `data` with invalid
            entries replaced by `null`. Note that it is a one-dimensional array
            with lenght equal to the number of columns of `data`.
        """
        if isinstance(null, float) or any(isinstance(value, float) for value in values):
            dtype = float
        else:
            dtype = int
        
        values = np.asanyarray(values, dtype=dtype)
        
        if np.isnan(null):
            notnull = ~np.isnan(values)
        else:
            notnull = values != null

        log = np.dot(values[notnull], data[notnull])
        
        # Define como null os valores não preenchidos pela multiplicação da
        # linha anterior, isto é, onde uma coluna de data[notnull] não tem
        # nenhuma entrada não nula
        log[~np.sum(data[notnull], axis=0, dtype=bool)] = null
        
        return log
    
    @staticmethod
    def getfromlog(logdata, null=-1):
        """
        Inverse method of `getaslog`.
        
        From a log-like representation of a partition it returns the boolean
        matrix and a array containing the codes related to each line.
        
        Parameters
        ----------
        logdata : array-like
            A one-dimensional array of integers that will be transformed into
            a boolean matrix.
        null : int, optional
            The null value of `logdata`, i.e. a value that will be excluded
            during the transformation.
        
        Returns
        -------
        np.ndarray
            The boolean matrix representation of `logdata`.
        np.ndarray
            The codes associated with each lines of the the boolean matrix.
        """
        if not np.equal(np.mod(logdata[np.isfinite(logdata)], 1), 0).all():
            print u"Não é partição!"
            return
        codes = np.unique(logdata)
        tokeep = np.isfinite(codes)*(codes != null)
        codes = codes[tokeep]
        
        booldata = np.zeros((len(codes), len(logdata)), dtype=bool)
        for j in range(len(codes)):
            booldata[j][logdata == codes[j]] = True
        
        return booldata, codes
    
    def _getstate(self):
        state = super(Partition, self)._getstate()
        state.update(self.attributes)
        return state


class Well(ParentObject, DataTypeIndexMixin):
    """
    A set of data related to a well.
    
    During the life-cycle of a oil well, from the drilling to the abandonment,
    various forms of data acquisition can be performed. For example, multiple
    logs can be produced in different times with different purposes. The `Well`
    `DataType` is used to group this data.
    
    A `Well` can be associated as 'parent' of other data types present in
    the `DataType` module, such as `Depth`, `Log` and `Partition`.
    
    Attributes
    ----------
    name : str
        The name of the well.
    
    See also
    --------
    DataTypes.DataTypes.Depth
    DataTypes.DataTypes.Log
    DataTypes.DataTypes.Partition
    """
    tid = "well"
    _OM_TREE_PARENT_LABEL = 'Well'
    _ACCEPT_MULTIPLE_INDEXES = True
    
    def __init__(self, **attributes):
        super(Well, self).__init__()
        self.attributes = attributes
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
    
    def _getstate(self):
        state = super(Well, self)._getstate()
        state.update(self.attributes)
        return state

        
        
class Core(GenericDataType, DataTypeUnitMixin, DataTypeCurveMixin):
    tid = "core"
    
    def __init__(self, data, **attributes):
        super(Core, self).__init__(data, **attributes)
        self._data.flags.writeable = False
        
        
        
###############################################################################


class TracePosStack(GenericDataType):
    tid = "trace_pos_stack"
    
    def __init__(self, data, **attributes):
        super(TracePosStack, self).__init__(data, **attributes)
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
          
                
                
class PosStackSeismic(ParentObject, DataTypeUnitMixin):
    tid = "seismic_pos_stack"
    #label = 'Seismic Post-Stacked'
    
    def __init__(self, **attributes):
        super(PosStackSeismic, self).__init__()
        self.attributes = attributes
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']        

    def _getstate(self):
        state = super(PosStackSeismic, self)._getstate()
        state.update(self.attributes)
        return state
        
        
 
class OffsetPreStack(GenericDataType):
    tid = "offset_pre_stack"
    
    def __init__(self, data, **attributes):
        super(OffsetPreStack, self).__init__(data, **attributes)
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
       
        
class TracePreStack(ParentObject):
    tid = "trace_pre_stack"
    
    def __init__(self, **attributes):
        super(TracePreStack, self).__init__()
        self.attributes = attributes
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']        

    def _getstate(self):
        state = super(TracePreStack, self)._getstate()
        state.update(self.attributes)
        return state
        


class PreStackSeismic(ParentObject, DataTypeUnitMixin):
    tid = 'seismic_pre_stack'
   # label = 'Seismic Pre-Stacked'
    
    def __init__(self, **attributes):
        super(PreStackSeismic, self).__init__()
        self.attributes = attributes
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']        

    def _getstate(self):
        state = super(PreStackSeismic, self)._getstate()
        state.update(self.attributes)
        return state
        
        
###############################################################################
###############################################################################
        

        
class IndexCurve(Property, DataTypeMinMaxMixin):   
    tid = "index_curve"
    _DATATYPE_VALID_TYPES = ['Depth', 'Time']
    _DEFAULTDATATYPE = 'Depth'
    # TODO: Mudar isso com a criacao de class para units
    _DEFAULTDEPTHUNIT = 'm'
    _DEFAULTTIMEUNIT = 'ms'
    _OM_TREE_PARENT_LABEL = 'Index'
    _OM_TREE_ATTR_SHOWN = [('curvetype', 'Curve Type'),
                           ('unit', 'Units'),
                           ('min', 'Min Value'),
                           ('max', 'Max Value')
    ]
    
    
    def __init__(self, data, **attributes):
        super(IndexCurve, self).__init__(data, **attributes)
        self._data.flags.writeable = False
        if attributes.get('curvetype') is None:
            self.curvetype = self._DEFAULTDATATYPE
        elif attributes.get('curvetype') not in self._DATATYPE_VALID_TYPES:
            raise Exception('Invalid curve type. Valid types: {}'.format(str(self._DATATYPE_VALID_TYPES)))
        else:
            self.curvetype = attributes.get('curvetype')
            
        if attributes.get('unit') is None:
            if self.curvetype == 'Depth':
                self.unit = self._DEFAULTDEPTHUNIT
            else:    
                self.unit = self._DEFAULTTIMEUNIT
        
        self.min = np.nanmin(self._data)
        self.max = np.nanmax(self._data)
           

        
        
###############################################################################
###############################################################################


class Seismic(GenericDataType):
    tid = 'seismic'
    _OM_TREE_PARENT_LABEL = 'Seismic'
    _OM_TREE_ATTR_SHOWN = [('stacked', 'Stacked'),
                           ('domain', 'Domain'),    
                           ('unit', 'Units'),
                           ('datum', 'Datum'),
                           ('sample_rate', 'Sample Rate'),
                           ('samples', 'Samples per trace'),
                           ('traces', 'Traces')
    ] 


    def __init__(self, data, **attributes):
        super(Seismic, self).__init__(data, **attributes)



class Velocity(GenericDataType):
    tid = 'velocity'
    _OM_TREE_PARENT_LABEL = 'Velocity'
    _OM_TREE_ATTR_SHOWN = [
                           ('domain', 'Domain'),    
                           ('unit', 'Units'),
                           ('datum', 'Datum'),
                           ('sample_rate', 'Sample Rate'),
                           ('samples', 'Samples per trace'),
                           ('traces', 'Traces')
    ] 


    def __init__(self, data, **attributes):
        super(Velocity, self).__init__(data, **attributes)
        
        
        
###############################################################################
###############################################################################

        
class Scale(GenericDataType):
    tid = "scale"
    
    def __init__(self, data, **attributes):
        super(Scale, self).__init__(data, **attributes)
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
    
    @name.deleter
    def name(self):
        del self.attributes['name']
          
        
    
class Scalogram(GenericDataType):
    tid = 'scalogram'
    _OM_TREE_PARENT_LABEL = 'Scalogram'
    _OM_TREE_ATTR_SHOWN = [
                           ('type', 'Type'),                             
                           ('domain', 'Domain'),    
                           ('unit', 'Units'),
                           ('datum', 'Datum'),
                           ('sample_rate', 'Sample Rate'),
                           ('samples', 'Samples per scale'),
                           ('scales', 'Scales per trace'),
                           ('traces', 'Traces')
    ] 


    def __init__(self, data, **attributes):
        super(Scalogram, self).__init__(data, **attributes)
        
        
###############################################################################
        
""" Moved to app.gripy_controller.py 
   
ObjectManager.registertype(Core, Well)
#ObjectManager.registertype(Core, Well) # the idea is this!

ObjectManager.registertype(Well)
#ObjectManager.registertype(Depth, Well)
ObjectManager.registertype(Log, Well)
ObjectManager.registertype(Partition, Well)
ObjectManager.registertype(Part, Partition)
ObjectManager.registertype(Property, Partition)


ObjectManager.registertype(IndexCurve, Well)

ObjectManager.registertype(Seismic)

ObjectManager.registertype(Velocity)

#ObjectManager.registertype(IndexCurve, Seismic)

#ObjectManager.registertype(PosStackSeismic)
#ObjectManager.registertype(TracePosStack, PosStackSeismic)

#ObjectManager.registertype(PreStackSeismic)
#ObjectManager.registertype(TracePreStack, PreStackSeismic)
#ObjectManager.registertype(OffsetPreStack, TracePreStack)


ObjectManager.registertype(Scalogram)
#ObjectManager.registertype(Scale, Scalogram)

"""
