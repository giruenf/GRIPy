# -*- coding: utf-8 -*-
import wx
import numpy as np
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.axes import Axes
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import NullFormatter
from matplotlib.ticker import MultipleLocator
from App.utils import LogPlotDisplayOrder
from App import log



class DummyAxes(Axes):    
    
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
        'facecolor': 'white',
        'spines_color': 'black',
        'tick_grid_color': '#A9A9A9'    #'#DFDFDF'#
    }  
    

    _properties = {
        'y_major_grid_lines': None,
        'y_minor_grid_lines': None,
        'decades': None,
        'log_base': 10,
        'scale_lines': None,
        'plotgrid': None,
        'leftscale': None,
        'minorgrid': None,
        'depth_lines': None,
        'xlim': (0.0, 100.0), # Used only when x_scale is linear
    }

         

    def __init__(self, figure, **initial_properties):
        if matplotlib.__version__.startswith('2.'):
            Axes.__init__(self, figure, 
                    [0.0, 0.0, 1.0, 1.0], 
                    facecolor=self._internal_props['facecolor'] # MPL 2.0
            )
        else:
            Axes.__init__(self, figure, 
                    [0.0, 0.0, 1.0, 1.0], 
                    axisbg=self._internal_props['facecolor'] # MPL 1.X
            )
        
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
        #self.update()
        
        for key, value in initial_properties.items():
            if key in self._valid_keys:
                self._properties[key] = value
        self.update('x_scale', self._properties.get('x_scale'))        


