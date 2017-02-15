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
from App import log



class DummyAxes(Axes):       
    _props = {
        'y_major_grid_lines': 500.0,
        'y_minor_grid_lines': 100.0,
        'log_base': 10,
        'scale_lines': 5,
        'x_scale': 0,
        'depth_lines': 0,
        'xlim': (0.0, 100.0),
        'ylim': (6000.0, 0.0),
        'major_tick_width': 1.4,        
        'minor_tick_width': 0.7,
        'major_tick_lenght': 10,
        'minor_tick_lenght': 5,
        'dummy_ax_zorder': 0,
        'ticks_zorder': 8,
        'spines_zorder': 10,
        'grid_linestyle': '-',
        'axes_bgcolor': 'white',
        'spines_color': 'black',
        'tick_grid_color': '#A9A9A9'    #'#DFDFDF'#
    }


    _valid_props_keys = [
        'plotgrid',
        'ylim',
        'y_major_grid_lines',
        'y_minor_grid_lines',
        'x_scale',
        'decades',
        'leftscale',
        'minorgrid',
        'scale_lines',
        'depth_lines',
    ]          
      
      

    def __init__(self, figure, properties, layout_properties=None):
        Axes.__init__(self, figure, 
                      [0.0, 0.0, 1.0, 1.0], 
                      axisbg=self._props.get('axes_bgcolor')
        )
        self.set_spines_visibility(False)    
        
        
        self.props = {}
        self.major_y_grid_mapping = {'color': self._props['tick_grid_color'], 
                             'linestyle': self._props['grid_linestyle'], 
                             'linewidth': self._props['major_tick_width']
        }
        self.default_grid_mapping = {'color': self._props['tick_grid_color'], 
                             'linestyle': self._props['grid_linestyle'], 
                             'linewidth': self._props['minor_tick_width']
        }
        
        self.set_zorder(self._props['dummy_ax_zorder'])
        
        # EIXO Y SEMPRE SERÁ LINEAR
        self.set_yscale('linear')        
        
        # EIXO Y NÃO TERÁ LABELS
        self.yaxis.set_major_formatter(NullFormatter())
        self.yaxis.set_minor_formatter(NullFormatter())
        
        self.yaxis.set_tick_params('major', size=10)
        self.yaxis.set_tick_params('minor', size=5)        
        
        # EIXO X NÃO POSSUI TICKS
        self.hide_x_ticks()
        
        # EIXO Y TICKS
        self.tick_params(axis='y', which='major', direction='in',
                color=self._props['tick_grid_color'],          
                length=self._props['major_tick_lenght'],
                width=self._props['major_tick_width'], 
                zorder=self._props['ticks_zorder'])
        self.tick_params(axis='y', which='minor', direction='in',
                color=self._props['tick_grid_color'],         
                length=self._props['minor_tick_lenght'],
                width=self._props['minor_tick_width'], 
                zorder=self._props['ticks_zorder'])
        
        # PARA NÃO HAVER SOBREPOSIÇÃO DE TICKS E GRIDS SOBRE OS SPINES(EIXO GRÁFICO) 
        self.spines['left'].set_zorder(self._props['spines_zorder'])
        self.spines['right'].set_zorder(self._props['spines_zorder'])
        self.spines['top'].set_zorder(self._props['spines_zorder'])
        self.spines['bottom'].set_zorder(self._props['spines_zorder'])
        
        self.set_spines_color(self._props['spines_color'])
        
        self.update(**properties)  



    def set_spines_visibility(self, boolean):                
        self.spines['right'].set_visible(boolean)
        self.spines['top'].set_visible(boolean)
        self.spines['left'].set_visible(boolean)
        self.spines['bottom'].set_visible(boolean)



    def get_properties(self):
        return self.props


    def update(self, **properties):
        #print '\nupdate: ', properties
    
        valid_props = {}
        for key, value in properties.items():
            if key in self._valid_props_keys:
                valid_props[key] = value
        properties = valid_props     
        
        
        self.props = self.check_properties(properties)


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



    def hide_x_ticks(self):
        self.xaxis.set_tick_params('major', size=0)
        self.xaxis.set_tick_params('minor', size=0)

    def show_y_ticks(self):
        self.yaxis.set_tick_params('major', size=10)
        self.yaxis.set_tick_params('minor', size=5)
        self.yaxis.set_major_locator(MultipleLocator(self.props.get('y_major_grid_lines')))
        self.yaxis.set_minor_locator(MultipleLocator(self.props.get('y_minor_grid_lines')))

    def hide_y_ticks(self):
        self.yaxis.set_tick_params('major', size=0)
        self.yaxis.set_tick_params('minor', size=0)


    def set_spines_color(self, color):
        self.spines['bottom'].set_color(color)
        self.spines['top'].set_color(color)
        self.spines['left'].set_color(color)
        self.spines['right'].set_color(color)
         
        
        
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
        

 



