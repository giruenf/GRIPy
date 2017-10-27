# -*- coding: utf-8 -*-
import numpy as np
import wx

import matplotlib
#matplotlib.interactive(False)
#matplotlib.use('WXAgg')

from matplotlib.axes import Axes
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.scale import ScaleBase, register_scale
from matplotlib.transforms import Transform
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter, NullLocator, MultipleLocator

#from App import log
from UI.uimanager import UIManager


###############################################################################
###############################################################################


# TODO: Review it!
# Keeping MPL version 1 parameters
if matplotlib.__version__.startswith('2.'):
    #print matplotlib.rcParams['mathtext.rm']
    matplotlib.rcParams['mathtext.fontset'] = 'cm'
    matplotlib.rcParams['mathtext.rm'] = 'serif'
    #
    matplotlib.rcParams['figure.figsize'] = [8.0, 6.0]
    matplotlib.rcParams['figure.dpi'] = 80
    matplotlib.rcParams['savefig.dpi'] = 100
    #    
    matplotlib.rcParams['font.size'] = 10
    matplotlib.rcParams['legend.fontsize'] = 'large'
    matplotlib.rcParams['figure.titlesize'] = 'medium'


# TODO: Parametros: levar para App.utils ou Parameters.manager
DEFAULT_LABEL_BG_COLOR  = '#B0C4DE' #LightSteelBlue  
SELECTION_WIDTH = 2
SELECTION_COLOR = 'green'


###############################################################################
###############################################################################


# Mixin for a selectable Panel
class SelectPanelMixin(object):

    def is_selected(self):
        return self._selected
    
    def process_change_selection(self):
        self._selected = not self._selected
        if self._selected:
            self.create_selection()
            self.refresh_selection()
            self.Bind(wx.EVT_PAINT, self.on_paint_selection)
        else:
            self.Unbind(wx.EVT_PAINT, handler=self.on_paint_selection)
            self.destroy_selection()
    
    def on_paint_selection(self, event):
        self.refresh_selection()
        event.Skip()
    
    def create_selection(self): 
        # Using pos=(0,0) and size=(0,0) to avoid flicker on selection.
        self._sel_obj_0 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_0.SetBackgroundColour(SELECTION_COLOR)
        self._sel_obj_1 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_1.SetBackgroundColour(SELECTION_COLOR)           
        self._sel_obj_2 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_2.SetBackgroundColour(SELECTION_COLOR)       
        self._sel_obj_3 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_3.SetBackgroundColour(SELECTION_COLOR)      
        self._selected = True

    def destroy_selection(self):
        self._sel_obj_0.Destroy()
        self._sel_obj_1.Destroy()
        self._sel_obj_2.Destroy()
        self._sel_obj_3.Destroy()
        self._selected = False
    
    def refresh_selection(self):
        if self._selected:
            self._sel_obj_0.SetSize(0, 0, SELECTION_WIDTH, self.GetSize()[1])
            self._sel_obj_1.SetSize(self.GetSize()[0] - SELECTION_WIDTH, 0, 
                                    SELECTION_WIDTH, self.GetSize()[1]
            )
            self._sel_obj_2.SetSize(0, 0, self.GetSize()[0], SELECTION_WIDTH)
            self._sel_obj_3.SetSize(0, self.GetSize()[1]- SELECTION_WIDTH,
                                    self.GetSize()[0], SELECTION_WIDTH
            )
            self._sel_obj_0.Refresh() 
            self._sel_obj_1.Refresh() 
            self._sel_obj_2.Refresh() 
            self._sel_obj_3.Refresh() 


###############################################################################
###############################################################################


class GripyScale(ScaleBase):
    name = 'gripyscale'
    
    def __init__(self, axis, **kwargs):
        ScaleBase.__init__(self)
        self.min_value = kwargs.pop("min_value", 0.0)
        self.max_value = kwargs.pop("max_value", 100.0)

    def get_transform(self):
        return GripyTransform(self.min_value, self.max_value)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(NullLocator())
        axis.set_major_formatter(NullFormatter())
        axis.set_minor_formatter(NullFormatter())

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return max(vmin, self.min_value), min(vmax, self.max_value)


class GripyTransform(Transform):
    input_dims = 1
    output_dims = 1
    is_separable = True
    has_inverse = True

    def __init__(self, min_value, max_value):
        Transform.__init__(self)
        self.min_value = min_value
        self.max_value = max_value

    def transform_non_affine(self, a):
        range_ = self.max_value - self.min_value
        translated_a = np.absolute(a - self.min_value)
        return (translated_a / range_)

    def inverted(self):
        return InvertedGripyTransform(self.min_value, self.max_value)


class InvertedGripyTransform(Transform):
    input_dims = 1
    output_dims = 1
    is_separable = True
    has_inverse = True

    def __init__(self, min_value, max_value):
        Transform.__init__(self)
        self.min_value = min_value
        self.max_value = max_value

    def transform_non_affine(self, a):
        range_ = self.max_value - self.min_value
        translated_a = a * range_
        return self.min_value + translated_a
        
    def inverted(self):
        return GripyTransform(self.min_value, self.max_value)


# Now that the Scale class has been defined, it must be registered so
# that ``matplotlib`` can find it.
register_scale(GripyScale)

###############################################################################
###############################################################################

"""
    Inner class to all Figures used in this Project
"""
class GripyMPLFigure(Figure):
    
    def __init__(self, *args, **kwargs):
        super(GripyMPLFigure, self).__init__(*args, **kwargs)  
        
    def display_to_figure_coordinates(self, display_coordinates):
        return self.transFigure.inverted().transform(display_coordinates) 
        
    def figure_to_display_coordinates(self, figure_coordinates):
        return self.transFigure.transform(figure_coordinates)    
        

