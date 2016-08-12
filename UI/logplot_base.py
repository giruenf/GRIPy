# -*- coding: utf-8 -*-
import wx
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator
import matplotlib.patches as Patches
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from matplotlib.ticker import NullFormatter, MultipleLocator
from matplotlib.colors import colorConverter



# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 28
LOG_LABEL_TITLE_BGCOLOR = 'white'
FACTOR = 1.57

# Basis class to all Classes in this project 
class Base(object):
    # _default_layout_properties refers to mandatory properties
    # Child classes can override this in order to specify 
    # theirs own mandatory properties
    _default_layout_properties = {}
    # _valid_props refers to optional properties
    # Child classes should override this in order to specify 
    # theirs own optionL properties
    _valid_props = []
    __id = 1
    
    def __init__(self, layout_properties=None):
        self.__name = self.__get_unique_label()
        if layout_properties is None:
            layout_properties = self._default_layout_properties
        else:
            for key, value in self._default_layout_properties.items():
                if key not in layout_properties \
                        or layout_properties[key] is None:
                    layout_properties[key] = value
        self.layout_properties = layout_properties
                    
    @classmethod
    def __get_unique_label(cls):
        label = '%s %i' % (cls.__name__, cls.__id)
        cls.__id += 1
        return label

    @classmethod
    def _get_valid_props(cls, props):
        valid_props = {}
        for key, value in props.items():
            if key in cls._valid_props:
                valid_props[key] = value
        return valid_props
    
    def _get_name(self):
        return self.__name
        
    def set_properties(self, **props):
        raise NotImplementedError('This method should be implemented by child classes.')  

    def get_properties(self):
        raise NotImplementedError('This method should be implemented by child classes.')  
   


# Basis class to all types of Axes in this project 
class AxesBase(Axes, Base):
    _default_layout_properties = {'bgcolor': 'white'}

    def __init__(self, figure, rect, layout_properties=None):
        Base.__init__(self, layout_properties)
        self.rect = rect
        Axes.__init__(self, figure, self.rect, label=self._get_name(), 
                    axisbg=self.layout_properties['bgcolor'])
        self.set_spines_visibility(False)                    
                    
                    
    def set_spines_visibility(self, boolean):                
        self.spines['right'].set_visible(boolean)
        self.spines['top'].set_visible(boolean)
        self.spines['left'].set_visible(boolean)
        self.spines['bottom'].set_visible(boolean)




