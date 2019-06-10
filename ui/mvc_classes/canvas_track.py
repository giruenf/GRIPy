# -*- coding: utf-8 -*-

import wx

from app import pubsub 
from app import log
from classes.ui import UIManager
from ui.mvc_classes.canvas_base import CanvasBaseController

from ui.mvc_classes.canvas_base import CanvasBaseView

from ui.mvc_classes.extras import SelectablePanelMixin

from matplotlib.lines import Line2D







# On linear X axis scale, base_axis limits will be fixed as below
XMAX_PLUS = 0.0
LINEAR_XLIM = (0.0, 100.0 + XMAX_PLUS)






class TrackCanvasController(CanvasBaseController):
    tid = 'track_canvas_controller'

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
            'default_value': 500.0, 
            'type': float
        },       
                
        'ygrid_minor_lines': {
            'default_value': 100.0, 
            'type': float
        }    

    }  
    
    def __init__(self, **state):
        super().__init__(**state)

        #self.rect = (0.15, 0.15, 0.7, 0.7) #(0.05, 0.05, 0.9, 0.9) #(0.0, 0.0, 1.0, 1.0)   #(0.1, 0.1, 0.8, 0.8)
        self.rect = (0.0, 0.0, 1.0, 1.0)
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
            self.set_value_from_event('ygrid_major_lines', old_value)
        finally:
            self.view.draw()

    def on_change_ygrid_minor_lines(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_ygrid_minor_lines(new_value)
        except:
            self.set_value_from_event('ygrid_minor_lines', old_value)
        finally:
            self.view.draw()
        
    def on_change_leftscale(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            if new_value <= 0:
                raise ValueError('Wrong value for leftscale. ' + \
                                                 'Valid values are > 0.0')
            if self.xscale != 'log':
                return
            self.view.adjust_scale_xlim('log')
        except:
            self.set_value_from_event('leftscale', old_value)
        finally:
            self.view.draw()     

    def on_change_decades(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            if new_value <= 0:
                raise ValueError('Wrong value for decades. ' + \
                                                 'Valid values are > 0.0')  
            if self.xscale != 'log':
                return
            self.view.adjust_scale_xlim('log')
        except:
            self.set_value_from_event('decades', old_value)
        finally:
            self.view.draw()     
            
    def on_change_minorgrid(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_minorgrid(new_value)
        except:
            self.set_value_from_event('minorgrid', old_value)
        finally:
            self.view.draw()              

    def on_change_scale_lines(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_scale_lines(new_value)
        except:
            self.set_value_from_event('scale_lines', old_value)
        finally:
            self.view.draw()    
        
        
    def on_change_depth_lines(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):  
#        print ('\n\n\non_change_depth_lines:', old_value, new_value, topic)
        try:
            self.view.set_depth_lines(new_value)
        except:
            self.set_value_from_event('depth_lines', old_value)
        finally:
            self.view.draw()
            
            
    def on_change_plotgrid(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC):          
        try:
            self.view.set_plotgrid(new_value)
        except:
            self.set_value_from_event('plotgrid', old_value)
        finally:
            self.view.draw()           
            
            
    def on_change_lim(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):   
#        print ('\nTrackCanvasController.on_change_lim:', old_value, new_value, topic.getName())
        
        key = topic.getName().split('.')[2]
        if new_value[0] == new_value[1]:
            
            self.set_value_from_event(key, old_value)
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
            self.set_value_from_event(key, old_value)
            return
        # This time we only have X axis 
        if new_value not in ["linear", "log"]:
            # TODO: Check for coding a Exception here
            self.set_value_from_event(key, old_value)
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
            self.view.set_scale_lines(self.scale_lines)
        else:
            # On log scales is necessary adjust xlim before change scale. 
            # This is made to avoid non-positive limits for log-scale axis.
            self.view.adjust_scale_xlim(new_value)
            super().on_change_scale(old_value, new_value, topic)
            # Returning with locators
            self.set_locator('log', 'x', 'major', numdecs=self.decades)            
            self.view.set_minorgrid(self.minorgrid)
        self.view.set_plotgrid(self.plotgrid)




    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_rect(self, old_value, new_value):        
        self.set_value_from_event('rect', old_value)


    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_figure_facecolor(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        self.set_value_from_event(key, old_value)
            

    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_spine_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):  
        key = topic.getName().split('.')[2]
        self.set_value_from_event(key, old_value)
        
    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_axis_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        self.set_value_from_event(key, old_value)
        


    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_axes_properties(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        self.set_value_from_event(key, old_value)


        
    # TODO: Check if it is the best way        
    # Overriding super class method
    def on_change_text_properties(self, old_value, new_value, topic=pubsub.AUTO_TOPIC): 
        key = topic.getName().split('.')[2]
        self.set_value_from_event(key, old_value) 



    def on_change_grid_parameters(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        param_key = topic.getName().split('.')[2]
        key_type = param_key.split('_')[0]
        # grid keys are unchangeable (grid_color, grid_alpha, grid_linestyle and grid_linewidth)
        if key_type == 'grid':
            self.set_value_from_event(param_key, old_value) 
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
        


        

        
class TrackCanvas(CanvasBaseView, SelectablePanelMixin):  
    tid = 'track_canvas'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
                
    def PostInit(self):
        self._depth_canvas = None
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self.adjust_scale_xlim(controller.xscale)
        super().PostInit()
        self.set_ygrid_major_lines(controller.ygrid_major_lines)
        self.set_ygrid_minor_lines(controller.ygrid_minor_lines)
        if controller.xscale == 'log':
            self.set_locator('log', 'x', 'major', 
                                             numdecs=controller.decades)
        wx.CallAfter(self.set_plotgrid, controller.plotgrid)
        

    def PreDelete(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        granpa_controller_uid = UIM._getparentuid(parent_controller_uid)
        granpa_controller =  UIM.get(granpa_controller_uid)
        if parent_controller.overview:
            try:
                granpa_controller._pre_delete_overview_track()
            except:
                pass
        else:    
            granpa_controller.view._detach_bottom_window(self)
        #
        self.destroy_depth_canvas()
        #
                
    # Just to override super class method 
    def _load_labels_properties(self):
        pass



    def get_one_depth_per_pixel(self, depth_min, depth_max):
        """
        Retorna uma lista contendo uma profundidade por pixel, respeitando os
        limites de depth_min e depth_max.
        
        Este metodo eh usado em track_object.py, no processo de interpolacao 
        de linhas (classe LineRepresentation).       
        """
        y_px_size = self.GetSize()[1] 
        depth_list = []
        for depth_px in range(y_px_size):
            depth = self._get_depth_from_ypixel(depth_px)   
            if depth > depth_min and depth < depth_max: 
                depth_list.append(depth)
        return depth_list        


#    def change_selection(self, selected):
#        change_selection(new_value)


    def adjust_scale_xlim(self, scale):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        if scale == 'linear':
            controller.xlim = LINEAR_XLIM

        elif scale == 'log':
            min_ = controller.leftscale
            max_ = controller.leftscale*10.0**controller.decades + \
                                                                    XMAX_PLUS
            controller.xlim = (min_, max_)

 
    # Log properties            
    def set_minorgrid(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        if controller.xscale == 'log' and controller.plotgrid:
            controller.xgrid_minor = value
            

    # Linear properties
    def set_scale_lines(self, value):
        if value <= 0:
            raise ValueError('Wrong value for scale_lines. ' + \
                                                 'Valid values are > 0.')   
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 

        if controller.xscale == 'linear' and controller.plotgrid:
            x0, x1 = LINEAR_XLIM
            x1 -= XMAX_PLUS
            x_major_grid_lines = (x1-x0)/value
            # TODO: Verificar Locators
            self.set_locator('multiple', 'x', 'major', x_major_grid_lines)
            controller.xgrid_major = True


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
        if controller.plotgrid:
            self._ticks = False
            self._postpone_draw = True
            # DEPTH LINES == DEFAULT - X GRIDS, BUT NO TICKS
            if value == 0:
                controller.ygrid_major = True
                controller.ygrid_minor = True
                controller.ytick_major_left = False
                controller.ytick_minor_left = False
                controller.ytick_major_right = False
                controller.ytick_minor_right = False
            # DEPTH LINES == LEFT 
            elif value == 1:
                self._ticks = True
                controller.ygrid_major = False
                controller.ygrid_minor = False
                controller.axes_spines_left_position = ('axes', 0.0)
                controller.axes_spines_right_position = ('axes', 1.0)
                controller.ytick_direction = 'in'
                controller.ytick_major_left = True
                controller.ytick_minor_left = True
                controller.ytick_major_right = False
                controller.ytick_minor_right = False
            # DEPTH LINES == RIGHT
            elif value == 2:
                self._ticks = True
                controller.ygrid_major = False
                controller.ygrid_minor = False
                controller.axes_spines_left_position = ('axes', 0.0)
                controller.axes_spines_right_position = ('axes', 1.0)
                controller.ytick_direction = 'in'
                controller.ytick_major_left = False
                controller.ytick_minor_left = False
                controller.ytick_major_right = True
                controller.ytick_minor_right = True
            # DEPTH LINES == CENTER   
            elif value == 3:
                self._ticks = True             
                controller.ygrid_major = False
                controller.ygrid_minor = False 
                controller.axes_spines_left_position = ('axes', 0.5)
                controller.axes_spines_right_position = ('axes', 0.5)
                controller.ytick_direction = 'out'
                controller.ytick_major_left = True
                controller.ytick_minor_left = True
                controller.ytick_major_right = True
                controller.ytick_minor_right = True
            # DEPTH LINES == LEFT AND RIGHT    
            elif value == 4:   
                self._ticks = True
                controller.ygrid_major = False
                controller.ygrid_minor = False 
                controller.axes_spines_left_position = ('axes', 0.0)
                controller.axes_spines_right_position = ('axes', 1.0)
                controller.ytick_direction = 'in'
                controller.ytick_major_left = True
                controller.ytick_minor_left = True
                controller.ytick_major_right = True
                controller.ytick_minor_right = True
            # DEPTH LINES == NONE
            elif value == 5:
                controller.ygrid_major = False
                controller.ygrid_minor = False                 
                controller.axes_spines_left_position = ('axes', 0.0)
                controller.axes_spines_right_position = ('axes', 1.0)
                controller.ytick_major_left = False
                controller.ytick_minor_left = False
                controller.ytick_major_right = False
                controller.ytick_minor_right = False
            self._postpone_draw = False  


    def set_plotgrid(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        self._postpone_draw = True  
        if value:
            self.set_minorgrid(controller.minorgrid)
            self.set_scale_lines(controller.scale_lines)
            self.set_depth_lines(controller.depth_lines)
        else:
            controller.xgrid_major = False
            controller.xgrid_minor = False
            controller.ygrid_major = False
            controller.ygrid_minor = False
            controller.ytick_major_left = False
            controller.ytick_minor_left = False
            controller.ytick_major_right = False
            controller.ytick_minor_right = False
        self._postpone_draw = False  
       

    def create_depth_canvas(self):
        self._depth_canvas = DepthCanvas(self)
        
        
    def destroy_depth_canvas(self):
        del self._depth_canvas       


    def reposition_depth_canvas(self):
        if self._depth_canvas:
            self._depth_canvas.reposition_depth_canvas()


    # TODO: rever duplicidade com metodo da classe DepthCanvas
    def _get_max_min_pixels(self):             
        # Because we have Y axis from top to bottom, our Axes coordinated
        # inverted too. 
        #   Top-left: (0.0, 0.0)
        #   Bottom-right: (1.0, 1.0)
        #
        # Get minimum y pixel (considering top of canvas)
        _, min_y_px = self.get_transaxes().transform((0.0, 0.0))
        # Get maximum y pixel (considering top of canvas)
        _, max_y_px = self.get_transaxes().transform((1.0, 1.0))
        return int(min_y_px), int(max_y_px)
  
    # TODO: rever duplicidade com metodo da classe DepthCanvas
    def _get_ypixel_from_depth(self, depth):
        min_y_px, max_y_px = self._get_max_min_pixels()
        transdata = self.get_transdata()
        y_px = transdata.transform((0, depth))[1]
        y_px = (max_y_px - y_px) + min_y_px
        return y_px

    # TODO: rever duplicidade com metodo da classe DepthCanvas
    def _get_depth_from_ypixel(self, y_px):
        min_y_px, max_y_px = self._get_max_min_pixels()
        transdata_inv = self.get_transdata().inverted() 
        depth = transdata_inv.transform((0.0, max_y_px + min_y_px - y_px))[1]
        return depth     

    

    """
    def create_depth_canvas(self):
        ymin, ymax = self.get_ylim()

        print (self.get_xlim(), (ymax, ymax))
        self.line1 = Line2D(self.get_xlim(), (ymax, ymax), color='b', alpha=0.5, linewidth=7)
        self.base_axes.add_line(self.line1)
        
        self.line2 = Line2D(self.get_xlim(), (ymin, ymin), color='b', alpha=0.5, linewidth=7)
        self.base_axes.add_line(self.line2)        
        
        
        
        self.cidpress1 = self.line1.figure.canvas.mpl_connect(
                                            'button_press_event', self.on_press)
        
        
        self.draw()
        

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        print ('\non_press:', event.xdata, event.ydata)
        if event.inaxes != self.line1.axes: return

        contains, attrd = self.line1.contains(event)
        if not contains: return
        print('event contains', self.line1.get_data(), event.xdata, event.ydata)
        #x0, y0 = self.line.xy
        #self.press = x0, y0, event.xdata, event.ydata

    """

        
    """        
    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.line.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.line.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.line.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)        
    """    


        
        

               
            
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



class DepthCanvas():
    SASH_DRAG_NONE = 0 
    SASH_DRAG_DRAGGING = 1
    
    def __init__(self, track_canvas):
        self.tc = track_canvas
        self.create_depth_canvas()
        self.reposition_depth_canvas()
        self.tc.draw()
        self.tc.Bind(wx.EVT_SIZE, self._on_track_size)
        self.tc.Bind(wx.EVT_MOUSE_EVENTS, self._on_mouse) 

    def __del__(self):
        self.destroy_depth_canvas()       
        #wx.CallAfter(object.__del__())
        
    def create_depth_canvas(self):
        self._in_canvas = -1
        self._drag_mode = DepthCanvas.SASH_DRAG_NONE
        self.canvas_color = 'blue'
        self.canvas_alt_color = 'red'
        self.canvas_height = 3
        #
        self.d1_canvas = wx.Panel(self.tc, name='D1') 
        self.d1_canvas.SetBackgroundColour(self.canvas_color)    
        #
        self.d2_canvas = wx.Panel(self.tc, name='D2') 
        self.d2_canvas.SetBackgroundColour(self.canvas_color)  
        #
        self.d1_canvas.Bind(wx.EVT_MOUSE_EVENTS, self._on_canvas_mouse)
        self.d2_canvas.Bind(wx.EVT_MOUSE_EVENTS, self._on_canvas_mouse)        


    def destroy_depth_canvas(self):
        try:
            self.tc.Unbind(wx.EVT_SIZE, handler=self._on_track_size)  
            self.tc.Unbind(wx.EVT_MOUSE_EVENTS, handler=self._on_mouse)            
            self.d1_canvas.Unbind(wx.EVT_MOUSE_EVENTS, handler=self._on_canvas_mouse)
            self.d2_canvas.Unbind(wx.EVT_MOUSE_EVENTS, handler=self._on_canvas_mouse)
            del self.d1_canvas
            del self.d2_canvas
        except:
            pass
        

    def _on_track_size(self, event):
        event.Skip()
        wx.CallAfter(self.reposition_depth_canvas)
        
        
    def _on_canvas_mouse(self, event):
        """
        Joga o evento do canvas para o canvas track
        """
        if event.GetEventType() in [wx.wxEVT_MOTION, wx.wxEVT_LEFT_DOWN, 
                        wx.wxEVT_LEFT_UP, wx.wxEVT_MOTION|wx.wxEVT_LEFT_DOWN]:
            new_event = wx.MouseEvent(event.GetEventType())
            pos = self.tc.ScreenToClient(wx.GetMousePosition())
            new_event.SetPosition(pos)
            new_event.Skip()
            self.tc.GetEventHandler().ProcessEvent(new_event)   
            
            
    def _on_mouse(self, event):
        """
        O evento do canvas track retorna para cah
        """
        x, y = event.GetPosition()
        if self._drag_mode == DepthCanvas.SASH_DRAG_NONE:    
            self._canvas_hit_test(x, y)              
            if event.LeftDown():
                self.start_dragging(y)
        elif self._drag_mode == DepthCanvas.SASH_DRAG_DRAGGING:
            if event.LeftIsDown():
                self.drag_it(y)       
            elif event.LeftUp():
                self.end_dragging()
        event.Skip()

   
    def _canvas_hit_test(self, x, y, tolerance=5):
        """
        Test if a user click hitted one of the two canvas.
        
        Parameters
        ----------
        x: int
            X coordinate
        y: int
            Y coordinate            
        tolerance: int
            Number of pixels tolerated outside canvas.     
        """         
        r1 = self.d1_canvas.GetRect()   
        r2 = self.d2_canvas.GetRect() 
        if y >= r1.y - tolerance and y <= r1.y + r1.height + tolerance:
            self._in_canvas = self.d1_canvas
            self.tc.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
        elif y >= r2.y - tolerance and y <= r2.y + r2.height + tolerance:
            self._in_canvas = self.d2_canvas 
            self.tc.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
        else:
            self._in_canvas = None
            self.tc.SetCursor(wx.STANDARD_CURSOR)

    
    def start_dragging(self, y):
        """
        Prepare for dragging...
        """
        if self._in_canvas == None:
            return 
        if self._drag_mode != DepthCanvas.SASH_DRAG_NONE:
            return
        self._drag_mode = DepthCanvas.SASH_DRAG_DRAGGING
        #self.track.CaptureMouse()
        self._old_y = y
        self._in_canvas.SetBackgroundColour(self.canvas_alt_color)
        self._in_canvas.Refresh()    
        



    def drag_it(self, new_y):
        """
        During the drag....
        """
        if self._in_canvas == None:
            return
        if self._drag_mode != DepthCanvas.SASH_DRAG_DRAGGING:
            return       
        if new_y != self._old_y:
            inc = new_y - self._old_y
            x, y = self._in_canvas.GetPosition()  
            new_pos = y + inc
            #
            min_y_px, max_y_px = self.tc._get_max_min_pixels()


            
            #
#            """
            if new_pos < min_y_px:
                # Canvas top cannot exceed the minimum pixel permitted
                return
            elif (new_pos + self.canvas_height) > max_y_px:
                # Canvas bottom cannot exceed the maximum pixel permitted
                return
#            """


            #
            self._in_canvas.SetPosition((x, new_pos))
            self._in_canvas.Refresh()
            self._old_y = new_y   



            # Adjusting position (translating) for real canvas bottom position
            #new_pos = max_y_px + min_y_px - new_pos

            if self._in_canvas.GetName() == 'D1':
                new_depth = self.tc._get_depth_from_ypixel(new_pos)           
            else:    
                new_depth = self.tc._get_depth_from_ypixel(new_pos + 
                                                           self.canvas_height)    

            self.tc.SetToolTip(wx.ToolTip('{0:.2f}'.format(new_depth)))
            
            
            print(self._in_canvas.GetName(), min_y_px, max_y_px, new_pos, new_depth)
            print()

             
            
    """        
    def _get_max_min_pixels(self):             
        # Because we have Y axis from top to bottom, our Axes coordinated
        # inverted too. 
        #   Top-left: (0.0, 0.0)
        #   Bottom-right: (1.0, 1.0)
        #
        # Get minimum y pixel (considering top of canvas)
        _, min_y_px = self.tc.get_transaxes().transform((0.0, 0.0))
        # Get maximum y pixel (considering top of canvas)
        _, max_y_px = self.tc.get_transaxes().transform((1.0, 1.0))
        return int(min_y_px), int(max_y_px)
    """
    

    def end_dragging(self):
        """
        """
        print('\nend_dragging')
        #
        if self._in_canvas == None:
            return
        if self._drag_mode != DepthCanvas.SASH_DRAG_DRAGGING:
            return  
        #
        self._drag_mode = DepthCanvas.SASH_DRAG_NONE
        self._old_y = None
        #
        if self.tc.HasCapture():
            self.tc.ReleaseMouse()
        #       
        transdata_inv = self.tc.get_transdata().inverted()
        #
        min_y_px, max_y_px = self.tc._get_max_min_pixels()
        #
        top_canvas_px = self.d1_canvas.GetPosition()[1]
        bottom_canvas_px = self.d2_canvas.GetPosition()[1]
        
        
#        if top_canvas_px == bottom_canvas_px:  
#            if bottom_canvas_px 
        
        print (top_canvas_px, bottom_canvas_px)
        
        # Top canvas position must be smaller than bottom canvas
        if top_canvas_px > bottom_canvas_px:
            temp = top_canvas_px
            top_canvas_px = bottom_canvas_px
            bottom_canvas_px = temp
            
        print (top_canvas_px, bottom_canvas_px)
        


        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.tc._controller_uid)
        granpa_controller_uid = UIM._getparentuid(parent_controller_uid)
        granpa_controller = UIM.get(granpa_controller_uid)    
        
        

        if top_canvas_px == min_y_px:
            min_depth = granpa_controller.wellplot_ylim[0]
        else:
            min_depth = self.tc._get_depth_from_ypixel(top_canvas_px)         

        if bottom_canvas_px == max_y_px:
            max_depth = granpa_controller.wellplot_ylim[1]
        else:
            max_depth = self.tc._get_depth_from_ypixel(bottom_canvas_px + 
                                                            self.canvas_height) 
      

            
        """   
        #
        if y1_px <= y2_px:
            _, d1 = transdata_inv.transform((0.0, y1_px))
            _, d2 = transdata_inv.transform((0.0, y2_px + self.canvas_height))
        else:    
            _, d1 = transdata_inv.transform((0.0, y2_px))
            _, d2 = transdata_inv.transform((0.0, y1_px + self.canvas_height)) 
        #    
        """
        
        print (min_depth, max_depth)
        

        #
        granpa_controller.shown_ylim = (min_depth, max_depth)
        #
        self._in_canvas.SetBackgroundColour(self.canvas_color)
        self._in_canvas.Refresh()       
        self.tc.SetToolTip(wx.ToolTip('{0:.2f} - {1:.2f}'.format(min_depth, max_depth)))



    """
    def _get_ypixel_from_depth(self, depth):
        min_y_px, max_y_px = self.tc._get_max_min_pixels()
        transdata = self.tc.get_transdata()
        y_px = transdata.transform((0, depth))[1]
        y_px = (max_y_px - y_px) + min_y_px
        return y_px
    """

    """
    def _get_depth_from_ypixel(self, y_px):
        min_y_px, max_y_px = self.tc._get_max_min_pixels()
        transdata_inv = self.tc.get_transdata().inverted() 
        depth = transdata_inv.transform((0.0, max_y_px + min_y_px - y_px))[1]
        return depth                
    """


    """
    
    def _get_depth_canvas_display_coords(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.tc._controller_uid)
        granpa_controller_uid = UIM._getparentuid(parent_controller_uid)
        granpa_controller =  UIM.get(granpa_controller_uid)  
        #
        xmin, xmax = self.tc.get_xlim()
        ymin, ymax = granpa_controller.shown_ylim
        #
        transdata = self.tc.get_transdata()
        data_min = (xmin , ymin)
        data_max = (xmax , ymax)
        
        xmin_px, ymin_px = transdata.transform(data_min)
        
        display_xmax, ymax_px = transdata.transform(data_max)
        #
        ret_dict = {
                'xmin_px': int(xmin_px),
                'width_px': display_xmax-int(xmin_px),
                
                'ymin_px': int(ymin_px),
                'ymax_px': int(ymax_px)
                
        }
        return ret_dict

    """


    def reposition_depth_canvas(self):
        #display_coords = self._get_depth_canvas_display_coords()
        #
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.tc._controller_uid)
        granpa_controller_uid = UIM._getparentuid(parent_controller_uid)
        granpa_controller =  UIM.get(granpa_controller_uid)  
        #
        xmin, xmax = self.tc.get_xlim()
        depth_min, depth_max = granpa_controller.shown_ylim
        #
        top_px = self.tc._get_ypixel_from_depth(depth_min)
        bottom_px = self.tc._get_ypixel_from_depth(depth_max)
        #
        transaxes = self.tc.get_transaxes()
        #
#        xmin_px, _ = transaxes.transform((0.0, 0.0))
        xmin_px, top_px_ax = transaxes.transform((0.0, 0.0))
#        xmax_px, _ = transaxes.transform((1.0, 1.0))
        xmax_px, bottom_px_ax = transaxes.transform((1.0, 1.0))
        #
        print ('\nMin Max Y:', top_px, top_px_ax, bottom_px, bottom_px_ax)
        #
        self.d1_canvas.SetSize(int(xmin_px), int(top_px),
                                       xmax_px-xmin_px, self.canvas_height
        )        
        #
        self.d2_canvas.SetSize(int(xmin_px), int(bottom_px)-self.canvas_height,
                                       xmax_px-xmin_px, self.canvas_height
        )
        #       
       
        

        
        
    """    
    def on_canvas_mouse(self, event):
        if event.GetEventType() == wx.wxEVT_MOTION:
            canvas.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
            
        x, y = event.GetPosition()    
        
        if (self._drag_mode == SASH_DRAG_NONE) and (event.LeftDown()): 
            # Start dragging
            canvas.SetBackgroundColour(self.canvas_alt_color)
            canvas.Refresh()
            self._drag_mode = SASH_DRAG_DRAGGING
            self._old_y = y
        
        elif self._drag_mode == SASH_DRAG_DRAGGING:
            
            UIM = UIManager()
            parent_controller_uid = UIM._getparentuid(self._controller_uid)
            parent_controller =  UIM.get(parent_controller_uid)
            
            
            if event.LeftIsDown():
                # Still Dragging
                if y == self._old_y:
                    return
                yinc = y - self._old_y
                cx, cy = canvas.GetPosition()  
                new_ypos = cy + yinc
                
                #if new_ypos < 0:
                #    new_ypos = 0
                #if new_ypos > (self.track.GetClientSize()[1] - self.canvas_height):
                #    new_ypos = self.track.GetClientSize()[1] - self.canvas_height
                
                canvas.SetPosition((cx, new_ypos))
                canvas.Refresh()            
                
                  
                self._old_y = y  
                
            elif event.LeftUp():
                # End dragging
                self._drag_mode = SASH_DRAG_NONE
                self._old_y = None
                
                if self.track.HasCapture():
                    self.track.ReleaseMouse()
                  
                y1 = self.d1_canvas.GetPosition()[1]
                y2 = self.d2_canvas.GetPosition()[1]
        
        
                if y1 <= y2:
                    d1 = self.track.get_depth_from_ypixel(y1)
                    d2 = self.track.get_depth_from_ypixel(y2 + self.canvas_height)
                else:    
                    d1 = self.track.get_depth_from_ypixel(y2)
                    d2 = self.track.get_depth_from_ypixel(y1 + self.canvas_height)
                #    

                #
                parent_controller.set_value_from_event('shown_ylim', (d1, d2))
                parent_controller._reload_ylim()
                # 
                canvas.SetBackgroundColour(self.canvas_color)
                canvas.Refresh()  
                #                  
                self.track.SetToolTip(wx.ToolTip('{0:.2f} - {1:.2f}'.format(d1, d2)))

                
                
        event.Skip()
    """        
        
        
        