# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject
from classes.ui import UIViewObject 
from classes.ui import MainWindowController
from app import log


class ToolBarController(UIControllerObject):
    tid = 'toolbar_controller'
    _singleton_per_parent = True
    
    _ATTRIBUTES = {
        'id': {'default_value': wx.ID_ANY, 
               'type': int
        },
        'pos': {'default_value': wx.DefaultPosition, 
                'type': wx.Point
        },
        'size': {'default_value': wx.DefaultSize, 
                 'type': wx.Size
        },
        'style': {'default_value': wx.TB_FLAT|wx.TB_NODIVIDER, 
                  'type': int
        }
    }   
        
    def __init__(self, **state):
        super().__init__(**state)
      
  
class ToolBar(UIViewObject, wx.ToolBar):
    tid = 'toolbar'
    paneinfo = wx.aui.AuiPaneInfo().Name(tid).ToolbarPane().Top()
                          
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        #wx.SystemOptions.SetOption("msw.remap", '0')
        wx.ToolBar.__init__(self, parent_controller.view, controller.id, 
                            controller.pos,
                            controller.size, controller.style
        )
        self.Realize()  
        if isinstance(parent_controller, MainWindowController):
            mgr = wx.aui.AuiManager.GetManager(parent_controller.view)
            mgr.AddPane(self, self.paneinfo)
            mgr.Update()

    
    