class DummyAxes(AxesBase):       
    # Overriding Base._default_layout_properties
    _default_layout_properties = {
        'y_major_grid_lines': 500.0,
        'y_minor_grid_lines': 100.0,
        'log_base': 10,
        'scale_lines': 5,
        'x_scale': '0',
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
    _default_layout_properties.update(AxesBase._default_layout_properties)
    
    # Overriding AxesBase._valid_props 
    _valid_props = [
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
        'log_base']        
           

    def __init__(self, figure, properties, rect, layout_properties=None):
        AxesBase.__init__(self, figure, rect, layout_properties)
        self.props = {}
        self.major_y_grid_mapping = {'color': self.layout_properties['tick_grid_color'], 
                             'linestyle': self.layout_properties['grid_linestyle'], 
                             'linewidth': self.layout_properties['major_tick_width']
        }
        self.default_grid_mapping = {'color': self.layout_properties['tick_grid_color'], 
                             'linestyle': self.layout_properties['grid_linestyle'], 
                             'linewidth': self.layout_properties['minor_tick_width']
        }
        
        self.set_zorder(self.layout_properties['dummy_ax_zorder'])
        
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
                color=self.layout_properties['tick_grid_color'],          
                length=self.layout_properties['major_tick_lenght'],
                width=self.layout_properties['major_tick_width'], 
                zorder=self.layout_properties['ticks_zorder'])
        self.tick_params(axis='y', which='minor', direction='in',
                color=self.layout_properties['tick_grid_color'],         
                length=self.layout_properties['minor_tick_lenght'],
                width=self.layout_properties['minor_tick_width'], 
                zorder=self.layout_properties['ticks_zorder'])
        
        # PARA NÃO HAVER SOBREPOSIÇÃO DE TICKS E GRIDS SOBRE OS SPINES(EIXO GRÁFICO) 
        self.spines['left'].set_zorder(self.layout_properties['spines_zorder'])
        self.spines['right'].set_zorder(self.layout_properties['spines_zorder'])
        self.spines['top'].set_zorder(self.layout_properties['spines_zorder'])
        self.spines['bottom'].set_zorder(self.layout_properties['spines_zorder'])
        
        self.set_spines_color(self.layout_properties['spines_color'])
        
        self.update(**properties)  
        # self.update(depth_lines=5, x_scale='lin', plotgrid=False)
        # self.update(width=2.0, plotgrid=True, decades= 3, 
        #            depth_lines=0, leftscale=0.1, x_scale='lin', minorgrid=True)        


    def get_properties(self):
        return self.props


    """
    TODO: Alterar update para trabalhar somente com o que mudou
    """
    def update(self, **properties):
        #print '\nDummyAxes.update: ', properties
        self.props = self.check_properties(properties)

        # EIXO X - ESCALA LOGARITMICA
        if self.props.get('x_scale') == 1:
            self.set_xscale('log')
            xlim = (self.props.get('leftscale'), 
                self.props.get('leftscale')*(self.props.get('log_base')**self.props.get('decades')))
            self.set_xlim(xlim)
            if self.props.get('plotgrid') == True:
                self.grid(True, axis='x', which='major', **self.default_grid_mapping)
                if self.props.get('minorgrid') == True:
                    self.grid(True, axis='x', which='minor', **self.default_grid_mapping)
                
        
        # EIXO X - ESCALA LINEAR        
        if self.props.get('x_scale') == 0:
            self.set_xscale('linear')
            self.set_xlim(self.layout_properties['xlim'])
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
            #print '\nPLOTGRID: TRUE'
            # DEPTH LINES - GRIDS OU TICKS DE REFERENCIA PARA CURVA DATUM (DEPTH)
            # DEPTH LINES == FULL
            
            '''
                """set the position of the spine
        
                Spine position is specified by a 2 tuple of (position type,
                amount). The position types are:
        
                * 'outward' : place the spine out from the data area by the
                  specified number of points. (Negative values specify placing the
                  spine inward.)
        
                * 'axes' : place the spine at the specified Axes coordinate (from
                  0.0-1.0).
        
                * 'data' : place the spine at the specified data coordinate.
        
                Additionally, shorthand notations define a special positions:
        
                * 'center' -> ('axes',0.5)
                * 'zero' -> ('data', 0.0)
        
                """
                if position in ('center', 'zero'):
                    # special positions
                    pass
                else:
                    assert len(position) == 2, "position should be 'center' or 2-tuple"
                    assert position[0] in ['outward', 'axes', 'data']
            '''            
            
            if self.props.get('depth_lines') == 0:
                self.ticks = False
                self.grid(True, axis='y', which='major', **self.major_y_grid_mapping)
                self.grid(True, axis='y', which='minor', **self.default_grid_mapping)
            # DEPTH LINES == LEFT 
            elif self.props.get('depth_lines') == 1:
                self.ticks = True
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.tick_params(left=True, right=False, which='both', axis='y')
                self.grid(False, axis='y', which='both')
            # DEPTH LINES == RIGHT
            elif self.props.get('depth_lines') == 2:
                self.ticks = True
                self.spines['left'].set_position(('axes', 0.0))
                self.spines['right'].set_position(('axes', 1.0))
                self.tick_params(left=False, right=True, which='both', axis='y')
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
                self.tick_params(left=True, right=True, which='both', axis='y')
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
            #print '\nPLOTGRID: FALSE'
            self.grid(False, axis='both', which='both')
            #self.grid(True, axis='x', which='minor')
            #self.tick_params(left=False, right=False, which='both', axis='y')
            self.hide_y_ticks()
        #self.draw()    
        #print '\n FIM DummyAxes.update'


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
        #print 'check_properties: ', props
        props = self._get_valid_props(props)
        #print 'check_properties: ', props
        if not props.get('ylim'): 
            if not self.props.get('ylim'):
                props['ylim'] = self.layout_properties['ylim']
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


        if not props.get('log_base'):
            if not self.props.get('log_base'):
                props['log_base'] = self.layout_properties['log_base']
            else:
                props['log_base'] = self.props['log_base']
        elif not isinstance(props.get('log_base'), int): 
            raise ValueError('log_base deve ser inteiro.') 
        elif props.get('log_base') < 0:
            raise ValueError('log_base deve ser maior que 0.')    

        if not props.get('y_major_grid_lines'):
            if not self.props.get('y_major_grid_lines'):
                props['y_major_grid_lines'] = self.layout_properties['y_major_grid_lines']
            else:    
                props['y_major_grid_lines'] = self.props['y_major_grid_lines']
        elif not isinstance(props.get('y_major_grid_lines'), float):
            raise ValueError('y_major_grid_lines deve ser float.') 
        elif props.get('y_major_grid_lines') <= 0:
            raise ValueError('y_major_grid_lines deve ser maior que 0.')        

        if not props.get('y_minor_grid_lines'):
            if not self.props.get('y_minor_grid_lines'):
                props['y_minor_grid_lines'] = self.layout_properties['y_minor_grid_lines']
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
        '''        
        elif isinstance(props.get('plotgrid'), str):
            if props.get('plotgrid').lower() == 'yes':
                props['plotgrid'] = True
            elif props.get('plotgrid').lower() == 'no':    
                props['plotgrid'] = False
            else: 
                raise ValueError("""O valor de plotgrid deve ser True, 
                                 \'Yes\', False ou \'No\'.""")    
        '''                         
        if not isinstance(props.get('plotgrid'), (bool)):  
            raise ValueError('O valor de plotgrid deve ser True ou False.')
        
        
        if props.get('x_scale') is None:
            if self.props.get('x_scale') is None:
                props['x_scale'] = self.layout_properties['x_scale']
            else:
                props['x_scale'] = self.props['x_scale']
        #print 'props.get(\'x_scale\'): ', props.get('x_scale')   
        if not isinstance(props.get('x_scale'), int):
             raise ValueError('O valor de x_scals deve ser inteiro.')
        if not props.get('x_scale') in [0, 1, 2, 3]:
            #['lin', 'log', 'yes', 'no', 'sin', 'cos']:
            raise ValueError('A escala deve ser linear ou logaritmica(seno ou cosseno). (x_scale in [0, 1, 2, 3])')
                
        if props.get('x_scale') == 1:
            if not props.get('decades'):
                if not self.props.get('decades'):
                    raise ValueError('decades deve ser informado quando a escala é logaritmica.')
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
                        #print (props.get('leftscale'))
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
        '''        
        elif isinstance(props.get('minorgrid'), str):
            if props.get('minorgrid').lower() == 'yes':
                props['minorgrid'] = True
            elif props.get('minorgrid').lower() == 'no':    
                props['minorgrid'] = False
            else: 
                raise ValueError("""O valor de minorgrid deve ser True, 
                                 \'Yes\', False ou \'No\'.""")    
        '''                         
        if not isinstance(props.get('minorgrid'), (bool)):  
            raise ValueError('O valor de minorgrid deve ser True ou False.')  
            
            
        if props.get('scale_lines') is None:
            if self.props.get('scale_lines') is None: 
                props['scale_lines'] = self.layout_properties.get('scale_lines') 
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
                props['depth_lines'] = self.layout_properties['depth_lines']      
            else:
                props['depth_lines'] = self.props['depth_lines']
        else:
            if not isinstance(props.get('depth_lines'), int): 
                raise ValueError('depth_lines deve ser inteiro.')
            elif props.get('depth_lines') < 0 or props.get('depth_lines') > 5:
                raise ValueError('depth_lines deve ser entre 0 e 5.')    
                
        '''
            if isinstance(props.get('depth_lines'), str):
                if str(props.get('depth_lines')).lower() == 'yes':
                    props['depth_lines'] = 0
                elif int(props.get('depth_lines')) in [0, 1, 2, 3, 4, 5]: 
                    props['depth_lines'] = int(props.get('depth_lines'))
                else:    
                    raise ValueError('depth_lines deve ser inteiro.') 
            else:    
                raise ValueError('depth_lines deve ser inteiro.')
        elif props.get('depth_lines') < 0 or props.get('depth_lines') > 5:
            raise ValueError('depth_lines deve ser entre 0 e 5.')
        '''    
        return props
        

   
