"""
Gripy Base Metaclasses
======================

This file defines the base metaclasses for all GRIPy classes.

Here we have 2 main Metaclasses: GripyMeta and GripyManagerMeta. They are
responsible for create all classes inherits from GripyObject or GripyManager.

Another Metaclass in this file is GripyWxMeta is a convinience one for creating 
object inherits from GripyObject and wx.Object.

All GripyObjects will have GripyWxMeta as metaclass as well as 
GripyManagers have GripyManagerMeta. 

Our flavor of Metaclasses was bluit based on the references below.

    https://www.python-course.eu/python3_metaclasses.php and
    https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses

"""

from collections import OrderedDict

import wx

from app import log


class GripyMeta(type):

    def __new__(cls, clsname, superclasses, dict_):
        """
        Function reponsible for creating classes.
        
        In general every Gripy class is created on application startup.
        This method adjust attributes heritance, for example combining 
        class properties with parent classes ones.
        
        _ATTRIBUTES:
            * default_value --  As the name says.
            * type:             Valid type (e.g. int, str).
            * label:            Friendly name for attribute (used in a pg_property or Tree).
            * pg_property:      Kind of pg_property which deals with this attribute.
            * options_labels:   Options shown as valid for attribute (as shown in a wx.ComboBox).
            * options_values:   The truly options valid for attribute (returned from wx.ComboBox selection event).
            * 25/8/2018:        The least 4 above occours only in ui/mvc_classes/track_object.py and ui/mvc_classes/propgrid.py.
            
        _READ_ONLY:
            Properties that must be setted only during object initialization. 
            They cannot be deleted or changed (e.g. oid).
            
        """
        # Initializing class dictionary for _ATTRIBUTES and _READ_ONLY keys, if
        # they were not setted.
        if '_ATTRIBUTES' not in dict_:
            dict_['_ATTRIBUTES'] = OrderedDict()
        if '_READ_ONLY' not in dict_:
            dict_['_READ_ONLY'] = []
        # The method GripyObject.is_initialised is setted below. 
        # The idea is deal with GripyObject._GripyMeta__initialised only in 
        # this metaclass.
        dict_['is_initialised'] = lambda self: self.__dict__.get( \
            '_GripyMeta__initialised', False)
        # Time to create the new class...
        ret_class = super().__new__(cls, clsname, superclasses, dict_)

        # By default, _ATTRIBUTES and _READ_ONLY are incremented with every 
        # superclass _ATTRIBUTES and _READ_ONLY. 
        # If this behavior is not desired for _ATTRIBUTES, the key must be 
        # setted with None as value.

        #        print('\n\n', clsname)
        #        print('\tATTR:', ret_class.__dict__['_ATTRIBUTES'])
        for superclass in superclasses:
            #            print('\t\tSUPER:', superclass)
            if '_ATTRIBUTES' in superclass.__dict__:
                for key, value in superclass.__dict__['_ATTRIBUTES'].items():
                    if key not in ret_class.__dict__['_ATTRIBUTES']:
                        #                        print('\t\t\tkv:', key, value)
                        ret_class.__dict__['_ATTRIBUTES'][key] = value
            if '_READ_ONLY' in superclass.__dict__:
                for item in superclass.__dict__['_READ_ONLY']:
                    if item not in ret_class.__dict__['_READ_ONLY']:
                        ret_class.__dict__['_READ_ONLY'].append(item)

                    #        print('\tTOTAL ATTR:', ret_class.__dict__['_ATTRIBUTES'])
        log.debug('Successfully created class: {}.'.format(clsname))
        return ret_class

    def __call__(cls, *args, **kwargs):
        """
        Function reponsible for creating objects.
        
        """
        # Time to create the new object... 
        obj = super().__call__(*args, **kwargs)
        # Setting obj._GripyMeta__initialised used by is_initialised method.
        obj.__initialised = True
        #
        msg = 'Successfully created object from class: {}.'.format(
            obj.__class__)
        log.debug(msg)
        return obj


class GripyWxMeta(GripyMeta, wx.siplib.wrappertype):
    pass


class GripyManagerMeta(type):
    pass
    # def __new__(cls, clsname, superclasses, dict_):
    #    return super().__new__(cls, clsname, superclasses, dict_)
