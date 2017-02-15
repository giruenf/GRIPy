# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from main_window import MainWindowController
from App import log



 
class ToolBarController(UIControllerBase):
    tid = 'toolbar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(ToolBarController, self).__init__()
      
  
  
class ToolBarModel(UIModelBase):
    tid = 'toolbar_model'
    _ATTRIBUTES = {
        'id': {'default_value': wx.ID_ANY, 'type': int},
        'pos': {'default_value': wx.DefaultPosition, 'type': wx.Point},
        'size': {'default_value': wx.DefaultSize, 'type': wx.Size},
        'style': {'default_value': wx.TB_FLAT|wx.TB_NODIVIDER, 'type': long}
    }    
    

    def __init__(self, controller_uid, **base_state):     
        super(ToolBarModel, self).__init__(controller_uid, **base_state)    
               
        
        
class ToolBarView(UIViewBase, wx.ToolBar):
    tid = 'toolbar'
    paneinfo = wx.aui.AuiPaneInfo().Name(tid).ToolbarPane().Top()
                          
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        wx.ToolBar.__init__(self, parent_controller.view, controller.model.id, controller.model.pos,
                            controller.model.size, controller.model.style)
        self.Realize()  

        if isinstance(parent_controller, MainWindowController):
            mgr = wx.aui.AuiManager_GetManager(parent_controller.view)
            mgr.AddPane(self, self.paneinfo)
            mgr.Update()

