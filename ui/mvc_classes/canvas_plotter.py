# -*- coding: utf-8 -*-

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.ticker import MultipleLocator
from matplotlib import style as mstyle 
import matplotlib.ticker as mticker
from matplotlib import rcParams

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIModelObject 
from classes.ui import UIViewObject 
from app import pubsub 
from app import log


from ui.mvc_classes.canvas_base import CanvasBaseController
from ui.mvc_classes.canvas_base import CanvasBaseModel
from ui.mvc_classes.canvas_base import CanvasBaseView



class CanvasPlotterController(CanvasBaseController):
    tid = 'canvas_plotter_controller'
    
    def __init__(self):
        print ('\n\nCanvasPlotterController.Init')
        super().__init__()
        
    def PostInit(self):
        print ('CanvasPlotterController.PostInit')
        super().PostInit()
     

class CanvasPlotterModel(CanvasBaseModel):
    tid = 'canvas_plotter_model'

    def __init__(self, controller_uid, **base_state):
        print ('CanvasPlotterModel.Init')
        super().__init__(controller_uid, **base_state) 
    
    
    def PostInit(self):
        print ('CanvasPlotterModel.PostInit')
        pass 
    
    
class CanvasPlotter(CanvasBaseView):  
    tid = 'canvas_plotter'


    def __init__(self, controller_uid):
        print ('CanvasPlotter.Init')
        super().__init__(controller_uid)


    def PostInit(self):
        super().PostInit()
