# -*- coding: utf-8 -*-

import numpy as np

import wx

from matplotlib.colorbar import ColorbarBase
from matplotlib import style as mstyle 
from matplotlib import axis
from matplotlib import rcParams

from ui.mvc_classes.workpage import WorkPageController
from ui.mvc_classes.workpage import WorkPageModel
from ui.mvc_classes.workpage import WorkPage

from ui.plotstatusbar import PlotStatusBar

from classes.ui import UIManager
from app import log
from app.app_utils import GripyBitmap  



CP_NORMAL_TOOL = wx.NewId()        
CP_SELECTION_TOOL = wx.NewId()   
CP_FLOAT_PANEL = wx.NewId()  


class CrossPlotController(WorkPageController):
    tid = 'crossplot_controller'
    
    def __init__(self):
        super().__init__()

        
class CrossPlotModel(WorkPageModel):
    tid = 'crossplot_model'

    def __init__(self, controller_uid, **base_state):   
        super().__init__(controller_uid, **base_state)   

        
    
class CrossPlot(WorkPage):
    tid = 'crossplot'
    _FRIENDLY_NAME = 'Cross Plot'


    def __init__(self, controller_uid):   
        super().__init__(controller_uid) 

  
    def PostInit(self):

        try:
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self._tool_bar =  wx.aui.AuiToolBar(self)
            self.sizer.Add(self._tool_bar, 0, flag=wx.TOP|wx.EXPAND)
            #     
            UIM = UIManager()   
            canvas_controller = UIM.create('canvas_controller', 
                    self._controller_uid
            )
            self._main_panel = canvas_controller.view
            self._main_panel.mpl_connect('motion_notify_event', 
                                                     self.on_canvas_mouse_move)
            self.sizer.Add(self._main_panel, 1, flag=wx.EXPAND)
            #
            self._status_bar =  PlotStatusBar(self)
            self.sizer.Add(self._status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)
            self.SetSizer(self.sizer)   
            #
            self._build_tool_bar()
            self.Layout()
    
        except Exception as e:
            print ('ERROR IN CrossPlot.PostInit:', e)
            raise


    def PreDelete(self):
        try:
            self.sizer.Remove(0)
            del self._tool_bar
#            self._main_panel.mp
        except Exception as e:
            msg = 'PreDelete ' + self.__class__.__name__ + \
                                            ' ended with error: ' + str(e)
            print (msg)                                
            pass       


    def on_canvas_mouse_move(self, event):
        axes = event.inaxes
        if axes is None:
            return
        x_axis_label = 'X'
        y_axis_label = 'Y'
        msg = '{}: {:0.2f}, {}: {:0.2f}'.format(x_axis_label, event.xdata, 
                                                   y_axis_label, event.ydata
        )
        self._status_bar.SetStatusText(msg)
    



    def _on_change_tool(self, event):
        print 
        if event.GetId() == CP_NORMAL_TOOL:
            print ('CP_NORMAL_TOOL')
        elif event.GetId() == CP_SELECTION_TOOL:  
            print ('CP_SELECTION_TOOL')



    def _on_change_float_panel(self, event):
        # TODO: Integrar binds de toggle buttons...
        if event.GetId() == CP_FLOAT_PANEL:
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            controller.model.float_mode = event.IsChecked()            


    def _build_tool_bar(self):

        self.fp_item = self._tool_bar.AddTool(CP_FLOAT_PANEL, 
                      wx.EmptyString,
                      GripyBitmap('restore_window-25.png'), 
                      wx.NullBitmap,
                      wx.ITEM_CHECK,
                      'Float Panel', 
                      'Float Panel',
                      None
        )
        self._tool_bar.ToggleTool(CP_FLOAT_PANEL, False)
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_float_panel, None,
                  CP_FLOAT_PANEL
        )        
        self._tool_bar.AddSeparator()
        
        #
        self._tool_bar.AddTool(CP_NORMAL_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self._tool_bar.ToggleTool(CP_NORMAL_TOOL, True) 
        #
        self._tool_bar.AddTool(CP_SELECTION_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_tool, None,
                  CP_NORMAL_TOOL, CP_SELECTION_TOOL
        )
        #
        self._tool_bar.AddSeparator()
        
        '''
        lib = mstyle.library
        for k, values in lib.items():
            print ('\n\nSTYLE: {}'.format(k))
            
            for key, value in values.items():
                print ('{}: {}'.format(key, value))
        '''        
   

        '''
        print ('\n')
            
        for key, value in rcParams.items():
#            for k in ['grid.', 'axes.', 'figure.', 'xtick.', 'ytick.']:
#                if key.startswith(k):
            if key not in mstyle.core.STYLE_BLACKLIST:
                print ('{}: {}'.format(key, value))

        print ('\n')
        '''
        
        
        #print ('axis._gridline_param_names:', axis._gridline_param_names)

        self._tool_bar.label_MC = wx.StaticText(self._tool_bar, 
                                                label='MPL Theme:  '
        )
        #self._tool_bar.label_MC.SetLabel('Multi cursor:')
        self._tool_bar.AddControl(self._tool_bar.label_MC, '')

        
        styles = ['default'] + mstyle.available[:]
        self._tool_bar.choice_Style = wx.Choice(self._tool_bar, choices=styles)
        self._tool_bar.choice_Style.SetSelection(0)
        #
        #controller = UIM.get(self._controller_uid)
        #idx_index_type = ['MD', 'TVD', 'TVDSS', 'TWT', 'TIME'].index(controller.model.index_type)
        #self._tool_bar.choice_IT.SetSelection(idx_index_type)
        self._tool_bar.choice_Style.Bind(wx.EVT_CHOICE , self._on_choice_style) 
        self._tool_bar.AddControl(self._tool_bar.choice_Style, '')
        
        self._tool_bar.AddSeparator()
        
        self._tool_bar.Realize()  


    
    def set_own_name(self):
        UIM = UIManager()   
        controller = UIM.get(self._controller_uid)
        idx = 0
        lpcs = UIM.list('crossplot_controller')
        for lpc in lpcs:
            idx += 1
        controller.model.title = self._FRIENDLY_NAME + ' ['+ str(idx) + ']'    
        

    def _on_choice_style(self, event):
        lib_name = event.GetString()
        print ('\n\nLoading Style:', lib_name)
        UIM = UIManager()  
        cc = UIM.list('canvas_controller', self._controller_uid)[0]
        cc.load_style(lib_name)


