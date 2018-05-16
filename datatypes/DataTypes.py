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

from om.manager import ObjectManager

from app.gripy_base_classes import GripyObject

from basic.colors import COLOR_CYCLE_RGB



VALID_Z_AXIS_DATATYPES = [('MD', 'Measured Depth'), 
                          ('TVD', 'True Vertical Depth'),
                          ('TVDSS', 'True Vertical Depth Subsea'), 
                          ('TIME', 'One-Way Time'),
                          ('TWT', 'Two-Way Time')
]




# TODO: Rever docs
# TODO: Criar GripyObject._loadstate para nao necessitar de colocar tudo no __init__ dos objetos
class GenericDataType(GripyObject):
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
    >>> class NamedDataType(GripyObject):
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
    def __init__(self, *args, **attributes):
        super(GenericDataType, self).__init__()
        if not args:
            self._data = None
        else:
            self._data = args[0]
        self.attributes = attributes
        if isinstance(self._data, np.ndarray):
            self._data.flags.writeable = False    
    
    
    @property
    def name(self):
        if 'name' not in self.attributes:
            self.attributes['name'] = '{}.{}'.format(*self.uid)
        return self.attributes['name']
    
    @name.setter
    def name(self, value):
        self.attributes['name'] = value
        
    '''
    @name.deleter
    def name(self):
        del self.attributes['name']
    '''
    
    def get_friendly_name(self):
        return self.name
    
    @property
    def data(self):
        return self._data

    """
    TODO: Decidir isso
    
    @data.setter
    def data(self, value):
        msg = "Cannot set object data."
        raise TypeError(msg)

    @data.deleter
    def data(self):
        msg = "Cannot delete object data."
        raise TypeError(msg)

    """

    @property
    def min(self):
        if self.data is None:
            return None
        return np.nanmin(self._data)
        
    @property
    def max(self):
        if self.data is None:
            return None
        return np.nanmax(self._data)

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
    
    @property
    def datatype(self):
        if 'datatype' not in self.attributes:
            self.attributes['datatype'] = ''
        return self.attributes['datatype']
    
    @datatype.setter
    def datatype(self, value):
        self.attributes['datatype'] = value
    
    @datatype.deleter
    def datatype(self):
        del self.attributes['datatype']
           
        
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
                """
                inner_ord_dict = OrderedDict()
                for di in dis:
                    if di.dimension not in inner_ord_dict.keys():
                        inner_ord_dict[di.dimension] = []    
                    inner_ord_dict.get(di.dimension).append(di)    
                ret[index_set.uid] = inner_ord_dict    
                """
        return ret
    
    """
    def get_indexes_set(self):
        OM = ObjectManager()
        indexes_set = OM.list('index_set', self.uid)
        ret = OrderedDict()
        for index_set in indexes_set:
            dis = OM.list('data_index', index_set.uid)
            if not dis:
                ret[index_set.name] = None
            else:
                inner_ord_dict = OrderedDict()
                for di in dis:
                    if di.dimension not in inner_ord_dict.keys():
                        inner_ord_dict[di.dimension] = []    
                    inner_ord_dict.get(di.dimension).append(di)    
                ret[index_set.name] = inner_ord_dict    
        return ret    
    """
    
    def get_data_indexes(self, set_name):
        OM = ObjectManager()
        for index_set_uid, inner_ord_dict in self.get_indexes_set().items():
            index_set = OM.get(index_set_uid) 
            if set_name == index_set.name:
                return inner_ord_dict
        return None
    
    """
    def get_data_indexes(self, set_name):
        #OM = ObjectManager()
        for index_set_name, inner_ord_dict in self.get_indexes_set().items():
            #index_set = OM.get(index_set_uid) 
            if set_name == index_set_name:
                return inner_ord_dict
        return None
    """

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
    
    """
    def get_friendly_indexes_dict(self):
        #OM = ObjectManager()
        ret_od = OrderedDict()
        indexes_set = self.get_indexes_set()
        for index_set_name, indexes_ord_dict in indexes_set.items():
            #index_set = OM.get(index_set_uid)
            for dim_idx, data_indexes in indexes_ord_dict.items():
                for data_index in data_indexes:
                    di_friendly_name = data_index.name + '@' + index_set_name
                    ret_od[di_friendly_name] = data_index.uid       
        return ret_od
    """
    
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
        state = super(GenericDataType, self)._getstate()
        state.update(data=self._data)
        state.update(self.attributes)
        return state


    def _getparent(self):
        OM = ObjectManager()
        parent_uid = OM._getparentuid(self.uid)
        if not parent_uid:
            return None
        return OM.get(parent_uid)     