# This Class refers to track title (or track label), not curves titles     
class TrackTitleAxes(AxesBase):
    # Choose not to use properties because it is so simple
    def __init__(self, figure, rect, title_text='', title_bgcolor='white'):
        AxesBase.__init__(self, figure, rect)
        self.title_text = title_text
        self.title_bgcolor = title_bgcolor
        self.xaxis.set_major_locator(NullLocator())
        self.yaxis.set_major_locator(NullLocator())                
        self.patch = self.add_patch(
            Patches.Rectangle(
                (0.0, 0.0), 1.0, 1.0, 
                facecolor = self.title_bgcolor,
                fill = True, 
                linewidth = 0
            )
        )
        self.label = self.text(0.5, 0.5, self.title_text, 
                ha='center', va='center', fontsize='medium')
     

    def set_text(self, title_text):
        self.title_text = title_text
        self.label.set_text(self.title_text)
        
    def get_text(self):
        return self.title_text

    def set_color(self, color):
        self.title_bgcolor = color
        self.patch.set_facecolor(self.title_bgcolor)        

    def get_color(self):
        return self.patch.get_facecolor()

    def update_data(self, *args, **kwargs):
        if args[0]:
            self.set_text(args[0])
        elif kwargs['text']:
            self.set_text(kwargs['text'])
        if args[1]:
            self.set_color(color=args[1])
        elif kwargs['color']:
            self.set_color(kwargs['color'])    