#    def get_properties(self):
#        return self.props


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
                self.update('leftscale', self._properties.get('leftscale')) # leftscale or decades to update xlim 
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
                self.set_xlim(xlim)       
        elif key == 'minorgrid':  
            if not isinstance(value, bool):  
                raise ValueError('O valor de minorgrid deve ser True ou False.')  
            if self.get_xscale() == 'log' and self._properties.get('plotgrid'):    
                self.grid(value, axis='x', which='minor', **self.default_grid_mapping)
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
            
        
            
    """        
    def _update_old(self, **properties):
        print '\nDummyAxes.update: ', properties
    
        valid_props = {}
        for key, value in properties.items():
            if key in self._valid_keys:
                valid_props[key] = value
        properties = valid_props     
        
        self.props = self.check_properties(properties)
        print 'props:', self.props

        # EIXO X - ESCALA LOGARITMICA
        if self.props.get('x_scale') == 1:
            self.set_xscale('log')
            xlim = (self.props.get('leftscale'), 
                self.props.get('leftscale')*(self._props.get('log_base')**self.props.get('decades')))
            self.set_xlim(xlim)
            if self.props.get('plotgrid') == True:
                self.grid(True, axis='x', which='major', **self.default_grid_mapping)
                if self.props.get('minorgrid') == True:
                    self.grid(True, axis='x', which='minor', **self.default_grid_mapping)
                elif self.props.get('minorgrid') == False:
                    self.grid(False, axis='x', which='minor', **self.default_grid_mapping)
        # EIXO X - ESCALA LINEAR        
        if self.props.get('x_scale') == 0:
            self.set_xscale('linear')
            self.set_xlim(self._props['xlim'])
            if self.props.get('plotgrid'):
                x0, x1 = self.get_xlim()
                x_major_grid_lines = (x1-x0)/self.props.get('scale_lines')
                self.xaxis.set_major_locator(MultipleLocator(x_major_grid_lines))    
                self.grid(True, axis='x', which='major', **self.default_grid_mapping)
        self.xaxis.set_major_formatter(NullFormatter())    

        # EIXO Y - DATUM (DEPTH)
        self.set_ylim(self.props.get('ylim'))
        
        if self.props.get('x_scale') == 2:
            raise Exception('There no support yet to Sin scale.')
        if self.props.get('x_scale') == 3:    
            raise Exception('There no support yet to Cosin scale.')
            
        if self.props.get('plotgrid'):    
            if self.props.get('depth_lines') == 0:
                self.ticks = False
                self.grid(True, axis='y', which='major', **self.major_y_grid_mapping)
                self.grid(True, axis='y', which='minor', **self.default_grid_mapping)
            # DEPTH LINES == LEFT 
            elif self.props.get('depth_lines') == 1:
                self.ticks = True
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.tick_params(left=True, right=False, which='both', 
                                 axis='y', direction='in'
                )
                self.grid(False, axis='y', which='both')
            # DEPTH LINES == RIGHT
            elif self.props.get('depth_lines') == 2:
                self.ticks = True
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.tick_params(left=False, right=True, which='both',
                                 axis='y', direction='in'
                )                 
                self.grid(False, axis='y', which='both')
            # DEPTH LINES == CENTER   
            elif self.props.get('depth_lines') == 3:
                ### A DESENVOLVER
                self.ticks = True
                self.spines['left'].set_position('center')
                self.spines['right'].set_position('center')
                self.tick_params(left=True, right=True, which='both', axis='y',
                                 direction='out')
                self.grid(False, axis='y', which='both')            
            # DEPTH LINES == LEFT AND RIGHT    
            elif self.props.get('depth_lines') == 4:   
                self.ticks = True
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.tick_params(left=True, right=True, which='both', 
                                 axis='y', direction='in'
                )
                self.grid(False, axis='y', which='both')   
            # DEPTH LINES == NONE
            elif self.props.get('depth_lines') == 5:
                self.ticks = False
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.yaxis.set_ticks_position('none')
                self.grid(False, axis='y', which='both')                         
            if self.ticks:
                self.show_y_ticks()
            elif self.props.get('depth_lines') == 0:
                self.hide_y_ticks()
        else:
            self.grid(False, axis='both', which='both')
            self.hide_y_ticks()
    """        

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
         
        
    """    
    def check_properties(self, props):

        if not props.get('ylim'): 
            if not self.props.get('ylim'):
                props['ylim'] = self._props['ylim']
            else:
                props['ylim'] = self.props['ylim']
        else:        
            ymin, ymax =  props.get('ylim')
            if not isinstance(ymin, (int, float)) \
                        or not isinstance(ymax, (int, float)):
                raise ValueError('ylim deve ser uma tupla de int ou float.')
            elif ymax == ymin:
                raise ValueError('Os valores de ylim nao podem ser iguais.')
            elif ymin < 0 or ymax < 0:
                raise ValueError('Nenhum dos valores de ylim podem ser negativos.')            
            elif ymin < ymax:
                # DEVIDO AO EIXO Y SER INVERTIDO EM RELACAO AO AXES
                props['ylim'] = (ymax, ymin)    

        if not props.get('y_major_grid_lines'):
            if not self.props.get('y_major_grid_lines'):
                props['y_major_grid_lines'] = self._props['y_major_grid_lines']
            else:    
                props['y_major_grid_lines'] = self.props['y_major_grid_lines']
        elif not isinstance(props.get('y_major_grid_lines'), float):
            raise ValueError('y_major_grid_lines deve ser float.') 
        elif props.get('y_major_grid_lines') <= 0:
            raise ValueError('y_major_grid_lines deve ser maior que 0.')        

        if not props.get('y_minor_grid_lines'):
            if not self.props.get('y_minor_grid_lines'):
                props['y_minor_grid_lines'] = self._props['y_minor_grid_lines']
            else:        
                props['y_minor_grid_lines'] = self.props['y_minor_grid_lines']
        elif not isinstance(props.get('y_minor_grid_lines'), float):
            raise ValueError('y_minor_grid_lines deve ser float.') 
        elif props.get('y_minor_grid_lines') <= 0:
            raise ValueError('y_minor_grid_lines deve ser maior que 0.')     
        
        
        if props.get('plotgrid') is None:
            if self.props.get('plotgrid') is None:
                props['plotgrid'] = False
            else:
                props['plotgrid'] = self.props['plotgrid']
                 
        if not isinstance(props.get('plotgrid'), (bool)):  
            raise ValueError('O valor de plotgrid deve ser True ou False.')
        
        
        if props.get('x_scale') is None:
            if self.props.get('x_scale') is None:
                props['x_scale'] = self._props['x_scale']
            else:
                props['x_scale'] = self.props['x_scale']
        
 
        if not isinstance(props.get('x_scale'), int):
             raise ValueError('O valor de x_scale deve ser inteiro.')
        if not props.get('x_scale') in [0, 1, 2, 3]:
            raise ValueError('A escala deve ser linear ou logaritmica(seno ou cosseno). (x_scale in [0, 1, 2, 3])')
                
        if props.get('x_scale') == 1:
            if not props.get('decades'):
                if not self.props.get('decades'):
                    raise ValueError('decades deve ser informado quando a escala eh logaritmica.')
                else:
                    props['decades'] = self.props['decades']
            else:
                if not isinstance(props.get('decades'), int):
                    try:
                        props['decades'] = int(props.get('decades'))
                    except Exception:
                        raise ValueError('decades deve ser inteiro.')
                    if props.get('decades') <= 0:
                        raise ValueError('decades deve ser maior que 0.') 
            if not props.get('leftscale'):
                if not self.props.get('leftscale'):
                    raise ValueError('leftscale deve ser informado quando a escala é logaritmica.')
                else:
                    props['leftscale'] = self.props['leftscale']
            else:
                if not isinstance(props.get('leftscale'), float):
                    try:
                        props['leftscale'] = float(props.get('leftscale'))
                    except Exception:
                        raise ValueError('leftscale deve ser float.')    
                    if props.get('leftscale') <= 0:
                        raise ValueError('leftscale deve ser maior que 0.')
            
            
        if props.get('minorgrid') is None:
            if self.props.get('minorgrid') is None:
                props['minorgrid'] = True
            else:
                props['minorgrid'] = self.props['minorgrid']
       
        if not isinstance(props.get('minorgrid'), (bool)):  
            raise ValueError('O valor de minorgrid deve ser True ou False.')  
            
            
        if props.get('scale_lines') is None:
            if self.props.get('scale_lines') is None: 
                props['scale_lines'] = self._props.get('scale_lines') 
            else:
                props['scale_lines'] = self.props.get('scale_lines')
        else:
            if not isinstance(props.get('scale_lines'), int):
                try:
                    props['scale_lines'] = int(props.get('scale_lines'))
                except Exception:
                    raise ValueError('scale_lines deve ser inteiro.') 
                if props.get('scale_lines') <= 0:
                    raise ValueError('scale_lines deve ser maior que 0.')     
            
            
        if props.get('depth_lines') is None:
            if self.props.get('depth_lines') is None: 
                props['depth_lines'] = self._props['depth_lines']      
            else:
                props['depth_lines'] = self.props['depth_lines']
        else:
            if not isinstance(props.get('depth_lines'), int): 
                raise ValueError('depth_lines deve ser inteiro.')
            elif props.get('depth_lines') < 0 or props.get('depth_lines') > 5:
                raise ValueError('depth_lines deve ser entre 0 e 5.')    
                
        return props
        """

