# -*- coding: utf-8 -*-

import weakref

#import wx

import app
from app.pubsub import PublisherMixin
from app import log



"""
Parent class for Managers
"""
class Manager(PublisherMixin):

    def __init__(self):
        
        
        caller_info = app.app_utils.get_caller_info()
        
        '''
        print('\n')
        for i in range(len(caller_info)):
            ci = caller_info[i]
            print (i)
            print ('module:', ci.module)
            print ('obj:', ci.obj)
            print ('function_name:', ci.function_name)
            print ('filename:', ci.filename)
            print ('lineno:', ci.lineno)
            print ('traceback:', ci.traceback)
            print()
        
        '''
        '''
        owner = caller_info[1][1]

        if not owner:
            msg = 'ERROR sinistro: ' + str(owner)
            #print ('\n\n\n', msg, caller_info)
            raise Exception(msg)

        # TODO: Armengue feito para as funcoes dos menus.. tentar corrigir isso
        if not owner:
            owner = app.gripy_app.GripyApp.Get()
        try:
            owner_name = owner.uid
        except AttributeError:
            owner_name = owner.__class__.__name__
        msg = 'A new instance of ' + self.__class__.__name__ + \
                                ' was solicited by {}'.format(owner_name)
        log.debug(msg)       
        self._ownerref = weakref.ref(owner)
        '''