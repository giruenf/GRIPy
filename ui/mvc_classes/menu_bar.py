# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIModelObject 
from classes.ui import UIViewObject 
from app import log


class MenuBarController(UIControllerObject):
    tid = 'menubar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(MenuBarController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))
        

class MenuBarModel(UIModelObject):
    tid = 'menubar_model'

    def __init__(self, controller_uid, **base_state): 
        super(MenuBarModel, self).__init__(controller_uid, **base_state)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Model object from class: {}.'.format(class_full_name))

    
class MenuBarView(UIViewObject, wx.MenuBar):
    tid = 'menubar_view'
 
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        wx.MenuBar.__init__(self)
        #
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(controller_uid)
        parent_controller = UIM.get(parent_controller_uid)
        wx_parent = parent_controller._get_wx_parent()
        wx_parent.SetMenuBar(self)
        

        #class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        #log.debug('Successfully created View object from class: {}.'.format(class_full_name))
           