class WellData1D(GenericDataType):                             
    tid = "data1d"
    
    def __init__(self, data, **attributes):
        index_set_uid = attributes.get('index_set_uid')
        try:    
            tid, oid = index_set_uid 
        except:
            print (index_set_uid, type(index_set_uid))										
            raise Exception('Object attribute \"index_set_uid\" must be a \"uid\" tuple.')    
        if tid != 'index_set':
            raise Exception('Object attribute \"index_set_uid\" must have its first argument as \"index_set\".')
        super(WellData1D, self).__init__(data, **attributes)
        OM = ObjectManager()        
        OM.subscribe(self._on_OM_add, 'add')


    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        #print 'WellData1D._on_OM_add:', objuid
        OM = ObjectManager()
        try:
            OM.unsubscribe(self._on_OM_add, 'add')     
        except Exception as e:
            print ('Deu ruim no unsub:', e)
        try:
            parent_uid = OM._getparentuid(self.uid)
            # TODO: remover esse armengue
            if self.tid == 'part':
                parent_well_uid = OM._getparentuid(parent_uid)
            else:
                parent_well_uid = parent_uid
            # FIM - Armengue    
        #    print 'parent_well_uid:', parent_well_uid
            my_index_set = OM.get(self.index_set_uid)
        #    print 'my_index_set:', my_index_set
        #    print 'list:'
        #    for obj_is in OM.list('index_set', parent_well_uid):
        #        print obj_is
            if my_index_set not in OM.list('index_set', parent_well_uid):
                print ('DEU RUIM')
                raise Exception('Invalid attribute \"index_set\"={}'.format(self.index_set_uid))
        except:
            raise

    @property
    def index_set_uid(self):
        return self.attributes['index_set_uid']


    def get_data_indexes(self):
        OM = ObjectManager()            
        try:
            index_set = OM.get(self.index_set_uid)
            return index_set.get_data_indexes()
            """
            data_indexes = OM.list('data_index', self.index_set_uid)
            if not data_indexes:
                return None
            ret_dict = OrderedDict()
            for data_index in data_indexes:
                if data_index.dimension not in ret_dict.keys():
                    ret_dict[data_index.dimension] = []    
                ret_dict.get(data_index.dimension).append(data_index)    
            return ret_dict
            """
        except:
            return None
        
        
    def get_indexes(self):
        raise Exception('Invalid METHOD')   
    
    def get_friendly_name(self):
        OM = ObjectManager()
        parent_well_uid = OM._getparentuid(self.uid)
        parent_well = OM.get(parent_well_uid)         
        return self.name + '@' + parent_well.name



    
class Log(WellData1D):
                                  
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
        super(Log, self).__init__(data, **attributes)


        
    
class Property(GenericDataType):
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


class Part(WellData1D):
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
    _FRIENDLY_NAME = 'Part'
    
    def __init__(self, data=None, **attributes):        
        super(Part, self).__init__(data, **attributes)

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


class Partition(WellData1D):
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
    _FRIENDLY_NAME = 'Partition'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
													   
    ] 
    
    def __init__(self, data=None,**attributes):        
        super(Partition, self).__init__(data,**attributes)
        self.children = OrderedDict()