"""
    Inner class to all Axes used in this Project
"""
class GripyMPLAxes(Axes):

    def __init__(self, *args, **kwargs):
        super(GripyMPLAxes, self).__init__(*args, **kwargs)            
    
    def data_to_axes_coordinates(self, data_coordinates):
        return self.transLimits.transform(data_coordinates)
    
    def axes_to_data_coordinates(self, axes_coordinates):
        return self.transLimits.inverted().transform(axes_coordinates)

    def data_to_display_coordinates(self, data_coordinates):
        return self.transData.transform(data_coordinates)   

    def display_to_data_coordinates(self, display_coordinates):
        return self.transData.inverted().transform(display_coordinates)   
    
    def display_to_figure_coordinates(self, display_coordinates):
        return self.figure.display_to_figure_coordinates(display_coordinates) 
        
    def figure_to_display_coordinates(self, figure_coordinates):
        return self.figure.figure_to_display_coordinates(figure_coordinates)
   
    
    
class BaseAxes(GripyMPLAxes):    
    
    _valid_keys = [
        'y_major_grid_lines',
        'y_minor_grid_lines',
        'x_scale',
        'decades',
        'scale_lines',
        'plotgrid',
        'leftscale',
        'minorgrid',
        'depth_lines',
        'ylim',
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

        if matplotlib.__version__.startswith('2.'):
            GripyMPLAxes.__init__(self, figure, 
                    [0.0, 0.0, 1.0, 1.0]#, 
                    #facecolor=self._internal_props['facecolor'] # MPL 2.0
            )
        else:
            GripyMPLAxes.__init__(self, figure, 
                    [0.0, 0.0, 1.0, 1.0]#, 
                    #axisbg=self._internal_props['facecolor'] # MPL 1.X
            )
    
        self._properties = {
            'y_major_grid_lines': 1000.0,
            'y_minor_grid_lines': 100.0,
            'decades': None,
            'log_base': 10,
            'scale_lines': None,
            'plotgrid': None,
            'leftscale': None,
            'minorgrid': None,
            'depth_lines': None,
            'xlim': (0.0, 100.0), # Used only when x_scale is linear
        }

    
#        self.set_spines_visibility(False)    
        self.spines['right'].set_visible(False)
        self.spines['top'].set_visible(False)
        self.spines['left'].set_visible(False)
        self.spines['bottom'].set_visible(False)
        
#        self.props = {}
        self.major_y_grid_mapping = {'color': self._internal_props['tick_grid_color'], 
                             'linestyle': self._internal_props['grid_linestyle'], 
                             'linewidth': self._internal_props['major_tick_width']
        }
        self.default_grid_mapping = {'color': self._internal_props['tick_grid_color'], 
                             'linestyle': self._internal_props['grid_linestyle'], 
                             'linewidth': self._internal_props['minor_tick_width']
        }        
        self.set_zorder(self._internal_props['dummy_ax_zorder'])        
        # EIXO Y SEMPRE SERÁ LINEAR
        self.set_yscale('linear')                
        # EIXOS X e Y NÃO TERÃO LABELS
        self.xaxis.set_major_formatter(NullFormatter())
        self.xaxis.set_minor_formatter(NullFormatter())
        self.yaxis.set_major_formatter(NullFormatter())
        self.yaxis.set_minor_formatter(NullFormatter())  
        # EIXO X NÃO POSSUI TICKS
        self.xaxis.set_tick_params('major', size=0)
        self.xaxis.set_tick_params('minor', size=0)     
        # EIXO Y TICKS
        self.yaxis.set_tick_params('major', size=10)
        self.yaxis.set_tick_params('minor', size=5)           
        self.tick_params(axis='y', which='major', direction='in',
                color=self._internal_props['tick_grid_color'],          
                length=self._internal_props['major_tick_lenght'],
                width=self._internal_props['major_tick_width'], 
                zorder=self._internal_props['ticks_zorder'])
        self.tick_params(axis='y', which='minor', direction='in',
                color=self._internal_props['tick_grid_color'],         
                length=self._internal_props['minor_tick_lenght'],
                width=self._internal_props['minor_tick_width'], 
                zorder=self._internal_props['ticks_zorder'])        
        # PARA NÃO HAVER SOBREPOSIÇÃO DE TICKS E GRIDS SOBRE OS SPINES(EIXO GRÁFICO) 
        self.spines['left'].set_zorder(self._internal_props['spines_zorder'])
        self.spines['right'].set_zorder(self._internal_props['spines_zorder'])
        self.spines['top'].set_zorder(self._internal_props['spines_zorder'])
        self.spines['bottom'].set_zorder(self._internal_props['spines_zorder'])        
        self.set_spines_color(self._internal_props['spines_color'])

        self.hide_y_ticks()

        for key, value in initial_properties.items():
            if key in self._valid_keys:
                self._properties[key] = value
        self.update('x_scale', self._properties.get('x_scale'))        
        self.update('y_minor_grid_lines', self._properties.get('y_minor_grid_lines'))    
        self.update('y_major_grid_lines', self._properties.get('y_major_grid_lines'))    


    def update(self, key, value):
        if key == 'ylim':
            if not isinstance(value, tuple):
                raise ValueError('ylim deve ser uma tupla')
            ymin, ymax =  value
            if not isinstance(ymin, (int, float)) \
                        or not isinstance(ymax, (int, float)):
                raise ValueError('ylim deve ser uma tupla de int ou float.')
            elif ymax == ymin:
                raise ValueError('Os valores de ylim nao podem ser iguais.')
            elif ymin < 0 or ymax < 0:
                raise ValueError('Nenhum dos valores de ylim podem ser negativos.')          
            self.set_ylim(value)
        elif key == 'x_scale':
            if not isinstance(value, int):
                 raise ValueError('O valor de x_scale deve ser inteiro.')
            if not value in [0, 1, 2, 3]:
                raise ValueError('A escala deve ser linear ou logaritmica(seno ou cosseno). (x_scale in [0, 1, 2, 3])')     
            if value == 0:
                self.set_xscale('linear')
                self.set_xlim(self._properties.get('xlim'))    
            if value == 1:
                self.set_xscale('log')
                # leftscale or decades to update xlim
                self.update('leftscale', self._properties.get('leftscale'))  
            if value == 2:
                raise Exception('There no support yet to Sin scale.')
            if value == 3:    
                raise Exception('There no support yet to Cosin scale.')  
            self.update('plotgrid', self._properties.get('plotgrid'))           
        elif key == 'y_major_grid_lines':
            if not isinstance(value, float):
                raise ValueError('y_major_grid_lines deve ser float.') 
            elif value <= 0:
                raise ValueError('y_major_grid_lines deve ser maior que 0.') 
    #            print 'setting y_major_grid_lines:', value
            self.yaxis.set_major_locator(MultipleLocator(value))
            self._properties['y_major_grid_lines'] = value             
        elif key == 'y_minor_grid_lines':
            if not isinstance(value, float):
                raise ValueError('y_minor_grid_lines deve ser float.') 
            elif value <= 0:
                raise ValueError('y_minor_grid_lines deve ser maior que 0.')
            self.yaxis.set_minor_locator(MultipleLocator(value))
            self._properties['y_minor_grid_lines'] = value                 
        elif key == 'decades' or key == 'leftscale':
            if key == 'decades':
                if not isinstance(value, int):
                    raise ValueError('decades deve ser inteiro.')
                if value <= 0:
                    raise ValueError('decades deve ser maior que 0.') 
                self._properties['decades'] = value    
            elif key == 'leftscale':
                if not isinstance(value, float):
                    raise ValueError('leftscale deve ser float.')    
                if value <= 0:
                    raise ValueError('leftscale deve ser maior que 0.')   
                self._properties['leftscale'] = value     
            if self.get_xscale() == 'log':
                xlim = (self._properties.get('leftscale'), 
                    self._properties.get('leftscale')*(self._properties.get('log_base')**self._properties.get('decades')))
     #           print 'xlim (log):', xlim
                self.set_xlim(xlim)       
        elif key == 'minorgrid':  
            if not isinstance(value, bool):  
                raise ValueError('O valor de minorgrid deve ser True ou False.')  
            if self.get_xscale() == 'log' and self._properties.get('plotgrid'): 
     #           print 'grid({}, axis=x, which=minor, {})'.format(value, self.default_grid_mapping)
                if value:
                    self.grid(value, axis='x', which='minor', **self.default_grid_mapping)
                else:
                    self.grid(value, which='minor', axis='x')    
            self._properties['minorgrid'] = value
        elif key == 'scale_lines':
            if not isinstance(value, int):
                raise ValueError('scale_lines deve ser inteiro.') 
            if value <= 0:
                raise ValueError('scale_lines deve ser maior que 0.')  
            if self.get_xscale() == 'linear' and self._properties.get('plotgrid'): 
                x0, x1 = self.get_xlim()
                x_major_grid_lines = (x1-x0)/value
                self.xaxis.set_major_locator(MultipleLocator(x_major_grid_lines))
            self._properties['scale_lines'] = value       
        elif key == 'plotgrid': 
            self._properties['plotgrid'] = value
            if value:
                self.update('minorgrid', self._properties.get('minorgrid'))
                self.update('scale_lines', self._properties.get('scale_lines'))
                self.grid(True, axis='x', which='major', **self.default_grid_mapping)            
                self.update('depth_lines', self._properties.get('depth_lines'))
            else:
                self.grid(False, axis='both', which='both')
                self.hide_y_ticks()
        elif key == 'depth_lines':
            if not isinstance(value, int): 
                raise ValueError('depth_lines deve ser inteiro.')
            elif value < 0 or value > 5:
                raise ValueError('depth_lines deve ser entre 0 e 5.')    
            if self._properties.get('plotgrid'):
                self.ticks = False
                if value == 0:
                    self.grid(True, axis='y', which='major', **self.major_y_grid_mapping)
                    self.grid(True, axis='y', which='minor', **self.default_grid_mapping)
                    self.hide_y_ticks()
                # DEPTH LINES == LEFT 
                elif value == 1:
                    self.ticks = True
                    self.spines['left'].set_position(('axes', 0.0))
                    self.spines['right'].set_position(('axes', 1.0))
                    self.tick_params(left=True, right=False, which='both', 
                                     axis='y', direction='in'
                    )
                    self.grid(False, axis='y', which='both')
                # DEPTH LINES == RIGHT
                elif value == 2:
                    self.ticks = True
                    self.spines['left'].set_position(('axes', 0.0))
                    self.spines['right'].set_position(('axes', 1.0))
                    self.tick_params(left=False, right=True, which='both',
                                     axis='y', direction='in'
                    )                 
                    self.grid(False, axis='y', which='both')
                # DEPTH LINES == CENTER   
                elif value == 3:
                    self.ticks = True
                    self.spines['left'].set_position('center')
                    self.spines['right'].set_position('center')
                    self.tick_params(left=True, right=True, which='both', axis='y',
                                     direction='out')
                    self.grid(False, axis='y', which='both')            
                # DEPTH LINES == LEFT AND RIGHT    
                elif value == 4:   
                    self.ticks = True
                    self.spines['left'].set_position(('axes', 0.0))
                    self.spines['right'].set_position(('axes', 1.0))
                    self.tick_params(left=True, right=True, which='both', 
                                     axis='y', direction='in'
                    )
                    self.grid(False, axis='y', which='both')   
                # DEPTH LINES == NONE
                elif value == 5:
                    self.spines['left'].set_position(('axes', 0.0))
                    self.spines['right'].set_position(('axes', 1.0))
                    self.yaxis.set_ticks_position('none')
                    self.grid(False, axis='y', which='both')                         
                if self.ticks:
                    self.show_y_ticks()
                    self.update('y_major_grid_lines', self._properties.get('y_major_grid_lines'))
                    self.update('y_minor_grid_lines', self._properties.get('y_minor_grid_lines'))
            self._properties['depth_lines'] = value
             

    def show_y_ticks(self):
        self.yaxis.set_tick_params('major', size=10)
        self.yaxis.set_tick_params('minor', size=5)
        #self.yaxis.set_tick_params('zorder', Z_ORDER_TRACKGRID

    def hide_y_ticks(self):
        self.yaxis.set_tick_params('major', size=0)
        self.yaxis.set_tick_params('minor', size=0)

    def set_spines_color(self, color):
        self.spines['bottom'].set_color(color)
        self.spines['top'].set_color(color)
        self.spines['left'].set_color(color)
        self.spines['right'].set_color(color)
 




class PlotFigureCanvas(FigureCanvas, SelectPanelMixin):
    _PLOT_XMIN = 0.0
    _PLOT_XMAX = 1.0
    
    
    def __init__(self, wx_parent, track_view_object, pos, size, **base_axes_properties):   
        self.figure = GripyMPLFigure()
        FigureCanvas.__init__(self, wx_parent, -1, self.figure)
        #self.selectedCanvas = []
        self.SetSize(size)
        #
        self.base_axes = BaseAxes(self.figure, **base_axes_properties)
        self.figure.add_axes(self.base_axes)
        self.base_axes.set_zorder(0)
        #
        # Add 
        self.plot_axes = GripyMPLAxes(self.figure, 
                         rect=self.base_axes.get_position(True), 
                         sharey=self.base_axes, 
                         frameon=False
        )
        self.figure.add_axes(self.plot_axes)
        self.plot_axes.set_xlim(self._PLOT_XMIN, self._PLOT_XMAX)
        self.plot_axes.xaxis.set_visible(False)
        self.plot_axes.yaxis.set_visible(False)        
        self.plot_axes.set_zorder(1)
        #
        self.track_view_object = track_view_object
        #self._selected = False
        #
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('pick_event', self.on_pick)
        #
        #print '\nsupports_blit:', self.supports_blit
        #self.create_multicursor()

    def on_pick(self, event):
        if event.mouseevent.button == 1:
            self._just_picked = True
            obj_uid = event.artist.get_label()
            UIM = UIManager()
            toc_ctrl = UIM.get(obj_uid)
            track_uid = UIM._getparentuid(toc_ctrl)
            if not event.mouseevent.guiEvent.ControlDown():
                selected_tocs = UIM.do_query('track_object_controller', 
                                               track_uid, 'selected=True'
                )
                for sel_toc in selected_tocs:
                    if sel_toc != toc_ctrl:
                        sel_toc.model.selected = False
            toc_ctrl.model.selected = not toc_ctrl.model.selected
            event.mouseevent.guiEvent.Skip(False)

        
    def on_press(self, event):
        if event.guiEvent.GetSkipped():
            self.track_view_object.process_event(event)

        
    def display_to_figure_coordinates(self, display_coordinates):
        return self.figure.display_to_figure_coordinates(display_coordinates) 
        
    def figure_to_display_coordinates(self, figure_coordinates):
        return self.figure.figure_to_display_coordinates(figure_coordinates)
    
    def add_axes(self, zorder=None):
        raise Exception('Cannot use it.')
             
    def update(self, key, value):
        self.base_axes.update(key, value)
        self.draw()            

    def set_xlim(self, xlim):
        raise Exception('Cannot use it.')
                   
    def set_ylim(self, ylim):
        self.base_axes.update('ylim', ylim)
        self.draw()
        
        
    def get_ypixel_from_depth(self, depth):
        pos = self.base_axes.data_to_display_coordinates((0, depth))[1]
        return self.GetClientSize().height - pos


    def get_depth_from_ypixel(self, ypx):
        y_max, y_min = self.base_axes.get_ylim()
        if ypx <= 0:
            return y_min
        elif ypx >= self.GetClientSize().height:
            return y_max
        pos = self.GetClientSize().height - ypx
        return self.base_axes.display_to_data_coordinates((0, pos))[1]


    def wx_position_to_depth(self, wx_pos):
        y_max, y_min = self.dummy_ax.get_ylim()
        if wx_pos <= 0:
            return y_min
        elif wx_pos >= self.GetClientSize()[1]:   
            return y_max
        mpl_y_pos = self.transform_display_position(wx_pos)
        return self.dummy_ax.transData.inverted().transform((0, mpl_y_pos))[1] 
    
    
    # TODO: separar create e add
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
        else:
            raise Exception('artist_type not known.')
            
            

class TrackFigureCanvas(PlotFigureCanvas, SelectPanelMixin):
    _PLOT_XMIN = 0.0
    _PLOT_XMAX = 1.0
    
    
    def __init__(self, wx_parent, track_view_object, pos, size, **base_axes_properties): 
        super(TrackFigureCanvas, self).__init__(wx_parent, track_view_object, pos, size, **base_axes_properties)
        self.selectedCanvas = []
        self._selected = False
        self.create_multicursor()
        
        """
        self.figure = GripyMPLFigure()
        FigureCanvas.__init__(self, wx_parent, -1, self.figure)
        
        self.SetSize(size)
        #
        self.base_axes = BaseAxes(self.figure, **base_axes_properties)
        self.figure.add_axes(self.base_axes)
        self.base_axes.set_zorder(0)
        #
        self.plot_axes = GripyMPLAxes(self.figure, 
                         rect=self.base_axes.get_position(True), 
                         sharey=self.base_axes, 
                         frameon=False
        )
        self.figure.add_axes(self.plot_axes)
        self.plot_axes.set_xlim(self._PLOT_XMIN, self._PLOT_XMAX)
        self.plot_axes.xaxis.set_visible(False)
        self.plot_axes.yaxis.set_visible(False)        
        self.plot_axes.set_zorder(1)
        #
        self.track_view_object = track_view_object
        self._selected = False
        #
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('pick_event', self.on_pick)
        #
        #print '\nsupports_blit:', self.supports_blit
        self.create_multicursor()
        """
        
    def create_multicursor(self):
        xmin, xmax = self.plot_axes.get_xlim()
        ymin, ymax = self.plot_axes.get_ylim()
        xmid = 0.5 * (xmin + xmax)
        ymid = 0.5 * (ymin + ymax)

        self._mc_horizOn = False
        self._mc_vertOn = False
        
        self.background = None
        #self.needclear = False

        self._mc_vline = self.plot_axes.axvline(xmid, visible=False, animated=True, lw=2) #color='r',
        self._mc_hline = self.plot_axes.axhline(ymid, visible=False, animated=True, lw=2) #color='r',
        
        """connect events"""
        #self._cidmotion = self.mpl_connect('motion_notify_event', self.onmove)
        self._ciddraw = self.mpl_connect('draw_event', self.on_clear_cursor)
        

    def update_multicursor(self, value):
        #self._do_clear_cursor()
        if value == 'None':
            self._mc_horizOn = False
            self._mc_vertOn = False
        elif value == 'Horizon':
            self._mc_horizOn = True
            self._mc_vertOn = False        
        elif value == 'Vertical':
            self._mc_horizOn = False
            self._mc_vertOn = True   
        elif value == 'Both':
            self._mc_horizOn = True
            self._mc_vertOn = True
            
        
        
    def disconnect_multicursor(self):
        """disconnect events"""
        #self.mpl_disconnect(self._cidmotion)
        self._do_clear_cursor()
        self.mpl_disconnect(self._ciddraw)
        
        
    def on_clear_cursor(self, event):
        """clear the cursor"""
        #print 'on_clear_cursor'
        self._do_clear_cursor()
        
        
    def _do_clear_cursor(self):    
        self.background = (self.copy_from_bbox(self.figure.bbox))
        if self._mc_vertOn:
            self._mc_vline.set_visible(False)
            #self.plot_axes.draw_artist(self._mc_vline)
        if self._mc_horizOn:
            self._mc_hline.set_visible(False)
            #self.plot_axes.draw_artist(self._mc_hline)
        #print '_do_clear_cursor'
        #self.blit(self.figure.bbox)
        

    # TODO: Melhorar esses metodos de cursor
    def show_cursor(self, xdata, ydata, event_under_me=False):
        if not self.widgetlock.available(self):
            return
        #self.needclear = True
        #if not self._mc_vertOn and not self._mc_horizOn:
        #    return
        if event_under_me:
            if self._mc_vertOn:
                self._mc_vline.set_xdata((xdata, xdata))
                self._mc_vline.set_visible(True)
        else:
            self._mc_vline.set_visible(False)
        if self._mc_horizOn:
            self._mc_hline.set_ydata((ydata, ydata))
            self._mc_hline.set_visible(True)
        self._update()


    def _update(self):
        if self.background is not None:
            self.restore_region(self.background)
        if self._mc_vertOn:
            self.plot_axes.draw_artist(self._mc_vline)
        if self._mc_horizOn:
            self.plot_axes.draw_artist(self._mc_hline)
        self.blit(self.figure.bbox)


    def mark_vertical(self, xdata):
        print 'mark_vertical'
        marked_vert_line = self.plot_axes.axvline(xdata, visible=True, lw=2, color='Lime')
        self.plot_axes.draw_artist(marked_vert_line)    
        print 'mark_vertical ended'
            
        
    """    
    def on_pick(self, event):
        if event.mouseevent.button == 1:
            self._just_picked = True
            obj_uid = event.artist.get_label()
            UIM = UIManager()
            toc_ctrl = UIM.get(obj_uid)
            track_uid = UIM._getparentuid(toc_ctrl)
            if not event.mouseevent.guiEvent.ControlDown():
                selected_tocs = UIM.do_query('track_object_controller', 
                                               track_uid, 'selected=True'
                )
                for sel_toc in selected_tocs:
                    if sel_toc != toc_ctrl:
                        sel_toc.model.selected = False
            toc_ctrl.model.selected = not toc_ctrl.model.selected
            event.mouseevent.guiEvent.Skip(False)

        
    def on_press(self, event):
        if event.guiEvent.GetSkipped():
            self.track_view_object.process_event(event)

        
    def display_to_figure_coordinates(self, display_coordinates):
        return self.figure.display_to_figure_coordinates(display_coordinates) 
        
    def figure_to_display_coordinates(self, figure_coordinates):
        return self.figure.figure_to_display_coordinates(figure_coordinates)
    
    def add_axes(self, zorder=None):
        raise Exception('Cannot use it.')
             
    def update(self, key, value):
        self.base_axes.update(key, value)
        self.draw()            

    def set_xlim(self, xlim):
        raise Exception('Cannot use it.')
                   
    def set_ylim(self, ylim):
        self.base_axes.update('ylim', ylim)
        self.draw()
        
        
    def get_ypixel_from_depth(self, depth):
        pos = self.base_axes.data_to_display_coordinates((0, depth))[1]
        return self.GetClientSize().height - pos


    def get_depth_from_ypixel(self, ypx):
        y_max, y_min = self.base_axes.get_ylim()
        if ypx <= 0:
            return y_min
        elif ypx >= self.GetClientSize().height:
            return y_max
        pos = self.GetClientSize().height - ypx
        return self.base_axes.display_to_data_coordinates((0, pos))[1]


    def wx_position_to_depth(self, wx_pos):
        y_max, y_min = self.dummy_ax.get_ylim()
        if wx_pos <= 0:
            return y_min
        elif wx_pos >= self.GetClientSize()[1]:   
            return y_max
        mpl_y_pos = self.transform_display_position(wx_pos)
        return self.dummy_ax.transData.inverted().transform((0, mpl_y_pos))[1] 
    
    
    # TODO: separar create e add
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
        else:
            raise Exception('artist_type not known.')


    """


###############################################################################  
###
###############################################################################

# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40
VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']


def prepare_float_value(value):
    value = "{0:.3f}".format(value)#str(value)
    if len(value.split('.')) > 1:
        v0 = value.split('.')[0]
        #v0 = str(int(v0))
        v1 = value.split('.')[1].rstrip('0')
        if len(v1) == 0:
            return v0 + '.'
        else:
            if len(v1) > 2: # Trimming decimals to 2 caracters
                v1 = v1[0:2]
            return v0 + '.' + v1      
    return value        



###############################################################################  
###
###############################################################################


class PlotLabelTitle(FigureCanvas):
    """
    Class for PlotLabel's title.
    
    Parameters
    ----------
    parent : wx.Window
        Window that owns this component.

    Attributes
    ----------
    _patch: matplotlib.patches.Patch
        A patch for drawing background color.
    _label: matplotlib.text.Text
        Title's container.

    """
    def __init__(self, parent, title=None, color=None, fontsize=10):
        height = float(28)/DPI
        fig = Figure(figsize=(1, height), dpi=DPI)
        super(PlotLabelTitle, self).__init__(parent, -1, fig)   
        #self.figure.set_facecolor(self._COLOR)
        #(0.5, loc, "%g" % loc, ha='center', 
        #                                va='center',  fontsize=10
        #    )
        #
        
        
        '''
        extent = [0.0, 0.0, 1.0, 1.0]
        ax = create_and_prepare_axes(fig, extent)
        #ax.        
        line = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
        ax.add_line(line)        '''
        #
        #'''
        l = matplotlib.lines.Line2D([0.0, 1.0], [0.05, 0.05])
        l.set_linewidth(1)
        l.set_color('black')  
        fig._set_artist_props(l)
        fig.lines.append(l)
        l._remove_method = lambda h: self.lines.remove(h)
        fig.stale = True
        #'''
        #rect = 0, 1.0, 1.0, 1.0
        #fig.add_axes(rect)
        #fig.add_axes(rect, frameon=False, facecolor='g')
        
        self._text = self.figure.text(0.5, 0.5, '', ha='center', va='center')
        self.update(title, color, fontsize)        
        self.mpl_connect('button_press_event', self._on_press)
        #self.Bind(wx.EVT_PAINT, self.on_paint)

    #def on_paint(self, event):
    #    print 'PlotLabelTitle.on_paint'
    #    event.Skip()
                
    def _on_press(self, event):
       # print 'PlotLabelTitle._on_press'
        self.GetParent()._on_press(event)        
        #l.draw()
        #fig.lines.append(l)  
              
    def update(self, title=None, color=None, fontsize=10):
        """
        Update PlotLabelTitle properties.
        
        Parameters
        ----------
        title : str
            Title string.
        bcolor : mpl color spec
            Tiles's background color. 
        """

        if title is not None:
            self._text.set_text(title)
        if color is not None:    
            self.figure.set_facecolor(color)
        if fontsize is not None:
            self._text.set_fontsize(fontsize)
          

    def get_properties(self):
        """
        Get PlotLabelTitle properties.
        
        Returns
        -------
        properties : dict
            The PlotLabelTitle properties with 'text' and 'bgcolor' keys.
        """
        properties = {}
        properties['text'] = self.figure.get_text()
        properties['color'] = self.figure.get_facecolor()
        properties['fontsize'] = self.figure.text.get_fontsize()
        return properties
       



class VisDataLabel(FigureCanvas):
    """
    Class for PlotLabel's visual object.
    
    Parameters
    ----------
    parent : wx.Window
        Window that owns this component.

    Attributes
    ----------
    _axes: matplotlib.axes.Axes
        A axes for drawing.
    parent : wx.Window
        Window that owns this component.

    """
    _COLOR = 'white' #'lightblue' #'white'
    
    def __init__(self, parent):
        self.parent = parent
        #fig = Figure(figsize=(1, 0.35))
        fig = Figure(figsize=(1, 0.40))
        super(VisDataLabel, self).__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        self._obj_uid = None  
        #self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        self._mplot_objects = {}
        self._properties = {}
        self._start_variables()
        self.mpl_connect('button_press_event', self._on_press)


    def destroy(self):
        wx.CallAfter(self.parent.remove_object, self)
               
    def _on_press(self, event):
        self.GetParent()._on_press(event)

    def _start_variables(self):
        self.title = None 
        self.plottype = None
        self.left_scale = None
        self.right_scale = None
        self.unit = None
        self.thickness = None
        self.color = None
        self.cmap = None
        self.xlim = None
        self.zlabel = None        
        self.zlim = None
        self.xlabel = None        
        #self.xlim = None

    def set_object_uid(self, object_uid):
        self._obj_uid = object_uid 


    def set_title(self, title):
   #     print '\nVisDataLabel.set_title:', title
        if self.title == title:
   #         print 'retornou'
            return
        props = self._properties.get('title', None)
        if props:
            title_text = self._mplot_objects.get('title_text', None)
            if not title_text:
                title_text = create_text(self.figure, title, props)
                self._mplot_objects['title_text'] = title_text
   #             print 111
            else:
                title_text.set_text(title)
   #             print 222
            self.draw()    
            self.title = title   
       # else:
       #     print 'not props'
        #print 'set title ended'    
   
    
    def set_unit(self, unit):
        if self.unit == unit:
            return
        props = self._properties.get('sub_title', None)
        if props:
            unit_text = self._mplot_objects.get('unit_text', None)
            if not unit_text:
                unit_text = create_text(self.figure, '(' + unit + ')', props)
                self._mplot_objects['unit_text'] = unit_text
            else:
                unit_text.set_text('(' + unit + ')')
            self.draw()    
            self.unit = unit   
                                
            
    def set_color(self, color):
        if self.plottype == 'line':
            if self.color == color:
                return
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent)                    
                line = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
                #self._mplot_objects['line_axes'] = ax
            line.set_color(color) 
            self.draw()
            self.color = color


    def set_thickness(self, thickness):
        if self.plottype == 'line':
            if self.thickness == thickness:
                return
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent)        
                line = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
                #self._mplot_objects['line_axes'] = ax
            line.set_linewidth(thickness) 
            self.draw()
            self.thickness = thickness
            
    def set_colormap(self, cmap):
        #print '\nVisDataLabel.set_colormap'
        if self.plottype == 'density':
            if self.cmap == cmap:
                return
            cmap_img = self._mplot_objects.get('cmap_img', None) 
            if not cmap_img:
                extent = self._properties.get('cmap_axes_extent', None)
                ax = create_and_prepare_axes(self.figure, extent) 
                gradient = np.linspace(0, 1, 256)
                gradient = np.vstack((gradient, gradient))
                cmap_img = ax.imshow(gradient, aspect='auto')
                self._mplot_objects['cmap_img'] = cmap_img
                self.figure.add_axes(ax)
            cmap_img.set_cmap(cmap)    
            self.draw()
            self.cmap = cmap


    def set_zlabel(self, z_axis_label):
        if self.plottype == 'density' or self.plottype == 'wiggle' or self.plottype == 'both':
            if self.zlabel == z_axis_label:
                return
            props = self._properties.get('zlabel', None)    
            zlt = self._mplot_objects.get('zlabel_text', None) 
            if not zlt:
                zlt = create_text(self.figure, z_axis_label, props)
                self._mplot_objects['zlabel_text'] = zlt
            else:    
                zlt.set_text(z_axis_label)    
            self.draw()
            self.zlabel = z_axis_label
            

    def set_xlim(self, xlim):
        if self.xlim == xlim:
            return
        xmin, xmax = xlim
        props = self._properties.get('xmin', None)
        if props:
            xmin_text = self._mplot_objects.get('xmin_text', None)
            xmin = prepare_float_value(xmin)
            if not xmin_text:    
                self._mplot_objects['xmin_text'] = create_text(self.figure, 
                                                                xmin, props
                )
            else:
                xmin_text.set_text(xmin)
        else:
            raise Exception()
        props = self._properties.get('xmax', None)
        if props:
            xmax_text = self._mplot_objects.get('xmax_text', None)
            xmax = prepare_float_value(xmax)
            if not xmax_text:  
                self._mplot_objects['xmax_text'] =  create_text(self.figure, 
                                                                xmax, props
                )
            else:
                xmax_text.set_text(xmax)
        else:
            raise Exception()  
        self.draw()             
        self.xlim == xlim    
        
        
    def set_zlim(self, zlim):
        if self.zlim == zlim:
            return
        zmin, zmax = zlim
        props = self._properties.get('zmin', None)
        if props:
            zmin_text = self._mplot_objects.get('zmin_text', None)
            zmin = prepare_float_value(zmin)
            if not zmin_text:                
                self._mplot_objects['zmin_text'] = create_text(self.figure, 
                                                                zmin, props
                )
            else:
                zmin_text.set_text(zmin)
        else:
            raise Exception()
        props = self._properties.get('zmax', None)
        if props:
            zmax_text = self._mplot_objects.get('zmax_text', None)
            zmax = prepare_float_value(zmax)
            if not zmax_text:  
                self._mplot_objects['zmax_text'] =  create_text(self.figure, 
                                                                zmax, props
                )
            else:
                zmax_text.set_text(zmax)
        else:
            raise Exception()  
        self.draw()             
        self.zlim == zlim                   
            
    
    def set_xlabel(self, x_axis_label):
        #print '\nVisDataLabel.set_xlabel:', x_axis_label
        if self.plottype == 'density' or self.plottype == 'wiggle':
            if self.xlabel == x_axis_label:
                return
            props = self._properties.get('xlabel', None)    
            xlt = self._mplot_objects.get('xlabel_text', None) 
            if not xlt:
                xlt = create_text(self.figure, x_axis_label, props)
                self._mplot_objects['xlabel_text'] = xlt
            else:    
                xlt.set_text(x_axis_label)    

            self.xlabel = x_axis_label

            self.draw()


    def set_offsets(self, offsets_list):
        if self.plottype == 'wiggle':
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent)     
                ax.set_xlim((0, len(offsets_list)+1))
                ax.set_ylim((-1.0, 1.0))
                line = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
                line.set_color('black')
                line.set_linewidth(1)
                self._mplot_objects['line'] = ax.add_line(line)
                x_data = np.array(range(0, len(offsets_list)+1), dtype=np.float)
                y_data = np.zeros(len(offsets_list)+1)
                
                factor = 0.5
                x_data[0] = x_data[0] + factor
                x_data[-1] = x_data[-1] + factor
                    
                ax.plot(x_data[0], 0.5, '|', color='black')
                ax.plot(x_data[-1], 0.5, '|', color='black')
                line.set_data(x_data, y_data)       
                for i in range(0, len(offsets_list)):
                    ax.plot(i+1, -0.5, '|', color='black')
                    ax.text(i+1, -2.4, str(offsets_list[i]), fontsize=8)

   

    def _remove_all_artists(self):
        for value in self._mplot_objects.values():
            if value:
                value.remove()
        self._mplot_objects = {}              
        

    def set_plot_type(self, plottype):
   #     print '\n\nVisDataLabel.set_plotype: ', plottype
        if plottype == self.plottype:
   #         print 111
            return
        if plottype not in VALID_PLOT_TYPES:
   #         print 222
            return


        self._remove_all_artists()


        self._start_variables()   
   #     print 333




        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        
        
        if plottype == 'line':
            self._properties['title'] = {'x': 0.5, 'y':0.64, 'ha':'center', 'fontsize':10}
            self._properties['sub_title'] = {'x': 0.5, 'y':0.19, 'ha':'center', 'fontsize':9}        
            self._properties['xmin'] = {'x': self._properties['xleft'],
                             'y':0.33, 'ha':'left', 'va':'center', 'fontsize':9
            }     
            self._properties['xmax'] = {'x': self._properties['xright'],
                             'y':0.33, 'ha':'right', 'va':'center', 'fontsize':9
            }
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.05, 
                        self._properties['xright']-self._properties['xleft'],
                        0.15
            ]
            
        elif plottype == 'density':
            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
                                                                'fontsize':10}            
            self._properties['cmap_axes_extent'] = [self._properties['xleft'],
                        0.10, 
                        self._properties['xright']-self._properties['xleft'],
                        0.22
            ]
            ypos = 0.5
            self._properties['zlabel'] = {'x': 0.5, 'y':ypos, 'ha':'center', 
                                                'va':'center', 'fontsize':9
            }
            self._properties['zmin'] = {'x':self._properties['xleft'],
                         'y':ypos, 'ha':'left', 'va':'center', 'fontsize':9
            }
            self._properties['zmax'] = {'x': self._properties['xright'],
                        'y':ypos, 'ha':'right', 'va':'center', 'fontsize':9
            }
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.0, 
                        self._properties['xright']-self._properties['xleft'],
                        0.2
            ]
            ypos = 0.18
            self._properties['xlabel'] = {'x': 0.5, 'y':ypos, 'ha':'center', 
                                                'va':'center', 'fontsize':10}   
            self._properties['xmin'] = {'x':self._properties['xleft'],
                         'y':ypos, 'ha':'left', 'va':'center', 'fontsize':9
            }
            self._properties['xmax'] = {'x': self._properties['xright'],
                        'y':ypos, 'ha':'right', 'va':'center', 'fontsize':9
            }    
                    
        elif plottype == 'wiggle':  
            #self._properties['title'] = {'x': 0.5, 'y':0.75, 'ha':'center', 
            #                                                    'fontsize':10}  
            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
                                                                'fontsize':10}   
            #
            #self._properties['zlabel'] = {'x': 0.5, 'y':0.58, 'ha':'center', 
            #                                    'va':'center', 'fontsize':9
            #}  
            self._properties['zlabel'] = {'x': 0.5, 'y':0.16, 'ha':'center', 'fontsize':9}    
            #                                                  
            self._properties['xlabel'] = {'x': 0.5, 'y':0.35, 'ha':'center', 
                                                'va':'center', 'fontsize':9}    
            
            self._properties['line_axes_extent'] = [0.0,  0.15, 1.0, 0.2]
            # Falta x_range
            self._properties['xmin'] = {'x': self._properties['xleft'],
                             'y':0.3, 'ha':'left', 'va':'center', 'fontsize':9
            }     
            self._properties['xmax'] = {'x': self._properties['xright'],
                             'y':0.3, 'ha':'right', 'va':'center', 'fontsize':9
            }
            ###
        elif plottype == 'both':
            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
                                                                'fontsize':10}            
            self._properties['cmap_axes_extent'] = [self._properties['xleft'],
                        0.10, 
                        self._properties['xright']-self._properties['xleft'],
                        0.22
            ]
            ypos = 0.5
            self._properties['zlabel'] = {'x': 0.5, 'y':ypos, 'ha':'center', 
                                                'va':'center', 'fontsize':9
            }
            self._properties['zmin'] = {'x':self._properties['xleft'],
                         'y':ypos, 'ha':'left', 'va':'center', 'fontsize':9
            }
            self._properties['zmax'] = {'x': self._properties['xright'],
                        'y':ypos, 'ha':'right', 'va':'center', 'fontsize':9
            }
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.0, 
                        self._properties['xright']-self._properties['xleft'],
                        0.2
            ]
            ypos = 0.18
            self._properties['xlabel'] = {'x': 0.5, 'y':ypos, 'ha':'center', 
                                                'va':'center', 'fontsize':10}   
            self._properties['xmin'] = {'x':self._properties['xleft'],
                         'y':ypos, 'ha':'left', 'va':'center', 'fontsize':9
            }
            self._properties['xmax'] = {'x': self._properties['xright'],
                        'y':ypos, 'ha':'right', 'va':'center', 'fontsize':9
            }                
        elif plottype == 'partition' or plottype == 'index':
            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
                                                                'fontsize':10}
            self._properties['sub_title'] = {'x': 0.5, 'y':0.2, 'ha':'center', 
                                                                'fontsize':9}
            
        #self.draw()                                                                    
        self.plottype = plottype                                                        



            
 
