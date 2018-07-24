# -*- coding: utf-8 -*-

import wx
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.ticker import MultipleLocator
from matplotlib import style as mstyle 
from matplotlib import rcParams


from ui.uimanager import UIManager
from ui.uimanager import UIControllerBase 
from ui.uimanager import UIModelBase 
from ui.uimanager import UIViewBase 
from app import pubsub 
from app import log


# From matplotlib.axes._base.set_xscale
CANVAS_SCALES = ["linear", "log", "symlog", "logit"]



class BaseAxes(Axes):    
    
    _valid_keys = [
        'y_major_grid_lines',
        'y_minor_grid_lines',
        
        'x_scale',
        'plotgrid',
        
        'leftscale',
        'decades',
        'scale_lines',
        'minorgrid',
        'y_scale',
        'y_plotgrid',
        'y_scale_lines',
        'y_minorgrid',
        'ylim',
        'depth_lines',
        
    ]        
    
    _internal_props = {
        'major_tick_width': 1.4,        
        'minor_tick_width': 0.7,
        'major_tick_lenght': 10,
        'minor_tick_lenght': 5,
        'dummy_ax_zorder': 0,
        'ticks_zorder': 8,
        'spines_zorder': 10,
        'grid_linestyle': '-',
        'spines_color': 'black',
        'tick_grid_color': '#A9A9A9'    #'#DFDFDF'#
    }  
    

    def __init__(self, figure, **initial_properties):
        
        print ('\nBaseAxes.__init__:', initial_properties)

        rect = initial_properties.get('rect', None)
        if rect is None:
            rect = [0.0, 0.0, 1.0, 1.0]
            
        
        super().__init__(figure, rect)







# From: matplotlib\backends\backend_wxagg.py
"""
    The FigureCanvas contains the figure and does event handling.

    In the wxPython backend, it is derived from wxPanel, and (usually)
    lives inside a frame instantiated by a FigureManagerWx. The parent
    window probably implements a wxSizer to control the displayed
    control size - but we give a hint as to our preferred minimum
    size.
    """