#        self.attributes = attributes
    
    def getdata(self, partlist=None, asbool=True):
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
        if partlist == None: partlist = self.list('part')
#        data = np.vstack(part.data for part in self.list('part'))
        data = np.vstack(part.data for part in partlist)
        if data.dtype == bool or asbool == False:
            print ('\n1data', data)
            return data
        else:
            bdata = np.zeros_like(data, dtype=bool)
            bdata.T[np.arange(bdata.shape[1]), np.argmax(data, axis=0)] = True
            print ('\n2data', bdata)
            return bdata
        
    def getaslog(self, partlist=None, propuid=None):
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
        if partlist == None: partlist = self.list('part')
        if propuid is None:
#            values = [part.code for part in self.list('part')]
            values = [part.code for part in partlist]
            null = -1
        else:
            prop = self.get(propuid)
#            values = [prop.getdata(part.uid) for part in self.list('part')]
            values = [prop.getdata(part.uid) for part in partlist]
            null = np.nan
        return self._getaslog(values, self.getdata(partlist), null)

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
            print ('Não é partição!')
            return
        codes = np.unique(logdata)
        tokeep = np.isfinite(codes)*(codes != null)
        codes = codes[tokeep]
        
        booldata = np.zeros((len(codes), len(logdata)), dtype=bool)
        for j in range(len(codes)):
            booldata[j][logdata == codes[j]] = True
        
        return booldata, codes

    """
    def get_index(self):
        _OM = ObjectManager()
        parent_uid = _OM._getparentuid(self.uid)
        parent = _OM.get(parent_uid)
        return parent.get_index()
    """
    
    @property
    def start(self):
        if 'start' not in self.attributes:
            data = self.getaslog()
            index_data = self.get_index()._data
            self.attributes['start'] = float(index_data[np.isfinite(data)][0])
        return self.attributes['start']
    
    @property
    def end(self):
        if 'end' not in self.attributes:
            data = self.getaslog()
            index_data = self.get_index()._data
            self.attributes['end'] = float(index_data[np.isfinite(data)][-1])
        return self.attributes['end']
   
class RockTable(Partition):
    """
    new type
    """
    tid = "rocktable"
    _FRIENDLY_NAME = 'RockTable'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
													   
    ] 
    
    def __init__(self, data=None,**attributes):        
        super(RockTable, self).__init__(data,**attributes)

class RockType(Part):
    """
    New type
    """
    tid = "rocktype"
    _FRIENDLY_NAME = 'RockType'
    _SHOWN_ATTRIBUTES = [
#                            ('suporte', 'Suporte'),
                            ('fracgrain', 'FracGrain'),
                            ('grain', 'Grain'),
                            ('fracmatrix', 'FracMatrix'),
                            ('matrix', 'Matrix'),
                            ('vp', 'Vp'),
                            ('vs', 'Vs'),                             
                            ('rho', 'Density'),
                            ('k', 'Kmodulus'),
                            ('mi', 'Gmodulus'),
                            ('poi', 'Poisson')
    ] 
    def __init__(self, data=None,**attributes):        
        super(RockType, self).__init__(data,**attributes)
    
    @property
    def k(self):
        return self.attributes['k']
    
    @property
    def grain(self):
        return self.attributes['grain']
        
    @grain.setter
    def grain(self, value):
        self.attributes['grain'] = value
    
    @grain.deleter
    def grain(self):
        del self.attributes['grain']
    
    @property
    def matrix(self):
        return self.attributes['matrix']
    
    @matrix.setter
    def matrix(self, value):
        self.attributes['matrix'] = value
    
    @matrix.deleter
    def matrix(self):
        del self.attributes['matrix']
        
    @property
    def fracgrain(self):
        return self.attributes['fracgrain']
        
    @fracgrain.setter
    def fracgrain(self, value):
        self.attributes['fracgrain'] = value
    
    @fracgrain.deleter
    def fracgrain(self):
        del self.attributes['fracgrain']
    
    @property
    def fracmatrix(self):
        return self.attributes['fracmatrix']
    
    @fracmatrix.setter
    def fracmatrix(self, value):
        self.attributes['fracmatrix'] = value
    
    @fracmatrix.deleter
    def fracmatrix(self):
        del self.attributes['fracmatrix']
        
