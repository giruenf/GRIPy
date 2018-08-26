# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 20:27:47 2018

@author: Adriano
"""

import os

from app import app_utils
from app import pubsub
from classes.base.metaclasses import GripyManagerMeta
from app import log


class GripyManager(pubsub.PublisherMixin, metaclass=GripyManagerMeta):  
    """
    Parent class for Managers
    """

    _LOADING_STATE = False
    

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
            
            
            function_ = app_utils.get_function_from_filename(full_filename, function_name)
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

    def is_loading_state(self):
        return self.__class__._LOADING_STATE 

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
        
    
    
    