class CanvasController(UIControllerBase):
    tid = 'canvas_controller'
    
    def __init__(self):
        super().__init__()
        
        
    def PostInit(self):
        self.subscribe(self.on_change_suptitle, 'change.figure_title')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_x')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_y')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_fontsize')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_weight')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_ha')
        self.subscribe(self.on_change_suptitle, 'change.figure_title_va')
        #
        self.subscribe(self.on_change_spine_visibility, 
                                           'change.spine_right_visibility')
        self.subscribe(self.on_change_spine_visibility, 
                                           'change.spine_left_visibility')
        self.subscribe(self.on_change_spine_visibility, 
                                           'change.spine_bottom_visibility')
        self.subscribe(self.on_change_spine_visibility, 
                                           'change.spine_top_visibility')
        #
        self.subscribe(self.on_change_axis_visibility, 
                                           'change.xaxis_visibility')
        self.subscribe(self.on_change_axis_visibility, 
                                           'change.yaxis_visibility')
        #
        self.subscribe(self.on_change_rect, 'change.rect')
        #
        self.subscribe(self.on_change_lim, 'change.xlim')
        self.subscribe(self.on_change_lim, 'change.ylim')
        #
        self.subscribe(self.on_change_scale, 'change.xscale')
        self.subscribe(self.on_change_scale, 'change.yscale')        
        #
        self.subscribe(self.on_change_tick_params, 'change.xgrid_major_visible')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_major_color')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_major_alpha')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_major_linestyle')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_major_linewidth')
        #
        self.subscribe(self.on_change_tick_params, 'change.xgrid_minor_visible')  
        self.subscribe(self.on_change_tick_params, 'change.xgrid_minor_color')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_minor_alpha')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_minor_linestyle')
        self.subscribe(self.on_change_tick_params, 'change.xgrid_minor_linewidth')  
        #
        self.subscribe(self.on_change_tick_params, 'change.ygrid_major_visible')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_major_color')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_major_alpha')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_major_linestyle')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_major_linewidth')
        #
        self.subscribe(self.on_change_tick_params, 'change.ygrid_minor_visible') 
        self.subscribe(self.on_change_tick_params, 'change.ygrid_minor_color')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_minor_alpha')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_minor_linestyle')
        self.subscribe(self.on_change_tick_params, 'change.ygrid_minor_linewidth')           
        #
        self.subscribe(self.on_change_locator, 'change.xgrid_major_locator')
        self.subscribe(self.on_change_locator, 'change.xgrid_minor_locator')
        self.subscribe(self.on_change_locator, 'change.ygrid_major_locator')
        self.subscribe(self.on_change_locator, 'change.ygrid_minor_locator') 
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_major_bottom') 
        self.subscribe(self.on_change_tick_params, 'change.xtick_major_top') 
        self.subscribe(self.on_change_tick_params, 'change.xtick_minor_bottom')
        self.subscribe(self.on_change_tick_params, 'change.xtick_minor_top')
        self.subscribe(self.on_change_tick_params, 'change.ytick_major_left') 
        self.subscribe(self.on_change_tick_params, 'change.ytick_major_right')
        self.subscribe(self.on_change_tick_params, 'change.ytick_minor_left')
        self.subscribe(self.on_change_tick_params, 'change.ytick_minor_right')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_major_size') 
        self.subscribe(self.on_change_tick_params, 'change.xtick_minor_size')
        self.subscribe(self.on_change_tick_params, 'change.ytick_major_size') 
        self.subscribe(self.on_change_tick_params, 'change.ytick_minor_size')
        #        
        self.subscribe(self.on_change_tick_params, 'change.xtick_major_width') 
        self.subscribe(self.on_change_tick_params, 'change.xtick_minor_width')
        self.subscribe(self.on_change_tick_params, 'change.ytick_major_width') 
        self.subscribe(self.on_change_tick_params, 'change.ytick_minor_width')
        #             
        self.subscribe(self.on_change_tick_params, 'change.xtick_major_pad') 
        self.subscribe(self.on_change_tick_params, 'change.xtick_minor_pad')
        self.subscribe(self.on_change_tick_params, 'change.ytick_major_pad') 
        self.subscribe(self.on_change_tick_params, 'change.ytick_minor_pad')      
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_bottom')
        self.subscribe(self.on_change_tick_params, 'change.xtick_top')
        self.subscribe(self.on_change_tick_params, 'change.ytick_left')
        self.subscribe(self.on_change_tick_params, 'change.ytick_right')     
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_labelbottom')
        self.subscribe(self.on_change_tick_params, 'change.xtick_labeltop')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelleft')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelright')  
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_direction') 
        self.subscribe(self.on_change_tick_params, 'change.ytick_direction')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_labelsize')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelsize')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_labelsize')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelsize')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_color')
        self.subscribe(self.on_change_tick_params, 'change.ytick_color')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_labelcolor')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelcolor')
        #
        self.subscribe(self.on_change_tick_params, 'change.xtick_labelrotation')
        self.subscribe(self.on_change_tick_params, 'change.ytick_labelrotation')
        #
        self.subscribe(self.on_change_axes_properties, 'change.axes_facecolor')
        self.subscribe(self.on_change_axes_properties, 'change.axes_edgecolor')
        self.subscribe(self.on_change_axes_properties, 'change.axes_axisbelow')



    def on_change_axes_properties(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        prop = key.split('_')[1]
    
        if prop == 'facecolor':
            self.view.set_facecolor(new_value)
        elif prop == 'edgecolor':
            self.view.set_edgecolor(new_value)            
        elif prop == 'axisbelow':
            self.view.set_axisbelow(new_value)      
            
        self.view.draw()  
        
        
        
    def load_style(self, style_name):
        
        if style_name == 'default':
            lib_dict = rcParams
        else:    
            lib_dict = mstyle.library.get(style_name)
        
        self.view._postpone_draw = True
        
        for key, value in lib_dict.items():
            if key not in mstyle.core.STYLE_BLACKLIST:
                keys = key.split('.')
                new_key = '_'.join(keys)
                
                if keys[0] in ['xtick', 'ytick', 'grid']:
                    print ('Loading: {} = {}'.format(new_key, value))
                    if new_key.startswith('grid'):
                        new_key = new_key.split('_')[1]
                        self.model['xgrid_major_'+new_key] = value
                        self.model['xgrid_minor_'+new_key] = value
                        self.model['ygrid_major_'+new_key] = value
                        self.model['ygrid_minor_'+new_key] = value
                    else:    
                        self.model[new_key] = value
                        
                elif keys[0] == 'axes' and keys[1] in ['facecolor', 
                         'edgecolor', 'axisbelow']:
                    print ('Loading: {} = {}'.format(new_key, value))
                    self.model[new_key] = value
                    
                elif new_key == 'axes_prop_cycle':
                    continue
                else:
                    print ('NOT LOADED: {} = {}'.format(new_key, value))
                    
        self.view._postpone_draw = False
        self.view.draw()
        
        
    def on_change_suptitle(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        try:
            self.view.suptitle(self.model.figure_title, x=self.model.figure_title_x, 
                y=self.model.figure_title_y, ha=self.model.figure_title_ha, 
                va=self.model.figure_title_va, size=self.model.figure_title_fontsize, 
                weight=self.model.figure_title_weight
            )
        except:
            self.model.set_value_from_event(key, old_value)
        finally:
            self.view.draw()       


    def on_change_spine_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        spine = key.split('_')[1]
        try:
            self.view.set_spine_visibility(spine, new_value)
        except Exception as e:
            # log(e)
            self.model.set_value_from_event(key, old_value)
        finally:
            self.view.draw()
        
        
    def on_change_axis_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        axis = key[0] # x or y  
        try:
            self.view.set_axis_visibility(axis, new_value)
        except Exception as e:
            # log(e)
            self.model.set_value_from_event(key, old_value)
        finally:
            self.view.draw()        
        
        
    def on_change_rect(self, old_value, new_value):        
        try:
            self.view.set_position(new_value)
            self.view.draw()  
        except Exception as e:
            # log(e)
            self.model.rect(old_value)


    def on_change_lim(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        axis = key[0] # x or y  
        try:
            self.view.set_lim(axis, new_value)
            self.view.draw()
        except Exception as e:
            # log(e)
            self.model[key] = old_value
      

    def on_change_scale(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        if new_value not in CANVAS_SCALES:
            self.model.set_value_from_event(key, old_value)
            return
        axis = key[0] # x or y         
        self.view.set_scale(axis, new_value)
        self.view.draw()  

 
    def on_change_locator(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):           
        key = topic.getName().split('.')[2]
        axis, which, _ =  key.split('_')
        axis = axis[0] # x or y  (e.g. xgrid -> x)        
        
        self.view.set_locator(axis, which, new_value)
        self.view.draw()
    
    

    def on_change_tick_params(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):      
        
#        print ('\nEntrou on_change_tick_params')
        
        try:
            key = topic.getName().split('.')[2]
            keys = key.split('_')
            if len(keys) == 3:
                axis_type_obj, which, param_key = keys
            elif len(keys) == 2:
                axis_type_obj, param_key = keys
                which = 'both'
            type_obj = axis_type_obj[1:]
            axis = axis_type_obj[0] # x or y  (e.g. xgrid -> x)  
            #
#            print ('Loading: ', axis, type_obj, which, param_key)
            
            if type_obj == 'grid':
                kw = {'grid_' + param_key: new_value} 
                self.view.set_tick_params(axis, which, **kw)
            
            elif param_key in ['top', 'bottom', 'left', 'right']:
                if param_key.startswith('label'):
                    param_key_2 = param_key[5:]
                    
                else:
                    param_key_2 = param_key
                
#                print ('param_key_2:', param_key_2)
                
                if which == 'major' or which == 'both':
                    kw = {param_key: (self.model[axis+'tick_'+param_key] and 
                                      self.model[axis+'tick_major_'+param_key_2])
                    }
                    self.view.set_tick_params(axis, 'major', **kw)
                    
                if which == 'minor' or which == 'both':
                    kw = {param_key: (self.model[axis+'tick_'+param_key] and 
                                      self.model[axis+'tick_minor_'+param_key_2])
                    }
                    self.view.set_tick_params(axis, 'minor', **kw)
            else:
                kw = {param_key: new_value}
                self.view.set_tick_params(axis, which, **kw) 
        except Exception as e:
#            print ('\n\nERRO:', e)
            raise            
        #
        self.view.draw()        
 
        """
        self.base_axes.tick_params(
            top=(controller.model.xtick_top and controller.model.xtick_major_top),
            bottom=(controller.model.xtick_bottom and controller.model.xtick_major_bottom),
            left=(controller.model.ytick_left and controller.model.ytick_major_left),
            right=(controller.model.ytick_right and controller.model.ytick_major_right),
            
            labeltop=(controller.model.xtick_labeltop and controller.model.xtick_major_top),
            labelbottom=(controller.model.xtick_labelbottom and controller.model.xtick_major_bottom),
            labelleft=(controller.model.ytick_labelleft and controller.model.ytick_major_left),
            labelright=(controller.model.ytick_labelright and controller.model.ytick_major_right),
            
            which='major'
        )
        self.base_axes.tick_params(
            top=(controller.model.xtick_top and controller.model.xtick_minor_top),
            bottom=(controller.model.xtick_bottom and controller.model.xtick_minor_bottom),
            labeltop=(controller.model.xtick_labeltop and controller.model.xtick_minor_top),
            labelbottom=(controller.model.xtick_labelbottom and controller.model.xtick_minor_bottom),
            
            left=(controller.model.ytick_left and controller.model.ytick_minor_left),
            right=(controller.model.ytick_right and controller.model.ytick_minor_right),
            labelleft=(controller.model.ytick_labelleft and controller.model.ytick_minor_left),
            labelright=(controller.model.ytick_labelright and controller.model.ytick_minor_right),
            
            which='minor'
        )  
        """


       
        
    def on_change_tick_size(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):     
        key = topic.getName().split('.')[2]
        axis, which, _ =  key.split('_')
        axis = axis[0] # x or y  (e.g. xgrid -> x)    
        
        #self.yaxis.set_tick_params('major', size=10)
        #self.yaxis.set_tick_params('minor', size=5)
        
        '''
        gridOn', 'tick1On', 'tick2On', 'label1On', 'label2On']
        switches = [k for k in kw if k in switchkw]
        for k in switches:
            setattr(self, k, kw.pop(k))
        newmarker = [k for k in kw if k in ['size', 'width', 'pad', 'tickdir']
        '''



        #def tick_params(self, axis='both', **kwargs):
        """Change the appearance of ticks, tick labels, and gridlines.

        color : color
            Tick color; accepts any mpl color spec.

        pad : float
            Distance in points between tick and label.

        labelsize : float or str
            Tick label font size in points or as a string (e.g., 'large').

        labelcolor : color
            Tick label color; mpl color spec.

        zorder : float
            Tick and label zorder.

        labelbottom, labeltop, labelleft, labelright : bool
            Whether to draw the respective tick labels.

        labelrotation : float
            Tick label rotation



        Examples
        --------

        Usage ::

            ax.tick_params(direction='out', length=6, width=2, colors='r',
                           grid_color='r', grid_alpha=0.5)

        This will make all major ticks be red, pointing out of the box,
        and with dimensions 6 points by 2 points.  Tick labels will
        also be red.  Gridlines will be red and translucent.

        """


        
        
        
class CanvasModel(UIModelBase):
    tid = 'canvas_model'

    _ATTRIBUTES = {

        'figure_title': {
                'default_value': wx.EmptyString, 
                'type': str
        },
        'figure_title_x': {
                'default_value': 0.5, 
                'type': float
        },        
        'figure_title_y': {
                'default_value': 0.95, 
                'type': float
        },
        'figure_title_fontsize': {
                'default_value': 16, 
                'type': int
        },
        'figure_title_weight': {
                'default_value': 'normal', 
                'type': str
        },                
        'figure_title_ha': {
                'default_value': 'center', 
                'type': str
        },                  
        'figure_title_va': {
                'default_value': 'center', 
                'type': str
        },                   
        'spine_right_visibility': {
                'default_value': True, 
                'type': bool
        },  
        'spine_left_visibility': {
                'default_value': True, 
                'type': bool
        },  
        'spine_bottom_visibility': {
                'default_value': True, 
                'type': bool
        },  
        'spine_top_visibility': {
                'default_value': True, 
                'type': bool
        },        
               
        'xaxis_visibility': {
                'default_value': True, 
                'type': bool
        },          
        'yaxis_visibility': {
                'default_value': True, 
                'type': bool
        },                 
        'rect': {
                #'default_value': (0.0, 0.0, 1.0, 1.0), 
                'default_value': (0.1, 0.1, 0.8, 0.8), 
                'type': (tuple, float, 4)  
        },
        'xscale': {
                'default_value': 'linear', #["linear", "log", "symlog", "logit"]
                'type': str
        },
        'yscale': {
                'default_value': 'linear', 
                'type': str
        },
        'xlim': {
                'default_value': (0.001, 1000.0), 
                'type': (tuple, float, 2)  
        },        
        'ylim': {
                'default_value': (0.001, 1000.0), 
                'type': (tuple, float, 2)  
        },
        # Grid Properties
        'xgrid_major_visible': {
                'default_value': True, 
                'type': bool
        },     
        'xgrid_major_color': {
                'default_value': '#A9A9A9',
                'type': str
        },  
        'xgrid_major_alpha': {
                'default_value': 1.0, 
                'type': float
        },  
        'xgrid_major_linestyle': {
                'default_value': '-', 
                'type': str
        }, 
        'xgrid_major_linewidth': {
                'default_value': 1.4, 
                'type': float
        },     
        'xgrid_minor_visible': {
                'default_value': True, 
                'type': bool
        },                  
        'xgrid_minor_color': {
                'default_value': '#A9A9A9',
                'type': str
        },
        'xgrid_minor_alpha': {
                'default_value': 1.0, 
                'type': float
        },  
        'xgrid_minor_linestyle': {
                'default_value': '-', 
                'type': str
        }, 
        'xgrid_minor_linewidth': {
                'default_value': 0.7, 
                'type': float
        },   
        'ygrid_major_visible': {
                'default_value': True, 
                'type': bool
        },                   
        'ygrid_major_color': {
                'default_value': '#A9A9A9',
                'type': str
        }, 
        'ygrid_major_alpha': {
                'default_value': 1.0, 
                'type': float
        },          
        'ygrid_major_linestyle': {
                'default_value': '-', 
                'type': str
        }, 
        'ygrid_major_linewidth': {
                'default_value': 1.4, 
                'type': float
        },                     
        'ygrid_minor_visible': {
                'default_value': True, 
                'type': bool
        },  
        'ygrid_minor_color': {
                'default_value': '#A9A9A9',
                'type': str
        },
        'ygrid_minor_alpha': {
                'default_value': 1.0, 
                'type': float
        },                  
        'ygrid_minor_linestyle': {
                'default_value': '-', 
                'type': str
        }, 
        'ygrid_minor_linewidth': {
                'default_value': 0.7, 
                'type': float
        },
        # Tick locator        
        'xgrid_major_locator': {
                'default_value': 5, 
                'type': int
        },                
        'xgrid_minor_locator': {
                'default_value': 20, 
                'type': int
        },    
        'ygrid_major_locator': {
                'default_value': 5, 
                'type': int
        },                
        'ygrid_minor_locator': {
                'default_value': 20, 
                'type': int
        },
        # Tick visibility   
        'xtick_labelbottom': {
                'default_value': True, 
                'type': bool
        },    
        'xtick_labeltop': {
                'default_value': False, 
                'type': bool
        },
        'ytick_labelleft': {
                'default_value': True, 
                'type': bool
        },
        'ytick_labelright': {
                'default_value': False, 
                'type': bool
        },                   
        # Tick visibility (detailed)   
        'xtick_major_bottom': {
                'default_value': True, 
                'type': bool
        },
        'xtick_major_top': {
                'default_value': True, 
                'type': bool
        },        
        'xtick_minor_bottom': {
                'default_value': True, 
                'type': bool
        },       
        'xtick_minor_top': {
                'default_value': True, 
                'type': bool
        },             
        'ytick_major_left': {
                'default_value': True, 
                'type': bool
        },
        'ytick_major_right': {
                'default_value': True, 
                'type': bool
        },
        'ytick_minor_left': {
                'default_value': True, 
                'type': bool
        },   
        'ytick_minor_right': {
                'default_value': True, 
                'type': bool
        },  
        # Tick visibility   
        'xtick_bottom': {
                'default_value': True, 
                'type': bool
        },    
        'xtick_top': {
                'default_value': False, 
                'type': bool
        },
        'ytick_left': {
                'default_value': True, 
                'type': bool
        },
        'ytick_right': {
                'default_value': False, 
                'type': bool
        },                   
        # Tick direction        
        'xtick_direction': {
                'default_value': 'out', 
                'type': str
        },                
  
        'ytick_direction': {
                'default_value': 'out',
                'type': str
        },                
        # Tick length   
        'xtick_major_size': {
                'default_value': 10.0, 
                'type': float
        },  
        'xtick_minor_size': {
                'default_value': 5.0, 
                'type': float
        },           
        'ytick_major_size': {
                'default_value': 10.0, 
                'type': float
        }, 
        'ytick_minor_size': {
                'default_value': 5.0, 
                'type': float
        },     
        # Tick width                 
        'xtick_major_width': {
                'default_value': 1.4, 
                'type': float
        },          
        'xtick_minor_width': {
                'default_value': 5, 
                'type': float
        },           
        'ytick_major_width': {
                'default_value': 10, 
                'type': float
        }, 
        'ytick_minor_width': {
                'default_value': 5, 
                'type': float
        },                  
        # Tick pad                 
        'xtick_major_pad': {
                'default_value': 3.5, 
                'type': float
        },          
        'xtick_minor_pad': {
                'default_value': 3.4, 
                'type': float
        },           
        'ytick_major_pad': {
                'default_value': 3.5, 
                'type': float
        }, 
        'ytick_minor_pad': {
                'default_value': 3.4, 
                'type': float
        },
        # Tick label size       
        'xtick_labelsize': {
                'default_value': '10.0', 
                'type': str
        },                
        'ytick_labelsize': {
                'default_value': '10.0',
                'type': str
        },
        # Tick color    
        'xtick_color': {
                'default_value': 'black', 
                'type': str
        },                
        'ytick_color': {
                'default_value': 'black', 
                'type': str
        }, 
        # Tick label color     
        'xtick_labelcolor': {
                'default_value': 'black', 
                'type': str
        },                
        'ytick_labelcolor': {
                'default_value': 'black', 
                'type': str
        },    
        # Tick label rotation   
        'xtick_labelrotation': {
                'default_value': 0.0, 
                'type': float
        },                
        'ytick_labelrotation': {
                'default_value': 0.0,
                'type': float
        },
        # Axes
        'axes_facecolor': {
                'default_value': 'white', 
                'type': str
        },   
        'axes_edgecolor': {
                'default_value': 'black', 
                'type': str
        },        
        'axes_axisbelow': {
                'default_value': 'line', 
                'type': str
        },                 
    }  
        
    def __init__(self, controller_uid, **base_state):      
        super().__init__(controller_uid, **base_state) 
    
    
    
    
class Canvas(UIViewBase, FigureCanvas):  
    tid = 'canvas'


    def __init__(self, controller_uid):
        
        print ('\nCanvas.__init__')
        
        try:
            UIViewBase.__init__(self, controller_uid)
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            #
            parent_uid = UIM._getparentuid(self._controller_uid)
            parent_obj = UIM.get(parent_uid)
            
            print (self._controller_uid, parent_obj.view, 
                   controller.model.name) #TODO: self.model.name
            #
            self._postpone_draw = False
            #
            wx_parent = parent_obj.view
            #
            self.figure = Figure()    
            
            self.figure.set_facecolor('lightblue')
            
            FigureCanvas.__init__(self, wx_parent, -1, self.figure)

            
            controller.model.figure_title = 'Titulo'
            
            share_x = True

        
            self.base_axes = Axes(self.figure, controller.model.rect,
                                      facecolor=None,
                                      frameon=True,
                                      sharex=None,  # use Axes instance's xaxis info
                                      sharey=None,  # use Axes instance's yaxis info
                                      label='',
                                      xscale=controller.model.xscale,
                                      yscale=controller.model.yscale,
                                      xlim=controller.model.xlim,
                                      ylim=controller.model.ylim
            )
                                      #**base_axes_properties)
            self.figure.add_axes(self.base_axes)
            self.base_axes.set_zorder(0)
            #
            # Add 
            
            if share_x:
                self.plot_axes = Axes(self.figure, 
                                 rect=self.base_axes.get_position(True), 
                                 sharey=self.base_axes, 
                                 sharex=self.base_axes, 
                                 frameon=False
                )
            else:    
                self.plot_axes = Axes(self.figure, 
                                 rect=self.base_axes.get_position(True), 
                                 sharey=self.base_axes, 
                                 frameon=False
                )
                self.plot_axes.set_xlim(xlim=controller.model.xlim,
                                                ylim=controller.model.ylim
                )
            
            self.figure.add_axes(self.plot_axes)
            self.plot_axes.xaxis.set_visible(False)
            self.plot_axes.yaxis.set_visible(False)        
            self.plot_axes.set_zorder(1)
            #
            #
            #
            #
            self.set_axis_visibility('x', controller.model.xaxis_visibility)
            self.set_axis_visibility('y', controller.model.yaxis_visibility)
            #
            self.set_spine_visibility('right', 
                                      controller.model.spine_right_visibility) 
            self.set_spine_visibility('left', 
                                      controller.model.spine_left_visibility) 
            self.set_spine_visibility('bottom', 
                                      controller.model.spine_bottom_visibility) 
            self.set_spine_visibility('top', 
                                      controller.model.spine_top_visibility) 
            #
            if controller.model.figure_title:
                self.suptitle(controller.model.figure_title, 
                    x=controller.model.figure_title_x, y=controller.model.figure_title_y, 
                    ha=controller.model.figure_title_ha, va=controller.model.figure_title_va,
                    size=controller.model.figure_title_fontsize, 
                    weight=controller.model.figure_title_weight
                )
                
            #grid_color, grid_alpha, grid_linewidth, grid_linestyle
            #
            self._load_locator_properties()
            self._load_ticks_properties()
            self._load_grids_properties()
            #
            self.mpl_connect('motion_notify_event', self.on_track_move)
            #
            
            
        except Exception as e:        
            print ('ERROR IN Canvas.PostInit:', e)
            raise
        # matplotlib.axis line 1439
        # gridkw = {'grid_' + item[0]: item[1] for item in kwargs.items()}
        

    def _load_locator_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self.set_locator('x', 'major', 
                                     controller.model.xgrid_major_locator)
        self.set_locator('x', 'minor', 
                                     controller.model.xgrid_minor_locator)
        self.set_locator('y', 'major', 
                                     controller.model.ygrid_major_locator)
        self.set_locator('y', 'minor', 
                                     controller.model.ygrid_minor_locator)        

    def _load_ticks_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        self.base_axes.tick_params(
            top=(controller.model.xtick_top and controller.model.xtick_major_top),
            bottom=(controller.model.xtick_bottom and controller.model.xtick_major_bottom),
            labeltop=(controller.model.xtick_labeltop and controller.model.xtick_major_top),
            labelbottom=(controller.model.xtick_labelbottom and controller.model.xtick_major_bottom),
            left=(controller.model.ytick_left and controller.model.ytick_major_left),
            right=(controller.model.ytick_right and controller.model.ytick_major_right),
            labelleft=(controller.model.ytick_labelleft and controller.model.ytick_major_left),
            labelright=(controller.model.ytick_labelright and controller.model.ytick_major_right),
            which='major'
        )
        self.base_axes.tick_params(
            top=(controller.model.xtick_top and controller.model.xtick_minor_top),
            bottom=(controller.model.xtick_bottom and controller.model.xtick_minor_bottom),
            labeltop=(controller.model.xtick_labeltop and controller.model.xtick_minor_top),
            labelbottom=(controller.model.xtick_labelbottom and controller.model.xtick_minor_bottom),
            left=(controller.model.ytick_left and controller.model.ytick_minor_left),
            right=(controller.model.ytick_right and controller.model.ytick_minor_right),
            labelleft=(controller.model.ytick_labelleft and controller.model.ytick_minor_left),
            labelright=(controller.model.ytick_labelright and controller.model.ytick_minor_right),
            which='minor'
        )  
        
        self.base_axes.tick_params(axis='x', which='major', size=controller.model.xtick_major_size)
        self.base_axes.tick_params(axis='x', which='minor', size=controller.model.xtick_minor_size)
        self.base_axes.tick_params(axis='y', which='major', size=controller.model.ytick_major_size)
        self.base_axes.tick_params(axis='y', which='minor', size=controller.model.ytick_minor_size)
        
        
        
    def _load_grids_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self.base_axes.grid(controller.model.xgrid_major_visible, 
                        axis='x', which='major', 
                        color=controller.model.xgrid_major_color,
                        linestyle=controller.model.xgrid_major_linestyle, 
                        linewidth=controller.model.xgrid_major_linewidth
        )
        self.base_axes.grid(controller.model.xgrid_minor_visible, 
                        axis='x', which='minor', 
                        color=controller.model.xgrid_minor_color,
                        linestyle=controller.model.xgrid_minor_linestyle, 
                        linewidth=controller.model.xgrid_minor_linewidth
        )
        self.base_axes.grid(controller.model.ygrid_major_visible, 
                        axis='y', which='major', 
                        color=controller.model.ygrid_major_color,
                        linestyle=controller.model.ygrid_major_linestyle, 
                        linewidth=controller.model.ygrid_major_linewidth
        )
        self.base_axes.grid(controller.model.ygrid_minor_visible, 
                        axis='y', which='minor', 
                        color=controller.model.ygrid_minor_color,
                        linestyle=controller.model.ygrid_minor_linestyle, 
                        linewidth=controller.model.ygrid_minor_linewidth
        )


    def draw(self, drawDC=None):
        if not self._postpone_draw:
            super().draw(drawDC)


    def suptitle(self, text, **kwargs):
        print ('suptitle:', text, kwargs)
        try:
            suptitle_text = self.figure.suptitle(text, **kwargs)
            return suptitle_text
        except:
            raise

    def set_axis_visibility(self, axis, visibility):
        if axis == 'x':
            ax = self.base_axes.xaxis
        elif axis == 'y':
            ax = self.base_axes.yaxis
        else:
            raise Exception('Invalid axis [{}].'.format(axis))
        ax.set_visible(visibility)
         
    def set_spine_visibility(self, spine, visibility):
        try:
            self.base_axes.spines[spine].set_visible(visibility)
        except:
            raise
            
    def set_position(self, rect):
        try:
            self.base_axes.set_position(rect)
            self.plot_axes.set_position(rect)
        except:
            raise
                        

    def on_track_move(self, event):
        #print ('on_track_move:', event.xdata, event.ydata)
        pass


    # Only for base_axes
    def set_lim(self, axis, lim):
        if axis == 'x':
            return self.base_axes.set_xlim(lim)
        elif axis == 'y':
            return self.base_axes.set_ylim(lim)
        else:
            raise Exception('Invalid axis [{}].'.format(axis))        


    # Only for base_axes
    def set_scale(self, axis, scale):            
        if axis == 'x':
            return self.base_axes.set_xscale(scale)
        elif axis == 'y':
            return self.base_axes.set_yscale(scale)
        else:
            raise Exception('Invalid axis [{}].'.format(axis))   
  

    def set_tick_params(self, axis, which, **kwargs):  
        if axis not in ['x', 'y', 'both']:
            raise Exception('Invalid axis.')
        #    
        if which not in ['minor', 'major', 'both']:
            raise Exception('Invalid which.') 
        #
        
        b = kwargs.pop('grid_visible', None)
        if b is None:
            if axis in ['x', 'both']:
                axis_ = self.base_axes.xaxis
                try:
                    axis_.set_tick_params(which=which, **kwargs)
                except:
                    raise
                finally:
                    axis_.stale = True 
            if axis in ['y', 'both']:
                axis_ = self.base_axes.yaxis
                try:
                    axis_.set_tick_params(which=which, **kwargs)
                except:
                    raise
                finally:
                    axis_.stale = True                    
            
        else:    
            kwargs['gridOn'] = b
            if axis in ['x', 'both']:
                axis_ = self.base_axes.xaxis
                if which in ['major', 'both']:
                    try:
                        old_b = axis_._gridOnMajor
                        axis_._gridOnMajor = b
                        axis_.set_tick_params(which='major', **kwargs)
                    except:
                        axis_._gridOnMajor = old_b
                        raise
                    finally:
                        axis_.stale = True 
                    
                if which in ['minor', 'both']:
                    try:
                        old_b = axis_._gridOnMinor
                        axis_._gridOnMinor = b
                        axis_.set_tick_params(which='minor', **kwargs)
                    except:
                        axis_._gridOnMinor = old_b
                        raise
                    finally:
                        axis_.stale = True 

            if axis in ['y', 'both']:
                axis_ = self.base_axes.yaxis
                if which in ['major', 'both']:
                    try:
                        old_b = axis_._gridOnMajor
                        axis_._gridOnMajor = b
                        axis_.set_tick_params(which='major', **kwargs)
                    except:
                        axis_._gridOnMajor = old_b
                        raise
                    finally:
                        axis_.stale = True 
                    
                if which in ['minor', 'both']:
                    try:
                        old_b = axis_._gridOnMinor
                        axis_._gridOnMinor = b
                        axis_.set_tick_params(which='minor', **kwargs)
                    except:
                        axis_._gridOnMinor = old_b
                        raise
                    finally:
                        axis_.stale = True                     
                
                    


    def set_locator(self, axis, which, value):
        try: 
            if axis not in ['x', 'y']:
                raise Exception('Invalid axis.')
            if which not in ['minor', 'major']:
                raise Exception('Invalid which.')    
            if axis == 'x':
                axis_ = self.base_axes.xaxis
                val_0, val_1 = self.base_axes.get_xlim()
            else:
                axis_ = self.base_axes.yaxis            
                val_0, val_1 = self.base_axes.get_ylim()  
                
            val_min = min(val_0, val_1)    
            val_max = max(val_0, val_1)
            n_grid_lines = (val_max - val_min)/value   

            if which == 'major':
                axis_.set_major_locator(MultipleLocator(n_grid_lines))
            else:
                axis_.set_minor_locator(MultipleLocator(n_grid_lines))
                
        except Exception as e:
            raise
        

    def set_axisbelow(self, b):
        self.base_axes.set_axisbelow(b)
        
    def set_facecolor(self, color):
        self.base_axes.set_facecolor(color)
        
    def set_edgecolor(self, color):
        self.base_axes.patch.set_edgecolor(color)


        '''
        grid_color, grid_alpha, grid_linewidth, grid_linestyle
        
        grid_color : color
        Changes the gridline color to the given mpl color spec.
        grid_alpha : float
        Transparency of gridlines: 0 (transparent) to 1 (opaque).
        grid_linewidth : float
        Width of gridlines in points.
        grid_linestyle : string

        #gridkw = {'grid_' + item[0]: item[1] for item in kwargs.items()}
        self.base_axes.xaxis._gridOnMajor = value
        self.base_axes.xaxis.set_tick_params(which='major', 
                                             gridOn=self._gridOnMajor,
                                 **gridkw
        )
        self.base_axes.xaxis.stale = True
        '''

        """
        def set_ticks_locator(self, value, axis, which):  
            
            if axis == 'x':
                self.base_axes.xaxisset_xscale(scale)
            elif axis == 'y':
                return self.base_axes.set_yscale(scale)
            else:
                raise Exception('Invalid axis [{}].'.format(axis))   
            
            self.base_axes.yaxis.set_minor_locator(MultipleLocator(value))
    
    
        """

        #xax.grid(color='r', linestyle='-', linewidth=2)


        # self._gridOnMajor = True
        # self._gridOnMinor = True
        
#        self.base_axes.xaxis.set_tick_params(which='minor', 
#                                    gridOn=self._gridOnMinor, **gridkw
#        )


    
#       # matplotlib.axes._base line 2848
#       def tick_params(self, axis='both', **kwargs):
        """Change the appearance of ticks, tick labels, and gridlines.

        Parameters
        ----------
        axis : {'x', 'y', 'both'}, optional
            Which axis to apply the parameters to.

        Other Parameters
        ----------------

        axis : {'x', 'y', 'both'}
            Axis on which to operate; default is 'both'.

        reset : bool
            If *True*, set all parameters to defaults
            before processing other keyword arguments.  Default is
            *False*.

        which : {'major', 'minor', 'both'}
            Default is 'major'; apply arguments to *which* ticks.

        direction : {'in', 'out', 'inout'}
            Puts ticks inside the axes, outside the axes, or both.

        length : float
            Tick length in points.

        width : float
            Tick width in points.

        color : color
            Tick color; accepts any mpl color spec.

        pad : float
            Distance in points between tick and label.

        labelsize : float or str
            Tick label font size in points or as a string (e.g., 'large').

        labelcolor : color
            Tick label color; mpl color spec.

        colors : color
            Changes the tick color and the label color to the same value:
            mpl color spec.

        zorder : float
            Tick and label zorder.

        bottom, top, left, right : bool
            Whether to draw the respective ticks.

        labelbottom, labeltop, labelleft, labelright : bool
            Whether to draw the respective tick labels.

        labelrotation : float
            Tick label rotation

        grid_color : color
            Changes the gridline color to the given mpl color spec.

        grid_alpha : float
            Transparency of gridlines: 0 (transparent) to 1 (opaque).

        grid_linewidth : float
            Width of gridlines in points.

        grid_linestyle : string
            Any valid :class:`~matplotlib.lines.Line2D` line style spec.

        Examples
        --------

        Usage ::

            ax.tick_params(direction='out', length=6, width=2, colors='r',
                           grid_color='r', grid_alpha=0.5)

        This will make all major ticks be red, pointing out of the box,
        and with dimensions 6 points by 2 points.  Tick labels will
        also be red.  Gridlines will be red and translucent.

        """



            
        """
        x = kwargs.pop('x', 0.5)
        y = kwargs.pop('y', 0.98)

        if ('horizontalalignment' not in kwargs) and ('ha' not in kwargs):
            kwargs['horizontalalignment'] = 'center'
        if ('verticalalignment' not in kwargs) and ('va' not in kwargs):
            kwargs['verticalalignment'] = 'top'

        if 'fontproperties' not in kwargs:
            if 'fontsize' not in kwargs and 'size' not in kwargs:
                kwargs['size'] = rcParams['figure.titlesize']
            if 'fontweight' not in kwargs and 'weight' not in kwargs:
                kwargs['weight'] = rcParams['figure.titleweight']

        sup = self.text(x, y, t, **kwargs)
        if self._suptitle is not None:
            self._suptitle.set_text(t)
            self._suptitle.set_position((x, y))
            self._suptitle.update_from(sup)
            sup.remove()
        else:
            self._suptitle = sup
        if self._layoutbox is not None:
            # assign a layout box to the suptitle...
            figlb = self._layoutbox
            self._suptitle._layoutbox = layoutbox.LayoutBox(
                                            parent=figlb,
                                            name=figlb.name+'.suptitle')
            for child in figlb.children:
                if not (child == self._suptitle._layoutbox):
                    w_pad, h_pad, wspace, hspace =  \
                            self.get_constrained_layout_pads(
                                    relative=True)
                    layoutbox.vstack([self._suptitle._layoutbox, child],
                                     padding=h_pad*2., strength='required')
        self.stale = True
        return self._suptitle
    
        """
        
        
        """
        
        class _AxesBase(martist.Artist):
        
        
        Build an :class:`Axes` instance in
        :class:`~matplotlib.figure.Figure` *fig* with
        *rect=[left, bottom, width, height]* in
        :class:`~matplotlib.figure.Figure` coordinates

        Optional keyword arguments:

          ================   =========================================
          Keyword            Description
          ================   =========================================
          *adjustable*       [ 'box' | 'datalim' ]
          *alpha*            float: the alpha transparency (can be None)
          *anchor*           [ 'C', 'SW', 'S', 'SE', 'E', 'NE', 'N',
                               'NW', 'W' ]
          *aspect*           [ 'auto' | 'equal' | aspect_ratio ]
          *autoscale_on*     bool; whether to autoscale the *viewlim*
          *axisbelow*        [ bool | 'line' ] draw the grids
                             and ticks below or above most other artists,
                             or below lines but above patches
          *cursor_props*     a (*float*, *color*) tuple
          *figure*           a :class:`~matplotlib.figure.Figure`
                             instance
          *frame_on*         bool; whether to draw the axes frame
          *label*            the axes label
          *navigate*         bool
          *navigate_mode*    [ 'PAN' | 'ZOOM' | None ] the navigation
                             toolbar button status
          *position*         [left, bottom, width, height] in
                             class:`~matplotlib.figure.Figure` coords
          *sharex*           an class:`~matplotlib.axes.Axes` instance
                             to share the x-axis with
          *sharey*           an class:`~matplotlib.axes.Axes` instance
                             to share the y-axis with
          *title*            the title string
          *visible*          bool, whether the axes is visible
          *xlabel*           the xlabel
          *xlim*             (*xmin*, *xmax*) view limits
          *xscale*           [%(scale)s]
          *xticklabels*      sequence of strings
          *xticks*           sequence of floats
          *ylabel*           the ylabel strings
          *ylim*             (*ymin*, *ymax*) view limits
          *yscale*           [%(scale)s]
          *yticklabels*      sequence of strings
          *yticks*           sequence of floats
          ================   =========================================
        """