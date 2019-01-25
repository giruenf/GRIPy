# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIModelObject 
from classes.ui import UIViewObject 
from ui import Interface

from app import log


class WorkPageController(UIControllerObject):
    tid = 'workpage_controller'
    
    def __init__(self):
        super().__init__()
        
       
class WorkPageModel(UIModelObject):
    tid = 'workpage_model'

    _ATTRIBUTES = {
        'pos': {
                'default_value': -1, 
                'type': int
        },
        'title': {
                'default_value': wx.EmptyString, 
                'type': str
        },
        'float_mode': {
                'default_value': False, 
                'type': bool                
        }          
    }  
        
    def __init__(self, controller_uid, **base_state):      
        super().__init__(controller_uid, **base_state) 
    
    
    
class WorkPage(UIViewObject, wx.Panel):  
    tid = 'workpage'
       
    def __init__(self, controller_uid):
        """
        """
        #
        # Basic WorkPage interface structure
        # ==================================
        #   Top: ToolBar
        #   Center: A (main) panel where the 'things happens' ;-)
        #   Bottom: StatusBar
        #
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(controller_uid)
        parent_uid = UIM._getparentuid(controller.uid)
        parent_controller = UIM.get(parent_uid)
        parent_view = parent_controller.view.main_area_panel
        wx.Panel.__init__(self, parent_view)
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.get_notebook_page_count()      
        # 
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        #
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')
        #    
        controller.subscribe(self._set_title, 'change.title')            
        controller.subscribe(self._set_pos, 'change.pos')
        controller.subscribe(self._set_float_mode, 'change.float_mode')

        # Set notebook page name                
        self._set_own_name()
   

    def PreDelete(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        if controller.model.float_mode:
            raise Exception('TRATAR DELETE ON FLOAT MODE')
        mwc = Interface.get_main_window_controller()
        mwc.remove_notebook_page(self)
        
                              
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
        if new_value < 0 or new_value > main_window.view.get_notebook_page_count()-1:
            # Undo wrong event
            controller.model.set_value_from_event('pos', old_value)
            return 
        # Broadcasting position change to other pages 
        for mw_child in UIM.list(tidfilter='workpage_controller', 
                                            parentuidfilter=main_window_uid):
            pos = main_window.view.get_notebook_page_index(mw_child.view)
            mw_child.model.set_value_from_event('pos', pos)
        
        

    def _set_float_mode(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_uid = UIM._getparentuid(controller.uid)
        if new_value:
            controller.unsubscribe(self._set_title, 'change.title')            
            controller.unsubscribe(self._set_pos, 'change.pos')
            fc = UIM.create('frame_controller', parent_uid, 
                            title=controller.model.title
            )
            UIM.reparent(self._controller_uid, fc.uid)
            fc.view.Show()
        else:
            mwc_uid = UIM._getparentuid(parent_uid)
            mwc = UIM.get(mwc_uid)
            UIM.reparent(self._controller_uid, mwc.uid)
            UIM.remove(parent_uid)
            controller.subscribe(self._set_title, 'change.title')            
            controller.subscribe(self._set_pos, 'change.pos')


    def reparent(self, old_parent_uid, new_parent_uid):
        UIM = UIManager()
        old_parent_controller = UIM.get(old_parent_uid)
        new_parent_controller = UIM.get(new_parent_uid)

        if old_parent_controller.tid == 'main_window_controller':
            try:
                ret_val = old_parent_controller.remove_notebook_page(self)     
                self.Reparent(new_parent_controller.view)
            except Exception as e:
                print ('ERROR:', e)
        else:
            # Then old_parent_controller is a Frame
            self.Reparent(new_parent_controller.view)
            controller = UIM.get(self._controller_uid)
            ret_val = new_parent_controller.insert_notebook_page(
                    controller.model.pos, self, 
                    controller.model.title, True
            )     
        return ret_val          
        
        
        