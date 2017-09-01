# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from UI.uimanager import UI_MODEL_ATTR_CLASS
from menu_bar import MenuBarController
from App import log



class MenuController(UIControllerBase):
    tid = 'menu_controller'

    def __init__(self):
        super(MenuController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))


    def insert_menu_item(self, menu_item_ctrl):
        self.view._InsertItem(menu_item_ctrl.model.pos, menu_item_ctrl.view)
        if menu_item_ctrl.model.callback:
            UIM = UIManager()
            root_ctrl = UIM.get_root_controller()
            root_ctrl.view.Bind(wx.EVT_MENU, menu_item_ctrl.model.callback, 
                                id=menu_item_ctrl.model.id
            )        

    def remove_menu_item(self, menu_item_ctrl):
        if menu_item_ctrl.model.callback:
            UIM = UIManager()
            root_ctrl = UIM.get_root_controller()
            root_ctrl.view.Unbind(wx.EVT_MENU, id=menu_item_ctrl.model.id)
        self.view._RemoveItem(menu_item_ctrl.view)
        
        
class MenuModel(UIModelBase):
    tid = 'menu_model'

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
    }    
    
    def __init__(self, controller_uid, **base_state):   
        super(MenuModel, self).__init__(controller_uid, **base_state)   
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Model object from class: {}.'.format(class_full_name))
        
          
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
        log.debug('Successfully created View object from class: {}.'.format(class_full_name))        


    def PostInit(self):
        log.debug('{}.PostInit started'.format(self.name))
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
                log.warning(msg)
                controller.model.pos = parent_controller.view.GetMenuCount() 

            parent_controller.view.Insert(controller.model.pos, 
                                              controller.model.id, 
                                              controller.model.label, 
                                              self, 
                                              controller.model.help
            )

        elif isinstance(parent_controller, MenuBarController):
            if controller.model.pos == -1:
                # Appending - Not needed to declare pos
                controller.model.pos = parent_controller.view.GetMenuCount()
            if controller.model.pos >  parent_controller.view.GetMenuCount():
                # If pos was setted out of range for inserting in parent Menu
                msg = 'Invalid position for Menu with label={}. Position will be setting to {}'.format(controller.model.label, parent_controller.view.GetMenuCount())
                log.warning(msg)
                controller.model.pos = parent_controller.view.GetMenuCount()
            ret_val = parent_controller.view.Insert(controller.model.pos, self, controller.model.label)
            if not ret_val:
                raise Exception()
        else:
            raise Exception()  
        log.debug('{}.PostInit ended'.format(self.name))   


    def _InsertItem(self, pos, menu_item_view):
        self.Insert(pos, menu_item_view)

    def _RemoveItem(self, menu_item_view):   
        self.RemoveItem(menu_item_view)       
        
        