# This Class refers to log curves titles, including title, xmax, xmin, 
# and line_properties as colors and line style            
class CurveTitleAxes(AxesBase):
    # Overriding AxesBase._default_layout_properties
    _default_layout_properties = {
        'bgcolor': 'white',
        'horizontal_margin': 0.025,
        'vertical_margin': 0.25,
        'text_size': 'medium',
        'number_size': 'small',
        'line_size': 0.5
    }
    
    # Overriding AxesBase._valid_props 
    _valid_props = [
        'aa',
        'antialiased',
        'c',
        'color',
        'dash_capstyle',
        'dash_joinstyle',
        'drawstyle',
        'fillstyle',
        'linestyle',
        'linewidth',
        'ls',
        'lw',
        'marker',
        'markeredgecolor',
        'markeredgewidth',
        'markerfacecolor',
        'markerfacecoloralt',
        'markersize',
        'markevery',
        'mec',
        'mew',
        'mfc',
        'mfcalt',
        'ms',
        'solid_capstyle',
        'solid_joinstyle'
    ]

    def __init__(self, figure, rect, layout_properties=None):
        AxesBase.__init__(self, figure, rect, None)
        self.xaxis.set_major_locator(NullLocator())
        self.yaxis.set_major_locator(NullLocator())
        
        t = 1.0 - self.layout_properties['vertical_margin']
        b = self.layout_properties['vertical_margin']
        l = self.layout_properties['horizontal_margin']
        r = 1.0 - self.layout_properties['horizontal_margin']
        ts = self.layout_properties['text_size']
        ns = self.layout_properties['number_size']
        ls = self.layout_properties['line_size']

        self.label = self.text(0.5, t, '', ha='center', va='top', fontsize=ts)
        self.xmin = self.text(l, b, '', ha='left', va='center', fontsize=ns)
        self.xmax = self.text(r, b, '', ha='right', va='center', fontsize=ns)
        self.line = matplotlib.lines.Line2D([0.5 - ls/2, 0.5 + ls/2], [b, b])
        self.add_line(self.line)

    def set_xlim(self, xlim):
        xmin, xmax = xlim
        self.xmin.set_text(str(xmin))
        self.xmax.set_text(str(xmax))

    def get_xlim(self):
        xmin = self.xmin.get_text()
        xmax = self.xmax.get_text()
        return xmin, xmax

    def set_text(self, text):
        self.label.set_text(text)

    def get_text(self):
        return self.label.get_text()

    def set_color(self, color):
        self.set_properties(color=color)

    def get_color(self):
        return self.line.get_color() 

    def set_properties(self, **props):
        self.line.update(self._get_valid_props(props))

    def get_all_properties(self):
        return self._get_valid_props(self.line.properties())
        
    def update_data(self, *args, **kwargs):
        if args[0]:
            self.set_text(args[0])
        elif kwargs['title_text']:
            self.set_text(kwargs['title_text'])
        if args[1]:
            self.set_xlim(args[1])
        elif kwargs['xlim']:
            self.set_xlim(kwargs['xlim'])    
        if args[2]:
            self.set_properties(color=args[2])
        elif kwargs['color']:
            self.set_properties(kwargs['color'])       
        



# CLASSE BASE PARA CLASSES QUE HERDAM DE FIGURECANVAS
# NESTA CLASSE SÃO DEFINIDOS OS PARAMETROS PARA RESIZE E UPDATE DO FIGURECANVAS

