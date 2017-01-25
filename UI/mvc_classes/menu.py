# -*- coding: utf-8 -*-

import wx
import logging

from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from menu_bar import MenuBarController



class MenuController(UIControllerBase):
    tid = 'menu_controller'

    def __init__(self):
        super(MenuController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created Controller object from class: {}.'.format(class_full_name))

        
class MenuModel(UIModelBase):
    tid = 'menu_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 'type': int},
        'id': {'default_value': wx.ID_ANY, 'type': int},
        'label': {'default_value': wx.EmptyString, 'type': unicode},
        'help': {'default_value': wx.EmptyString, 'type': unicode},  
    }    
    
    def __init__(self, controller_uid, **base_state):   
        super(MenuModel, self).__init__(controller_uid, **base_state)   
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created Model object from class: {}.'.format(class_full_name))
        
          
class MenuView(UIViewBase, wx.Menu):
    tid = 'menu_view'
 
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if controller.model.id == wx.ID_ANY: 
            controller.model.id = _UIM.new_wx_id()
        wx.Menu.__init__(self)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created View object from class: {}.'.format(class_full_name))        


    def PostInit(self):
        logging.debug('{}.PostInit started'.format(self.name))
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        
        if isinstance(parent_controller, MenuController):
            if controller.model.pos == -1:
                # Appending - Not needed to declare pos
                controller.model.pos = parent_controller.view.GetMenuItemCount()
            if controller.model.pos >  parent_controller.view.GetMenuItemCount():
                # If pos was setted out of range for inserting in parent Menu
                msg = 'Invalid position for Menu with label={}. Position will be setting to {}'.format(controller.model.label, parent_controller.view.GetMenuItemCount())
                logging.warning(msg)
                controller.model.pos = parent_controller.view.GetMenuCount()            
            parent_controller.view.InsertMenu(controller.model.pos, controller.model.id, controller.model.label, self, controller.model.help)
        elif isinstance(parent_controller, MenuBarController):
            if controller.model.pos == -1:
                # Appending - Not needed to declare pos
                controller.model.pos = parent_controller.view.GetMenuCount()
            if controller.model.pos >  parent_controller.view.GetMenuCount():
                # If pos was setted out of range for inserting in parent Menu
                msg = 'Invalid position for Menu with label={}. Position will be setting to {}'.format(controller.model.label, parent_controller.view.GetMenuCount())
                logging.warning(msg)
                controller.model.pos = parent_controller.view.GetMenuCount()
            ret_val = parent_controller.view.Insert(controller.model.pos, self, controller.model.label)
            if not ret_val:
                raise Exception()
        else:
            raise Exception()  
        logging.debug('{}.PostInit ended'.format(self.name))   




            