###############################################################################  
###
###############################################################################


      
class TrackFigureCanvas(FigureCanvas):

        
    def __init__(self, wx_parent, view_object, size, **properties):
        self.dummy_ax = None
        self.properties = properties
        ### _BaseFigureCanvas - Inicio
        self.dpi = 80
        self.height_inches_used = 0.0
        self.width_inches = 0.01            
        self.figure = Figure(facecolor='white', 
                             figsize=(self.width_inches, self.height_inches_used)) 
        FigureCanvas.__init__(self, wx_parent, -1, self.figure)
        self.SetSize(size)
        self.dummy_ax = DummyAxes(self.figure, properties)
        self.figure.add_axes(self.dummy_ax)
        ### _BaseFigureCanvas - Fim
        self._view = view_object
        self.axes = []
        self._selected = False
        self.selectedCanvas = []
        self.index_axes = None
        
        self.mpl_connect('button_press_event', self._on_press)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        
        
    def _on_press(self, event):
        self._view.process_event(event)

        
    def is_selected(self):
        return self._selected
        
        
    def _on_middle_down(self, event):
        self._view.set_selected(self, not self._selected)   
        self._do_select()
        event.Skip()
        
        
    def _do_select(self):
        self._selected = not self._selected
        self.GetParent()._draw_window_selection(self)         
        
        
    #def get_transformed_values(self, point_px):
    #    if point_px is None:
    #        return None, None
    #    dummydata = self.dummy_ax.transData.inverted().transform_point(point_px)       
    #    values = []        
    #    for ax in self.axes:
    #        valuedata = ax.transData.inverted().transform_point(point_px)         
    #        values.append(valuedata.tolist()[0])
    #    return dummydata.tolist(), values     
        
     
    def update_properties(self, **kwargs):
        if self.dummy_ax is not None:
            self.dummy_ax.update(**kwargs)
            self.draw()            
  
    def get_properties(self):
        return self.dummy_ax.get_properties()   
              
              
    def set_dummy_spines_visibility(self, boolean):
        if self.dummy_ax is not None:
            self.dummy_ax.set_spines_visibility(boolean)
                 
    
    def set_ylim(self, ylim):
        print '\n\nTrackFigureCanvas.set_ylim: ', ylim, '\n\n'
        min_, max_ = ylim
        if min_ == max_:
            return
        if max_ < min_:
            ylim = (max_, min_)
        self.dummy_ax.update(ylim=ylim)
        self.draw()


    def show_index_curve(self, step=500):
        if not self.index_axes:
            self.index_axes = self.figure.add_axes(self.dummy_ax.get_position(True),
                              sharey=self.dummy_ax, 
                              frameon=False
            )
            self.index_axes.xaxis.set_visible(False)
            self.index_axes.yaxis.set_visible(False)
            self.axes.append(self.index_axes)  
            self.index_axes.set_zorder(100)  
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
        #raise Exception()    
        self.draw()     


    def hide_index_curve(self):
        if not self.index_axes:
            return
        self.index_axes.texts = []
        self.draw() 

            

        
        

        