class PlotLabel(wx.Panel, SelectPanelMixin):
    
    def __init__(self, wx_parent, view_object):
        super(PlotLabel, self).__init__(wx_parent)
        self.track_view_object = view_object
        self._title = None
        self._visual_objects = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))  
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_press)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_press)
        self._selected = False

    def _on_press(self, event):
        self.track_view_object.process_event(event)

    def create_title(self):
        self._title = PlotLabelTitle(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
                        
    def update_title(self, text='', bgcolor=None, fontsize=10):
        if self._title is None:
            self.create_title()
        if not bgcolor:
            bgcolor = DEFAULT_LABEL_BG_COLOR
        self._title.update(text, bgcolor, fontsize) 
        self.Layout() 
                  
    def remove_title(self):
        if self._title is not None:
            self.GetSizer().Remove(self._title)
            t = self._title
            self._title = None
            t.Destroy()
            self.Layout()

    def get_title_properties(self):
        if self._title:
            return self._title.get_properties()
        return None          
                
    def append_object(self):
        return self.insert_object(len(self._visual_objects))
        
    def insert_object(self, pos):
        """
        Insert a new visual object at given pos with properties informed.
        """
        vdl = VisDataLabel(self)
        self._visual_objects.insert(pos, vdl)
        self.GetSizer().Add(vdl, 0,  wx.EXPAND)
        self.Layout()
        return vdl
                
    def remove_object(self, *args):
        """
        Removes the track is a given position. 
        """
        if not args[0]:
            return
        if isinstance(args[0], int):    
            vdl = self._visual_objects.pop(args[0])
        elif isinstance(args[0], VisDataLabel):   
            vdl = args[0]
            self._visual_objects.remove(vdl)
        else:
            raise Exception()            
        self.GetSizer().Detach(vdl)
        vdl.Destroy()
        self.Layout()           



def create_and_prepare_axes(figure, extent):
    #import matplotlib.figure.Figure.text
    ax = Axes(figure, extent)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.xaxis.set_major_locator(NullLocator())
    ax.yaxis.set_major_locator(NullLocator())
    figure.add_axes(ax)
    return ax


def create_text(figure, to_print, props):
    #print '\ncreate_text:', props,  str(to_print)
    text = figure.text(props.get('x'), props.get('y'), str(to_print),
                       ha=props.get('ha'), fontsize=props.get('fontsize')
    )
    vertical_alignment = props.get('va', None)
    if vertical_alignment:
        text.update({'va': vertical_alignment})
    return text
            
  