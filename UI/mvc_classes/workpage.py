# -*- coding: utf-8 -*-
import wx
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
            
        self.__class__.__name__    
        controller.model.title = self._FRIENDLY_NAME + \
                                    ' ['+ str(self._controller_uid[1]+1) + ']'    
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')



        
        