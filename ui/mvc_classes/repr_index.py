from collections import OrderedDict

import numpy as np
from matplotlib.patches import FancyBboxPatch

from classes.ui import UIManager
from ui.mvc_classes.representation import RepresentationController
from ui.mvc_classes.representation import RepresentationView


class IndexRepresentationController(RepresentationController):
    tid = 'index_representation_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['step'] = {
            'default_value': 100.0,
            'type': float   
    }
    _ATTRIBUTES['pos_x'] = {
            'default_value': 0.5, 
            'type': float
    }
    _ATTRIBUTES['fontsize'] = {
            'default_value': 11, 
            'type': int
    }
    _ATTRIBUTES['color'] = {
            'default_value': 'Black',
            'type': str
    }    
    _ATTRIBUTES['bbox'] = {
            'default_value': True ,
            'type': bool
    }   
    _ATTRIBUTES['bbox_style'] = {
            'default_value': 'round', 
            'type': str
    }
    _ATTRIBUTES['bbox_color'] = {
            'default_value': 'White',
            'type': str
    }         
    _ATTRIBUTES['bbox_alpha'] = {
            'default_value': 0.5,
            'type': float    
    }    
    _ATTRIBUTES['ha'] = {
            'default_value': 'center',
            'type': str
    } 
    _ATTRIBUTES['va'] = {
            'default_value': 'center',
            'type': str
    }  
    
    def __init__(self, **state):
        super().__init__(**state)
 
    def _get_pg_properties(self):
        """
        """
        props = OrderedDict()
        props['step'] = {
            'pg_property': 'FloatProperty',
            'label': 'Step'
        } 
        props['pos_x'] = {
            'pg_property': 'EnumProperty',
            'label': 'Text Horizontal Alignment',
            'options_labels': ['Left', 'Center', 'Right'],
            'options_values': [0.1, 0.5, 0.9]
        }
        props['fontsize'] = {
            'pg_property': 'EnumProperty',
            'label': 'Text Font Size',
            'options_labels': ['7', '8', '9', '10', '11', '12', '13'],
            'options_values': [7, 8, 9, 10, 11, 12, 13]
        }
        props['color'] = {
            'pg_property': 'MPLColorsProperty',
            'label': 'Text Color'
        }    
        props['bbox'] = {
            'pg_property': 'BoolProperty',
            'label': 'Bbox'
        }   
        props['bbox_style'] = {
            'pg_property': 'EnumProperty',
            'label': 'Bbox Style',
            'options_labels': ['Circle', 'DArrow', 'LArrow', 'RArrow', 
                       'Round', 'Round4', 'Roundtooth', 'Sawtooth',
                       'Square'
            ],
            'options_values': ['circle', 'darrow', 'larrow', 'rarrow',
                       'round', 'round4', 'roundtooth', 'sawtooth',
                       'square'
            ]
        }
        props['bbox_color'] = {
            'pg_property': 'MPLColorsProperty',
            'label': 'Bbox Color'
        }         
        props['bbox_alpha'] = {
            'pg_property': 'FloatProperty',
            'label': 'Bbox Alpha'      
        }    
        props['ha'] = {
            'pg_property': 'EnumProperty',
            'label': 'Horizontal Alignment in the TextBox',
            'options_labels': ['Left', 'Center', 'Right'],
            'options_values': ['left', 'center', 'right']
        } 
        props['va'] = {
            'pg_property': 'EnumProperty',
            'label': 'Vertical Alignment in the TextBox',
            'options_labels': ['Top', 'Center', 'Bottom', 'Baseline'],
            'options_values': ['top', 'center', 'bottom', 'baseline']
        }  
        return props
    

class IndexRepresentationView(RepresentationView):
    tid = 'index_representation_view'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)        

    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        controller.subscribe(self._draw, 'change.step')    
        controller.subscribe(self._draw, 'change.pos_x') 
        controller.subscribe(self._draw, 'change.ha')
        controller.subscribe(self._draw, 'change.va')
        controller.subscribe(self._draw, 'change.fontsize')
        controller.subscribe(self._draw, 'change.color') 
        controller.subscribe(self._draw, 'change.bbox')
        controller.subscribe(self._draw, 'change.bbox_style')
        controller.subscribe(self._draw, 'change.bbox_color')
        controller.subscribe(self._draw, 'change.bbox_alpha')
        controller.subscribe(self._draw, 'change.zorder')
                  
    def _draw(self, new_value, old_value):
        # Bypass function
       # print '\nIndexRepresentationView._draw (bypass)'
        self.draw()
       # print '\nIndexRepresentationView._draw (bypass) end'
                
    def get_data_info(self, event):
        #ydata = dm.get_last_dimension_index_data()
        #print('get_data_info:', event.ydata)
        return None       
        """
        OM = ObjectManager()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
                
        ### Z axis Conversion 
        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)
        filter_ = toc.get_filter()
        di_uid, display, is_range, z_first, z_last = filter_.data[0]
        z_data_index = OM.get(di_uid)
        position_data = z_data_index.data[z_first:z_last]    
        ### END - Z axis Conversion 
        
        y_pos_index = (np.abs(position_data - event.ydata)).argmin()
        return str(controller._data[y_pos_index])
        """
           
    def draw(self):
        try:
            if self._mplot_objects:
                self.clear() 
            self._mplot_objects['text'] = []    
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            toc = self.get_parent_controller()

            index_type = toc.get_well_plot_index_type()
            #
            ydata = toc.get_last_dimension_index_data()
            if ydata is None:
                return
            equivalent_ydata = toc.get_equivalent_index_data(datatype=index_type)
            if equivalent_ydata is None:
                # There is no equivalent data to be plotted. For example, 
                # we have a TWT index_type and do not have TWT indexed data.
                # Then, no plot!
                return
            #
            '''
            y_min, y_max = np.nanmin(ydata), np.nanmax(ydata)
            if y_min%controller.step:
                y_min = (y_min//controller.step + 1) * controller.step  
            y_values = np.arange(y_min, y_max, controller.step)   
            '''
            y_min, y_max = np.nanmin(equivalent_ydata), np.nanmax(equivalent_ydata)
            if y_min%controller.step:
                y_min = (y_min//controller.step + 1) * controller.step  
            y_values = np.arange(y_min, y_max, controller.step)               
            #
#            track_controller_uid = UIM._getparentuid(toc_uid)
            track_controller = self.get_track_controller()  
            #
            canvas = self.get_canvas()
            transformated_pos_x = canvas.transform(controller.pos_x, 0.0, 1.0)         
            #
#            print('y_values:', y_values)
            
            for y_value in y_values:
#                print('\ny_value:', y_value)
                y_pos_index = (np.abs(equivalent_ydata - y_value)).argmin()
                y_pos = ydata[y_pos_index]
                text = track_controller.append_artist('Text', 
                                        transformated_pos_x, y_pos,
                                        "%g"%y_value,
                                        color=controller.color,
                                        horizontalalignment=controller.ha,
                                        verticalalignment=controller.va,
                                        fontsize=controller.fontsize
                )                        
                if controller.bbox:
                    pad = 0.2
                    boxstyle = controller.bbox_style
                    boxstyle += ",pad=%0.2f" % pad
                    text._bbox_patch = FancyBboxPatch(
                                        (0., 0.),
                                        1., 1.,
                                        boxstyle=boxstyle,
                                        color=controller.bbox_color,
                                        alpha=controller.bbox_alpha
                    )                    
                #text.zorder = controller.zorder
                self._mplot_objects['text'].append(text)
            self.draw_canvas()   
        except Exception as e:
            print ('ERROR IndexRepresentationView.draw', e)
            raise
            