class Inference(Partition):
    """
    new type
    """
    tid = "inference"
    _FRIENDLY_NAME = 'Inference'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
													   
    ] 
    
    def __init__(self, data=None,**attributes):        
        super(RockTable, self).__init__(data,**attributes)
        
class Well(GenericDataType):
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
    _FRIENDLY_NAME = 'Well'
    _ACCEPT_MULTIPLE_INDEXES = True
    
    
    def __init__(self, **attributes):
        # Well does not have data
        super(Well, self).__init__(None, **attributes)


                       
class Core(GenericDataType):
    tid = "core"
    
    def __init__(self, data, **attributes):
        super(Core, self).__init__(data, **attributes)
        #self._data.flags.writeable = False
        
        
        
###############################################################################
###############################################################################
                

class Density(GenericDataType):
    tid = 'density'

    def __init__(self, data, **attributes):
        super(Density, self).__init__(data, **attributes)

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
        super(Seismic, self).__init__(data, **attributes)
                

class WellGather(Density):
    tid = 'gather'
    _FRIENDLY_NAME = 'Gather'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id')  
    ]

    def __init__(self, data, **attributes):
        super(WellGather, self).__init__(data, **attributes)
            

class Scalogram(Density):
    tid = 'scalogram'
    _FRIENDLY_NAME = 'Scalogram'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')                       
    ] 

    def __init__(self, data, **attributes):
        super(Scalogram, self).__init__(data, **attributes)



class GatherScalogram(Scalogram):
    tid = 'gather_scalogram'

    def __init__(self, data, **attributes):
        super(GatherScalogram, self).__init__(data, **attributes)



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
        super(Angle, self).__init__(data, **attributes)



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
        super(Velocity, self).__init__(data, **attributes)




class Spectogram(Density):
    tid = 'spectogram'
    _FRIENDLY_NAME = 'Spectogram'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')                       
    ] 

    def __init__(self, data, **attributes):
        super(Spectogram, self).__init__(data, **attributes)



class GatherSpectogram(Spectogram):
    tid = 'gather_spectogram'
    _FRIENDLY_NAME = 'Spectogram'
    
    def __init__(self, data, **attributes):
        super(GatherSpectogram, self).__init__(data, **attributes)
        
        
###############################################################################
###############################################################################


class Inversion(GenericDataType):
    tid = "inversion"
    _FRIENDLY_NAME = 'Inversion'
    _ACCEPT_MULTIPLE_INDEXES = True
    
    def __init__(self, **attributes):
        super(Inversion, self).__init__(**attributes)


    
class InversionParameter(GenericDataType):
                                 
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
        super(InversionParameter, self).__init__(data, **attributes)


###############################################################################
###############################################################################


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
        raise Exception('Invalid index code. [index_trype={}]'.format(index_type))
    if axis_unit not in index_props.get('units'):
        raise Exception('Invalid index unit.')


class IndexSet(GripyObject):
    tid = 'index_set'
    _FRIENDLY_NAME = 'Indexes Set'    
    
    def __init__(self, **attrbutes):
        super(IndexSet, self).__init__()
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
        OM.subscribe(self._on_OM_add, 'add')
                   
    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        OM = ObjectManager()        
        OM.unsubscribe(self._on_OM_add, 'add')
        
        parent_uid = OM._getparentuid(self.uid)
        for obj in OM.list(self.tid, parent_uid):
            if obj is not self and obj.name == self.name:
                raise Exception('Parent object has another son with same name.')

    @property
    def name(self):
        return self.attributes['name']

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


    def _getstate(self):
        state = super(IndexSet, self)._getstate()
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



