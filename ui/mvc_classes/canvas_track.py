# -*- coding: utf-8 -*-

import wx

from app import pubsub 
from app import log
from classes.ui import UIManager
from ui.mvc_classes.canvas_base import CanvasBaseController
from ui.mvc_classes.canvas_base import CanvasBaseModel
from ui.mvc_classes.canvas_base import CanvasBaseView


# On linear X axis scale, base_axis limits will be fixed as below
XMAX_PLUS = 0.0
LINEAR_XLIM = (0.0, 100.0 + XMAX_PLUS)



class TrackCanvasController(CanvasBaseController):
    tid = 'track_canvas_controller'
    
    def __init__(self):
        super().__init__()
        
    def PostInit(self):
        super().PostInit()
        self.subscribe(self.on_change_ygrid_major_lines, 
                                                   'change.ygrid_major_lines')
        self.subscribe(self.on_change_ygrid_minor_lines, 
                                                   'change.ygrid_minor_lines')
        self.subscribe(self.on_change_leftscale, 'change.leftscale')
        self.subscribe(self.on_change_decades, 'change.decades')
        self.subscribe(self.on_change_minorgrid, 'change.minorgrid')
        self.subscribe(self.on_change_scale_lines, 'change.scale_lines')
        self.subscribe(self.on_change_depth_lines, 'change.depth_lines')
        self.subscribe(self.on_change_plotgrid, 'change.plotgrid')

   
    def on_change_ygrid_major_lines(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_ygrid_major_lines(new_value)
        except:
            self.model.set_value_from_event('ygrid_major_lines', old_value)
        finally:
            self.view.draw()

    def on_change_ygrid_minor_lines(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_ygrid_minor_lines(new_value)
        except:
            self.model.set_value_from_event('ygrid_minor_lines', old_value)
        finally:
            self.view.draw()
        
    def on_change_leftscale(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            if new_value <= 0:
                raise ValueError('Wrong value for leftscale. ' + \
                                                 'Valid values are > 0.0')
            if self.model.xscale != 'log':
                return
            self.view.adjust_scale_xlim('log')
        except:
            self.model.set_value_from_event('leftscale', old_value)
        finally:
            self.view.draw()     

    def on_change_decades(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            if new_value <= 0:
                raise ValueError('Wrong value for decades. ' + \
                                                 'Valid values are > 0.0')  
            if self.model.xscale != 'log':
                return
            self.view.adjust_scale_xlim('log')
        except:
            self.model.set_value_from_event('decades', old_value)
        finally:
            self.view.draw()     
            
    def on_change_minorgrid(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_minorgrid(new_value)
        except:
            self.model.set_value_from_event('minorgrid', old_value)
        finally:
            self.view.draw()              

    def on_change_scale_lines(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_scale_lines(new_value)
        except:
            self.model.set_value_from_event('scale_lines', old_value)
        finally:
            self.view.draw()    
        
        
    def on_change_depth_lines(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):  
#        print ('\n\n\non_change_depth_lines:', old_value, new_value, topic)
        try:
            self.view.set_depth_lines(new_value)
        except:
            self.model.set_value_from_event('depth_lines', old_value)
        finally:
            self.view.draw()
            
            
    def on_change_plotgrid(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_plotgrid(new_value)
        except:
            self.model.set_value_from_event('plotgrid', old_value)
        finally:
            self.view.draw()           
            
            
    def on_change_lim(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):   
#        print ('\nTrackCanvasController.on_change_lim:', old_value, new_value, topic.getName())
        
        key = topic.getName().split('.')[2]
        if new_value[0] == new_value[1]:
            
            self.model.set_value_from_event(key, old_value)
            raise Exception('Limits for {} axis cannot be same. {}'.format(
                            key[0], new_value)
            )
        
        # Inverting Y axis limits if necessary
        if (key[0] == 'y') and (new_value[0] < new_value[1]):
            new_value = (new_value[1], new_value[0])

        super().on_change_lim(old_value, new_value, topic)
    



    def on_change_scale(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):
#        print ('\n\nTrackCanvasController.on_change_scale:', old_value, new_value, topic.getName())
                
        key = topic.getName().split('.')[2]
        axis = key[0] # x or y  
        # Y axis (depth) is linear and will not be changed.
        if axis == 'y':
            # TODO: Check for coding a Exception here
            self.model.set_value_from_event(key, old_value)
            return
        # This time we only have X axis 
        if new_value not in ["linear", "log"]:
            # TODO: Check for coding a Exception here
            self.model.set_value_from_event(key, old_value)
            return            
        # Setting locators to NullLocator. 
        # This is made to avoid "exceeds Locator.MAXTICKS" RuntimeError
        self.view.set_locator(None, 'x', 'major')
        self.view.set_locator(None, 'x', 'minor') 
        #
        if new_value == "linear":  
            super().on_change_scale(old_value, new_value, topic)
            self.view.adjust_scale_xlim(new_value)
            # Returning with locators
            self.view.set_scale_lines(self.model.scale_lines)
        else:
            # On log scales is necessary adjust xlim before change scale. 
            # This is made to avoid non-positive limits for log-scale axis.
            self.view.adjust_scale_xlim(new_value)
            super().on_change_scale(old_value, new_value, topic)
            # Returning with locators
            self.set_locator('log', 'x', 'major', numdecs=self.model.decades)            
            self.view.set_minorgrid(self.model.minorgrid)
        self.view.set_plotgrid(self.model.plotgrid)




    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_rect(self, old_value, new_value):        
        self.model.set_value_from_event('rect', old_value)


    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_figure_facecolor(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        self.model.set_value_from_event(key, old_value)
            

    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_spine_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):  
        key = topic.getName().split('.')[2]
        self.model.set_value_from_event(key, old_value)
        
        
        
    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_axis_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        self.model.set_value_from_event(key, old_value)
        


    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_axes_properties(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        self.model.set_value_from_event(key, old_value)


        
    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_text_properties(self, old_value, new_value, topic=pubsub.AUTO_TOPIC): 
        key = topic.getName().split('.')[2]
        self.model.set_value_from_event(key, old_value) 



    def on_change_grid_parameters(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        param_key = topic.getName().split('.')[2]
        key_type = param_key.split('_')[0]
        # grid keys are unchangeable (grid_color, grid_alpha, grid_linestyle and grid_linewidth)
        if key_type == 'grid':
            self.model.set_value_from_event(param_key, old_value) 
        else:  
            super().on_change_grid_parameters(old_value, new_value, topic)



    # TODO: Check if it is the best way        
    # Overriding super class method
    def load_style(self, style_name):
        pass


    # TODO: Check if it is the best way        
    # Overriding super class method
    def _load_dict(self, lib_dict):
        pass
        






###############################################################################
###############################################################################

# ESSES 2 METODOS ABAIXO PRECISAM SER DECIDIDOS ONDE FICARAO
 
#    def on_change_locator(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):           

#    def on_change_tick_params(self, old_value, new_value, 
#                                                      topic=pubsub.AUTO_TOPIC):      


###############################################################################
###############################################################################
        
    
        
class TrackCanvasModel(CanvasBaseModel):
    tid = 'track_canvas_model'

    _ATTRIBUTES = {
        #['depth_lines', 'plotgrid', 'leftscale', 'decades', 'minorgrid', 
        # 'scale_lines', 'ygrid_major_lines', 'ygrid_minor_lines']    
        'xscale': {
                'default_value': 'linear', #'log', #["linear", "log", "symlog", "logit"]
                'type': str
        },            
            
        'depth_lines': {        
            'default_value': 0,
            'type': int
        }, 
        'plotgrid': {
            'default_value': True, 
            'type': bool
        },  
                
        'leftscale': {
            'default_value': 0.2, 
            'type': float
        }, 
        'decades': {
            'default_value': 4, 
            'type': int
        },                 
        'minorgrid': {
            'default_value': True, 
            'type': bool
        }, 

        'scale_lines': {        
            'default_value': 5,
            'type': int
        }, 
                
        'ygrid_major_lines': {
            'default_value': 10.0, 
            'type': float
        },                 
        'ygrid_minor_lines': {
            'default_value': 2.0, 
            'type': float
        }    

    }  
        
    def __init__(self, controller_uid, **base_state):      
        super().__init__(controller_uid, **base_state) 
    
       
    def PostInit(self):
        self.rect = (0.05, 0.05, 0.9, 0.9) #(0.0, 0.0, 1.0, 1.0)   #(0.1, 0.1, 0.8, 0.8)
        # 
        self.axes_spines_right = False
        self.axes_spines_left = False
        self.axes_spines_bottom = False
        self.axes_spines_top = False
        #"""
        #self.axes_spines_right_position = ('axes', 0.8)
        #self.axes_spines_left_position = ('axes', 0.2)
        #self.axes_spines_bottom_position = ('axes', 0.8)
        #self.axes_spines_top_position = ('axes', 1.0)
        #
        self.xaxis_visibility = True
        self.yaxis_visibility = True
        # Y Ticks visibility will be controlled by ytick_major_left, 
        # ytick_minor_left, ytick_major_right and ytick_minor_right flags.
        self.xtick_top = False
        self.xtick_bottom = False        
        self.ytick_left = True
        self.ytick_right = True
        #
        self.xtick_labeltop = False
        self.xtick_labelbottom = True
        self.ytick_labelleft = False
        self.ytick_labelright = False
        #
        thinner = 0.6 
        thicker = 1.2
        #
        self.xtick_direction = 'in'
        self.xtick_major_size = 0.0
        self.xtick_minor_size = 0.0
        self.xtick_major_width = thinner #1.4
        self.xtick_minor_width = thinner #0.7
        self.xgrid_major_linewidth = thinner
        self.xgrid_minor_linewidth = thinner
        self.xtick_color = '#A9A9A9'
        #
        self.ytick_direction = 'in'
        self.ytick_major_size = 10.0
        self.ytick_minor_size = 5.0
        self.ytick_major_width = thicker
        self.ytick_minor_width = thinner
        self.ygrid_major_linewidth = thicker
        self.ygrid_minor_linewidth = thinner
        self.ytick_color = '#A9A9A9'
        #
        self.xgrid_major =  False
        self.xgrid_minor =  False
        
        #self.figure_facecolor = 'white'
        


ShowGridId = wx.NewId()
HideGridId = wx.NewId()
#
ScaleLinGridId = wx.NewId()
ScaleLogGridId = wx.NewId()
#
DepthLinesAllId = wx.NewId()
DepthLinesLeftId = wx.NewId()
DepthLinesRightId = wx.NewId()
DepthLinesCenterId = wx.NewId()
DepthLinesLeftRightId = wx.NewId()
DepthLinesNoneId = wx.NewId()
#
LinScaleLines0Id = wx.NewId()
LinScaleLines1Id = wx.NewId()
LinScaleLines2Id = wx.NewId()
LinScaleLines3Id = wx.NewId()
LinScaleLines4Id = wx.NewId()
LinScaleLines5Id = wx.NewId()
LinScaleLines6Id = wx.NewId()
LinScaleLines7Id = wx.NewId()
#   
LogDecades1Id = wx.NewId()
LogDecades10Id = wx.NewId()
LogDecades100Id = wx.NewId()
LogDecades1000Id = wx.NewId()
LogDecades10000Id = wx.NewId()
LogDecades100000Id = wx.NewId()
LogDecades1000000Id = wx.NewId()
#
ShowMinorgridId = wx.NewId()
HideMinorgridId = wx.NewId()     


        
class TrackCanvas(CanvasBaseView):  
    tid = 'track_canvas'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
              
        
    def PostInit(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self.adjust_scale_xlim(controller.model.xscale)
        super().PostInit()
        self.set_ygrid_major_lines(controller.model.ygrid_major_lines)
        self.set_ygrid_minor_lines(controller.model.ygrid_minor_lines)
        if controller.model.xscale == 'log':
            self.set_locator('log', 'x', 'major', 
                                             numdecs=controller.model.decades)
        wx.CallAfter(self.set_plotgrid, controller.model.plotgrid)
        self.mpl_connect('button_press_event', self._on_button_press)


    def PreDelete(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        granpa_controller_uid = UIM._getparentuid(parent_controller_uid)
        granpa_controller =  UIM.get(granpa_controller_uid)
        if parent_controller.model.overview: 
            granpa_controller._pre_delete_overview_track()
        else:    
            granpa_controller.view._detach_bottom_window(self)
        

    # To override super class method 
    def _load_labels_properties(self):
        pass


    def adjust_scale_xlim(self, scale):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        if scale == 'linear':
            controller.model.xlim = LINEAR_XLIM

        elif scale == 'log':
            min_ = controller.model.leftscale
            max_ = controller.model.leftscale*10.0**controller.model.decades +\
                                                                    XMAX_PLUS
            controller.model.xlim = (min_, max_)

 
    # Log properties            
    def set_minorgrid(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        if controller.model.xscale == 'log' and controller.model.plotgrid:
            controller.model.xgrid_minor = value
            

    # Linear properties
    def set_scale_lines(self, value):
        if value <= 0:
            raise ValueError('Wrong value for scale_lines. ' + \
                                                 'Valid values are > 0.')   
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 

        if controller.model.xscale == 'linear' and controller.model.plotgrid:
            x0, x1 = LINEAR_XLIM
            x1 -= XMAX_PLUS
            x_major_grid_lines = (x1-x0)/value
            # TODO: Verificar Locators
            self.set_locator('multiple', 'x', 'major', x_major_grid_lines)
            controller.model.xgrid_major = True


    def set_ygrid_major_lines(self, value):
        if value <= 0.0:
            raise ValueError('Wrong value for ygrid_major_lines. ' + \
                                                 'Valid values are > 0.0.')
        self.set_locator('multiple', 'y', 'major', value)    
        
                      
    def set_ygrid_minor_lines(self, value):
        if value <= 0.0:
            raise ValueError('Wrong value for ygrid_minor_lines. ' + \
                                                 'Valid values are > 0.0.')              
        self.set_locator('multiple', 'y', 'minor', value)  



    def set_depth_lines(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if value < 0 or value > 5:
            raise ValueError('Wrong value for depth_lines. ' + \
                                                     'Valid values are 0-5.')            
        if controller.model.plotgrid:
            self._ticks = False
            self._postpone_draw = True
            # DEPTH LINES == DEFAULT - X GRIDS, BUT NO TICKS
            if value == 0:
                controller.model.ygrid_major = True
                controller.model.ygrid_minor = True
                controller.model.ytick_major_left = False
                controller.model.ytick_minor_left = False
                controller.model.ytick_major_right = False
                controller.model.ytick_minor_right = False
            # DEPTH LINES == LEFT 
            elif value == 1:
                self._ticks = True
                controller.model.ygrid_major = False
                controller.model.ygrid_minor = False
                controller.model.axes_spines_left_position = ('axes', 0.0)
                controller.model.axes_spines_right_position = ('axes', 1.0)
                controller.model.ytick_direction = 'in'
                controller.model.ytick_major_left = True
                controller.model.ytick_minor_left = True
                controller.model.ytick_major_right = False
                controller.model.ytick_minor_right = False
            # DEPTH LINES == RIGHT
            elif value == 2:
                self._ticks = True
                controller.model.ygrid_major = False
                controller.model.ygrid_minor = False
                controller.model.axes_spines_left_position = ('axes', 0.0)
                controller.model.axes_spines_right_position = ('axes', 1.0)
                controller.model.ytick_direction = 'in'
                controller.model.ytick_major_left = False
                controller.model.ytick_minor_left = False
                controller.model.ytick_major_right = True
                controller.model.ytick_minor_right = True
            # DEPTH LINES == CENTER   
            elif value == 3:
                self._ticks = True             
                controller.model.ygrid_major = False
                controller.model.ygrid_minor = False 
                controller.model.axes_spines_left_position = ('axes', 0.5)
                controller.model.axes_spines_right_position = ('axes', 0.5)
                controller.model.ytick_direction = 'out'
                controller.model.ytick_major_left = True
                controller.model.ytick_minor_left = True
                controller.model.ytick_major_right = True
                controller.model.ytick_minor_right = True
            # DEPTH LINES == LEFT AND RIGHT    
            elif value == 4:   
                self._ticks = True
                controller.model.ygrid_major = False
                controller.model.ygrid_minor = False 
                controller.model.axes_spines_left_position = ('axes', 0.0)
                controller.model.axes_spines_right_position = ('axes', 1.0)
                controller.model.ytick_direction = 'in'
                controller.model.ytick_major_left = True
                controller.model.ytick_minor_left = True
                controller.model.ytick_major_right = True
                controller.model.ytick_minor_right = True
            # DEPTH LINES == NONE
            elif value == 5:
                controller.model.ygrid_major = False
                controller.model.ygrid_minor = False                 
                controller.model.axes_spines_left_position = ('axes', 0.0)
                controller.model.axes_spines_right_position = ('axes', 1.0)
                controller.model.ytick_major_left = False
                controller.model.ytick_minor_left = False
                controller.model.ytick_major_right = False
                controller.model.ytick_minor_right = False
            self._postpone_draw = False  


    def set_plotgrid(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        self._postpone_draw = True  
        if value:
            self.set_minorgrid(controller.model.minorgrid)
            self.set_scale_lines(controller.model.scale_lines)
            self.set_depth_lines(controller.model.depth_lines)
        else:
            controller.model.xgrid_major = False
            controller.model.xgrid_minor = False
            controller.model.ygrid_major = False
            controller.model.ygrid_minor = False
            controller.model.ytick_major_left = False
            controller.model.ytick_minor_left = False
            controller.model.ytick_major_right = False
            controller.model.ytick_minor_right = False
        self._postpone_draw = False  
       
        


    def _on_button_press(self, event):
        #if event.guiEvent.GetSkipped():

        """
        if isinstance(event, wx.MouseEvent):        
            gui_evt = event
        else:
            gui_evt = event.guiEvent
            print (gui_evt)
            
        if gui_evt.GetEventObject() and gui_evt.GetEventObject().HasCapture():            
            gui_evt.GetEventObject().ReleaseMouse()  
        #  
        """

        if event.button == 3: 
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)  
            menu = wx.Menu()
            #
            grid_submenu = wx.Menu()
            grid_submenu.AppendRadioItem(ShowGridId, 'Show')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ShowGridId)
            grid_submenu.AppendRadioItem(HideGridId, 'Hide')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=HideGridId)
            if controller.model.plotgrid:
                grid_submenu.Check(ShowGridId, True)
            else:
                grid_submenu.Check(HideGridId, True)
            menu.AppendSubMenu(grid_submenu, 'Grid')
            #
            scale_submenu = wx.Menu()
            scale_submenu.AppendRadioItem(ScaleLinGridId, 'Linear')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLinGridId)
            scale_submenu.AppendRadioItem(ScaleLogGridId, 'Logarithmic')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ScaleLogGridId)
            
            if controller.model.xscale == 'linear':
                scale_submenu.Check(ScaleLinGridId, True)
            elif controller.model.xscale == 'log':
                scale_submenu.Check(ScaleLogGridId, True)
            
            menu.AppendSubMenu(scale_submenu, 'Scale')
            #           
            depth_lines_submenu = wx.Menu()
            
            depth_lines_submenu.AppendRadioItem(DepthLinesAllId, 'All')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesAllId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesLeftId, 'Left')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftId)

            depth_lines_submenu.AppendRadioItem(DepthLinesRightId, 'Right')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesRightId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesCenterId, 'Center')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesCenterId)
            
            depth_lines_submenu.AppendRadioItem(DepthLinesLeftRightId, 'Left and Right')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesLeftRightId)  
 
            depth_lines_submenu.AppendRadioItem(DepthLinesNoneId, 'None')
            event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=DepthLinesNoneId)  
           
            if controller.model.depth_lines == 0:
                depth_lines_submenu.Check(DepthLinesAllId, True)
                
            elif controller.model.depth_lines == 1:
                depth_lines_submenu.Check(DepthLinesLeftId, True)
                
            elif controller.model.depth_lines == 2:
                depth_lines_submenu.Check(DepthLinesRightId, True)
                
            elif controller.model.depth_lines == 3:
                depth_lines_submenu.Check(DepthLinesCenterId, True)  

            elif controller.model.depth_lines == 4:
                depth_lines_submenu.Check(DepthLinesLeftRightId, True)  
                
            elif controller.model.depth_lines == 5:
                depth_lines_submenu.Check(DepthLinesNoneId, True)                  
                
            menu.AppendSubMenu(depth_lines_submenu, 'Depth Lines')
            #                   
         
            menu.AppendSeparator() 
            if controller.model.xscale == 'linear':
                scale_lines_submenu = wx.Menu()

                scale_lines_submenu.AppendRadioItem(LinScaleLines0Id, 'None')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines0Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines1Id, '1')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines1Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines2Id, '2')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines2Id)            
                scale_lines_submenu.AppendRadioItem(LinScaleLines3Id, '3')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines3Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines4Id, '4')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines4Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines5Id, '5')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines5Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines6Id, '6')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines6Id)
                scale_lines_submenu.AppendRadioItem(LinScaleLines7Id, '7')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LinScaleLines7Id)

                if controller.model.scale_lines == 0:
                    scale_lines_submenu.Check(LinScaleLines0Id, True)  
                elif controller.model.scale_lines == 1:
                    scale_lines_submenu.Check(LinScaleLines1Id, True)  
                elif controller.model.scale_lines == 2:
                    scale_lines_submenu.Check(LinScaleLines2Id, True)  
                elif controller.model.scale_lines == 3:
                    scale_lines_submenu.Check(LinScaleLines3Id, True)  
                elif controller.model.scale_lines == 4:
                    scale_lines_submenu.Check(LinScaleLines4Id, True)  
                elif controller.model.scale_lines == 5:
                    scale_lines_submenu.Check(LinScaleLines5Id, True)                   
                elif controller.model.scale_lines == 6:
                    scale_lines_submenu.Check(LinScaleLines6Id, True)
                elif controller.model.scale_lines == 7:
                    scale_lines_submenu.Check(LinScaleLines7Id, True)    
                menu.AppendSubMenu(scale_lines_submenu, 'Scale Lines')
                
            elif controller.model.xscale == 'log':
                decades_submenu = wx.Menu()
            
                decades_submenu.AppendRadioItem(LogDecades1Id, '1')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1Id)
                decades_submenu.AppendRadioItem(LogDecades10Id, '10')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades10Id)
                decades_submenu.AppendRadioItem(LogDecades100Id, '100')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades100Id)
                decades_submenu.AppendRadioItem(LogDecades1000Id, '1.000')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1000Id)        
                decades_submenu.AppendRadioItem(LogDecades10000Id, '10.000')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades10000Id)
                decades_submenu.AppendRadioItem(LogDecades100000Id, '100.000')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades100000Id)
                decades_submenu.AppendRadioItem(LogDecades1000000Id, '1.000.000')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=LogDecades1000000Id)
                if controller.model.decades == 1:
                    decades_submenu.Check(LogDecades1Id, True)  
                elif controller.model.decades == 2:
                    decades_submenu.Check(LogDecades10Id, True)  
                elif controller.model.decades == 3:
                    decades_submenu.Check(LogDecades100Id, True)  
                elif controller.model.decades == 4:
                    decades_submenu.Check(LogDecades1000Id, True)  
                elif controller.model.decades == 5:
                    decades_submenu.Check(LogDecades10000Id, True)                   
                elif controller.model.decades == 6:
                    decades_submenu.Check(LogDecades100000Id, True)
                elif controller.model.decades == 7:
                    decades_submenu.Check(LogDecades1000000Id, True)    
                menu.AppendSubMenu(decades_submenu, 'Log Max')
                #
                # Minorgrid submenu
                minorgrid_submenu = wx.Menu()
                minorgrid_submenu.AppendRadioItem(ShowMinorgridId, 'Show')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=ShowMinorgridId)
                minorgrid_submenu.AppendRadioItem(HideMinorgridId, 'Hide')
                event.canvas.Bind(wx.EVT_MENU, self._menu_selection, id=HideMinorgridId)                
                if controller.model.minorgrid:
                    minorgrid_submenu.Check(ShowMinorgridId, True)
                else:
                    minorgrid_submenu.Check(HideMinorgridId, True)
                menu.AppendSubMenu(minorgrid_submenu, 'Minor Grid')
            #   
                
            event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
            menu.Destroy() # destroy to avoid mem leak
            # If Menu was displayed, return True to TrackFigureCanvas.on_press    
            #return True
                    
              
    def _menu_selection(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        if event.GetId() == ShowGridId:
            controller.model.plotgrid = True    
        elif event.GetId() == HideGridId:
            controller.model.plotgrid = False
        elif event.GetId() == ScaleLinGridId:
            controller.model.xscale = 'linear'  
        elif event.GetId() == ScaleLogGridId:
            controller.model.xscale = 'log'       
        elif event.GetId() == DepthLinesAllId:
            controller.model.depth_lines = 0
        elif event.GetId() == DepthLinesLeftId:
            controller.model.depth_lines = 1  
        elif event.GetId() == DepthLinesRightId:
            controller.model.depth_lines = 2
        elif event.GetId() == DepthLinesCenterId:
            controller.model.depth_lines = 3   
        elif event.GetId() == DepthLinesLeftRightId:
            controller.model.depth_lines = 4           
        elif event.GetId() == DepthLinesNoneId:
            controller.model.depth_lines = 5       
        elif event.GetId() == LogDecades1Id:
            controller.model.decades = 1
        elif event.GetId() == LogDecades10Id:
            controller.model.decades = 2
        elif event.GetId() == LogDecades100Id:
            controller.model.decades = 3
        elif event.GetId() == LogDecades1000Id:
            controller.model.decades = 4
        elif event.GetId() == LogDecades10000Id:
            controller.model.decades = 5
        elif event.GetId() == LogDecades100000Id:
            controller.model.decades = 6
        elif event.GetId() == LogDecades1000000Id:
            controller.model.decades = 7          
        elif event.GetId() == LinScaleLines0Id:
            controller.model.scale_lines = 0            
        elif event.GetId() == LinScaleLines1Id:
            controller.model.scale_lines = 1             
        elif event.GetId() == LinScaleLines2Id:
            controller.model.scale_lines = 2             
        elif event.GetId() == LinScaleLines3Id:
            controller.model.scale_lines = 3
        elif event.GetId() == LinScaleLines4Id:
            controller.model.scale_lines = 4
        elif event.GetId() == LinScaleLines5Id:
            controller.model.scale_lines = 5
        elif event.GetId() == LinScaleLines6Id:
            controller.model.scale_lines = 6
        elif event.GetId() == LinScaleLines7Id:
            controller.model.scale_lines = 7
        elif event.GetId() == ShowMinorgridId:
            controller.model.minorgrid = True    
        elif event.GetId() == HideMinorgridId:
            controller.model.minorgrid = False
           
            
    # TODO: Under Testing...     
    """        
    def get_xaxis_ticklabels(self):        
        return self.base_axes.xaxis.get_majorticklabels()
    
    def get_xaxis_ticklines(self):  
        lines = []
        ticks = self.base_axes.xaxis.self.get_major_ticks()
        for tick in ticks:
            lines.append(tick.tick1line)
        return lines   
            
    def get_xaxis_ticklocs(self):
        return self.base_axes.xaxis.get_majorticklocs()            
    """        
    