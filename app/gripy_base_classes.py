# -*- coding: utf-8 -*-
"""
Base Objects
=======

This file defines the base classes for all GRIPy objects.
"""

import os
#import weakref

import wx

import app
from app.pubsub import PublisherMixin
from app import log


class GripyMeta(type):
    
    def __new__(cls, clsname, superclasses, attributedict):
#        print("clsname: ", clsname)
#        print("superclasses: ", superclasses)
#        print("attributedict: ", attributedict)
        return type.__new__(cls, clsname, superclasses, attributedict)


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
#class GripyObject(PublisherMixin, metaclass=GripyWxMeta):
    
    
class GripyObject(PublisherMixin):    
    """
    The simplest object that can be managed by `ObjectManager`.
    
    Attributes
    ----------
    tid : string
        A identificator for the type. Subclasses of `GenericObject` must have
        their own unique `tid`.
    oid : int
        A identificator for the object. Objects of the same type cannot have
        the same `oid` (on the other hand, objects from different types might
        share the same `oid`).
    uid : tuple
        A unique identificator for the object. A combination (a tuple) of the
        type identificator (`tid`) and the object identificator (`oid`). No
        object can share the same `uid` with another.
    """
    tid = None

    def __init__(self):
        self._oid = None

    def __str__(self):
        return str(self.uid)        

    
    @property
    def name(self): 
        return '{}.{}'.format(*self.uid)
   
    @name.setter
    def name(self, value):
        msg = "Cannot set GripyObject object name."
        raise TypeError(msg)
    
    @name.deleter
    def name(self):
        msg = "Cannot delete GRIPy object name."
        raise TypeError(msg)  
        

    @property
    def oid(self):
        return self._oid

    @oid.setter
    def oid(self, _oid):
        if self._oid is None:
            self._oid = _oid
        else:
            msg = "Cannot change object id."
            raise TypeError(msg)

    @oid.deleter
    def oid(self):
        msg = "Cannot delete object id."
        raise TypeError(msg)

    @property
    def uid(self):
        return self.tid, self.oid
    
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



class GripyManager(PublisherMixin):
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