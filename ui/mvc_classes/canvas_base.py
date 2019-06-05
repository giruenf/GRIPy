# -*- coding: utf-8 -*-

import matplotlib
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.ticker import NullLocator
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import LogLocator
from matplotlib.ticker import LogFormatterMathtext

from matplotlib import style as mstyle 
import matplotlib.ticker as mticker
from matplotlib import rcParams

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 
from app import pubsub 
from app import log


# From matplotlib.axes._base.set_xscale
CANVAS_SCALES = ["linear", "log", "symlog", "logit"]



# From: matplotlib\backends\backend_wxagg.py
"""
    The FigureCanvas contains the figure and does event handling.

    In the wxPython backend, it is derived from wxPanel, and (usually)
    lives inside a frame instantiated by a FigureManagerWx. The parent
    window probably implements a wxSizer to control the displayed
    control size - but we give a hint as to our preferred minimum
    size.
    """



"""
O CanvasBaseController eh a classe de base para todos objeto de Plotagem!!!
"""
class CanvasBaseController(UIControllerObject):
    tid = None

    _ATTRIBUTES = {
            
        # Top level properties    
        'rect': {
                'default_value': (0.1, 0.1, 0.8, 0.8), 
                #'default_value': (0.0, 0.0, 1.0, 1.0), 
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
                'default_value': (0.0, 100.0), 
                'type': (tuple, float, 2)  
        },        
        'ylim': {
                'default_value': (0.0, 100.0), 
                'type': (tuple, float, 2)
        },
        
        
        ##
        'xaxis_labeltext': {
                'default_value': 'X Axis label', 
                'type': str                
        },
        'yaxis_labeltext': {
                'default_value': 'Y Axis label', 
                'type': str                
        },       
                
        # Figure properties
        'figure_facecolor': {
                'default_value': 'white', #'lightyellow',
                'type': str
        },


        'figure_titletext': {
                'default_value': 'Figure Title', #wx.EmptyString, 
                'type': str
        },
        'figure_titlex': {
                'default_value': 0.5, 
                'type': float
        },        
        'figure_titley': {
                'default_value': 0.95, 
                'type': float
        },
        'figure_titlesize': {
                'default_value': '15.0', 
                'type': str
        },
        'figure_titleweight': {
                'default_value': 'normal', 
                'type': str
        },                
        'figure_titleha': {
                'default_value': 'center', 
                'type': str
        },                  
        'figure_titleva': {
                'default_value': 'center', 
                'type': str
        },    
          
        # Axes properties
        'axes_facecolor': {
                'default_value': 'ivory', #'white', 
                'type': str
        },   
        'axes_edgecolor': {
                'default_value': 'red', 
                'type': str
        },        
        'axes_axisbelow': {
                'default_value': 'line', # 'line', True, False
                'type': str
        },  
        'axes_linewidth': {
                'default_value': 0.8, 
                'type': float
        },                
                
                
        'xgrid_major': {
                'default_value': True, 
                'type': bool
        },   
        'xgrid_minor': {
                'default_value': True, 
                'type': bool
        },           
        'ygrid_major': {
                'default_value': True, 
                'type': bool
        },   
        'ygrid_minor': {
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


        # Grid locator        
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




        'axes_labelcolor': {
                'default_value': 'black', 
                'type': str
        },   
        'axes_labelpad': {        
                'default_value': 4.0, 
                'type': float
        },  
        'axes_labelsize': {
                'default_value': '12.0', 
                'type': str
        },                 
        'axes_labelweight': {        
                'default_value': 'normal',
                'type': str
        },  


        'axes_titletextcenter': {
                'default_value': 'Axes title (center)',
                'type': str
        },
        'axes_titletextleft': {
                'default_value': 'Axes title (left)', 
                'type': str
        },
        'axes_titletextright': {
                'default_value': 'Axes title (right)', 
                'type': str
        },
                
        'axes_titlecolor': {
                'default_value': 'black', 
                'type': str
        },         
        'axes_titlepad': {        
                'default_value': 6.0, 
                'type': float
        },  
        'axes_titlesize': {
                'default_value': 'large', 
                'type': str
        },                 
        'axes_titleweight': {        
                'default_value': 'normal',
                'type': str
        },  
         
                
                
        # Spines visibility       
        'axes_spines_right': {
                'default_value': True, 
                'type': bool
        },  
        'axes_spines_left': {
                'default_value': True, 
                'type': bool
        },  
        'axes_spines_bottom': {
                'default_value': True, 
                'type': bool
        },  
        'axes_spines_top': {
                'default_value': True, 
                'type': bool
        },        
                
        # Spines location        
        'axes_spines_right_position': {
                'default_value': ('axes', 1.0), #   ('axes',0.5)      ['outward', 'axes', 'data']
                'type': (tuple, str, 2)  
        },  
        'axes_spines_left_position': {
                'default_value': ('axes', 0.0), 
                'type': (tuple, str, 2)  
        },  
        'axes_spines_bottom_position': {
                'default_value': ('axes', 0.0), 
                'type': (tuple, str, 2)  
        },  
        'axes_spines_top_position': {
                'default_value': ('axes', 1.0), 
                'type': (tuple, str, 2)                 
        },    

     
                
        'xaxis_visibility': {
                'default_value': True, 
                'type': bool
        },          
        'yaxis_visibility': {
                'default_value': True, 
                'type': bool
        },                 

        

                
                

                           
            
            
        # Tick label visibility   
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
        'xtick_minor_visible': {
                'default_value': True, 
                'type': bool
        },        
        'ytick_minor_visible': {
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
                'default_value': 3.5, #10.0, 
                'type': float
        },  
        'xtick_minor_size': {
                'default_value': 2.0, #5.0, 
                'type': float
        },           
        'ytick_major_size': {
                'default_value': 3.5, #10.0,
                'type': float
        }, 
        'ytick_minor_size': {
                'default_value': 2.0, #5.0, 
                'type': float
        },     
                
        # Tick width                 
        'xtick_major_width': {
                'default_value': 0.8, #1.4, 
                'type': float
        },          
        'xtick_minor_width': {
                'default_value': 0.6, #5, 
                'type': float
        },           
        'ytick_major_width': {
                'default_value': 0.8, #1.4,  
                'type': float
        }, 
        'ytick_minor_width': {
                'default_value': 0.6, #5, 
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
        }        
        
        
        
        
    }  

    
    def __init__(self, **state):
        super().__init__(**state)
          
        
    def PostInit(self):
        
        print('CanvasBaseController.PostInit')
        #
        self.subscribe(self.on_change_figure_facecolor, 
                       'change.figure_facecolor')
        #
        self.subscribe(self.on_change_spine, 'change.axes_spines_right')
        self.subscribe(self.on_change_spine, 'change.axes_spines_left')
        self.subscribe(self.on_change_spine, 'change.axes_spines_bottom')
        self.subscribe(self.on_change_spine, 'change.axes_spines_top')
        self.subscribe(self.on_change_spine,
                                       'change.axes_spines_right_position')
        self.subscribe(self.on_change_spine,
                                       'change.axes_spines_left_position')
        self.subscribe(self.on_change_spine,
                                       'change.axes_spines_bottom_position')
        self.subscribe(self.on_change_spine,
                                       'change.axes_spines_top_position')        
        #
        self.subscribe(self.on_change_axis_visibility, 
                                           'change.xaxis_visibility')
        self.subscribe(self.on_change_axis_visibility, 
                                           'change.yaxis_visibility')
        #
        self.subscribe(self.on_change_rect, 'change.rect')
        #
        self.subscribe(self.on_change_locator, 'change.xgrid_major_locator')
        self.subscribe(self.on_change_locator, 'change.xgrid_minor_locator')
        self.subscribe(self.on_change_locator, 'change.ygrid_major_locator')
        self.subscribe(self.on_change_locator, 'change.ygrid_minor_locator') 
        #
        #
        self.subscribe(self.on_change_axes_properties, 'change.axes_facecolor')
        self.subscribe(self.on_change_axes_properties, 'change.axes_edgecolor')
        self.subscribe(self.on_change_axes_properties, 'change.axes_axisbelow')
        self.subscribe(self.on_change_axes_properties, 'change.axes_linewidth')
        #
        
        # Grid Visibility
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_major')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_minor')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_major')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_minor')
        # Major X Grid Properties
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_major_color')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_major_alpha')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_major_linestyle')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_major_linewidth')  
        # Major X Grid Properties
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_minor_color')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_minor_alpha')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_minor_linestyle')
        self.subscribe(self.on_change_grid_parameters, 'change.xgrid_minor_linewidth')  
        # Major Y Grid Properties
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_major_color')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_major_alpha')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_major_linestyle')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_major_linewidth') 
        # Minor Y Grid Properties
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_minor_color')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_minor_alpha')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_minor_linestyle')
        self.subscribe(self.on_change_grid_parameters, 'change.ygrid_minor_linewidth')          

        #
        self.subscribe(self.on_change_text_properties, 'change.xaxis_labeltext')
        self.subscribe(self.on_change_text_properties, 'change.yaxis_labeltext')
        #        
        self.subscribe(self.on_change_text_properties, 'change.axes_labelcolor')
        self.subscribe(self.on_change_text_properties, 'change.axes_labelpad')
        self.subscribe(self.on_change_text_properties, 'change.axes_labelsize')
        self.subscribe(self.on_change_text_properties, 'change.axes_labelweight')
        #
        self.subscribe(self.on_change_text_properties, 'change.axes_titletextleft')
        self.subscribe(self.on_change_text_properties, 'change.axes_titletextcenter')
        self.subscribe(self.on_change_text_properties, 'change.axes_titletextright')
        self.subscribe(self.on_change_text_properties, 'change.axes_titlecolor')
        self.subscribe(self.on_change_text_properties, 'change.axes_titlepad')
        self.subscribe(self.on_change_text_properties, 'change.axes_titlesize')
        self.subscribe(self.on_change_text_properties, 'change.axes_titleweight')    
        #
        self.subscribe(self.on_change_text_properties, 'change.figure_titletext')
        self.subscribe(self.on_change_text_properties, 'change.figure_titlex')
        self.subscribe(self.on_change_text_properties, 'change.figure_titley')
        self.subscribe(self.on_change_text_properties, 'change.figure_titlesize')
        self.subscribe(self.on_change_text_properties, 'change.figure_titleweight')
        self.subscribe(self.on_change_text_properties, 'change.figure_titleha')
        self.subscribe(self.on_change_text_properties, 'change.figure_titleva')
        #           
        

        self.subscribe(self.on_change_lim, 'change.xlim')
        self.subscribe(self.on_change_lim, 'change.ylim')
        self.subscribe(self.on_change_scale, 'change.xscale')
        self.subscribe(self.on_change_scale, 'change.yscale')        

        ###
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
        ###
        
        #
        self.subscribe(self.on_change_minor_tick_visibility, 
                                               'change.xtick_minor_visible')
        self.subscribe(self.on_change_minor_tick_visibility, 
                                               'change.ytick_minor_visible')
        #
        print('CanvasBaseController.PostInit fim')


    def on_change_axes_properties(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        prop = key.split('_')[1]
    
        if prop == 'facecolor':
            self.view.set_axes_facecolor(new_value)
        elif prop == 'edgecolor':
            self.view.set_axes_edgecolor(new_value)            
        elif prop == 'axisbelow':
            self.view.set_axes_axisbelow(new_value)      
        elif prop == 'linewidth':   
            self.view.set_axes_axislinewidth(new_value)
        self.view.draw()  




    def on_change_grid_parameters(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
#        print ('\non_change_grid_params:', old_value, new_value, topic)
        key = topic.getName().split('.')[2]
        axis = key[0]           # x or y  (e.g. xgrid_major_color -> x)  
        keys = key.split('_')
        # Grid Visibility
        if len(keys) == 2:      
            _, which = keys
            kw = {}
            for param_key in ['color', 'alpha', 'linestyle', 'linewidth']:
                kw['grid_' + param_key] = self[axis + 'grid_' \
                                                  + which + '_' + param_key]
            self.view.set_grid_parameters(axis, which, gridOn=new_value, **kw)

        # Grid Properties    
        elif len(keys) == 3:    
            _, which, param_key = keys
            kw = {param_key: new_value}
            self.view.set_grid_parameters(axis, which, **kw)
        self.view.draw()
        

        
        
    def load_style(self, style_name):
        self.view._postpone_draw = True   
        print ('\nReseting style...')
        self._load_dict(rcParams)
        print ('Style Reseted.\n')
        if style_name != 'default':
            print ('\nSetting new style [{}]...'.format(style_name))
            lib_dict = mstyle.library.get(style_name)        
            self._load_dict(lib_dict)
            print ('Style {} Setted.\n'.format(style_name))
        self.view._postpone_draw = False
        self.view.draw()


    def _load_dict(self, lib_dict):
        for key, value in lib_dict.items():
            if key not in mstyle.core.STYLE_BLACKLIST:
                keys = key.split('.')
                new_key = '_'.join(keys)
                # TODO: Check verbose.fileo for app.log
                if keys[0] in ['keymap', 'pdf', 'ps', 'svg', 'polaraxes', 
                               'pgf', 'verbose', 'mathtext', 'date', 'backend',
                               'animation', 'agg', 'examples', 'savefig']:
                    # Do not load
                    continue 
                elif new_key == 'axes_prop_cycle':
                    # Do not load
                    continue     
                elif new_key == '_internal_classic_mode':
                    # Do not load
                    continue           
                
                elif keys[0] == 'grid':
                    print ('Will not load: {} = {} (canvas_base.py - line 80)'.format(new_key, value))
                elif keys[0] in ['xtick', 'ytick']:
                    print ('Loading: {} = {}'.format(new_key, value))
                    self[new_key] = value
                        
                elif keys[0] == 'axes' and keys[1] in ['facecolor', 
                         'edgecolor', 'axisbelow', 'grid', 'labelpad', 
                         'labelcolor', 'labelsize', 'labelweight',
                         'spines', 'titlepad', 'titlesize', 'titleweight']:
                    print ('Loading: {} = {}'.format(new_key, value))
                    self[new_key] = value
                  
                elif keys[0] == 'figure' and keys[1] in ['facecolor']:    
                    print ('Loading: {} = {}'.format(new_key, value))
                    self[new_key] = value
                    
                else:
                    print ('NOT LOADED: {} = {}'.format(new_key, value))
                    

    def on_change_figure_facecolor(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):
        try:
            self.view.set_figure_facecolor(new_value)
        except:
            key = topic.getName().split('.')[2]
            self.set_value_from_event(key, old_value)
        finally:
            self.view.draw()         
            
  

    def on_change_spine(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        spine = key.split('_')[2]
        
        try:
            if len(key.split('_')) == 3:
                self.view.set_spine_visibility(spine, new_value)
            elif len(key.split('_')) == 4 and key.split('_')[3] == 'position':
                self.view.set_spine_position(spine, new_value)
        except Exception as e:
            self.set_value_from_event(key, old_value)
        finally:
            self.view.draw()
        
           
            
    def on_change_axis_visibility(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):   
        key = topic.getName().split('.')[2]
        axis = key[0] # x or y  
        try:
            self.view.set_axis_visibility(axis, new_value)
        except:
            self.set_value_from_event(key, old_value)
        finally:
            self.view.draw()        
        
        
    def on_change_rect(self, old_value, new_value):  
        print ('on_change_rect')
        try:
            self.view.set_position(new_value)
            self.view.draw()  
        except:
            self.rect(old_value)

 
    # TODO: rever isso
    def on_change_locator(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):           
        key = topic.getName().split('.')[2]
        axis, which, _ =  key.split('_')
        axis = axis[0] 
        
        if axis == 'x' and self.xscale == 'log':
            return
        if axis == 'y' and self.yscale == 'log':
            return
        
        try:
            self.view.set_locator('multiple', axis, which, new_value)
        except:
            self.set_value_from_event(key, old_value)
        finally:
            self.view.draw()                                        



    def on_change_text_properties(self, old_value, new_value, topic=pubsub.AUTO_TOPIC): 
        attr_name = topic.getName().split('.')[2]
        who, param_key = attr_name.split('_') 
        axis = 'both'
        if who[0] == 'x' or who[0] == 'y':
            axis = who[0]
            who = who[1:]
        param = param_key[:5]
        key = param_key[5:]
        kw = {key: new_value}
        if who == 'axes':
            if param == 'label':
                who = 'axis'        # axes_label refers to Axis label
            elif key.startswith('text'):
                kw['loc'] = key[4:]
                kw.pop(key)         # key == textcenter, textleft or textright
                kw['text'] = new_value
        if who == 'axis':
            kw['axis'] = axis
        self.view.set_label_properties(who, **kw)
        self.view.draw()     






    def on_change_tick_params(self, old_value, new_value, 
                                                      topic=pubsub.AUTO_TOPIC):      

        #
#        print ('\non_change_tick_params:', old_value, new_value, topic)
                                                    
        try:
            key = topic.getName().split('.')[2]
            keys = key.split('_')
            if len(keys) == 3:
                axis_type_obj, which, param_key = keys
            elif len(keys) == 2:
                axis_type_obj, param_key = keys
                which = 'both'

            axis = axis_type_obj[0] # x or y  (e.g. xgrid -> x)  

            if param_key in ['top', 'bottom', 'left', 'right']:
                if param_key.startswith('label'):
                    param_key_2 = param_key[5:]
                    
                else:
                    param_key_2 = param_key
                
                
                if which == 'major' or which == 'both':
                    kw = {param_key: (self[axis+'tick_'+param_key] and 
                                      self[axis+'tick_major_'+param_key_2])
                    }
                    self.view.set_tick_params(axis, 'major', **kw)
                    
                if which == 'minor' or which == 'both':
                    kw = {param_key: (self[axis+'tick_'+param_key] and 
                                      self[axis+'tick_minor_'+param_key_2])
                    }
                    self.view.set_tick_params(axis, 'minor', **kw)
            else:
                print ('ELSE')
                kw = {param_key: new_value}
                self.view.set_tick_params(axis, which, **kw) 
        except Exception as e:
#            print ('\n\nERRO:', e)
            raise            
        #
        self.view.draw()    


    def on_change_minor_tick_visibility(self, old_value, new_value, 
                                                    topic=pubsub.AUTO_TOPIC): 
        attr_name = topic.getName().split('.')[2]
        who, _, _ = attr_name.split('_') 
        axis = who[0]
        
        self.view.set_minor_tick_visibility(axis, new_value)
        self.view.draw() 


 
    def on_change_lim(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):
#        print ('\nCanvasBaseController.on_change_lim:', old_value, new_value, topic.getName())
        key = topic.getName().split('.')[2]
        axis = key[0] # x or y  
        try:
            self.view.set_lim(axis, new_value)
            self.view.draw()
        except Exception as e:
            print ('ERROR:', e)
            raise
            #self.set_value_from_event(key, old_value)
            #self[key] = old_value
            
            
      
    def on_change_scale(self, old_value, new_value, topic=pubsub.AUTO_TOPIC):
#        print ('\nnCanvasBaseController.on_change_scale:', old_value, new_value, topic.getName())
        key = topic.getName().split('.')[2]
        if new_value not in CANVAS_SCALES:
            self.set_value_from_event(key, old_value)
            return
        axis = key[0] # x or y         
        self.view.set_scale(axis, new_value)
        self.view.draw()  

    
    
    
class CanvasBaseView(UIViewObject, FigureCanvas):  
    tid = None

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        #
        self.figure = Figure()
        #
        # Get wx parent from parent UIView object
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self._controller_uid)
        parent_controller = UIM.get(parent_uid)        
        wx_parent = parent_controller._get_wx_parent(self.tid)
        #
        FigureCanvas.__init__(self, wx_parent, -1, self.figure)



    def PostInit(self):
        # Here, the model object was created and model.PostInit() was called.    
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        self._postpone_draw = False
        #
        share_x = True
        #
        self.base_axes = Axes(self.figure, controller.rect,
                                  facecolor=None,
                                  frameon=True,
                                  sharex=None,  # use Axes instance's xaxis info
                                  sharey=None,  # use Axes instance's yaxis info
                                  label='',
                                  xscale=controller.xscale,
                                  yscale=controller.yscale,
                                  xlim=controller.xlim,
                                  ylim=controller.ylim
        )
        self.figure.add_axes(self.base_axes)
        self.base_axes.set_zorder(0)        
        #
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
            self.plot_axes.set_xlim(xlim=controller.xlim,
                                            ylim=controller.ylim
            )
        #
        self.figure.add_axes(self.plot_axes)
        #
        self.plot_axes.xaxis.set_visible(False)
        self.plot_axes.yaxis.set_visible(False)        
        self.plot_axes.set_zorder(1)        
        
        
        #
        self.set_axis_visibility('x', controller.xaxis_visibility)
        self.set_axis_visibility('y', controller.yaxis_visibility)


        #  
        self.figure.set_facecolor(controller.figure_facecolor)


        #
        self._load_spines_properties()
        self._load_locator_properties()
        self._load_ticks_properties()
        self._load_grids_properties()
        self._load_labels_properties()
        #
        
        
                                       

        #self._postpone_draw = True
        

    def _load_spines_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        #
        self.set_spine_visibility('right', controller.axes_spines_right) 
        self.set_spine_visibility('left', controller.axes_spines_left) 
        self.set_spine_visibility('bottom', 
                                          controller.axes_spines_bottom) 
        self.set_spine_visibility('top', controller.axes_spines_top) 
        #        
        self.set_spine_position('right', 
                                controller.axes_spines_right_position)
        self.set_spine_position('left',
                                controller.axes_spines_left_position)
        self.set_spine_position('bottom',
                                controller.axes_spines_bottom_position)
        self.set_spine_position('top',
                                controller.axes_spines_top_position)
        #
        self.base_axes.spines['left'].set_zorder(10)
        self.base_axes.spines['right'].set_zorder(10)
        self.base_axes.spines['top'].set_zorder(10)
        self.base_axes.spines['bottom'].set_zorder(10)          
        #
        
        
    # TODO: Melhorar isso    
    def _load_locator_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        if controller.xscale == 'log':
            return
            
        loc_type = 'multiple'
      
        self.set_locator(loc_type, 'x', 'major', 
                                     controller.xgrid_major_locator)
        self.set_locator(loc_type, 'x', 'minor', 
                                     controller.xgrid_minor_locator)
        self.set_locator(loc_type, 'y', 'major', 
                                     controller.ygrid_major_locator)
        self.set_locator(loc_type, 'y', 'minor', 
                                     controller.ygrid_minor_locator)        


    # TODO: colocar Tick label no centro matplotlib.axis.py (435)
    # TODO: zorder
    def _load_ticks_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        # Major Ticks and its label visibility
        self.base_axes.tick_params(which='major',
            top=(controller.xtick_top and 
                 controller.xtick_major_top),
            bottom=(controller.xtick_bottom and 
                    controller.xtick_major_bottom),
            labeltop=(controller.xtick_labeltop and 
                      controller.xtick_major_top),
            labelbottom=(controller.xtick_labelbottom and 
                         controller.xtick_major_bottom),
            left=(controller.ytick_left and 
                  controller.ytick_major_left),
            right=(controller.ytick_right and 
                   controller.ytick_major_right),
            labelleft=(controller.ytick_labelleft and 
                       controller.ytick_major_left),
            labelright=(controller.ytick_labelright and 
                        controller.ytick_major_right)   
        )
        # Minor Ticks and its label visibility
        self.base_axes.tick_params(which='minor',
            top=(controller.xtick_top and 
                 controller.xtick_minor_top),
            bottom=(controller.xtick_bottom and 
                    controller.xtick_minor_bottom),
            labeltop=(controller.xtick_labeltop and 
                      controller.xtick_minor_top),
            labelbottom=(controller.xtick_labelbottom and 
                         controller.xtick_minor_bottom),
            left=(controller.ytick_left and 
                  controller.ytick_minor_left),
            right=(controller.ytick_right and 
                   controller.ytick_minor_right),
            labelleft=(controller.ytick_labelleft and 
                       controller.ytick_minor_left),
            labelright=(controller.ytick_labelright and 
                        controller.ytick_minor_right)
        )  
        # Ticks Properties
        self.base_axes.tick_params(axis='x', which='major', 
                           direction=controller.xtick_direction,
                           length=controller.xtick_major_size,
                           width=controller.xtick_major_width,
                           pad=controller.xtick_major_pad,
                           labelcolor=controller.xtick_labelcolor,
                           labelrotation=controller.xtick_labelrotation,
                           labelsize=controller.xtick_labelsize,
                           color=controller.xtick_color#,
                           #zorder=
        )
        self.base_axes.tick_params(axis='x', which='minor', 
                           direction=controller.xtick_direction,
                           length=controller.xtick_minor_size,
                           width=controller.xtick_minor_width,
                           pad=controller.xtick_minor_pad,
                           labelcolor=controller.xtick_labelcolor,
                           labelrotation=controller.xtick_labelrotation,
                           labelsize=controller.xtick_labelsize,
                           color=controller.xtick_color#,
                           #zorder=
        )
        self.base_axes.tick_params(axis='y', which='major', 
                           direction=controller.ytick_direction,
                           length=controller.ytick_major_size,
                           width=controller.ytick_major_width,
                           pad=controller.ytick_major_pad,
                           labelcolor=controller.ytick_labelcolor,
                           labelrotation=controller.ytick_labelrotation,
                           labelsize=controller.ytick_labelsize,
                           color=controller.ytick_color#,
                           #zorder=
        )
        self.base_axes.tick_params(axis='y', which='minor', 
                           direction=controller.ytick_direction,
                           length=controller.ytick_minor_size,
                           width=controller.ytick_minor_width,
                           pad=controller.ytick_minor_pad,
                           labelcolor=controller.ytick_labelcolor,
                           labelrotation=controller.ytick_labelrotation,
                           labelsize=controller.ytick_labelsize,
                           color=controller.ytick_color#,
                           #zorder=
        )




        
    def _load_grids_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self.set_grid_parameters(axis='x', which='major',                          
                         gridOn=controller.xgrid_major,
                         grid_color=controller.xgrid_major_color,
                         grid_alpha=controller.xgrid_major_alpha,
                         grid_linestyle=controller.xgrid_major_linestyle,
                         grid_linewidth=controller.xgrid_major_linewidth
        ) 
        self.set_grid_parameters(axis='x', which='minor',                          
                         gridOn=controller.xgrid_minor,
                         grid_color=controller.xgrid_minor_color,
                         grid_alpha=controller.xgrid_minor_alpha,
                         grid_linestyle=controller.xgrid_minor_linestyle,
                         grid_linewidth=controller.xgrid_minor_linewidth
        )
        self.set_grid_parameters(axis='y', which='major',                          
                         gridOn=controller.ygrid_major,
                         grid_color=controller.ygrid_major_color,
                         grid_alpha=controller.ygrid_major_alpha,
                         grid_linestyle=controller.ygrid_major_linestyle,
                         grid_linewidth=controller.ygrid_major_linewidth
        ) 
        self.set_grid_parameters(axis='y', which='minor',                          
                         gridOn=controller.ygrid_minor,
                         grid_color=controller.ygrid_minor_color,
                         grid_alpha=controller.ygrid_minor_alpha,
                         grid_linestyle=controller.ygrid_minor_linestyle,
                         grid_linewidth=controller.ygrid_minor_linewidth
        )




        self.teste('red')


    def _load_labels_properties(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        self.set_label_properties('figure', 
                        text=controller.figure_titletext, 
                        x=controller.figure_titlex, 
                        y=controller.figure_titley, 
                        ha=controller.figure_titleha, 
                        va=controller.figure_titleva,
                        size=controller.figure_titlesize, 
                        weight=controller.figure_titleweight
        )
        #
        self.set_label_properties('axes', 
                                  loc='left',
                                  text=controller.axes_titletextleft,
                                  color=controller.axes_titlecolor,
                                  pad=controller.axes_titlepad,
                                  size=controller.axes_titlesize,
                                  weight=controller.axes_titleweight
        ) 
        self.set_label_properties('axes', 
                                  loc='center',
                                  text=controller.axes_titletextcenter,
                                  color=controller.axes_titlecolor,
                                  pad=controller.axes_titlepad,
                                  size=controller.axes_titlesize,
                                  weight=controller.axes_titleweight
        ) 
        self.set_label_properties('axes', 
                                  loc='right',
                                  text=controller.axes_titletextright,
                                  color=controller.axes_titlecolor,
                                  pad=controller.axes_titlepad,
                                  size=controller.axes_titlesize,
                                  weight=controller.axes_titleweight
        )                               
        #
        self.set_label_properties('axis', axis='x', 
                                text=controller.xaxis_labeltext, 
                                color=controller.axes_labelcolor, 
                                pad=controller.axes_labelpad,
                                size=controller.axes_labelsize,
                                weight=controller.axes_labelweight
        )
        self.set_label_properties('axis', axis='y', 
                                text=controller.yaxis_labeltext,
                                color=controller.axes_labelcolor, 
                                pad=controller.axes_labelpad,
                                size=controller.axes_labelsize,
                                weight=controller.axes_labelweight
        )    



        
    def draw(self, drawDC=None):
        if not self._postpone_draw:
            super().draw(drawDC)



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
  

    def set_figure_facecolor(self, color):
        try:
            self.figure.set_facecolor(color)
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


    def set_spine_position(self, spine, position):
        try:
            self.base_axes.spines[spine].set_position(position)
        except:
            raise

            
    def set_position(self, rect):
        try:
            self.base_axes.set_position(rect)
            self.plot_axes.set_position(rect)
        except:
            raise
                        
            
    def set_grid_parameters(self, axis, which, **kwargs):
#        print ('\nset_grid_params:', axis, which, kwargs)
        gridOn = kwargs.pop('gridOn', None)
        
        if gridOn is None:
            if axis == 'x' or axis == 'both':
                self.base_axes.xaxis.set_tick_params(**kwargs)
            if axis == 'y' or axis == 'both':
                self.base_axes.yaxis.set_tick_params(**kwargs)     
                          
        else:    
            if axis == 'x'or axis == 'both':            
                ax = self.base_axes.xaxis
                if which == 'major': 
                    ax._gridOnMajor = gridOn
                    ax.set_tick_params(which='major', 
                                           gridOn=ax._gridOnMajor, **kwargs)
                elif which == 'minor':     
                    ax._gridOnMinor = gridOn
                    ax.set_tick_params(which='minor', 
                                           gridOn=ax._gridOnMinor, **kwargs) 
            
            elif axis == 'y'or axis == 'both':
                ax = self.base_axes.yaxis
                if which == 'major': 
                    ax._gridOnMajor = gridOn
                    ax.set_tick_params(which='major', 
                                           gridOn=ax._gridOnMajor, **kwargs)
                elif which == 'minor':     
                    ax._gridOnMinor = gridOn
                    ax.set_tick_params(which='minor', 
                                           gridOn=ax._gridOnMinor, **kwargs) 
                    

    def set_locator(self, locator_type, axis, which, *args, **kwargs):
        try: 
            # TODO: Check Formatter (FmtType)
            FmtType = None
            if locator_type is None:
                LocType = NullLocator
            elif locator_type == 'multiple':
                LocType = MultipleLocator
            elif locator_type == 'log':
                LocType = LogLocator
                FmtType = LogFormatterMathtext
            else:
                raise Exception('Invalid locator_type.')
            #    
            if axis not in ['x', 'y']:
                raise Exception('Invalid axis.')
            if which not in ['minor', 'major']:
                raise Exception('Invalid which.')
            #            
            if axis == 'x':
                ax = self.base_axes.xaxis
            else:
                ax = self.base_axes.yaxis  
            #    
            if which == 'major':
                ax.set_major_locator(LocType(*args, **kwargs))
                if FmtType:
                    ax.set_major_formatter(FmtType())
            else:
                ax.set_minor_locator(LocType(*args, **kwargs))
                if FmtType:
                    ax.set_minor_formatter(FmtType())
        except:
            raise
        

    def set_axes_axisbelow(self, b):
        """
        Set whether axis ticks and gridlines are above or below most artists.

        .. ACCEPTS: [ bool | 'line' ]

        Parameters
        ----------
        b : bool or 'line'
            
        *axisbelow*        [ bool | 'line' ] draw the grids
                             and ticks below or above most other artists,
                             or below lines but above patches
        """  
        self.base_axes.set_axisbelow(b)
        


    def teste(self, color):
        self.base_axes.patch.set_edgecolor(color)
        
    def set_axes_facecolor(self, color):
        self.base_axes.set_facecolor(color)
        
        
    def set_axes_edgecolor(self, color):
        self.base_axes.spines['left'].set_edgecolor(color)
        self.base_axes.spines['right'].set_edgecolor(color)
        self.base_axes.spines['bottom'].set_edgecolor(color)
        self.base_axes.spines['top'].set_edgecolor(color)
        

    def set_axes_linewidth(self, value):
        self.base_axes.spines['left'].set_linewidth(value)
        self.base_axes.spines['right'].set_linewidth(value)
        self.base_axes.spines['bottom'].set_linewidth(value)
        self.base_axes.spines['top'].set_linewidth(value)     

    
    def set_label_properties(self, who, **kwargs):
        text = kwargs.pop('text', None)
        pad = kwargs.pop('pad', None)
        #
        axis = kwargs.pop('axis', None)
        loc = kwargs.pop('loc', 'all')
        #
        text_objs = []
          
        if who == 'axes':
            if loc == 'left' or loc == 'all':
                text_objs.append(self.base_axes._left_title)
            if loc == 'center' or loc == 'all':
                text_objs.append(self.base_axes.title)    
            if loc == 'right' or loc == 'all':
                text_objs.append(self.base_axes._right_title)       
  
        elif who == 'axis':
            if pad is not None:
                if axis == 'x' or axis == 'both':
                    self.base_axes.xaxis.labelpad = pad 
                    self.base_axes.xaxis.stale = True
                if axis == 'y' or axis == 'both':
                    self.base_axes.yaxis.labelpad = pad
                    self.base_axes.yaxis.stale = True 
            if axis == 'x' or axis == 'both':
                 text_objs.append(self.base_axes.xaxis.label)
            if axis == 'y' or axis == 'both':     
                 text_objs.append(self.base_axes.yaxis.label)
                 
        elif who == 'figure':  
            if self.figure._suptitle is None:
                x = kwargs.pop('x', 0.5)
                y = kwargs.pop('y', 0.98)
                if text is None:
                    text = ''
                self.figure._suptitle = self.figure.text(x, y, text) 
            text_objs.append(self.figure._suptitle)
            
            
        for text_obj in text_objs:
            if text is not None:
                text_obj.set_text(text)
            text_obj.update(kwargs) 
            
            
    
    def set_tick_params(self, axis, which, **kwargs):  
#        print ('\nset_tick_params:', axis, which, kwargs)
        if axis not in ['x', 'y', 'both']:
            raise Exception('Invalid axis.')
        #    
        if which not in ['minor', 'major', 'both']:
            raise Exception('Invalid which.') 
        #
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
    
    
    
    def set_minor_tick_visibility(self, axis, b):
        axis_list = []
        if axis == 'x' or axis == 'both':
            axis_list.append(self.base_axes.xaxis)
        if axis == 'y' or axis == 'both':
            axis_list.append(self.base_axes.yaxis)
        if b:
            for ax in axis_list:
                scale = ax.get_scale()    
                if scale == 'log':
                    s = ax._scale
                    ax.set_minor_locator(mticker.LogLocator(s.base, s.subs))
                elif scale == 'symlog':
                    s = ax._scale
                    ax.set_minor_locator(
                        mticker.SymmetricalLogLocator(s._transform, s.subs))
                else:
                    ax.set_minor_locator(mticker.AutoMinorLocator())
        else:
            for ax in axis_list:
                ax.set_minor_locator(mticker.NullLocator()) 



    def get_xlim(self):
        return self.base_axes.get_xlim()    
    
    def get_ylim(self):
        return self.base_axes.get_ylim()     
    
    def get_transdata(self):    
        return self.base_axes.transData   
    
    def get_transaxes(self):
        return self.base_axes.transAxes    
    
    

    def append_artist(self, artist_type, *args, **kwargs):
        if artist_type == 'Line2D':
            line = matplotlib.lines.Line2D(*args, **kwargs)
            return self.plot_axes.add_line(line)
        
        elif artist_type == 'Text':
            return self.plot_axes.text(*args, **kwargs)
        
        elif artist_type == 'AxesImage':
            image = matplotlib.image.AxesImage(self.plot_axes, *args, **kwargs)
            self.plot_axes.add_image(image)
            return image
        
        elif artist_type == 'Rectangle':
            rect = matplotlib.patches.Rectangle(*args, **kwargs)
            return rect
        
        elif artist_type == 'PatchCollection':
            collection = matplotlib.collections.PatchCollection(*args, **kwargs)
            return self.plot_axes.add_collection(collection)
        
        elif artist_type == 'contourf':
            #contours = mcontour.QuadContourSet(self.plot_axes, *args, **kwargs)
            #self.plot_axes.autoscale_view()
            image = self.plot_axes.contourf(*args, **kwargs)
            #self.plot_axes.add_image(image)
            return image
        
        elif artist_type == 'scatter':
            # TODO: rever linha abaixo, colocando de forma similar as de cima
            return self.plot_axes.scatter(*args, **kwargs)
            #def scatter(self, x, y, s=None, c=None, marker=None, cmap=None, norm=None,
            #    vmin=None, vmax=None, alpha=None, linewidths=None,
            #    verts=None, edgecolors=None,
            #    **kwargs):
        
        else:
            raise Exception('artist_type not known.')  
    