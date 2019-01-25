# -*- coding: utf-8 -*-

import logging
from types import FunctionType

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from ui.mvc_classes.main_window import MainWindowController
from app import log
from app.app_utils import GripyBitmap


class ToolBarToolController(UIControllerObject):
    tid = 'toolbartool_controller'
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        },
        'id': {'default_value': wx.ID_ANY, 
               'type': int
        },
        'bitmap': {'default_value': wx.EmptyString, 
                   'type': str
        },
        'kind': {'default_value': wx.ITEM_NORMAL, 
                 'type': int
        },
        'label': {'default_value': wx.EmptyString, 
                  'type': str
        },
        'help': {'default_value': wx.EmptyString, 
                 'type': str
        },
        'long_help': {'default_value': wx.EmptyString, 
                      'type': str
        },
        'callback': {'default_value': None, 
                     'type': FunctionType
        }
    }   
        
    def __init__(self, **state): 
        super().__init__(**state)
      
    def PostInit(self):
        log.debug('{}.AfterInit started'.format(self.name))
        UIM = UIManager()        
        main_window = wx.App.Get().GetTopWindow()
            
        # DetachPane if granpa object has a AuiManager...    
        parent_uid = UIM._getparentuid(self.uid)
        grampa_uid = UIM._getparentuid(parent_uid)
        parent = UIM.get(parent_uid)
        grampa =  UIM.get(grampa_uid)
        if isinstance(grampa, MainWindowController):  
            mgr = wx.aui.AuiManager.GetManager(main_window)
            if mgr is not None:
                mgr.DetachPane(parent.view)
            
        if self.pos == -1:
            # Appending - Not needed to declare pos
            self.pos =  parent.view.GetToolsCount()
        if self.pos >  parent.view.GetToolsCount():
            # If pos was setted out of range for inserting in parent Menu
            msg = 'Invalid tool position for ToolBarTool with text={}. Position will be setting to {}'.format(self.label, parent.view.GetToolsCount())
            logging.warning(msg)
            self.pos = parent.view.GetToolsCount() 
       
        bitmap = GripyBitmap(self.bitmap)

        # TODO: Rever isso
        try:
            tool = parent.view.InsertTool(self.pos, self.id,
                                            self.label, bitmap, 
                                            wx.NullBitmap, self.kind,
                                            self.help, 
                                            self.long_help, None
            )
        except Exception as e:
            msg = 'Error in creating ToolBarTool: ' + e
            logging.exception(msg)
            print ('\n\n', msg)
            raise
            
        if self.callback and tool:
            main_window.Bind(wx.EVT_TOOL, self.callback, tool)
            parent.view.Realize()
            
        # AtachPane again if granpa object had it detached...    
        if isinstance(grampa, MainWindowController):        
            mgr.AddPane(parent.view, parent.view.paneinfo)
            mgr.Update()

        logging.debug('{}.AfterInit ended'.format(self.name))    

      


