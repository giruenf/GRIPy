# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from App import log
 
     
class StatusBarController(UIControllerBase):
    tid = 'statusbar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(StatusBarController, self).__init__()

    def SetStatusText(self, text, i=0):
        self.view.SetStatusText(text, i)
        
        
class StatusBarModel(UIModelBase):
    tid = 'statusbar_model'

    _ATTRIBUTES = {
        'label': {'default_value': wx.EmptyString, 'type': unicode}
    }    
    
    def __init__(self, controller_uid, **base_state):
        super(StatusBarModel, self).__init__(controller_uid, **base_state)  


class StatusBar(UIViewBase, wx.StatusBar):
    tid = 'statusbar'
 
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        wx.StatusBar.__init__(self, parent_controller.view)
        
        """
        self.paneinfo = wx.aui.AuiPaneInfo().Name(self.tid).Bottom()
        
        mgr = wx.aui.AuiManager_GetManager(self.parent)
        mgr.AddPane(self, self.paneinfo)
        mgr.Update()
        """
        parent_controller.view.SetStatusBar(self)
        #if isinstance(self.parent, MainWindow):
        #    self.parent.SetStatusBar(self)        
        #else:
        #    raise Exception('')


    def PostInit(self):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        self.SetStatusText(controller.model.label)
        
        
        