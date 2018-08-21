# -*- coding: utf-8 -*-
"""
Base Objects
=======

This file defines the base classes for all GRIPy objects.
"""

import os
import types
from collections import OrderedDict
from collections import Sequence
import wx

import app
import app.pubsub as pubsub
from app import log

#
# Based on https://www.python-course.eu/python3_metaclasses.php
#      and https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/
#
class GripyMeta(type):
    
    def __new__(cls, clsname, superclasses, attributedict):
        if '_ATTRIBUTES' not in attributedict:
            attributedict['_ATTRIBUTES'] = OrderedDict()
        if '_BYPASSES_KEYS' not in attributedict:
            attributedict['_BYPASSES_KEYS'] = []
        if '_IMMUTABLES_KEYS' not in attributedict:
            attributedict['_IMMUTABLES_KEYS'] = []            
        ret_class = super().__new__(cls, clsname, superclasses, attributedict)
        for superclass in superclasses:
            if '_ATTRIBUTES' in superclass.__dict__:
                for key, value in superclass.__dict__['_ATTRIBUTES'].items():
                    if key not in ret_class.__dict__['_ATTRIBUTES']:
                        ret_class.__dict__['_ATTRIBUTES'][key] = value
            if '_BYPASSES_KEYS' in superclass.__dict__:
                for item in superclass.__dict__['_BYPASSES_KEYS']:
                    if item not in ret_class.__dict__['_BYPASSES_KEYS']:
                        ret_class.__dict__['_BYPASSES_KEYS'].append(item)
            if '_IMMUTABLES_KEYS' in superclass.__dict__:
                for item in superclass.__dict__['_IMMUTABLES_KEYS']:
                    if item not in ret_class.__dict__['_IMMUTABLES_KEYS']:
                        ret_class.__dict__['_IMMUTABLES_KEYS'].append(item)                      
        log.debug('Successfully created class: {}.'.format(clsname))                         
        return ret_class


    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj.__initialised = True 
        log.debug('Successfully created object from class: {}.'.format(obj.__class__))
        return obj


class GripyWxMeta(GripyMeta, wx.siplib.wrappertype):
    pass

  

#
# Opcao com metaclass:    
#   class GripyObject(PublisherMixin, metaclass=GripyWxMeta):
# Opcao sem metaclass:    
#   class GripyObject(PublisherMixin): 
#
# Usando metaclass é possível instanciar um GripyObject 
# em uma forma diferenciada. 
#    
#    

class GripyObject(pubsub.PublisherMixin, metaclass=GripyWxMeta):  
    tid = None
    # _BYPASSES_KEYS bypasses the checking made in __setattr__ or __setitem__
    _BYPASSES_KEYS = ['_processing_value_from_event']
    # _IMMUTABLES_KEYS must be setted only during __init__. 
    # They cannot be deleted.
    _IMMUTABLES_KEYS = ['oid']
    #
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['name'] = {
        'default_value': wx.EmptyString,
        'type': str        
    }   
    
    def __init__(self, **data): 
        _manager_class = self._get_manager_class()
        _manager = _manager_class()
        self.oid = _manager._getnewobjectid(self.tid)
        self._processing_value_from_event = True
        self.name = '{}.{}'.format(*self.uid)
        for attr_name, attr_props in self._ATTRIBUTES.items():
            self[attr_name] = data.get(attr_name, 
                                            attr_props.get('default_value')
            )    
        self._processing_value_from_event = False
       
    def __str__(self):
        return '{}.{}'.format(*self.uid)

    def _get_manager_class(self):
        raise NotImplementedError()
        
    def get_publisher_name(self):
        return pubsub.uid_to_pubuid(self.uid)    
        

    # TODO: rewrite it from UIBase
    """
    def check_creator(self):
        # Only UIManager can create objects. Checking it!   
        return True
        #
        callers_stack = app.app_utils.get_callers_stack()
        ok = False
        for idx, ci in enumerate(callers_stack):
            if (isinstance(ci.object_, UIManager) and \
                    ci.function_name == 'create' and \
                    isinstance(callers_stack[idx-1].object_, UIControllerBase)): 
                ok = True
                break     
        if not ok:
            msg = '{} objects must be created only by UIManager.'.format(self.__class__.__name__)
            log.exception(msg)
            raise Exception(msg)    
    """  
 
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
                value = app.app_utils.get_function_from_string(value)
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
#        print ('\n_getstate:', self.uid)
        state = OrderedDict()  
        for attr_name in self._ATTRIBUTES.keys():
