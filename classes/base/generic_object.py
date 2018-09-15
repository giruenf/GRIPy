# -*- coding: utf-8 -*-
"""
Gripy Base Classes
==================

This file defines the base classes for all GRIPy objects.

Here we have 2 main Metaclasses: GripyMeta and GripyManagerMeta. They are
responsible for create all classes inherits from GripyObject or GripyManager.
Another Metaclass in this file is GripyWxMeta is a convinience one for creating 
object inherits from GripyObject and wx.Object.

All GripyObjects have GripyWxMeta as metaclass as well as GripyManagers have
GripyManagerMeta. 

Our flavor of Metaclasses was bluit based on the references below.

    https://www.python-course.eu/python3_metaclasses.php and
    https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/



"""

import types
from collections import OrderedDict
from collections import Sequence

import wx

#from app.gripy_app import GripyApp
from app import app_utils
from app import pubsub
from classes.base.metaclasses import GripyWxMeta
from app import log



class GripyObject(pubsub.PublisherMixin, metaclass=GripyWxMeta):  
    """
    Base class for all GRIPy classes deal
    
    All GripyObjects have GripyWxMeta as metaclass.
    
    _ATTRIBUTES:
        * default_value:    As the name says.
        * type:             Valid type (e.g. int, str).
        * label:            Friendly name for attribute (used in a pg_property or Tree)
        * pg_property:      Kind of pg_property which deals with this attribute 
        * options_labels:   Options shown as valid for attribute (as shown in a wx.ComboBox).
        * options_values:   The truly options valid for attribute (returned from wx.ComboBox selection event).

        * 25/8/2018: The least 4 above occours only in ui/mvc_classes/track_object.py and ui/mvc_classes/propgrid.py.
        
    _IMMUTABLES_KEYS
        Attributes that must be setted only during object initialization. 
        They cannot be deleted or changed. (e.g. oid)
        
    _BYPASSES_KEYS
        Attributes that bypasses the checkage made in __setattr__ or 
        __setitem__ for default ones. This type was created for flags like
        "_processing_value_from_event" seen in GripyObject.
    """
    tid = None
    _BYPASSES_KEYS = ['_processing_value_from_event']
    _IMMUTABLES_KEYS = ['oid']

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['name'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }   
    
    def __init__(self, **kwargs): 
        _manager_class = self._get_manager_class()
        _manager_obj = _manager_class()
        #
        if _manager_obj.is_loading_state():
            self.oid = kwargs.pop['oid']
        else:    
            self.oid = _manager_obj._getnewobjectid(self.tid)     
        #    
        self._processing_value_from_event = True
        self.name = '{}.{}'.format(*self.uid)
        for attr_name, attr_props in self._ATTRIBUTES.items():
            self[attr_name] = kwargs.get(attr_name, 
                                            attr_props.get('default_value')
            )    
        self._processing_value_from_event = False

            
    def __str__(self):
        return '{}.{}'.format(*self.uid)
 
    def _get_manager_class(self):
        return wx.App.Get()._get_manager_class(self)

       
    def get_publisher_name(self):
        return pubsub.uid_to_pubuid(self.uid)    
         
    @property
    def uid(self):
        return self.tid, self.oid

    # TODO: try to put it in the Metaclass
    def is_initialised(self):
        return self.__dict__.get('_GripyMeta__initialised', False)    
    
    def set_value_from_event(self, key, value):
        self._processing_value_from_event = True
        try:
            self._do_set(key, value)
        except: 
            raise
        finally:    
            self._processing_value_from_event = False      
                       
            
    def __getattribute__(self, key):
        try:
            return object.__getattribute__(self, key)
        except Exception as e:
            try:
                return self.__class__.__getattr__(key)
            except:
                try:
                    return self[key]
                except Exception as e:
                    raise AttributeError('Invalid attribute: {}.'.format(key))


    def __getitem__(self, key):
        # https://docs.python.org/3.6/reference/datamodel.html#object.__getitem__
        try:
            return self.__dict__[key]
        except:
            # Maybe key is a property
            prop = None
            for cls in self.__class__.__mro__[:-2]:
                if key in cls.__dict__ and isinstance(cls.__dict__[key], property):
                    prop = cls.__dict__[key]      
                    break
            if not prop:
                raise Exception ('ERROR __getitem__({}, {}): property not found.'.format(self, key)) 
            try:
                return prop.__get__(self, key)
            except Exception:
                raise Exception ('ERROR __getitem__({}, {}): property cannot be obtained.'.format(self, key)) 
                    
                
    def __delitem__(self, key):
        self._do_del(key)
        
    def __delattr__(self, key):  
        self._do_del(key)
        
    def _do_del(self, key):
        if key in self._IMMUTABLES_KEYS:
            msg = 'Cannot delete attribute {}.'.format(key)
            raise AttributeError(msg)           
        if key in self._ATTRIBUTES:
            msg = 'Cannot delete _ATTRIBUTE {}.'.format(key)
            raise AttributeError(msg)     
        object.__delattr__(self, key)
 
    def __setitem__(self, key, value):
        self._do_set(key, value)

    def __setattr__(self, key, value):
        if key in self._BYPASSES_KEYS:
            self.__dict__[key] = value
            return
        elif key in self._IMMUTABLES_KEYS:
            if not self.is_initialised():
                self.__dict__[key] = value
                return
            else:
                msg = '{} cannot be changed. It is on {}._IMMUTABLES_KEYS.'.format(key, self.__class__.__name__)
                raise Exception(msg)   
        self._do_set(key, value)
        
        
