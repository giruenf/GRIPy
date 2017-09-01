# -*- coding: utf-8 -*-
import wx
import logging
import types
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UI_MODEL_ATTR_CLASS
from main_window import MainWindowController
from App import log


class ToolBarToolController(UIControllerBase):
    tid = 'toolbartool_controller'
    
    def __init__(self): 
        super(ToolBarToolController, self).__init__()
      
    def PostInit(self):
        logging.debug('{}.AfterInit started'.format(self.name))
        UIM = UIManager()
        root_ctrl = UIM.get_root_controller()
        
        if not isinstance(root_ctrl, MainWindowController):
            raise Exception()
            
        # DetachPane if granpa object has a AuiManager...    
        parent_uid = UIM._getparentuid(self.uid)
        grampa_uid = UIM._getparentuid(parent_uid)
        parent = UIM.get(parent_uid)
        grampa =  UIM.get(grampa_uid)
        if isinstance(grampa, MainWindowController):  
            mgr = wx.aui.AuiManager.GetManager(root_ctrl.view)
            if mgr is not None:
                mgr.DetachPane(parent.view)
            
        if self.model.pos == -1:
            # Appending - Not needed to declare pos
            self.model.pos =  parent.view.GetToolsCount()
        if self.model.pos >  parent.view.GetToolsCount():
            # If pos was setted out of range for inserting in parent Menu
            msg = 'Invalid tool position for ToolBarTool with text={}. Position will be setting to {}'.format(self.model.label, parent.view.GetToolsCount())
            logging.warning(msg)
            self.model.pos = parent.view.GetToolsCount() 
       
        if self.model.bitmap is None:
            bitmap = wx.Bitmap()
        else:
            bitmap = wx.Bitmap(self.model.bitmap)
            
        # TODO: Rever isso
        try:
            tool = parent.view.InsertTool(self.model.pos, self.model.id,
                                            self.model.label, bitmap, 
                                            wx.NullBitmap, self.model.kind,
                                            self.model.help, 
                                            self.model.long_help, None
            )
        except Exception:
            msg = 'Error in creating ToolBarTool.'
            logging.exception(msg)
            raise
        if self.model.callback and tool:
            root_ctrl.view.Bind(wx.EVT_TOOL, self.model.callback, tool)
            parent.view.Realize()
            
        # AtachPane again if granpa object had it detached...    
        if isinstance(grampa, MainWindowController):        
            mgr.AddPane(parent.view, parent.view.paneinfo)
            mgr.Update()

        logging.debug('{}.AfterInit ended'.format(self.name))    

      
    
class ToolBarToolModel(UIModelBase):
    tid = 'toolbartool_model'
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int, 
                'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'id': {'default_value': wx.ID_ANY, 
               'type': int,
               'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'bitmap': {'default_value': wx.EmptyString, 
                   'type': str,
                   'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'kind': {'default_value': wx.ITEM_NORMAL, 
                 'type': int,
                 'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'label': {'default_value': wx.EmptyString, 
                  'type': unicode,
                  'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'help': {'default_value': wx.EmptyString, 
                 'type': unicode,
                 'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'long_help': {'default_value': wx.EmptyString, 
                      'type': unicode,
                      'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'callback': {'default_value': None, 
                     'type': types.FunctionType,
                     'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        }
    }    
    
    def __init__(self, controller_uid, **base_state):    
        super(ToolBarToolModel, self).__init__(controller_uid, **base_state)  