#            print (attr_name)
            state[attr_name] = self[attr_name]
            
#        print ('\n\n\n\nstate:', state)    
        return state            


    """ 
    def _loadstate(self, **state):
        if not state:
            return
        log.debug('Loading {} state...'.format(self.__class__.__name__))
        for key, value in state.items():
            if key not in self._BYPASSES_KEYS:     
                try:
                    self[key] = value  
                except AttributeError:
                    msg = 'ERROR setting self[{}] = {}. Value type: {}'.format(str(key), \
                        str(value), str(type(value))
                    )
                    log.exception(msg)
            else:
                msg = '    {} cannot be loaded. [key in _BYPASSES_KEYS]'.format(key)
                log.error(msg)
        log.debug('{} state has loaded.'.format(self.__class__.__name__))


    """

    '''
    # TODO: Rever docs
    def _getstate(self):
        """
        Return the state of the object.
        
        This method is used by `ObjectManager` method `save`. It must return a
        dictionary containing all necessary data to reconstruct the object with
        a simple call to its constructor. For example::
        
            obj1 = SubClassOfGenericObject(someparameters)
            # do some changes to 'obj1'
            state = obj1._getstate()
            obj2 = SubClassOfGenericObject(**state)
            # now 'obj2' must behave the same as 'obj1'
        
        Returns
        -------
        dict
            The state necessary to reconstruct the object with a call to its
            constructor.
        
        Notes
        -----
        Not all of the data needs to be returned in this method. But the object
        recovered from the state must behave the same way as the original
        object.
        """
        return {}    
    '''


class GripyManagerMeta(type):
    
    def __new__(cls, clsname, superclasses, attributedict):
        return super().__new__(cls, clsname, superclasses, attributedict)                   



class GripyManager(pubsub.PublisherMixin, metaclass=GripyManagerMeta):  
    """
    Parent class for Managers
    """

    def __init__(self):
        #super().__init__()
        self._ownerref = None
        
        return
    
        print ('\nGripyManager.init')
     
        '''
        print ('\nGripyManager.init')
        
        #owner = app.gripy_app.GripyApp.Get()
        
        
        owner = wx.App.Get() 
        if owner is not None:
            print ('OK')
        else:
            print ('DEU RUIM')
        self._ownerref = weakref.ref(owner)
        '''
        
        """
        try:
            callers_stack = app.app_utils.get_callers_stack()     
        except Exception as e:
            print (e)
            raise
            
        """    

        '''
        owner = wx.App.Get() 
        if owner is not None:
            print ('OK')
        else:
            print ('DEU RUIM')
        self._ownerref = weakref.ref(owner)   
        
        '''
        
        
        '''
        for ci in callers_stack:
            print ('\nGripyManager:', ci)
        print ('\n')         
        '''
      
        '''
        
        owner = wx.App.Get() 
        if owner is not None:
            print ('OK')
        else:
            print ('DEU RUIM')
        self._ownerref = weakref.ref(owner)        
        
        '''
        
        owner = callers_stack[2].object_
        
        #print ('owner:', owner, type(owner))
        
        
        
        if owner is None: 
            #print ('NOT OWNER')
            full_filename = os.path.normpath(callers_stack[2].filename)
            function_name = callers_stack[2].function_name
            
            
            '''
            function_ = get_function_from_filename(fi.filename, fi.function)
            if function_:
                module_ = function_.__module__  
            '''
            
            
            function_ = app.app_utils.get_function_from_filename(full_filename, function_name)
            if function_:
                #owner = function_
                # TODO: Armengue feito para as funcoes dos menus.. tentar corrigir isso
                owner = app.gripy_app.GripyApp.Get()
            else:    
                msg = 'ERROR: ' + str(owner)
                print (msg)
                raise Exception(msg)
        
        """
            
        # TODO: Armengue feito para as funcoes dos menus.. tentar corrigir isso
        #if not owner:
        #    owner = app.gripy_app.GripyApp.Get()
        
        """
        try:
            #print ('A')
            owner_name = owner.uid
        except AttributeError:
            #print ('B')
            owner_name = owner.__class__.__name__
        msg = 'A new instance of ' + self.__class__.__name__ + \
                                ' was solicited by {}'.format(owner_name)
                                
        log.debug(msg)       
        
        
        #self._ownerref = weakref.ref(owner)
        self._ownerref = None
        
        '''
        owner = wx.App.Get() 
        if owner is not None:
            print ('OK')
        else:
            print ('DEU RUIM')
        self._ownerref = weakref.ref(owner)
        
        print ('GripyManager.init ended')
        
        '''


    def get_publisher_name(self):
        return self.__class__.__name__
   
        
    def do_query(self, tid, parent_uid=None, *args, **kwargs):
        try:
            objects = self.list(tid, parent_uid)
            if not objects: return None  
            comparators = self._create_comparators(*args)  
            ret_list = []
            for obj in objects:
                ok = True
                for (key, operator, value) in comparators:
                    ok = False
                   
                    
                    attr = obj._ATTRIBUTES.get(key)
                    # TODO: acertar isso, pois a linha de cima deve servir de atalho
                    # para obj.model de forma transparente
                    obj_model = False
                    if attr is None:
                        attr = obj.model._ATTRIBUTES.get(key)
                        obj_model = True

                    type_ = attr.get('type')
                    value = type_(value)
                    
