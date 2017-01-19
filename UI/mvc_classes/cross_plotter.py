# -*- coding: utf-8 -*-

import wx
import logging

from plotter import PlotterController 
from plotter import PlotterModel
from plotter import Plotter



class CrossPlotController(PlotterController):
    tid = 'crossplot_controller'
    
    def __init__(self, caller, controller, **kwargs):
        super(CrossPlotController, self).__init__(caller, controller)


class CrossPlotModel(PlotterModel):
    tid = 'crossplot_model'
     
    def __init__(self, caller, controller, **kwargs):      
        super(CrossPlotModel, self).__init__(caller, controller)    
        
    
    
class CrossPlot(Plotter):
    tid = 'crossplot'

    def __init__(self, caller, controller, **kwargs):
        self.main_panel_class = wx.Panel
        super(CrossPlot, self).__init__(caller, controller) 
        self.main_panel.SetBackgroundColour('white')
    
    
    def get_title(self):
        return 'Cross Plot [oid:' + str(self._controller.oid) + ']' 



        
        