###############################################################################  
###
###############################################################################

     
class TrackFigureCanvas(FigureCanvas):

        
    def __init__(self, wx_parent, track_view_object, size, **properties):   
        self.figure = Figure(facecolor='white', 
                             figsize=(0.01, 0.0))
        FigureCanvas.__init__(self, wx_parent, -1, self.figure)
        self.SetSize(size)
        self.dummy_ax = DummyAxes(self.figure, **properties)
        self.figure.add_axes(self.dummy_ax)
        self.track_view_object = track_view_object
        self.axes = []
        self._selected = False
        self.selectedCanvas = []
        self.index_axes = None       
        self.mpl_connect('button_press_event', self._on_press)
        #self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        self.mpl_connect('motion_notify_event', self.on_move)
        

    def on_move(self, event):
        if event.inaxes is None:
            return
        info = 'Depth: ' + "{:0.2f}".format(event.ydata)    
        self.track_view_object.message(info)
        
        '''
        pixelsdata = event.inaxes.transData.transform_point((event.xdata, event.ydata))
        print pixelsdata    
        dummydata, values = self.get_transformed_values(pixelsdata) 
        print event.ydata, values
        '''
        
    '''    
    def get_transformed_values(self, point_px):
        if point_px is None:
            return None, None
        dummydata = self.dummy_ax.transData.inverted().transform_point(point_px)       
        values = []        
        for ax in self.figure.axes:
            valuedata = ax.transData.inverted().transform_point(point_px)         
            values.append(valuedata.tolist()[0])
        return dummydata.tolist(), values     
    '''
                
    def _on_press(self, event):
        self.track_view_object.process_event(event)
#        self._view.process_event(event)
    
    def is_selected(self):
        return self._selected
             
    #def _on_middle_down(self, event):
    #    self.track_view_object.set_selected(self, not self._selected)   
    #    self._do_select()
    #    event.Skip()
            
    def _do_select(self):
        self._selected = not self._selected
        self.GetParent()._draw_window_selection(self)         
                
           
    def update(self, key, value):
        self.dummy_ax.update(key, value)
        self.draw()            
  
                 
    def set_ylim(self, ylim):
        self.dummy_ax.update('ylim', ylim)
        self.draw()

    # TODO: VERIFICAR ISSO
    def show_index_curve(self, step=500):
        if not self.index_axes:
            self.index_axes = self.figure.add_axes(self.dummy_ax.get_position(True),
                              sharey=self.dummy_ax, 
                              frameon=False
            )
            self.index_axes.xaxis.set_visible(False)
            self.index_axes.yaxis.set_visible(False)
            self.axes.append(self.index_axes)  
            self.index_axes.set_zorder(LogPlotDisplayOrder.Z_ORDER_INDEX)  
        else:
            self.index_axes.texts = []
        start = 0
        end = 10000
        locs = np.arange(start, end, step)
        for loc in locs:
            text = self.index_axes.text(0.5, loc, "%g" % loc, ha='center', 
                                        va='center',  fontsize=10
            )
            text.set_bbox(dict(color='white', alpha=0.5, edgecolor='white'))  
        self.draw()     


    def hide_index_curve(self):
        if not self.index_axes:
            return
        self.index_axes.texts = []
        self.draw() 

            

        
        

        

