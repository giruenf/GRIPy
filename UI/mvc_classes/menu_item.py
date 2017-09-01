# -*- coding: utf-8 -*-
import types
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from UI.uimanager import UI_MODEL_ATTR_CLASS
from App import log


class MenuItemController(UIControllerBase):
    tid = 'menu_item_controller'

    def __init__(self):
        super(MenuItemController, self).__init__()

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


        
class MenuItemModel(UIModelBase):
    tid = 'menu_item_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int,
                'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'id': {'default_value': wx.ID_ANY, 
               'type': int,
               'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'label': {'default_value': wx.EmptyString, 
                  'type': unicode,
                  'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'help': {'default_value': wx.EmptyString, 
                 'type': unicode,
                 'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'kind': {'default_value': wx.ITEM_NORMAL, 
                 'type': int,
                 'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'callback': {'default_value': None, 
                     'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION,
                     'type': types.FunctionType
        }
    }    
    
    
    def __init__(self, controller_uid, **base_state):  
        super(MenuItemModel, self).__init__(controller_uid, **base_state) 
    
            
          
class MenuItemView(UIViewBase, wx.MenuItem):
    tid = 'menu_item_view'
     
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if controller.model.id == wx.ID_ANY: 
            controller.model.id = _UIM.new_wx_id()
        try:
            wx.MenuItem.__init__(self, None, controller.model.id, controller.model.label, 
                  controller.model.help, controller.model.kind
            )
        except Exception, e:
            print e.message
            raise e

    def PostInit(self):
        log.debug('{}.PostInit started'.format(self.name))
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        if controller.model.pos == -1:
            # Appending - Not needed to declare pos
            controller.model.pos = parent_controller.view.GetMenuItemCount()
        if controller.model.pos >  parent_controller.view.GetMenuItemCount():
            # If pos was setted out of range for inserting in parent Menu
            msg = 'Invalid menu position for MenuItem with text={}. Position will be setting to {}'.format(controller.model.label, parent_controller.view.GetMenuItemCount())
            log.warning(msg)
            controller.model.pos = parent_controller.view.GetMenuItemCount()   
        log.debug('{}.PostInit ended'.format(self.name))    


            