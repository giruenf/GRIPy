
import types
from collections import OrderedDict
from collections import Sequence

import numpy as np
import wx

from app import app_utils
from app import pubsub
from classes.base.metaclasses import GripyWxMeta
from app import log


class GripyObject(pubsub.PublisherMixin, metaclass=GripyWxMeta):  
    """
    Base for all GRIPy classes.
    
    All GripyObjects have GripyWxMeta as metaclass.
    
    _ATTRIBUTES:
        * default_value:    As the name says.
        * type:             Valid type (e.g. int, str).
        * label:            Friendly name for attribute (used in a pg_property or Tree)
        * pg_property:      Kind of pg_property which deals with this attribute 
        * options_labels:   Options shown as valid for attribute (as shown in a wx.ComboBox).
        * options_values:   The truly options valid for attribute (returned from wx.ComboBox selection event).

        * 25/8/2018: The least 4 above occours only in ui/mvc_classes/track_object.py and ui/mvc_classes/propgrid.py.
        
    _READ_ONLY
        Attributes that must be setted only during object initialization. 
        They cannot be deleted or changed. (e.g. oid)
        
    """
    tid = None
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['name'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }      
    _READ_ONLY = ['oid']
    
    def __init__(self, **kwargs): 
        _manager_class = self.get_manager_class()
        _manager_obj = _manager_class()
        #
        # TODO: verificar isso...
        if _manager_obj.is_loading_state():
            self.oid = kwargs.pop['oid']
        else:    
            self.oid = _manager_obj._getnewobjectid(self.tid)     
        # 
        # TODO: verificar isso...   
        self._processing_value_from_event = True
        self.name = '{}.{}'.format(*self.uid)
        for attr_name, attr_props in self._ATTRIBUTES.items():
            self[attr_name] = kwargs.get(attr_name, 
                                            attr_props.get('default_value')
            )    
        self._processing_value_from_event = False
        #
        
    def __str__(self):
        return '{}.{}'.format(*self.uid)
                            
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
        if key in self._READ_ONLY:
            msg = 'Cannot delete attribute {}.'.format(key)
            raise AttributeError(msg)           
        if key in self._ATTRIBUTES:
            msg = 'Cannot delete _ATTRIBUTE {}.'.format(key)
            raise AttributeError(msg)     
        object.__delattr__(self, key)
 
    def __setitem__(self, key, value):
        self._do_set(key, value)

    def __setattr__(self, key, value):
        if key in self._READ_ONLY:
            if not self.is_initialised():
                self.__dict__[key] = value
                return
            else:
                msg = '{} cannot be changed. It is on {}._READ_ONLY ' + \
                                'list.'.format(key, self.__class__.__name__)
                raise Exception(msg)   
        self._do_set(key, value)
        
           
    def _do_set(self, key, value):       
        """
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
        """
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
        attr = self.find_attribute(key)
        type_ = attr.get('type')
         
        
        # Special treatment for some Sequences attributes like 
        # _ATTRIBUTES.type: (sequence, sequence_inner_type, sequence_lenght)
        # e.g., 'type': (tuple, float, 2) or 'type': (tuple, [str, int])  
        # In case we have 'type': tuple, the default threatment will be given.
        if isinstance(type_, Sequence):
            # When a tuple attribute is setted to None, bypass the checkage
            if value is not None:
                if len(type_) >= 3:
                    seq_len = type_[2]   
                    if len(value) != seq_len:
                        raise Exception('Wrong lenght on attribute {}.{}'.format(\
                                        self.__class__.__name__, key)
                        )
                if len(type_) >= 2:
                    sequence_inner_type = type_[1]
                    if sequence_inner_type:
                        if isinstance(sequence_inner_type, Sequence):
                            if len(value) != len(sequence_inner_type):
                                raise Exception('Wrong lenght on attribute {}.{}'.format(\
                                                self.__class__.__name__, key)
                                )    
                            value = [sequence_inner_type[i](val) for i, val in enumerate(value)]    
                        else:    
                            value = [sequence_inner_type(val) for val in value]              
                type_ = type_[0]
                value = type_(value)
                     
        # Special treatment for numpy arrays. No events are generated.
        elif type_ == np.ndarray:
            value = np.asarray(value)
            self.__dict__[key] = value
            return
                     
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


    @property
    def uid(self):
        """
        """
        return self.tid, self.oid
    
    @uid.setter
    def uid(self, value):
        raise Exception('Object uid cannot be setted.')

    @uid.deleter
    def uid(self):
        raise Exception('Object uid cannot be deleted.')
     
    def _get_pubsub_uid(self):
        return pubsub.uid_to_pubuid(self.uid)         
        
    # TODO: get_manager_class ou get_manager_class
    def get_manager_class(self):
        """
        """
        app = wx.App.Get()
        return app.get_manager_class(self.tid)
    
    
    #TODO: Verificar se deve incluir a funcao get_manager()  

         
    # TODO: rever este nome
    def set_value_from_event(self, key, value):
        self._processing_value_from_event = True
        try:
            self._do_set(key, value)
        except: 
            raise
        finally:    
            self._processing_value_from_event = False   
            

    # TODO: Aqui serah pesquisado os atributos atraves dos subniveis...
    def find_attribute(self, key):
        """
        Find a Gripy attribute inside _ATTRIBUTES structure.
        """
        return self._ATTRIBUTES.get(key, None)
            

    def get_state(self):
        #print('\nGripyObject.get_state:', self.uid, self._ATTRIBUTES.keys())
        state = OrderedDict()
        for attr_name in self._ATTRIBUTES.keys():
            #print(attr_name, self[attr_name])
            state[attr_name] = self[attr_name]    
        return state  


    @classmethod
    def _get_tid_friendly_name(cls):
        """In general, classes tids are not adequated to be shown as a
        label. If class _TID_FRIENDLY_NAME is provided,
        it will be used by TreeController as tid node label.
        """
        tid_label = cls._TID_FRIENDLY_NAME
        if tid_label is None:
            # If _TID_FRIENDLY_NAME is not found, it will
            # be None because super class OMBaseObject stats it.
            tid_label = cls.tid
        return tid_label
    
    
    