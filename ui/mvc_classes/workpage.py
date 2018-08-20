# -*- coding: utf-8 -*-

import wx

from ui.uimanager import UIManager
from ui.uimanager import UIControllerBase 
from ui.uimanager import UIModelBase 
from ui.uimanager import UIViewBase 
from  ui import Interface

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
        },
        'float_mode': {
                'default_value': False, 
                'type': bool                
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
        #
        #
        #parent_view = parent_controller.view
        parent_view = parent_controller.view.main_area_panel

        wx.Panel.__init__(self, parent_view)
        self.SetBackgroundColour('green')

        #
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
#        self.set_own_name()
   

    def PreDelete(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        if controller.model.float_mode:
            #raise Exception('FLOAT MODE')
            print ('\n\nTRATAR FLOAT MODE')
            return
        mwc = Interface.get_main_window_controller()
        mwc.remove_notebook_page(self)
        
    """    
    def remove_notebook_page(self, page_window):
        # Remove page without destruct
        page_idx = self._notebook.GetPageIndex(page_window)
        ret_val =  self._notebook.RemovePage(page_idx)
        # Line below must exist in order to prevent SystemError
        wx.CallAfter(self.adjust_background_panel)
        return ret_val        
    """  
        
    
    
                                     
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
        print ('\n_set_float_mode:', new_value, old_value)
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_uid = UIM._getparentuid(controller.uid)

        if new_value:
            controller.unsubscribe(self._set_title, 'change.title')            
            controller.unsubscribe(self._set_pos, 'change.pos')
            fc = UIM.create('frame_controller', parent_uid)
            UIM.reparent(self._controller_uid, fc.uid)
            fc.view.Show()
        else:
            mwc_uid = UIM._getparentuid(parent_uid)
            mwc = UIM.get(mwc_uid)
            UIM.reparent(self._controller_uid, mwc.uid)
            print ('UIM.remove:', parent_uid)
            ret_val = UIM.remove(parent_uid)
            print ('UIM.remove:', ret_val)
            controller.subscribe(self._set_title, 'change.title')            
            controller.subscribe(self._set_pos, 'change.pos')



    def reparent(self, old_parent_uid, new_parent_uid):
        UIM = UIManager()
        old_parent_controller = UIM.get(old_parent_uid)
        new_parent_controller = UIM.get(new_parent_uid)
#        parent_wx = self.GetParent()
        
        print ('Reparent:', old_parent_uid, new_parent_uid)
        
        if old_parent_controller.tid == 'main_window_controller':
            try:
                ret_val = old_parent_controller.remove_notebook_page(self)     
                print (ret_val)
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
            print (ret_val)        
        
        
        