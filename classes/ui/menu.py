# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 
from classes.ui  import MenuBarController
from app import log


class MenuController(UIControllerObject):
    tid = 'menu_controller'
    
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        },
        'id': {'default_value': wx.ID_ANY, 
               'type': int
        },
        'label': {'default_value': wx.EmptyString, 
                  'type': str
        },
        'help': {'default_value': wx.EmptyString, 
                 'type': str
        },  
    }   
        
    def __init__(self, **state):
        super(MenuController, self).__init__(**state)

    def insert_menu_item(self, menu_item_ctrl):
        self.view._InsertItem(menu_item_ctrl.pos, menu_item_ctrl.view)
        if menu_item_ctrl.callback:
            main_window = wx.App.Get().GetTopWindow()
#            UIM = UIManager()
#            root_ctrl = UIM.get_root_controller()
            main_window.Bind(wx.EVT_MENU, menu_item_ctrl.callback, 
                                id=menu_item_ctrl.id
            )        

    def remove_menu_item(self, menu_item_ctrl):
        if menu_item_ctrl.callback:
#            UIM = UIManager()
#            root_ctrl = UIM.get_root_controller()
            main_window = wx.App.Get().GetTopWindow()
            main_window.Unbind(wx.EVT_MENU, id=menu_item_ctrl.id)
        self.view._RemoveItem(menu_item_ctrl.view)
        
              
          
class MenuView(UIViewObject, wx.Menu):
    tid = 'menu_view'
 
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if controller.id == wx.ID_ANY: 
            controller.id = UIM.new_wx_id()
        wx.Menu.__init__(self)

    def PostInit(self):
#        log.debug('{}.PostInit started'.format(self.name))
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        #
        if isinstance(parent_controller, MenuController):
            if controller.pos == -1:
                # Appending - Not needed to declare pos
                controller.pos = parent_controller.view.GetMenuItemCount()
            if controller.pos >  parent_controller.view.GetMenuItemCount():
                # If pos was setted out of range for inserting in parent Menu
                msg = 'Invalid position for Menu with label={}. Position will be setting to {}'.format(controller.label, parent_controller.view.GetMenuItemCount())
                log.warning(msg)
                controller.pos = parent_controller.view.GetMenuCount() 
            parent_controller.view.Insert(controller.pos, 
                                              controller.id, 
                                              controller.label, 
                                              self, 
                                              controller.help
            )
        elif isinstance(parent_controller, MenuBarController):
            if controller.pos == -1:
                # Appending - Not needed to declare pos
                controller.pos = parent_controller.view.GetMenuCount()
            if controller.pos >  parent_controller.view.GetMenuCount():
                # If pos was setted out of range for inserting in parent Menu
                msg = 'Invalid position for Menu with label={}. Position will be setting to {}'.format(controller.label, parent_controller.view.GetMenuCount())
                log.warning(msg)
                controller.pos = parent_controller.view.GetMenuCount()
            ret_val = parent_controller.view.Insert(controller.pos, self, controller.label)
            if not ret_val:
                raise Exception()
        else:
            raise Exception()  
#        log.debug('{}.PostInit ended'.format(self.name))   

    def _InsertItem(self, pos, menu_item_view):
        self.Insert(pos, menu_item_view)

    def _RemoveItem(self, menu_item_view):   
        self.RemoveItem(menu_item_view)       
        
        