class _BaseFigureCanvas(FigureCanvas, Base):
    _default_layout_properties = {
        'width': 0.01,
        'dpi': 80,
        'figure_facecolor': 'white'
    }
      
    _valid_props = []
        
    def __init__(self, parent, size, layout_properties=None): 
        #print '_BaseFigureCanvas.__init__'
        Base.__init__(self, layout_properties)
        self.figure = None
        self.height_inches_used = 0.0
        self.width_inches = self.layout_properties['width']
        
        #size = ???
        
        # Calcula a altura em polegadas do Figure    
       # self._calc_figure_height()
                            
        self.figure = Figure(facecolor=self.layout_properties['figure_facecolor'], 
                             figsize=(self.width_inches, self.height_inches_used)) 
        FigureCanvas.__init__(self, parent, -1, self.figure)
        #self._real_parent = None
        #print '\n\nsize: {}\n\n'.format(size)
        self.SetSize(size)
        self._draw_figure()
        self.mpl_connect('resize_event', self._on_resize)
        
       
    def _draw_figure(self):
        raise NotImplementedError("Please Implement this method")
              
    '''          
    def set_real_parent(self, real_parent):              
        self._real_parent = real_parent
        
    def get_real_parent(self):
        return self._real_parent
    '''
    
    def _on_resize(self, event):
       #print '_BaseFigureCanvas._on_resize()'
        self._draw_figure()
        #w, h = self.figure.get_size_inches()
        #self.figure.set_size_inches((w, self.height_inches_used), forward=True)
        #self.SetSize((self._inches_to_pixels(w), self._inches_to_pixels(h)))
        #self.draw()

    def _inches_to_pixels(self, inches):
        if self.figure is not None:
            return  inches * self.figure.dpi
        else:
            return inches * self.layout_properties['dpi']

    def _pixels_to_inches(self, pixels):
        if self.figure is not None:
            return  float(pixels) / self.figure.dpi
        else:
            return  float(pixels) / self.layout_properties['dpi']

    def _pixels_to_ratio(self, pixels):
        width, height = self.figure.get_size_inches() * self.figure.dpi
        ### TODO: Armengue - verificar
        if height == 0:
            height = 1
        ###    
        if width == 0:
            raise Exception('Divisao por zero. pixels={} width={} height={}'.format(pixels, width, height))
        return float(pixels)/width, float(pixels)/height
        
    def _ratio_to_pixels(self, ratio):
        width, height = self.figure.get_size_inches() * self.figure.dpi
        return ratio*width, ratio*height
        
        
    def get_width_inches(self):
        width, height = self.GetSize()
        return self._pixels_to_inches(width)
        
    # def set_width_inches(self, width_inches):
    #    width, height = self.GetSize()
    #    return self._pixels_to_inches(width)
        
        
        
        



