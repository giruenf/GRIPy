# -*- coding: utf-8 -*-

import types

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject
from classes.ui import UIViewObject 
from app import log


class MenuItemController(UIControllerObject):
    tid = 'menu_item_controller'
    
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
        'kind': {'default_value': wx.ITEM_NORMAL, 
                 'type': int
        },
        'callback': {'default_value': None, 
                     'type': types.FunctionType
                     
        }
    }
        
    def __init__(self, **state):
        super().__init__(**state)

    def PostInit(self):
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self.uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        parent_controller.insert_menu_item(self)
        
    def PreRemove(self):
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self.uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        parent_controller.remove_menu_item(self)

       
class MenuItemView(UIViewObject, wx.MenuItem):
    tid = 'menu_item_view'
     
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if controller.id == wx.ID_ANY: 
            controller.id = _UIM.new_wx_id()
        try:
            wx.MenuItem.__init__(self, None, controller.id, controller.label, 
                  controller.help, controller.kind
            )
        except Exception as e:
            print (e)
            raise

    def PostInit(self):
        log.debug('{}.PostInit started'.format(self.name))
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        if controller.pos == -1:
            # Appending - Not needed to declare pos
            controller.pos = parent_controller.view.GetMenuItemCount()
        if controller.pos >  parent_controller.view.GetMenuItemCount():
            # If pos was setted out of range for inserting in parent Menu
            msg = 'Invalid menu position for MenuItem with text={}. Position will be setting to {}'.format(controller.label, parent_controller.view.GetMenuItemCount())
            log.warning(msg)
            controller.pos = parent_controller.view.GetMenuItemCount()   
        log.debug('{}.PostInit ended'.format(self.name))    


            