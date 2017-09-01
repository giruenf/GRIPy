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
        controller.model.title = self.__class__.__name__ + \
                                    ' [id:'+str(self._controller_uid[1]) + ']'    
        result = parent_controller.insert_notebook_page(controller.model.pos, 
                                        self, controller.model.title, True
        )
        if not result:
            log.error('Page could not be inserted in MainWindow notebook.')


        
'''        
class LogPlotToolBar(aui.AuiToolBar):
    
    def __init__(self, parent):
        super(LogPlotToolBar, self).__init__(parent)
        self.SetToolBitmapSize(wx.Size(48, 48))  
        #
        self.AddTool(LP_NORMAL_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self.ToggleTool(LP_NORMAL_TOOL, True) 
        #
        self.AddTool(LP_SELECTION_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_change_tool, None,
                  LP_NORMAL_TOOL, LP_SELECTION_TOOL
        )
        #
        self.AddSeparator()
        #
        tb_item = self.AddTool(-1, u"Insert Track", 
                                  wx.Bitmap('./icons/table_add_24.png'),
                                  'Insert a new track'
        )
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_toolbar_insert_track, tb_item)
        #
        tb_item = self.AddTool(-1, u"Remove Track", 
                                  wx.Bitmap('./icons/table_delete_24.png'),
                                 'Remove selected tracks'
        )
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_toolbar_remove_track, tb_item)
        #
        self.AddSeparator()  
        #
        button_edit_format = wx.Button(self, label='Edit LogPlot')
        button_edit_format.Bind(wx.EVT_BUTTON , self.GetParent()._OnEditFormat)
        self.AddControl(button_edit_format, '')
        self.AddSeparator()    
        #    
        self.cbFit = wx.CheckBox(self, -1, 'Fit')        
        self.cbFit.Bind(wx.EVT_CHECKBOX , self.GetParent()._on_fit) 
        self.AddControl(self.cbFit, '')    
        #
        self.Realize()          
        
'''        
        
        
        