###############################################################################  
###
###############################################################################


      
class TrackFigureCanvas(_BaseFigureCanvas):
    _default_layout_properties = {
        'curves_zorder': 1000
    }
    _default_layout_properties.update(_BaseFigureCanvas._default_layout_properties)

    _valid_props = [
        'aa',
        'antialiased',
        'c',
        'color',
        'dash_capstyle',
        'dash_joinstyle',
        'drawstyle',
        'fillstyle',
        'linestyle',
        'linewidth',
        'ls',
        'lw',
        'marker',
        'markeredgecolor',
        'markeredgewidth',
        'markerfacecolor',
        'markerfacecoloralt',
        'markersize',
        'markevery',
        'mec',
        'mew',
        'mfc',
        'mfcalt',
        'ms',
        'solid_capstyle',
        'solid_joinstyle'
    ]
    
        
    def __init__(self, parent, size, properties, callback=None, layout_properties=None):
        #print '\nTrackFigureCanvas.__init__ FUNCIONA'
        self.dummy_ax = None
        self.props = properties
        _BaseFigureCanvas.__init__(self, parent, size, layout_properties)
        self.axes = []
        self.mpl_connect('motion_notify_event', self.on_move)
        
        self._callback =  callback
        
        # Zoom
        self.zoom_rect = Patches.Rectangle((0, 0), 0, 0, ec="CornflowerBlue", 
                                           fill=False, zorder=10)
        self.dummy_ax.add_patch(self.zoom_rect)                                   
        self.pressed = False
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.mpl_connect('button_press_event', self.on_press)
        self.mpl_connect('motion_notify_event', self._on_drag)
        self.mpl_connect('button_release_event', self.on_release)
        #

    ### Zoom functions
        
    def _on_drag(self, event):
        if self.pressed:
            if event.xdata and event.ydata:
                self.x1, self.y1 = self.get_transformed_values()[0]
                #print '\ndrag', [self.x0, self.x1], [self.y0, self.y1]
                self.zoom_rect.set_width(self.x1 - self.x0)
                self.zoom_rect.set_height(self.y1 - self.y0)
                self.zoom_rect.set_xy((self.x0, self.y0))
                self.draw()
            
    def on_press(self, event):         
        if event.button == 2:
            if event.xdata and event.ydata and self._zoom_callback:
                self.x0, self.y0 = self.get_transformed_values()[0]
                #print '\npress', self.x0, self.y0
                #print self.get_transformed_values()[0]
                self.pressed = True

    def on_release(self, event):
        if self.pressed:
            #print '\nrelease', self.y0, self.y1
            #print [(self.x0, self.y0),(self.x1, self.y1)]
            self.zoom_rect.set_width(0)
            self.zoom_rect.set_height(0)
            self.draw()
            self.pressed = False
            self._zoom_callback(np.nanmin([self.y0, self.y1]), 
                                np.nanmax([self.y0, self.y1]))
        
    def set_zoom_callback(self, zoom_callback_function):
        self._zoom_callback = zoom_callback_function
    
    ###    
        
    def set_callback(self, callback_function):
        self._callback = callback_function        
        
        
    def _create_dummy_axes(self, properties):
        #print 'TrackFigureCanvas._create_dummy_axes'
        #print 'PROPS: ', properties
        self.rect = [0.0, 0.0, 1.0, 1.0]
        self.dummy_ax = DummyAxes(self.figure, properties, self.rect)
        self.figure.add_axes(self.dummy_ax)
        
        
    def update_properties(self, **kwargs):
        #print '\nTrackFigureCanvas.update_properties'
        if self.dummy_ax is not None:
            self.dummy_ax.update(**kwargs)
            self.draw()            
            #self.blit()        
       
       
    def get_properties(self):
        return self.dummy_ax.get_properties()   
        
        
    def get_track_properties(self):
        return self.props
        
            
    def set_dummy_spines_visibility(self, boolean):
        if self.dummy_ax is not None:
            self.dummy_ax.set_spines_visibility(boolean)
            
       
    # Overrides super class method
    def _draw_figure(self):
        if not self.dummy_ax:
            self._create_dummy_axes(self.props)
        #else:    
        #    self.Refresh()
        #self.draw()
        #self.blit()


    def get_transformed_values(self):
        if self.pixelsdata is None:
            return None, None
        dummydata = self.dummy_ax.transData.inverted().\
            transform_point((self.pixelsdata[0], self.pixelsdata[1]))       
        values = []        
        for ax in self.axes:
            valuedata = ax.transData.inverted().\
                transform_point((self.pixelsdata[0], self.pixelsdata[1]))         
            values.append(valuedata.tolist()[0])
        return dummydata.tolist(), values
        
        
    def on_move(self, event):
        if event.inaxes is None:
            self.pixelsdata = None
            return
        else: 
            self.pixelsdata = event.inaxes.transData.transform_point((event.xdata, event.ydata))
        dummydata, values = self.get_transformed_values() 
        if self._callback:
            self._callback(dummydata, values)
        return        
    
    
    def set_ylim(self, ylim):
        min_, max_ = ylim
        if min_ == max_:
            return
        if max_ < min_:
            ylim = (max_, min_)
        self.dummy_ax.update(ylim=ylim)
        self.draw()




      
    def append_curve(self, x_data, y_data, **kwargs):
        ax = self.figure.add_axes(self.dummy_ax.get_position(True),
                          sharey=self.dummy_ax, 
                          frameon=False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        self.axes.append(ax)
        self.update_curve(len(self.axes)-1, x_data, y_data, **kwargs)
        


    def update_curve(self, curve_number, x_data, y_data, **kwargs):
        ax = self.axes[curve_number]
            
        if kwargs.get('left_scale') is not None and kwargs.get('right_scale') is not None:
            ax.set_xlim((kwargs.get('left_scale'), kwargs.get('right_scale')))            
        
        if kwargs.get('x_scale') is not None:
            if kwargs.get('x_scale') == 0:    
                ax.set_xscale('linear')
            if kwargs.get('x_scale') == 1:    
                ax.set_xscale('log')    
                
        if kwargs.get('point_plotting'):
            
            if kwargs.get('point_plotting') == 'Index':
                if len(ax.texts) == 0:
                    step = 500
                    locs = range(0, int(np.nanmax(y_data)), step)
                    for loc in locs:
                        ax.text(0.5, loc, "%g" % loc, ha='center', va='center', 
                            fontsize=10)#, bbox={'facecolor':'white', 'pad':1})
            
            elif kwargs.get('point_plotting') == 'Partition':
                if len(ax.images) == 0:
                    xmin, xmax = ax.get_xlim()
                    ymin = np.nanmin(y_data)
                    ymax = np.nanmax(y_data)
                    extent = (xmin, xmax, ymax, ymin) #scalars (left, right, bottom, top)
                    
                    for wxcolor, data in x_data.values():
                        mplcolor = [float(c)/255.0 for c in wxcolor]
                        color = colorConverter.to_rgba_array(mplcolor[:3])
                        im = np.tile(color, (data.shape[0], 1)).reshape(-1, 1, 4)
                        im[:, 0, -1] = data
                        ax.imshow(im, aspect='auto', extent=extent, interpolation='none')
            
            elif kwargs.get('point_plotting').lower() == 'solid':
                if len(ax.lines) > 0: # never should be greater than 1 
                    if kwargs: 
                        ax.lines[0].set_color(kwargs.get('color'))
                        ax.lines[0].set_linewidth(kwargs.get('thickness'))
                        ax.lines[0].set_zorder(10000)
                    ax.lines[0].set_data(x_data, y_data)            
                else:                        
                    line = matplotlib.lines.Line2D(x_data, y_data,
                            linewidth=kwargs.get('thickness'), 
                            color=kwargs.get('color')
                    )
                    ax.add_line(line)          
        self.draw()        
            
            
               
    def remove_curve(self, curve_number):       
        ax = self.axes.pop(curve_number)
        self.figure.delaxes(ax)
        self.draw()
        
        
        

        
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
    
    def __init__(self, parent):
        height = float(LABEL_TITLE_HEIGHT)/DPI
        fig = Figure(figsize=(1, height), dpi=DPI)
        super(PlotLabelTitle, self).__init__(parent, -1, fig)
        axes = Axes(fig, [0.0, 0.0 , 1.0, 1.0], axisbg='white')
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.spines['left'].set_visible(False)
        axes.spines['bottom'].set_visible(False)
        axes.xaxis.set_major_locator(NullLocator())
        axes.yaxis.set_major_locator(NullLocator())                
        self._patch = axes.add_patch(
            Patches.Rectangle(
                (0.0, 0.0), 1.0, 1.0, 
                facecolor = LOG_LABEL_TITLE_BGCOLOR,
                fill = True, 
                linewidth = 0
            )
        )
        self._label = axes.text(0.5, 0.5, '', 
                ha='center', va='center', fontsize=10)        
        fig.add_axes(axes)
        self.parent = parent    
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
           
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click for self.parent. 
        """
        wx.PostEvent(self.parent, event)
           
    def update(self, **kwargs):
        """
        Update PlotLabelTitle properties.
        
        Parameters
        ----------
        text : str
            Title string.
        bgcolor : mpl color spec
            Tiles's background color. 
        """
        if kwargs:
            if kwargs.get('text'):
                self._label.set_text(kwargs.get('text'))
            if kwargs.get('bgcolor'):
                self._patch.set_facecolor(kwargs.get('bgcolor'))  

    def get_properties(self):
        """
        Get PlotLabelTitle properties.
        
        Returns
        -------
        properties : dict
            The PlotLabelTitle properties with 'text' and 'bgcolor' keys.
        """
        properties = {}
        properties['text'] = self._label.get_text()
        properties['bgcolor'] = self._patch.get_facecolor()
        return properties
       
 
class PlotLabelTrack(FigureCanvas):
    """
    Class for PlotLabel's track.
    
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
    
    def __init__(self, parent, **kwargs):
        height = float(LABEL_TITLE_HEIGHT)/DPI
        fig = Figure(figsize=(1, height), dpi=DPI)
        super(PlotLabelTrack, self).__init__(parent, -1, fig)                
        self._axes = Axes(fig, [0.0, 0.0 , 1.0, 1.0], axisbg='white')
        self._axes.spines['right'].set_visible(False)
        self._axes.spines['top'].set_visible(False)
        self._axes.spines['left'].set_visible(False)
        self._axes.spines['bottom'].set_visible(False)
        self._axes.xaxis.set_major_locator(NullLocator())
        self._axes.yaxis.set_major_locator(NullLocator())
        fig.add_axes(self._axes)
        if kwargs:
            self.update(**kwargs)
        self.parent = parent    
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click to self.parent. 
        """
        wx.PostEvent(self.parent, event)

    def update(self, **kwargs):
        """
        Updates track information displayed.      
             
        Parameters
        ----------            
        'name': str
            Track name
        'tracktype': str
            Track type. Suported types: ['index', 'solid', 'partition']
        'unit': str
            Track values unit. Used when tracktype is index or solid.
        'xmin': str
            Track xdata min. Used when tracktype is solid.         
        'xmax': str
            Track xdata max. Used when tracktype is solid.                                        
        'linecolor': mpl color spec
            Color for track line. Used when tracktype is solid.   
        'linewidth': int
            Width for track line. Used when tracktype is solid. 
                  
        Examples
        --------
        >>> plt = PlotLabelTrack(None)
        >>> plt.update(name='DEPTH', tracktype='index', units='m')
        >>> plt.update(name='RHOZ', tracktype='solid', units='g/cm3', 
                       xmin='1.95', xmax='2.95', linecolor='red', linewidth=1)
        >>> plt.update(name='LITO', tracktype='partition')
        
        """
        self._axes.lines = []
        self._axes.texts = []
        if kwargs.get('tracktype').lower() == 'solid':
            if kwargs.get('unit') is not None:
                str_label = kwargs.get('name') + ' (' + kwargs.get('unit') + ')'
                self._axes.text(0.5, 0.55, str_label, ha='center', fontsize=10)
            else:
                self._axes.text(0.5, 0.55, kwargs.get('name'), ha='center', fontsize=10)
            ypos = 0.25
            self._axes.text(0.025, ypos, kwargs.get('xmin'), ha='left', va='center', fontsize=10)
            self._axes.text(0.975, ypos, kwargs.get('xmax'), ha='right', va='center', fontsize=10)
            line = matplotlib.lines.Line2D([0.25, 0.75], [ypos, ypos])
            line.set_linewidth(kwargs.get('linewidth'))
            line.set_color(kwargs.get('linecolor'))
            self._axes.add_line(line)
        elif kwargs.get('tracktype').lower() == 'index':
            self._axes.text(0.5, 0.6, kwargs.get('name'), ha='center', fontsize=10)
            if kwargs.get('unit') is not None:
                str_unit = '(' + kwargs.get('unit') + ')'
                self._axes.text(0.5, 0.3, str_unit, ha='center', va='center', fontsize=10)
        elif kwargs.get('tracktype').lower() == 'partition':
            self._axes.text(0.5, 0.6, kwargs.get('name'), ha='center', fontsize=10)
            self._axes.text(0.5, 0.3, '(Partition)', ha='center', va='center', fontsize=10)
        else:
            raise Exception()
        
        
class PlotLabel(wx.Panel):
    """
    PlotLabel is the PlotTrack identifier.
    
    It is responsible for drawing every track label and optionally can draw a 
    title (PlotLabelTitle).   

    Parameters
    ----------
    parent : wx.Window
        This compoent parent.

    Attributes
    ----------
    _title: PlotLabelTitle
        Responsible for title drawing.
    _tracks: list
        A list container for LogLabelTracks.
        
    """
    
    def __init__(self, parent):
        super(PlotLabel, self).__init__(parent)
        self._title = None
        self._tracks = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))     

    def create_title(self):
        """
        Creates title's container.
        
        Notes
        -----        
        Despite it creates the container where title properties will be 
        placed. It is necessary to call update_title to pass these
        properties.
            
        """
        self._title = PlotLabelTitle(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
            
    def update_title(self, **kwargs):
        """
        Updates title.

        Parameters
        ----------
        text : str
            Title string.
        bgcolor : mpl color spec
            Tiles's background color.   
            
        """
        if self._title is None:
            self.create_title()
        self._title.update(**kwargs) 
        self.Layout() 
        
    def get_title_properties(self):
        """
        Get title properties.
        
        Returns
        -------
        properties : dict
            The title properties with 'text' and 'bgcolor' keys.
        """
        if self._title:
            return self._title.get_properties()
        return None    
        
    def remove_title(self):
        """
        Removes (just) the title.
        """
        if self._title is not None:
            self.GetSizer().Remove(self._title)
            t = self._title
            self._title = None
            t.Destroy()
            self.Layout()
        
    def append_track(self, **kwargs):
        self.insert_track(len(self._tracks), **kwargs)
        
    def insert_track(self, pos, **kwargs):
        """
        Insert a new track at given pos with properties informed.
        """
        print '\nPlotLabel.insert_track', pos 
        print kwargs
        llt = PlotLabelTrack(self, **kwargs)    
        self._tracks.insert(pos, llt)
        self.GetSizer().Add(llt, 0,  wx.EXPAND)
        self.Layout()
        
    def update_track(self, pos, **kwargs):
        """
        Updates track information displayed.      
             
        Parameters
        ----------            
        'name': str
            Track name
        'tracktype': str
            Track type. Suported types: ['index', 'solid', 'partition']
        'unit': str
            Track values unit. Used when tracktype is index or solid.
        'xmin': str
            Track xdata min. Used when tracktype is solid.         
        'xmax': str
            Track xdata max. Used when tracktype is solid.                                        
        'linecolor': mpl color spec
            Color for track line. Used when tracktype is solid.   
        'linewidth': int
            Width for track line. Used when tracktype is solid. 
                  
        Examples
        --------
        >>> pl.update_track(name='DEPTH', tracktype='index', units='m')
        >>> pl.update_track(name='RHOZ', tracktype='solid', units='g/cm3', 
                       xmin='1.95', xmax='2.95', linecolor='red', linewidth=1)
        >>> pl.update_track(name='LITO', tracktype='partition')
        
        """
        print '\nPlotLabel.update_track',pos
        print kwargs
        self._tracks[pos].update(**kwargs)
        self.Layout() 
        
    def remove_track(self, pos):
        """
        Removes the track is a given position. 
        """
        print '\nPlotLabel.remove_track', pos
        llt = self._tracks.pop(pos)
        self.GetSizer().Remove(llt)
        llt.Destroy()
        self.Layout()        

 
    