# -*- coding: utf-8 -*-
import wx
import logging
import types
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from main_window import MainWindowController
from App import log


class ToolBarToolController(UIControllerBase):
    tid = 'toolbartool_controller'
    
    def __init__(self): 
        super(ToolBarToolController, self).__init__()
      

    def PostInit(self):
        logging.debug('{}.AfterInit started'.format(self.name))
        root_ctrl = self.get_root_controller()
        if not isinstance(root_ctrl, MainWindowController):
            raise Exception()
        _UIM = UIManager()    
        # DetachPane if granpa object has a AuiManager...    
        parent_uid = _UIM._getparentuid(self.uid)
        grampa_uid = _UIM._getparentuid(parent_uid)
        parent = _UIM.get(parent_uid)
        grampa =  _UIM.get(grampa_uid)
        if isinstance(grampa, MainWindowController):    
            mgr = wx.aui.AuiManager_GetManager(root_ctrl.view)
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
            tool = parent.view.DoInsertTool(self.model.pos, 
                self.model.id, self.model.label, bitmap, wx.NullBitmap, 
                self.model.kind, self.model.help, self.model.long_help, None)
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
        'pos': {'default_value': -1, 'type': int},
        'id': {'default_value': wx.ID_ANY, 'type': int},
        'bitmap': {'default_value': wx.EmptyString, 'type': str},
        'kind': {'default_value': wx.ITEM_NORMAL, 'type': int},
        'label': {'default_value': wx.EmptyString, 'type': unicode},
        'help': {'default_value': wx.EmptyString, 'type': unicode},
        'long_help': {'default_value': wx.EmptyString, 'type': unicode},
        'callback': {'default_value': None, 'type': types.FunctionType}
    }    
    
    def __init__(self, controller_uid, **base_state):    
        super(ToolBarToolModel, self).__init__(controller_uid, **base_state)  
               

