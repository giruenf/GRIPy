# -*- coding: utf-8 -*-

"""

"""

from collections import OrderedDict

import wx

from app import log


class GripyMeta(type):
    
    def __new__(cls, clsname, superclasses, attributedict):
        """Function reponsible for creating classes.
        
        In general every Gripy class is created on application startup.
        This method adjust attributes heritance, for example combining
        """
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
        """ 
        """
        obj = super().__call__(*args, **kwargs)
        obj.__initialised = True 
        log.debug('Successfully created object from class: {}.'.format(obj.__class__))
        return obj


class GripyWxMeta(GripyMeta, wx.siplib.wrappertype):
    pass


class GripyManagerMeta(type):
    pass
    #def __new__(cls, clsname, superclasses, attributedict):
    #    return super().__new__(cls, clsname, superclasses, attributedict)     
    
    