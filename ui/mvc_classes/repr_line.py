from collections import OrderedDict

import numpy as np
from scipy.interpolate import interp1d

from classes.ui import UIManager
from ui.mvc_classes.representation import RepresentationController
from ui.mvc_classes.representation import RepresentationView


class LineRepresentationController(RepresentationController):
    tid = 'line_representation_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['left_scale'] = {
            'default_value': 0.0,
            'type': float     
    }
    _ATTRIBUTES['right_scale'] = {
            'default_value': 1.0,
            'type': float
    }
    _ATTRIBUTES['thickness'] = {
            'default_value': 1, 
            'type': int
    }
    _ATTRIBUTES['color'] = {
            'default_value': 'Black',
            'type': str         
    }
    _ATTRIBUTES['x_scale'] = {
            'default_value': 0, 
            'type': int
    } 
    _ATTRIBUTES['interpolate'] = {
            'default_value': False,
            'type': bool
    }       

    def __init__(self, **state):
        super().__init__(**state)

    def _get_pg_properties_dict(self):
        """
        """
        props = OrderedDict()
        props['left_scale'] = {
            'pg_property': 'FloatProperty',
            'label': 'Left value'  
        } 
        props['right_scale'] = {
            'pg_property': 'FloatProperty',
            'label': 'Right value'
        }
        props['thickness'] = {
            'pg_property': 'EnumProperty',
            'label': 'Width',
            'options_labels': ['0', '1', '2', '3', '4', '5'],
            'options_values': [0, 1, 2, 3, 4, 5 ]
        }    
        props['color'] = {
            'pg_property': 'MPLColorsProperty',
            'label': 'Color'
        }     
        props['x_scale'] = {
            'pg_property': 'EnumProperty',
            'label': 'X axis scale',
            'options_labels': ['Linear', 'Logarithmic'],
            'options_values': [0, 1]
        }                
        props['interpolate'] = {
            'pg_property': 'BoolProperty',
            'label': 'Interpolate line'
        }              
        return props
    

class LineRepresentationView(RepresentationView):
    tid = 'line_representation_view'
    _picked_color = 'MediumSpringGreen'

    def __init__(self, controller_uid):
        super(LineRepresentationView, self).__init__(controller_uid)

    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        controller.subscribe(self.set_xlim, 'change.left_scale')    
        controller.subscribe(self.set_xlim, 'change.right_scale') 
        controller.subscribe(self.set_thickness, 'change.thickness')
        controller.subscribe(self.set_color, 'change.color')
        controller.subscribe(self.set_zorder, 'change.zorder')
        controller.subscribe(self.on_change_xscale, 'change.x_scale')
        controller.subscribe(self.on_change_interpolate, 'change.interpolate')

    def get_data_info(self, event):
        """
        Retorna o valor (float) do dado exibido em tela, de acordo com a 
        posicao do mouse no eixo y (event.ydata).
        """
        line = self._mplot_objects.get('line', None)
        if not line :
            return None
        ydata = line.get_ydata()
        if event.ydata < ydata[0] or event.ydata > ydata[-1]:
            return None
        #
        ydata_index = (np.abs(ydata-event.ydata)).argmin()
        transformated_xdata = line.get_xdata()
        transformated_xvalue = transformated_xdata[ydata_index]
        canvas = self.get_canvas() 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        xvalue = canvas.inverse_transform(transformated_xvalue, 
                                               controller.left_scale, 
                                               controller.right_scale, 
                                               controller.x_scale
        )        
        return xvalue

    def on_change_xscale(self, new_value, old_value):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        if new_value == 1:
            if controller.left_scale is None or \
                                            controller.left_scale <= 0.0:
                controller.set_value_from_event('left_scale', 0.2)
        self.set_xscale(new_value) 

    def on_change_interpolate(self, new_value, old_value):
        self.draw()

    def set_zorder(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_zorder(new_value)
            self.draw_canvas()
                
    def set_picked(self, new_value, old_value):
        print('set_picked:', new_value)
        if len(self._mplot_objects.values()) == 0:
            self.draw()
        if new_value:
            self._mplot_objects['line'].set_color(self._picked_color)    
        else:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            self._mplot_objects['line'].set_color(controller.color)
        self.draw_canvas()     
                
        
    def set_thickness(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_linewidth(new_value)
            self.draw_canvas()
            toc = self.get_parent_controller()
            label = toc.get_label()
            if label:
                label.set_thickness(new_value)
        else:
            self.draw()
                       
    def set_color(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_color(new_value)
            self.draw_canvas()   
            toc = self.get_parent_controller()
            label = toc.get_label()
            if label:
                label.set_color(new_value)
        else:
            self.draw()
                               
    def set_xscale(self, xscale):
        self.draw()
        
    def set_xlim(self, new_value, old_value):
        self.draw()
  
    
    def draw(self):
        print('\nLineRepresentationView.draw')
        if self._mplot_objects:
            self.clear() 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        toc = self.get_parent_controller()
        
        xdata = toc.get_filtered_data(dimensions_desired=1)
        if xdata is None:
            return
        #
        ydata = toc.get_last_dimension_index_data()
        xdata_valid_idxs = ~np.isnan(xdata)
        
        xdata = xdata[xdata_valid_idxs]
        ydata = ydata[xdata_valid_idxs]
        #
        canvas = self.get_canvas()
        transformated_xdata = canvas.transform(xdata, controller.left_scale, 
                    controller.right_scale, controller.x_scale)           
        #
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)        
        #
        if controller.interpolate:
            print('minmax xdata:', np.nanmin(xdata), np.nanmax(xdata))
            print('minmax trans_xdata:', np.nanmin(transformated_xdata), np.nanmax(transformated_xdata))
            interpolator = interp1d(ydata, transformated_xdata)   
            #
            tcc = track_controller._get_canvas_controller()
            depth_list = tcc.get_one_depth_per_pixel(np.nanmin(ydata),
                                                             np.nanmax(ydata))     
            if not self._mplot_objects.get('line'):
                line = track_controller.append_artist('Line2D', 
                            interpolator(depth_list), 
                            depth_list, 
                            linewidth=controller.thickness,
                            color=controller.color
                )
            else:
                print('else')
                line = self._mplot_objects['line']  
                line.set_data(interpolator(depth_list), depth_list)
        #        
        else:
            if not self._mplot_objects.get('line'):
                line = track_controller.append_artist('Line2D', 
                            transformated_xdata, 
                            ydata, 
                            linewidth=controller.thickness,
                            color=controller.color
                )
            else:
                line = self._mplot_objects.get('line')   
                line.set_data(transformated_xdata, ydata)
        #
        label = toc.get_label()
        if label:
            label.set_plot_type('line')
            label.set_xlim(
                (controller.left_scale, 
                 controller.right_scale)
            ) 
            label.set_color(controller.color)
            label.set_thickness(controller.thickness)  
        #        
        # Identifica a linha com o devido toc_uid
        line.set_label(toc_uid)
        # When we set picker to True (to enable line picking) function
        # Line2D.set_picker sets pickradius to True, 
        # then we need to set it again.
        toc = UIM.get(toc_uid)
        self._set_picking(line)
        canvas.mpl_connect('pick_event', toc.pick_event)
        self._mplot_objects['line'] = line
        return self.draw_canvas() 

          