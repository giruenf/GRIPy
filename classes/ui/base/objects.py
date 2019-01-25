# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 20:43:24 2018

@author: Adriano
"""


from types import MethodType

import wx

import app
from app import log
from classes.base import GripyObject
from classes.om import ObjectManager
#from classes.ui import UIManager


class UIBaseObject(GripyObject):
    """
    UIBaseObject é usado para separar as classes de UI das demais. Assim sendo,
    todas as classes de interface devem herdar, direta ou indiretamente, desta.
    """
    tid = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
      
    def PostInit(self):
        """To be overrriden"""
        pass

    def PreDelete(self):
        """To be overrriden"""
        pass

    # TODO: rever isso
    def _auto_removal(self):
        print ('_auto_removal:', self.uid)
        try:
            if isinstance(self, UIControllerObject):
                uid = self.uid
            else:
                uid = self._controller_uid
            UIM_class = self._get_manager_class()
            UIM = UIM_class()   
            wx.CallAfter(UIM.remove, uid)
            print ('wx.CallAfter(UIM.remove, {})'.format(uid))
        except Exception as e:
            print ('ERROR: _auto_removal ', e)
            raise


###############################################################################
###############################################################################
                                 

class UIControllerObject(UIBaseObject):
    """
    The base class for all Controller classes (MVC software architectural 
    pattern).
        
    """
    tid = None
    # TODO: verificar se vale a pena manter esses singletons
    _singleton = False
    _singleton_per_parent = False
       
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.view = None 
        self._attached_to = None
   
    
    def __getattribute__(self, key):
        """
        """
        #TODO: This Method do the function Delegation to View class
        try:
            return GripyObject.__getattribute__(self, key)
        except AttributeError:
            try:
                # Method Delegation to View class
                return GripyObject.__getattribute__(self.view, key)
            except:
                pass
            raise 

    
    def _check_OM_removals(self, objuid, topic=app.pubsub.AUTO_TOPIC):
        #key = topic.getName().split('.')[2]
        
        if objuid != self._attached_to:
            return
        
        print ('Achou! _check_OM_removals:', objuid, self.uid)
        #self.detach()
        self._auto_removal()
                  
        #topic = 'change.' + key
        #self.send_message(topic, old_value=old_value, new_value=new_value)
        
        
    
    def attach(self, OM_objuid):
        """Attaches this object to a ObjectManager object.
        
        Example: 
            self.attach(('log', 1))
            OM.remove(('log', 1))     -> self will be removed by UIManager 
        """
        print ('ATTACHING...')       
        #obj = OM.get(OM_objuid)
        try:
            OM = ObjectManager()
            # Is OM_objuid valid?
            obj = OM.get(OM_objuid)
            if obj:
                OM.subscribe(self._check_OM_removals, 'pre_remove')
                self._attached_to = obj.uid
                print ('{} IS NOW ATTACHED TO {} \n'.format(self.uid, self._attached_to))
        except Exception as e:
            print ('ERROR WHILE ATTACHING:', e)
            #raise
            #pass
           
            
    def detach(self):
        """Detach a object vinculated to a ObjectManager object 
        by attach function.
        
        Called automatic from UIManager.remove function.
        """
        if self._attached_to is None:
            return
        print ('DETACHING...')
        try:
            OM = ObjectManager()
            OM.unsubscribe(self._check_OM_removals, 'pre_remove')
            print ('DETACHED {} FROM {}! \n'.format(self.uid, self._attached_to))
            self._attached_to = None
        except Exception as e:
            print ('ERROR WHILE DETACHING:', e) 
            #raise
            #pass    


    def _create_view(self, **base_state): 
        # TODO:  ou seria GRIPy MC-V pattern, abaixo?
        """Function to create view objects (MVC pattern)."""
        UIM_class = self._get_manager_class()
        UIM = UIM_class()         
        view_class = UIM.get_view_class(self.tid)
        
        # Then, create view object   
        if view_class is not None:     
            try:
                self.view = view_class(self.uid)
            except Exception as e:
                msg = 'ERROR on creating MVC view {} object: {}'.format(view_class.__name__, e)
                log.exception(msg)
                print ('\n', msg, view_class, '\n')
                raise e             
        else:
            self.view = None  
    
    
    def _PostInit(self):
        """Redirects post init call made by UIManager.create to model, 
        view and controller objects.
        """

        try:    
            if self.view:        
                self.view.PostInit()
        except Exception as e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.view.__class__.__name__, e)
            log.exception(msg)
            print ('\n' + msg)
            raise
        try:                
            self.PostInit()    
        except Exception as e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.__class__.__name__, e)
            log.exception(msg)
            print ('\n', msg)
            raise
        
    '''
    def attach(self, OM_objuid):
        """Attaches this object to a ObjectManager object.
        
        Example: 
            self.attach(('log', 1))
            OM.remove(('log', 1))     -> self will be removed by UIManager 
        """
        
        print ('ATTACHING...')
        
        OM = ObjectManager()
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.subscribe(self._call_self_remove, 'pre_remove')
            #OM.subscribe(self._call_self_remove, 'pre_remove')
            print ('ATTACHED! \n')
        except Exception as e:
            print ('ERROR WHILE ATTACHING:', e)
            #raise
            #pass
           
    def detach(self, OM_objuid):
        """Detach a object vinculated to a ObjectManager object 
        by attach function.
        """
        print ('DETACHING...')
        OM = ObjectManager()
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.unsubscribe(self._call_self_remove, 'pre_remove')     
            print ('DETACHED! \n')
        except Exception as e:
            print ('ERROR WHILE DETACHING:', e)
            
            #raise
            #pass
    '''
    
        
    def get_state(self):
        """Returns MVC triad state.
        
        In general, object states are used add persistence to a object or to
        make an object clone.
        """
        return self._getstate()
        """
        UIM = UIManager()
        children = UIM.list(parentuidfilter=self.uid)
        if children:
            state['children'] = []
            for child in children:
                state['children'].append(child.get_state())
        return self.tid, state
        """
    
    """  
    # TODO: ver se deve-se manter o tid na chamada abaixo (@staticmethod)
    @staticmethod    
    def load_state(state, tid, parentuid=None):
        children = state.pop('children', None)
        UIM = UIManager()
        obj = UIM.create(tid, parentuid, **state)
        if children:
            for child_tid, child_state in children:
                UIControllerObject.load_state(child_state, child_tid, obj.uid)
        return obj
    """
    


class UIViewObject(UIBaseObject):
    """
    The base class for all View classes (MVC software architectural pattern).
        
    """
    tid = None
    _READ_ONLY = ['_controller_uid']
    
    def __init__(self, controller_uid):
        super().__init__()
        self._controller_uid = controller_uid        
        # We are considering that only Controller class objects 
        # can create View class objects. Then, we must verify it      
        UIM_class = self._get_manager_class()
        UIM = UIM_class()
        view_class = UIM.get_view_class(controller_uid[0])
        if self.__class__ != view_class:
            msg = 'Error! Only the controller can create the view.'
            log.exception(msg)
            raise Exception(msg)       


    def _get_wx_parent(self, *args, **kwargs):
        """
        Returns wx.Object parent necessary to child object creation.
        This way was chosen because UIViewObjects creation are segmentated
        between __init__ and PostInit methods.
        """
        raise NotImplementedError('Must be implemented by subclass.')
        
        
        