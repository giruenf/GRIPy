from classes.ui import UIManager
from ui.mvc_classes.canvas_base import CanvasBaseController
from ui.mvc_classes.canvas_base import CanvasBaseView
from app import log


class CanvasPlotterController(CanvasBaseController):
    tid = 'canvas_plotter_controller'
    
    def __init__(self, **state):
        super().__init__(**state)
        
    def PostInit(self):
        super().PostInit()
            
    def get_friendly_name(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent = UIM.get(parent_uid)
        return parent.get_friendly_name()
    
        
class CanvasPlotter(CanvasBaseView):  
    tid = 'canvas_plotter'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)

    def PostInit(self):
        super().PostInit()
