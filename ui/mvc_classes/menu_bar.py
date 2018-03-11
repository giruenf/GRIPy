# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from App import log


class MenuBarController(UIControllerBase):
    tid = 'menubar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(MenuBarController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))
        

class MenuBarModel(UIModelBase):
    tid = 'menubar_model'
    
    _ATTRIBUTES = {}
        
    def __init__(self, controller_uid, **base_state): 
        super(MenuBarModel, self).__init__(controller_uid, **base_state)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Model object from class: {}.'.format(class_full_name))

    
class MenuBarView(UIViewBase, wx.MenuBar):
    tid = 'menubar_view'
 
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        wx.MenuBar.__init__(self)
        UIM = UIManager()
        parent_uid = UIM._getparentuid(controller_uid)
        parent = UIM.get(parent_uid)
        parent.view.SetMenuBar(self)
        
        #class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        #log.debug('Successfully created View object from class: {}.'.format(class_full_name))
           