# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from App import log



class PlotterController(UIControllerBase):
    tid = None
    
    def __init__(self):
        super(PlotterController, self).__init__()


class PlotterModel(UIModelBase):
    tid = None
     
    def __init__(self, controller_uid, **base_state):    
        super(PlotterModel, self).__init__(controller_uid, **base_state)  
        
    
    
class Plotter(UIViewBase, wx.Panel):
    tid = None
    
    def __init__(self, controller_uid):
        if self.main_panel_class is None:
            raise Exception('In order to inherit from Plotter, self.main_panel_class must be setted.')
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(controller_uid)
        parent_uid = _UIM._getparentuid(controller.uid)
        parent_controller = _UIM.get(parent_uid)
        wx.Panel.__init__(self, parent_controller.view)



        
        
        