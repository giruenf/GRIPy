# -*- coding: utf-8 -*-

import wx

from ui.uimanager import UIManager
from ui.uimanager import UIControllerBase 
from ui.uimanager import UIModelBase 
from ui.uimanager import UIViewBase 

from app import log


class WorkPageController(UIControllerBase):
    tid = 'workpage_controller'
    
    def __init__(self):
        super().__init__()
        
       
class WorkPageModel(UIModelBase):
    tid = 'workpage_model'

    _ATTRIBUTES = {
        'pos': {
                'default_value': -1, 
                'type': int
        },
        'title': {
                'default_value': wx.EmptyString, 
                'type': str
        }          
    }  
        
    def __init__(self, controller_uid, **base_state):      
        super().__init__(controller_uid, **base_state) 
    
    
    
class WorkPage(UIViewBase, wx.Panel):  
    tid = 'workpage'
       
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(controller_uid)
        parent_uid = UIM._getparentuid(controller.uid)
        parent_controller = UIM.get(parent_uid)
        wx.Panel.__init__(self, parent_controller.view)
        #
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.note.GetPageCount()  
         
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')

        controller.subscribe(self._set_title, 'change.title')            
        controller.subscribe(self._set_pos, 'change.pos')               
        self.set_own_name()
        
                                     
    def _set_title(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        main_window_uid = UIM._getparentuid(controller.uid)
        main_window = UIM.get(main_window_uid)
        my_pos = main_window.view.get_notebook_page_index(self)
        controller.model.set_value_from_event('pos', my_pos)
        main_window.view.set_notebook_page_text(controller.model.pos, 
                                                      new_value
        )

    def _set_pos(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        main_window_uid = UIM._getparentuid(controller.uid)
        main_window = UIM.get(main_window_uid)     
        # Check event
        if new_value < 0 or new_value > main_window.view.note.GetPageCount()-1:
            # Undo wrong event
            controller.model.set_value_from_event('pos', old_value)
            return 
        # Broadcasting position change to other pages 
        for mw_child in UIM.list(tidfilter='workpage_controller', 
                                            parentuidfilter=main_window_uid):
            pos = main_window.view.get_notebook_page_index(mw_child.view)
            mw_child.model.set_value_from_event('pos', pos)
        


        