#
# key not in ATTR, not in DICT, is PROP, is INITED  -> OK -> Case 1   
# key not in ATTR, not in DICT, is PROP, not INITED  -> OK -> Case 1  
#        
# [DEPRECATED] - key not in ATTR, not in DICT, not PROP, is INITED -> ERROR -> Exception 1 
#                turned into case 2.3 below
#
# Setting DICT key while running object __init__       
# key not in ATTR, not in DICT, not PROP, not INITED -> OK  -> Case 2.1
#        
# Key DICT was setted on case 2.1 above         
# key not in ATTR, is in DICT, not INITED, not PROP -> OK  -> Case 2.2
# key not in ATTR, is in DICT, is INITED, not PROP -> OK -> Case 2.2
# key not in ATTR, not in DICT, is INITED, not PROP -> OK -> Case 2.3 
#        
# Key is monitorated attribute         
# key is in ATTR -> OK -> Case 3       
               
        
    def _do_set(self, key, value):       
        # Checking if key is a Data Descriptor, e.g. property
        if key not in self._ATTRIBUTES and key not in self.__dict__:
            prop = None
            for cls in self.__class__.__mro__[:-2]:
                if key in cls.__dict__ and isinstance(cls.__dict__[key], property):
                    prop = cls.__dict__[key]                 
            if prop:
                # Key was a property - Case 1
                try:
                    prop.__set__(self, value)
                    return
                except:
                    raise                    
             
        if key not in self._ATTRIBUTES:
            # Cases 2.1 and 2.2
            # Inserting or editing a non-monitorated attribute.
            object.__setattr__(self, key, value)
            return
              
        # Case 3: Okay,we have a monitorated attribute
        type_ = self._ATTRIBUTES[key].get('type')
         
        # Special treatment for some Sequences attributes like 
        # _ATTRIBUTES.type: (sequence, sequence_inner_type, sequence_lenght)
        # e.g., 'type': (tuple, float, 2) 
        # In case we have 'type': tuple, the default threatment will be given.
        if isinstance(type_, Sequence):
            if len(type_) >= 3:
                seq_len = type_[2]   
                if len(value) != seq_len:
                    raise Exception('Wrong lenght on attribute {}.{}'.format(\
                                    self.__class__.__name__, key)
                    )
            if len(type_) >= 2:
                sequence_inner_type = type_[1]
                if sequence_inner_type:
                    value = [sequence_inner_type(val) for val in value]              
            type_ = type_[0]
            value = type_(value)
                     
        # Special treatment for functions
        elif type_ == types.FunctionType:
            if isinstance(value, str):
                value = app_utils.get_function_from_string(value)
            if value is not None and not callable(value):
                msg = 'ERROR: Attributes signed as \"types.FunctionType\" can recieve only \"str\" or \"types.FunctionType\" values. '
                msg += 'Received: {} - Type: {}'.format(value, type(value))
                log.error(msg)
                raise AttributeError(msg) 
                
        elif not isinstance(value, type_):
            try:
                if value is not None:    
                    value = type_(value)
            except:
                raise 
                
        if not self.is_initialised():
            # Setting attribute under object.__init__.
            # No need to send any messages
            self.__dict__[key] = value
        else:    
            # Object was initializated.
            if self.__dict__[key] == value:
                # No change. Just return
                return      
            #
            old_value = self[key]    
            self.__dict__[key] = value
            #
            if not self._processing_value_from_event:
                # Notify about the change ocurred.
                topic = 'change.' + key
                self.send_message(topic, old_value=old_value, new_value=value)
                
        msg = '    {} has setted attribute {} = {}'.format(self.uid, key, self[key])  
        log.debug(msg)



    def _getstate(self):
        state = OrderedDict()  
        for attr_name in self._ATTRIBUTES.keys():
            state[attr_name] = self[attr_name]    
        return state  
          