# Class for discrete dimensions of Data Objects
class DataIndex(GenericDataType):
    tid = 'data_index'
    _FRIENDLY_NAME = 'Index'
    _SHOWN_ATTRIBUTES = [
                            #('_oid', 'Object Id'),
                            ('dimension', 'Dimension'),
                            ('datatype', 'Type'),
                            ('unit', 'Unit'),
                            ('start', 'Start'),
                            ('end', 'End'),
                            ('step', 'Step'),
                            ('samples', 'Samples')
    ]   
    
    
    def __init__(self, dimension_idx, name, datatype=None, unit=None, **kwargs):   
        if dimension_idx is None or dimension_idx < 0 or not isinstance(dimension_idx, int):
            raise Exception('Wrong value for dimension_idx [{}]'.format(dimension_idx))
        try:    
            check_data_index(datatype, unit)
        except:
            raise        
        data = kwargs.get('data') 
        start = kwargs.get('start') 
        end = kwargs.get('end') 
        step = kwargs.get('step')
        samples = kwargs.get('samples')
        if data is None or not isinstance(data, np.ndarray):
            try:
                end = start + step * samples
                data = np.arange(start, end, step)
            except:
                raise Exception('Data values were provided wrongly.')
        if start is None:        
            start = data[0]
        if end is None:
            end = data[-1]
        samples = len(data)
        super(DataIndex, self).__init__(data, name=name, 
                         datatype=datatype, unit=unit,
                         start=start, end=end, step=step, samples=samples
        )
        self.attributes['dimension'] = dimension_idx   
        #
        #OM = ObjectManager()        
        #OM.subscribe(self._on_OM_add, 'add')


    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        OM = ObjectManager()        
        OM.unsubscribe(self._on_OM_add, 'add')

    
    def get_data_indexes(self):
        OM = ObjectManager()            
        try:
            index_set_uid = OM._getparentuid(self.uid)
            index_set = OM.get(index_set_uid)
            return index_set.get_data_indexes()
        except:
            return None

    

    @property
    def start(self):
        #if 'start' not in self.attributes:
        self.attributes['start'] = self.data[0]
        return self.attributes['start']
    
    @property
    def end(self):
        #if 'end' not in self.attributes:
        self.attributes['end'] = self.data[-1]
        return self.attributes['end']

    @property
    def step(self):
        #if 'step' not in self.attributes:
        #self.attributes['step'] = None             
        return self.attributes.get('step')        

    @property
    def samples(self):
        #if 'samples' not in self.attributes:
        #self.attributes['samples'] = None             
        return len(self.data) #self.attributes.get('samples')      
    
    @property
    def dimension(self):
        return self.attributes['dimension']
    
    @classmethod
    def _loadstate(cls, **state):
        OM = ObjectManager()
        try:
            dimension = state.pop('dimension')
            name = state.pop('name')
            datatype = state.pop('datatype')
            unit = state.pop('unit')
            index = OM.new(cls.tid, dimension, name, datatype, unit, **state)
        except Exception as e:
            print ('\nERROR:', e, '\n', state)
        return index
        


class Model1D(Density):
    tid = 'model1d'
    _FRIENDLY_NAME = 'Model'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]

    def __init__(self, data, **attributes):
        super(Model1D, self).__init__(data, **attributes)

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



class ZoneSet(GenericDataType):
    tid = 'zone_set'
    _FRIENDLY_NAME = 'Zone Sets'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]
    
    def __init__(self, **attributes):
        super(ZoneSet, self).__init__(**attributes)


class Zone(GenericDataType):
    tid = 'zone'
    _FRIENDLY_NAME = 'Zones'
    _SHOWN_ATTRIBUTES = [
                            ('_oid', 'Object Id'),
                            ('datatype', 'Type')
    ]
    
    def __init__(self, **attributes):
        if attributes.get('start') is None or attributes.get('end') is None:
            raise Exception('No start or no end.')
        super(ZoneSet, self).__init__(**attributes)
        
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
    
    