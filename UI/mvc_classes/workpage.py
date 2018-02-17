# -*- coding: utf-8 -*-
import wx
#from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from App import log
import wx.aui as aui
from UI.plotstatusbar import PlotStatusBar


class WorkPageController(UIControllerBase):
    tid = 'workpage_controller'
    
    def __init__(self):
        super(WorkPageController, self).__init__()
        
       
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
        super(WorkPageModel, self).__init__(controller_uid, **base_state) 
    
    
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
        self.sizer = wx.BoxSizer(wx.VERTICAL) 
        #
        self.tool_bar = aui.AuiToolBar(self)    # top  
        self.center_panel = wx.Panel(self)      # center
        self.status_bar = PlotStatusBar(self)   # bottom
        #
        self.sizer.Add(self.tool_bar, 0, flag=wx.TOP|wx.EXPAND)
        self.sizer.Add(self.center_panel, 1, flag=wx.EXPAND)        
        self.sizer.Add(self.status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)                         
        self.SetSizer(self.sizer)          
        #
        
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.note.GetPageCount()  
        #controller.model.title = self._FRIENDLY_NAME + \
        #                            ' ['+ str(self._controller_uid[1]+1) + ']'    
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')

        controller.subscribe(self._set_title, 'change.title')            
        controller.subscribe(self._set_pos, 'change.pos')       
        
        #UIM.subscribe(self._post_remove, 'post_remove')
        
        
         
        
    """    
    def PostInit(self): 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_uid = UIM._getparentuid(controller.uid)
        parent_controller = UIM.get(parent_uid)
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.note.GetPageCount()  
        #controller.model.title = self._FRIENDLY_NAME + \
        #                            ' ['+ str(self._controller_uid[1]+1) + ']'    
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')
    """        


    def PreDelete(self):
        try:
            self.sizer.Remove(0)
            del self.tool_bar
        except Exception, e:
            msg = 'PreDelete ' + self.__class__.name + ' ended with error: ' + e.args 
            print msg       
        
            
            
    def _set_title(self, new_value, old_value):
        #print '_reset_title:', new_value, old_value
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
        #print '_reset_pos:', new_value, old_value
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        main_window_uid = UIM._getparentuid(controller.uid)
        main_window = UIM.get(main_window_uid)     
        # Check event
        if new_value < 0 or new_value > main_window.view.note.GetPageCount()-1:
            # Undo wrong event
            controller.model.set_value_from_event('pos', old_value)
            return 
        # Do it
        #print 'RemovePage:', main_window.view.note.RemovePage(old_value)
        #print 'InsertPage:', main_window.insert_notebook_page(new_value, 
        #                                self, controller.model.title, True
        #)
        # Broadcasting position change to other pages 
        for mw_child in self.get_all_workpages():
            pos = main_window.view.get_notebook_page_index(mw_child.view)
            mw_child.model.set_value_from_event('pos', pos)
        
        
    def get_all_workpages(self):
        UIM = UIManager()
        main_window_uid = UIM._getparentuid(self._controller_uid)
        return [mw_son for mw_son in UIM.list(parentuidfilter=main_window_uid) \
                        if isinstance(mw_son, WorkPageController)
        ]        
        
        
        