#                    print ('type_(value)', type_, value)
                    
                    if obj_model:
                        if operator == '>=':
                            ok = obj.model[key] >= value
                        elif operator == '<=':
                            ok = obj.model[key] <= value                  
                        elif operator == '>':
                            ok = obj.model[key] > value
                        elif operator == '<':
                            ok = obj.model[key] < value     
                        elif operator == '!=':
                            ok = obj.model[key] != value
                        elif operator == '=':
                            ok = obj.model[key] == value
                        
                    else:
                        if operator == '>=':
                            ok = obj[key] >= value
                        elif operator == '<=':
                            ok = obj[key] <= value                  
                        elif operator == '>':
                            ok = obj[key] > value
                        elif operator == '<':
                            ok = obj[key] < value     
                        elif operator == '!=':
                            ok = obj[key] != value
                        elif operator == '=':
                            ok = obj[key] == value
                            
#                    print ('{} ok: {}'.format(obj.name, ok))
                    
                    if not ok:
                        break
                if ok:
                    ret_list.append(obj)
            if kwargs:
                orderby = kwargs.get('orderby')
                if orderby and len(ret_list) >= 2:
                    aux_list = []
                    while len(ret_list) > 0:
                        minor_idx = 0
                        for idx, obj in enumerate(ret_list):
                            if obj.model[orderby] < ret_list[minor_idx].model[orderby]:
                                minor_idx = idx
                        aux_list.append(ret_list[minor_idx])
                        del ret_list[minor_idx]
                    ret_list = aux_list
                reverse = kwargs.get('reverse')
                if reverse:
                    ret_list.reverse()
#            print ('\nret_list:', ret_list)                         
            return ret_list
        except Exception as e:
            print ('\nERROR in {}.do_query({}, {}, {}, {})'.format( \
                   self.__class__.__name__,tid, parent_uid, args, kwargs)
            )
            raise
            
            
    def _create_comparators(self, *args):
        operators = ['>=', '<=', '>', '<', '!=', '=']
        ret_list = []
        for arg in args:
            operator = None
            for oper in operators:
                if oper in arg:
                    operator = oper
                    break
            if not operator:
                raise ValueError('Operator not found. Valid operators are: {}'\
                                 .format(operators)
                )
            ret_list.append((arg.split(operator)[0], operator, 
                             arg.split(operator)[1])
            )
        return ret_list          
        
    
    
    
