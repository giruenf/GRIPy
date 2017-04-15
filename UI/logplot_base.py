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


# TODO: Review it!
# Keeping MPL version 1 parameters
if matplotlib.__version__.startswith('2.'):
    matplotlib.rcParams['mathtext.fontset'] = 'cm'
    matplotlib.rcParams['mathtext.rm'] = 'serif'
    #
    matplotlib.rcParams['figure.figsize'] = [8.0, 6.0]
    matplotlib.rcParams['figure.dpi'] = 80
    matplotlib.rcParams['savefig.dpi'] = 100
    #    
    matplotlib.rcParams['font.size'] = 12
    matplotlib.rcParams['legend.fontsize'] = 'large'
    matplotlib.rcParams['figure.titlesize'] = 'medium'



# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40
LOG_LABEL_TITLE_BGCOLOR = 'white'
FACTOR = 1.57


VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']





def prepare_float_value(value):
    value = str(value)
    if len(value.split('.')) > 1:
        v0 = value.split('.')[0]
        v0 = str(int(v0))
        v1 = value.split('.')[1].rstrip('0')
        if len(v1) == 0:
            return v0 + '.'
        else:
            if len(v1) > 2: # Trimming decimals to 2 caracters
                v1 = v1[0:2]
            return v0 + '.' + v1
    return value        



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
    _default_layout_properties = {'facecolor': 'white'}

    def __init__(self, figure, rect, layout_properties=None):
        Base.__init__(self, layout_properties)
        self.rect = rect        
        if matplotlib.__version__.startswith('2.'):
            Axes.__init__(self, figure, self.rect, label=self._get_name(), 
                    facecolor=self.layout_properties['facecolor'] # MPL 2.0
            )
        else:
            Axes.__init__(self, figure, self.rect, label=self._get_name(), 
                    axisbg=self.layout_properties['facecolor'] # MPL 1.X
            )
                                    
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
        
        #self.invert_yaxis()
        
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
        
        if properties:
            self.update(**properties)
        else:
            self.update()

    def get_properties(self):
        return self.props


    """
    TODO: Alterar update para trabalhar somente com o que mudou
    """
    def update(self, **properties):
        #print '\nupdate: ', properties
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
                elif self.props.get('minorgrid') == False:
                    self.grid(False, axis='x', which='minor', **self.default_grid_mapping)
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
        self.set_ylim(self.props.get('ylim'), auto=None)
        if self.props.get('x_scale') == 2:
            raise Exception('There no support yet to Sin scale.')
        if self.props.get('x_scale') == 3:    
            raise Exception('There no support yet to Cosin scale.')
            
        if self.props.get('plotgrid'):
            ##print '\nPLOTGRID: TRUE'
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
            ##print '\nPLOTGRID: FALSE'
            self.grid(False, axis='both', which='both')
            #self.grid(True, axis='x', which='minor')
            #self.tick_params(left=False, right=False, which='both', axis='y')
            self.hide_y_ticks()
        #self.draw()    
        ##print '\n FIM DummyAxes.update'


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
        ##print 'check_properties: ', props
        props = self._get_valid_props(props)
        ##print 'check_properties: ', props
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

        ##print '\n', props.get('ylim')
        
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
        
 
        if not isinstance(props.get('x_scale'), int):
             raise ValueError('O valor de x_scale deve ser inteiro.')
        if not props.get('x_scale') in [0, 1, 2, 3]:
            #['lin', 'log', 'yes', 'no', 'sin', 'cos']:
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
                        ##print (props.get('leftscale'))
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
        #self.Show(False)
        #self._real_parent = None
        ##print '\n\nsize: {}\n\n'.format(size)
        self.SetSize(size)
        self._draw_figure()
        self.mpl_connect('resize_event', self._on_resize)
       
    def _draw_figure(self):
        raise NotImplementedError("Please Implement this method")
              
    
    def _on_resize(self, event):
        self._draw_figure()


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
        
        



###############################################################################  
###
###############################################################################


      
class TrackFigureCanvas(_BaseFigureCanvas):

        
    def __init__(self, wx_parent, view_object, size, **properties):
        self.dummy_ax = None

        self.properties = properties
        _BaseFigureCanvas.__init__(self, wx_parent, size)
        
        self._view = view_object
        self.axes = []
    
        
        #self.parent = parent
        
        # Zoom
        self.zoom_rect = Patches.Rectangle((0, 0), 0, 0, ec="CornflowerBlue", 
                                           fill=False, zorder=10)
        self.dummy_ax.add_patch(self.zoom_rect)                                   
        self.pressed = False
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
#        self.mpl_connect('motion_notify_event', self.on_move)        
        #self._callback =  properties.get('callback')
        self.mpl_connect('button_press_event', self.on_press)
     #   self.mpl_connect('motion_notify_event', self._on_drag)
     #   self.mpl_connect('button_release_event', self.on_release)
        #
     #   self.Bind(wx.EVT_SIZE, self._on_size)
        
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        
        self._selected = False
        self.selectedCanvas = []
        self.index_axes = None
        
        
    def is_selected(self):
        return self._selected
        
    def _on_middle_down(self, event):
        self._view.set_selected(self, not self._selected)   
        self._do_select()
        event.Skip()
        
    def _do_select(self):
        self._selected = not self._selected
        self.GetParent()._draw_window_selection(self)
    
    
    ### Zoom functions
        
    def _on_drag(self, event):
        if self.pressed:
            if event.xdata and event.ydata:
                x_px, y_px = event.inaxes.transData.transform_point((event.xdata, event.ydata))
                self.x1, self.y1 = self.get_transformed_values(x_px, y_px)[0]
                ##print '\ndrag', [self.x0, self.x1], [self.y0, self.y1]
                self.zoom_rect.set_width(self.x1 - self.x0)
                self.zoom_rect.set_height(self.y1 - self.y0)
                self.zoom_rect.set_xy((self.x0, self.y0))
                self.draw()

                
                
    def on_move(self, event):
        #print
        #print 'DEPTH tfc:', np.round(event.ydata, decimals=4) 
        for idx, ax in enumerate(self.axes):
            if len(ax.lines) > 0:
                line = ax.lines[0]
                contains, result = line.contains(event)
                #if contains: 
                    #print result
            if len(ax.images) > 0:
                image = ax.images[0]
                value = image.get_cursor_data(event)
                if value is not None:
                    value = np.round(value, decimals=4)
                #print value
        # Line.contains(self, mouseevent):
            
            
    def get_transformed_values(self, point_px):
        if point_px is None:
            return None, None
        dummydata = self.dummy_ax.transData.inverted().transform_point(point_px)       
        values = []        
        for ax in self.axes:
            valuedata = ax.transData.inverted().transform_point(point_px)         
            values.append(valuedata.tolist()[0])
        return dummydata.tolist(), values

            
        """
        Test whether the mouse event occurred on the line.  The pick
        radius determines the precision of the location test (usually
        within five points of the value).  Use
        :meth:`~matplotlib.lines.Line2D.get_pickradius` or
        :meth:`~matplotlib.lines.Line2D.set_pickradius` to view or
        modify it.

        Returns *True* if any values are within the radius along with
        ``{'ind': pointlist}``, where *pointlist* is the set of points
        within the radius.

        TODO: sort returned indices by distance
        """
        
        
        '''
        if event.inaxes is None:
            #self.pixelsdata = None
            return
        pixelsdata = event.inaxes.transData.transform_point((event.xdata, event.ydata))
        ##print 'pixelsdata:', pixelsdata
        dummydata, values = self.get_transformed_values(pixelsdata) 
        #print np.round(dummydata[1], decimals=2), values
        #if self._callback:
        #    self._callback(dummydata, values)
        #return    
        '''
            
    def on_press(self, event):
        self._view.process_event(event)
        #event.Skip()
        '''
        if event.button == 1:
            #print 'botao 1:', self.parent
        elif event.button == 2:
            #print 'botao 2'
        elif event.button == 3:
            #print 'botao 3'
        '''    
        '''
        if event.xdata and event.ydata and self._zoom_callback:
            x_px, y_px = event.inaxes.transData.transform_point((event.xdata, event.ydata))
            self.x0, self.y0 = self.get_transformed_values(x_px, y_px)[0]
            ##print '\npress', self.x0, self.y0
            ##print self.get_transformed_values()[0]
            self.pressed = True
            '''    

    def on_release(self, event):
        self._view.process_event(event)
        '''
        if self.pressed:
            ##print '\nrelease', self.y0, self.y1
            ##print [(self.x0, self.y0),(self.x1, self.y1)]
            self.zoom_rect.set_width(0)
            self.zoom_rect.set_height(0)
            self.draw()
            self.pressed = False
            self._zoom_callback(np.nanmin([self.y0, self.y1]), 
                                np.nanmax([self.y0, self.y1]))
        '''
        
    def set_zoom_callback(self, zoom_callback_function):
        self._zoom_callback = zoom_callback_function
    
    ### End - Zoom

    
        
    def set_callback(self, callback_function):
        self._callback = callback_function        
        
        
    def _create_dummy_axes(self, properties):
        ##print 'TrackFigureCanvas._create_dummy_axes'
        ##print 'PROPS: ', properties
        self.rect = [0.0, 0.0, 1.0, 1.0]
        self.dummy_ax = DummyAxes(self.figure, properties, self.rect)
        self.figure.add_axes(self.dummy_ax)
        
        
    def update_properties(self, **kwargs):
        ##print '\nTrackFigureCanvas.update_properties'
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
            self._create_dummy_axes(self.properties)

    
    def set_ylim(self, ylim):
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
        end = 12000
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

            
    def append_object(self, plot_type, object_id, **kwargs):
        self.insert_curve(len(self.axes)-1, plot_type, object_id, **kwargs)
   

    def insert_object(self, pos, plot_type, object_id, **kwargs):   
        ax = self.figure.add_axes(self.dummy_ax.get_position(True),
                          sharey=self.dummy_ax, 
                          frameon=False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        self.axes.append(ax)
        self.update_curve(pos, plot_type, object_id, **kwargs)
        

    def update_curve(self, pos, plot_type, object_id, **kwargs):
        ax = self.axes[pos]
        
        ls = kwargs.get('x_min', None)
        rs = kwargs.get('x_max', None)    

        #print 'x_lim:', ls, rs        
        
        if ls is not None and rs is not None:
            #print 1
            if ax.get_xlim() != (ls, rs):
                #print 2
                ax.set_xlim((ls, rs)) 
           # else:
                #print 3, ax.get_xlim()
        #print 4
        #print ax.get_xscale()  
        #print

        xs = kwargs.get('x_scale', None) 
        if xs is not None:
            if ax.get_xscale() == 'linear' and xs == 1:    
                ax.set_xscale('log')
            elif ax.get_xscale() == 'log' and xs == 0:  
                ax.set_xscale('linear')    
          
        """
        if plot_type == 'index':    
            ax.set_zorder(100)  
            start = 0
            step = kwargs.get('step', 500)
            end = 10000
            ax.set_ylim((10000.0, 0.0))
            #start = kwargs.get('y_min', 0)
            #ax.set_ylim((kwargs.get('y_max'), start))
            #step = kwargs.get('step', int((kwargs.get('y_max') -start)/10))
            locs = np.arange(start, end, step)
            #print '\nlocs:', locs
            #print ax.get_ylim()
            #print
            #locs = range(int(ymin), int(ymax), step)
            for loc in locs:
                text = ax.text(0.5, loc, "%g" % loc, ha='center', va='center', 
                    fontsize=10)#, bbox={'facecolor':'white', 'pad':1})
                text.set_bbox(dict(color='white', alpha=0.5, edgecolor='white'))
        """            
                    
        if plot_type == 'line': 
            
            #x_smooth = np.linspace(kwargs.get('x_data').min(), kwargs.get('x_data').max(), 200)
            #y_smooth = spline(kwargs.get('x_data'), kwargs.get('y_data'), x_smooth)

            '''
            idx  = np.arange(0, len(kwargs.get('y_data')), 1000, dtype=np.int)            

            # Pegar pixels dos y no axis e espaçar de acordo com isso                
            
            x_smooth = np.array([kwargs.get('x_data')[i] for i in idx])
            y_smooth = np.array([kwargs.get('y_data')[i] for i in idx])
            #idx = np.linspace(0, len(kwargs.get('y_data')), 200)
            #print '\nidx:', len(idx)
            '''
            linecolor = kwargs.get('linecolor', 'black')
            linewidth = kwargs.get('thickness')
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)
            
            if x_data is not None and y_data is not None:           
                
                if len(ax.lines) > 0: # never should be greater than 1 
                    #print '\n',len(ax.lines) > 0
                    ax.lines[0].set_color(linecolor)
                    ax.lines[0].set_linewidth(linewidth)
                    ax.lines[0].set_zorder(10000)  
                    ax.lines[0].set_data(x_data, y_data)      
                else: 
                    #print '\nELSE'                       
                    line = matplotlib.lines.Line2D(x_data, y_data, 
                            linewidth=linewidth, 
                            color=linecolor
                    )
                    ax.add_line(line) 
        
        
        elif plot_type == 'wiggle':         
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)

            if x_data is None or y_data is None:
                raise Exception('Wrong data informed. Check x_data and y_data.')

            if len(x_data.shape) == 1:
                x_data = x_data[:,np.newaxis]
                
            if len(x_data.shape) != 2:    
                raise Exception('Wrong number of dimensions: {}. Valid dimensions are 1 or 2.'.format(str(len(x_data.shape))))
                
            max_x_data = np.amax(np.absolute(x_data)) # for scaling  
            
            #print 'x_data.shape:', x_data.shape
            #print 'max_x_data:', max_x_data
            x_data = x_data / max_x_data
            
            for i in range(0, x_data.shape[0]):
                tr = x_data[i] 
                 
                line = matplotlib.lines.Line2D(i+tr+1, y_data,
                        linewidth=1, 
                        color='k'
                )
                ax.add_line(line)                    
                ax.fill_betweenx(y_data, i+1, i+tr+1, tr>=0, color='k')             
                
                
            ax.set_xlim((0, x_data.shape[0]+1))      
    
        elif plot_type == 'density':
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)
            
            if len(x_data.shape) == 1:
                #x_data = x_data[:,np.newaxis]
                x_data = x_data[np.newaxis, :]
            if len(x_data.shape) == 2:
                x_data = x_data[np.newaxis, :]
                

            x, y, z = x_data.shape 
            data = x_data.reshape((x*y, z))
            
            
            ylim = ax.get_ylim() 
            xmin, xmax = 0.0, data.shape[0]
            ax.set_xlim(xmin, xmax)
            ymin = np.nanmin(y_data)
            ymax = np.nanmax(y_data)
            extent = (xmin, xmax, ymax, ymin)
            vmin = kwargs.get('min_value', None)
            vmax = kwargs.get('max_value', None)
            
            if vmin is None or vmax is None:
                #print vmin, vmax
                raise Exception('')
                
            alpha = kwargs.get('alpha', 1.0)    
            ax.imshow(data.T, extent=extent, aspect='auto', 
                        cmap=kwargs.get('colormap'), 
                        vmin=vmin, 
                        vmax=vmax,
                        alpha=alpha
            )
            ax.set_ylim(ylim)             
            
        elif plot_type == 'partition':
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)
            ylim = ax.get_ylim()
            if len(ax.images) != 0:
                raise Exception('')
                
            
          #  def format_coord(x, y):
          #      col = int(x+0.5)
          #      row = int(y+0.5)
          #      #print 'format_coord:', col, row
          #      return 'AAA'
                '''
                if col>=0 and col<numcols and row>=0 and row<numrows:
                    if len(arr.shape) == 2:
                        z = arr[row,col]
                        return 'x=%1.4f, y=%1.4f, z=%1.1f'%(col, row,  z)
                    elif len(arr.shape) == 3:     
                        rgb = arr[row,col]
                        return 'x=%1.4f, y=%1.4f, red=%1.1f, green=%1.1f, blue=%1.1f'%(col, row, rgb[0], rgb[1], rgb[2])#(x, y, z)
                else:
                    return 'x=%1.4f, y=%1.4f'%(col, row)    
                '''
            xmin, xmax = 0.0, 1.0
            ax.set_xlim(xmin, xmax)
            
            # Attention with ymax and ymin
            ymin = np.nanmin(y_data)
            ymax = np.nanmax(y_data)
            ##print (xmin, xmax, ymax, ymin)
            extent = (xmin, xmax, ymax, ymin) #scalars (left, right, bottom, top)

            
            for wxcolor, data in x_data.values():
                mplcolor = [float(c)/255.0 for c in wxcolor]
                color = colorConverter.to_rgba_array(mplcolor[:3])
                im = np.tile(color, (data.shape[0], 1)).reshape(-1, 1, 4)
                im[:, 0, -1] = data
                axes_image = ax.imshow(im, extent=extent, interpolation='none', aspect='auto')

                
            ax.set_ylim(ylim)            
            ax.set_xlim(xmin, xmax)
        else:
            raise Exception('')      
            
            
        #ylim = (2942.0, 2514.0)         
        #ylim = (3000.0, 0.0)     
        #ylim = (500.0, 0.0) 
        ylim = (1000.0, 0.0) 
        #print '\nSetting... ', ylim 
        ax.set_ylim(ylim)       
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
    
    def __init__(self, parent, title=None, color=None, fontsize=None):
        #height = float(LABEL_TITLE_HEIGHT)/DPI
        height = float(28)/DPI
        fig = Figure(figsize=(1, height), dpi=DPI)#, linewidth=2, edgecolor='black')
        '''
        def __init__(self,
                     figsize=None,  # defaults to rc figure.figsize
                     dpi=None,  # defaults to rc figure.dpi
                     facecolor=None,  # defaults to rc figure.facecolor
                     edgecolor=None,  # defaults to rc figure.edgecolor
                     linewidth=0.0,  # the default linewidth of the frame
                     frameon=None,  # whether or not to draw the figure frame
                     subplotpars=None,  # default to rc
                     tight_layout=None,  # default to rc figure.autolayout
                     )    
        '''             
        super(PlotLabelTitle, self).__init__(parent, -1, fig)
        self._text = self.figure.text(0.5, 0.5, '', ha='center', va='center', fontsize=10)
        self.update(title, color, fontsize)        
        '''
        if title is not None:
            self.title = title 
        self.figure.patch.set_facecolor(color)
        self.figure.text(0.5, 0.5, '', ha='center', va='center', fontsize=10) 
        self.update(title, color)
        '''
        '''
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
        '''
 
 
    '''      
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click for self.parent. 
        """
        wx.PostEvent(self.parent, event)
    '''

           
    def update(self, title=None, color=None, fontsize=None):
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
        
        '''
        self._label.set_text(title)
        self._patch.set_facecolor(color)
        '''

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
       



###############################################################################  
###
###############################################################################



 
class PlotLabelObject(FigureCanvas):
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
    #(self,  name, plot_type, object_id, **kwargs)
    def __init__(self, parent, title=None, plot_type=None, object_id=None, **kwargs):
        if plot_type == 'wiggle':
            height = float(60)/DPI
            self.color = 'white'
            #self.color = 'lightblue'
        elif plot_type == 'density':
            height = float(60)/DPI
            self.color = 'white'
            #self.color = 'lightblue'            
        else:
            self.color = 'white'
            #self.color = 'lightblue'
            height = float(LABEL_TITLE_HEIGHT)/DPI
        #self.color = 'white'#'lightblue'
        self.parent = parent
        fig = Figure(figsize=(1, height), dpi=DPI)
        super(PlotLabelObject, self).__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self.color)
        
        '''      
        self._axes = Axes(fig, [0.0, 0.0 , 1.0, 1.0], axisbg='white')
        self._axes.spines['right'].set_visible(False)
        self._axes.spines['top'].set_visible(False)
        self._axes.spines['left'].set_visible(False)
        self._axes.spines['bottom'].set_visible(False)
        self._axes.xaxis.set_major_locator(NullLocator())
        self._axes.yaxis.set_major_locator(NullLocator())        
        fig.add_axes(self._axes)
        '''
     
        self.update(title, plot_type, object_id, **kwargs)
        self.obj_id = object_id    
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        
   
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click to self.parent. 
        """
        #print self.obj_id
        #wx.PostEvent(self.parent, event)



    def update(self, title, plot_type, object_id, **kwargs):
        """
        Updates track information displayed.      
             
        Parameters
        ----------            
        'name': str
            Track name
        'plottype': str
            Track type. Suported types: ['index', 'solid', 'partition']
        'unit': str
            Track values unit. Used when plottype is index or solid.
        'xmin': str
            Track xdata min. Used when plottype is solid.         
        'xmax': str
            Track xdata max. Used when plottype is solid.                                        
        'linecolor': mpl color spec
            Color for track line. Used when plottype is solid.   
        'linewidth': int
            Width for track line. Used when plottype is solid. 
                  
        Examples
        --------
        >>> plt = PlotLabelTrack(None)
        >>> plt.update(name='DEPTH', plottype='index', units='m')
        >>> plt.update(name='RHOZ', plottype='solid', units='g/cm3', 
                       xmin='1.95', xmax='2.95', linecolor='red', linewidth=1)
        >>> plt.update(name='LITO', plottype='partition')
        
        """

        if title is None or plot_type is None:
            return
        if plot_type not in VALID_PLOT_TYPES:
            return
             
             
        if plot_type == 'line':
            xleft = 0.05
            xright = 0.95
            ypos = 0.6
            
        
            unit = kwargs.get('x_unit', None)
            if unit is not None:
                self.figure.text(0.5, ypos, str(title), ha='center', fontsize=11)
                ypos -= 0.30
                unit = '(' + unit + ')'
                self.figure.text(0.5, ypos, unit, ha='center', fontsize=9)
            else:
                ypos -= 0.30
                self.figure.text(0.5, ypos, str(title), ha='center', fontsize=11)
                
            xmin = prepare_float_value(kwargs.get('x_min', ''))                
            xmax = prepare_float_value(kwargs.get('x_max', '')) 
            self.figure.text(xleft, ypos, xmin, ha='left', va='center', fontsize=9)
            self.figure.text(xright, ypos, xmax, ha='right', va='center', fontsize=9)
            
            #[left, bottom, width, height]    
            ax = Axes(self.figure, [xleft, 0.05, xright-xleft, 0.25])#, axisbg='white')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.xaxis.set_major_locator(NullLocator())
            ax.yaxis.set_major_locator(NullLocator())        
            self.figure.add_axes(ax)            
            line = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
            line.set_linewidth(kwargs.get('linewidth', 1))
            line.set_color(kwargs.get('linecolor', 'black'))    
            ax.add_line(line)    


        elif plot_type == 'index':
            self.figure.text(0.5, 0.55, str(title), ha='center', fontsize=11)
            if kwargs.get('unit') is not None:
                str_unit = '(' + str(kwargs.get('unit')) + ')'
                self.figure.text(0.5, 0.3, str_unit, ha='center', va='center', fontsize=9)
                
                
        elif plot_type == 'partition':
            self.figure.text(0.5, 0.55, str(title), ha='center', fontsize=11)
            self.figure.text(0.5, 0.3, '(partition)', ha='center', va='center', fontsize=9)        



        elif plot_type == 'density':
            self.figure.text(0.5, 0.75, str(title), ha='center', fontsize=11)
            ax0 = Axes(self.figure, [0.05, 0.35, 0.9, 0.15])
            ax0.spines['right'].set_visible(False)
            ax0.spines['top'].set_visible(False)
            ax0.spines['left'].set_visible(False)
            ax0.spines['bottom'].set_visible(False)
            ax0.xaxis.set_major_locator(NullLocator())
            ax0.yaxis.set_major_locator(NullLocator()) 
            gradient = np.linspace(0, 1, 256)
            gradient = np.vstack((gradient, gradient))
            ax0.imshow(gradient, aspect='auto', cmap=kwargs.get('colormap'))
            self.figure.add_axes(ax0)
            
            zmin = prepare_float_value(kwargs.get('z_min', ''))                
            zmax = prepare_float_value(kwargs.get('z_max', '')) 
            str_z =  kwargs.get('z_label', '')
            
            ypos = 0.60
            self.figure.text(0.5, ypos, str_z, ha='center', va='center', fontsize=9)
            self.figure.text(0.05, ypos, zmin, ha='left', va='center', fontsize=9) 
            self.figure.text(0.95, ypos, zmax, ha='right', va='center', fontsize=9) 
            
            ax1 = Axes(self.figure, [0.05, 0.00, 0.9, 0.2])#, axisbg='blue') #self.color)
            ax1.spines['right'].set_visible(False)
            ax1.spines['top'].set_visible(False)
            ax1.spines['left'].set_visible(False)
            ax1.spines['bottom'].set_visible(False)
            ax1.xaxis.set_major_locator(NullLocator())
            ax1.yaxis.set_major_locator(NullLocator())        
            self.figure.add_axes(ax1)     
          
            l1 = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
            l1.set_linewidth(kwargs.get('linewidth', 1))
            l1.set_color(kwargs.get('linecolor', 'black'))  
            
            ax1.add_line(l1)
                        
            ypos = 0.18            
            str_x = kwargs.get('x_label', '')
            if kwargs.get('x_unit', None) is not None:
                str_x = str_x + ' (' + kwargs.get('x_unit') + ')'
            self.figure.text(0.5, ypos, str_x, ha='center', 
                         va='center', fontsize=10
            )  
            xmin = prepare_float_value(kwargs.get('x_min', ''))                
            xmax = prepare_float_value(kwargs.get('x_max', '')) 
            self.figure.text(0.05, ypos, xmin, ha='left', va='center', fontsize=9) 
            self.figure.text(0.95, ypos, xmax, ha='right', va='center', fontsize=9)
            
            
        elif plot_type == 'wiggle':  
            self.figure.text(0.5, 0.75, str(title), ha='center', fontsize=11)   
            if kwargs.get('z_min') is not None and kwargs.get('z_max') is not None:
                zmin = prepare_float_value(kwargs.get('z_min'))                
                zmax = prepare_float_value(kwargs.get('z_max')) 
                str_z =  kwargs.get('z_label', '')
                str_z = str_z + ' [' + zmin + ':' + zmax + ']'  
                self.figure.text(0.5, 0.58, str_z, ha='center', va='center', fontsize=9)
         
         
            str_x = kwargs.get('x_label', '')
            if kwargs.get('x_unit', None) is not None:
                str_x = str_x + ' (' + kwargs.get('x_unit') + ')'
            self.figure.text(0.5, 0.35, str_x, ha='center', va='center', fontsize=9)         
            ax1 = Axes(self.figure, [0.00, 0.15, 1.0, 0.2]  ) #, axisbg='lightblue') #self.color)
            ax1.spines['right'].set_visible(False)
            ax1.spines['top'].set_visible(False)
            ax1.spines['left'].set_visible(False)
            ax1.spines['bottom'].set_visible(False)
            ax1.xaxis.set_major_locator(NullLocator())
            ax1.yaxis.set_major_locator(NullLocator())        
            self.figure.add_axes(ax1)     
            
            l1 = matplotlib.lines.Line2D([0.0, 1.0], [0.5, 0.5])
            l1.set_linewidth(kwargs.get('linewidth', 1))
            l1.set_color(kwargs.get('linecolor', 'black'))  
            
            if kwargs.get('x_range') is not None:
            

                ax1.set_xlim((0, len(kwargs.get('x_range'))+1))
                #print '\n\nx_lim:', ax1.get_xlim(),'\n\n'
                ax1.set_ylim((-1.0, 1.0))

                x_data = np.array(range(0, len(kwargs.get('x_range'))+1), dtype=np.float)
                y_data = np.zeros(len(kwargs.get('x_range'))+1)
                
    
                factor = 0.5
                x_data[0] = x_data[0] + factor
                x_data[-1] = x_data[-1] + factor
                
                ax1.plot(x_data[0], 0.5, '|', color='black')
                ax1.plot(x_data[-1], 0.5, '|', color='black')
                l1.set_data(x_data, y_data)           
                #r = self.figure.canvas.get_renderer()
                
                for i in range(0, len(kwargs.get('x_range'))):
                    ax1.plot(i+1, -0.5, '|', color='black')
                   
                    ax1.text(i+1, -2.4, str(kwargs.get('x_range')[i]), 
                                 fontsize=8#, horizontalalignment='left'
                    )
                    '''
                    t = ax1.text(i+1, 0.0, str(kwargs.get('x_range')[i]), 
                                 fontsize=9 #, horizontalalignment='left'
                    )                    
                    '''
                   # bb = t.get_window_extent(r)
                   # width = bb.width
                   # height = bb.height
                   # #print width, height
                  
            ax1.add_line(l1)   
            #else:
            #self._axes.text(0.5, 0.3, '(Wiggle)', ha='center', va='center', fontsize=10)    
            #self.parent.GetSizer().Fit(self)#Layout()#.Refresh()self.Layout()
        


        
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
    _visual_objects: list
        A list container for PlotLabelObject.
        
    """
    
    def __init__(self, wx_parent, view_object):
        super(PlotLabel, self).__init__(wx_parent)
        self._view = view_object
        self._title = None
        self._visual_objects = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))  
        
        #self.Bind(wx.EVT_MOTION, self._on_mouse)
        
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_middle_down)
        
        self._selected = False
        self.selectedCanvas = []
        
        
    def is_selected(self):
        return self._selected
        
    def _on_middle_down(self, event):
        self._view.set_selected(self, not self._selected)   
        self._do_select()
        event.Skip()
        
    def _do_select(self):
        self._selected = not self._selected
        self.GetParent()._draw_window_selection(self)
    

        

    def create_title(self):
        """
        Creates title's container.
        
        Notes
        -----        
        Despite it creates the container where title properties will be 
        placed. It is necessary to call update_title to send these
        properties.
            
        """
        self._title = PlotLabelTitle(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
            
            
    def update_title(self, text='', bgcolor='yellow'):
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
        self._title.update(text, bgcolor) 
        self.Layout() 
          
        
    def remove_title(self):
        """
        Removes the title.
        """
        if self._title is not None:
            self.GetSizer().Remove(self._title)
            t = self._title
            self._title = None
            t.Destroy()
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
        

    
    def append_object(self, name, plot_type, object_id, **kwargs):
        self.insert_object(len(self._visual_objects), name, plot_type, object_id, **kwargs)
        
        
    def insert_object(self, pos, name, plot_type, object_id, **kwargs):
        """
        Insert a new visual object at given pos with properties informed.
        """
        plt = PlotLabelObject(self, name, plot_type, object_id, **kwargs)    
        self._visual_objects.insert(pos, plt)
        self.GetSizer().Add(plt, 0,  wx.EXPAND)
        self.Layout()
        
        
    def update_object(self, pos, **kwargs):
        """
        Updates track information displayed.      
             
        Parameters
        ----------            
        'name': str
            Track name
        'plottype': str
            Track type. Suported types: ['index', 'solid', 'partition']
        'unit': str
            Track values unit. Used when plottype is index or solid.
        'xmin': str
            Track xdata min. Used when plottype is solid.         
        'xmax': str
            Track xdata max. Used when plottype is solid.                                        
        'linecolor': mpl color spec
            Color for track line. Used when plottype is solid.   
        'linewidth': int
            Width for track line. Used when plottype is solid. 
                  
        Examples
        --------
        >>> pl.update_object(name='DEPTH', plottype='index', units='m')
        >>> pl.update_object(name='RHOZ', plottype='solid', units='g/cm3', 
                       xmin='1.95', xmax='2.95', linecolor='red', linewidth=1)
        >>> pl.update_object(name='LITO', plottype='partition')
        
        """
        self._visual_objects[pos].update(**kwargs)
        self.Layout() 
        
        
    def remove_object(self, pos):
        """
        Removes the track is a given position. 
        """
        llt = self._visual_objects.pop(pos)
        self.GetSizer().Remove(llt)
        llt.Destroy()
        self.Layout()        

 
    
    
###############################################################################  
###
###############################################################################

SASH_DRAG_NONE = 0 
SASH_DRAG_DRAGGING = 1
      
class OverviewFigureCanvas(_BaseFigureCanvas):

        
    def __init__(self, parent, size, min_depth=0, max_depth=10000,
                                                 min_pos=None, max_pos=None):
        self.dummy_ax = None
       
        _BaseFigureCanvas.__init__(self, parent, size)
        self.axes = []
        #self._selected = False
        #self.selectedCanvas = []
        self.index_axes = None

        self._callback = None
        self.dummy_ax.set_ylim(max_depth, min_depth) 
        self.dummy_ax.set_xlim(0, 100)
        self.canvas_color = 'blue'
        self.canvas_alt_color = 'red'
        self.canvas_width = 3
        self.d1_canvas = None
        self.d2_canvas = None
        
        self.create_depth_canvas(min_pos, max_pos)
        #self.set_depth(min_depth, max_depth) 
        self._in_canvas = -1
        self._drag_mode = SASH_DRAG_NONE
        
        #self.mpl_connect('motion_notify_event', self.on_move)
        #self.mpl_connect('button_press_event', self.on_mouse_pressed)
        #self.mpl_connect('button_release_event', self.on_mouse_released)
        
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self._on_mouse)


        self.d1_canvas.Bind(wx.EVT_MOUSE_EVENTS, self._on_canvas_mouse)
        self.d2_canvas.Bind(wx.EVT_MOUSE_EVENTS, self._on_canvas_mouse)
        #self.d1_canvas.Bind(wx.EVT_PAINT, self.on_paint)
        #self.d2_canvas.Bind(wx.EVT_PAINT, self.on_paint)
     


    def set_callback(self, callback):
        self._callback = callback
        
    def remove_callback(self):
        self._callback = None


    def create_depth_canvas(self, min_pos=None, max_pos=None):
        if not self.d1_canvas:
            self.d1_canvas = wx.Panel(self) 
            self.d1_canvas.SetSize((self.GetClientSize().width, self.canvas_width))
            self.d1_canvas.SetBackgroundColour(self.canvas_color)    
        if not self.d2_canvas:
                self.d2_canvas = wx.Panel(self) 
                self.d2_canvas.SetSize((self.GetClientSize().width, self.canvas_width))
                self.d2_canvas.SetBackgroundColour(self.canvas_color)    

        max_depth, min_depth = self.dummy_ax.get_ylim()        
            
        if min_pos is None or min_pos < min_depth or min_pos > max_depth:
            self.d1 = min_depth
        else:
            self.d1 = min_pos
        if max_pos is None  or max_pos < min_depth or max_pos > max_depth:
            self.d2 = max_depth
        else:
            self.d2 = max_pos        
        ##print '\nMIN-MAX:', min_depth, max_depth, min_pos, max_pos, self.d1, self.d2     
        y1 = self.depth_to_wx_position(self.d1)
        self.d1_canvas.SetPosition((0, y1)) 
        #self.d1_canvas.Refresh()
        y2 = self.depth_to_wx_position(self.d2)          
        self.d2_canvas.SetPosition((0, y2)) 
        #self.d2_canvas.Refresh()


    def _reload_depths_from_canvas_positions(self):
        y1 = self.d1_canvas.GetPosition()[1]
        y2 = self.d2_canvas.GetPosition()[1]
        if y1 <= y2:
            self.d1 = self.wx_position_to_depth(y1)
            self.d2 = self.wx_position_to_depth(y2+self.canvas_width)
        else:
            self.d1 = self.wx_position_to_depth(y1+self.canvas_width)
            self.d2 = self.wx_position_to_depth(y2)


    def _reload_canvas_positions_from_depths(self):
        y1 = self.depth_to_wx_position(self.d1)
        y2 = self.depth_to_wx_position(self.d2)
        if y1 <= y2:
            self.d1_canvas.SetPosition((0, y1))
            self.d2_canvas.SetPosition((0, y2-self.canvas_width))
        else:
            self.d1_canvas.SetPosition((0, y1-self.canvas_width))
            self.d2_canvas.SetPosition((0, y2))    
        #self.d1_canvas.Refresh()
        #self.d2_canvas.Refresh()
        
    

    def get_depth(self):
        if self.d1 <= self.d2:
            return (self.d1, self.d2)
        else:
            return (self.d2, self.d1)
            

    """
    From wx display coords to mpl display position or vice-versa.
    """    
    def transform_display_position(self, pos):
        _, y = self.GetClientSize() 
        pos = y - pos
        return int(pos)
        
       
    def wx_position_to_depth(self, wx_pos):
        y_max, y_min = self.dummy_ax.get_ylim()
        if wx_pos <= 0:
            return y_min
        elif wx_pos >= self.GetClientSize()[1]:   
            return y_max
        mpl_y_pos = self.transform_display_position(wx_pos)
        return self.dummy_ax.transData.inverted().transform((0, mpl_y_pos))[1] 


    def depth_to_wx_position(self, depth):
        y_max, y_min = self.dummy_ax.get_ylim()
        if depth <= y_min:
            return 0
        elif depth >= y_max:
            return self.GetClientSize()[1]    
        x, y = self.dummy_ax.transData.transform((0, depth)) 
        return self.transform_display_position(y)


    def on_paint(self, event):
        event.Skip()
        if self._drag_mode == SASH_DRAG_DRAGGING:
            return
        #print 'OverviewFigureCanvas.on_paint'
        self._reload_canvas_positions_from_depths()


    def on_size(self, event):
        #print 'OverviewFigureCanvas.on_size'
        ##print 'Internal depth:', self.get_depth()
        #self._reload_canvas_positions_from_depths()
        
        
        y1 = self.d1_canvas.GetPosition()[1]
        y2 = self.d2_canvas.GetPosition()[1]
        if y1 <= y2:
            d1 = self.wx_position_to_depth(y1)
            d2 = self.wx_position_to_depth(y2+self.canvas_width)
        else:
            d1 = self.wx_position_to_depth(y1+self.canvas_width)
            d2 = self.wx_position_to_depth(y2)      
        ##print y1, y2, d1, d2, '\n'
        
        event.Skip()
        

    def _on_mouse(self, event):
        x, y = event.GetPosition()
        #data_y = self.wx_position_to_depth((y)
        ##print '_on_mouse:', x, y, data_y, event.GetEventType()
            
        if self._drag_mode == SASH_DRAG_NONE:    
            self._set_in_canvas(self._canvas_hit_test(x, y))              
            if event.LeftDown():
                self.start_dragging(y)
        elif self._drag_mode == SASH_DRAG_DRAGGING:
            if event.LeftIsDown():
                self.drag_it(y)       
            elif event.LeftUp():
                self.end_dragging()


    def _adjust_canvas_position(self, inc):
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        elif self._in_canvas == 2:
            canvas = self.d2_canvas
        x, y = canvas.GetPosition()  
        new_pos = y + inc
        if new_pos < 0:
            new_pos = 0
        if new_pos > (self.GetClientSize()[1] - self.canvas_width):
            new_pos = self.GetClientSize()[1] - self.canvas_width
        canvas.SetPosition((x, new_pos))
        canvas.Refresh()
        


    def start_dragging(self, start_y):
        ##print '\nPressed button on canvas ', self._in_canvas
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_NONE:
            return
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        else:
            canvas = self.d2_canvas
        self._drag_mode = SASH_DRAG_DRAGGING
        self.CaptureMouse()
        self._old_y = start_y
        canvas.SetBackgroundColour(self.canvas_alt_color)
        canvas.Refresh()            


    def drag_it(self, new_y):
        ##print '\nDragging canvas:', self._in_canvas
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_DRAGGING:
            return       
        ##print new_y, self._old_y 
        if new_y != self._old_y:
            self._adjust_canvas_position(new_y - self._old_y)
            self._old_y = new_y


    def end_dragging(self):
        ##print 'Release button of canvas', self._in_canvas
        if self._in_canvas == -1:
            return 
        if self._drag_mode != SASH_DRAG_DRAGGING:
            return    
        if self._in_canvas == 1:
            canvas = self.d1_canvas
        else:
            canvas = self.d2_canvas
        self._drag_mode = SASH_DRAG_NONE
        self._old_y = None
        if self.HasCapture():
            self.ReleaseMouse()
        self._reload_depths_from_canvas_positions()    
        if self._callback:
            self._callback(self.get_depth())
        #print 'Send ' + str(self.get_depth()) + ' to callback...'    
        canvas.SetBackgroundColour(self.canvas_color)
        canvas.Refresh()  
                   
        d1, d2 = self.get_depth()           
        self.SetToolTip(wx.ToolTip('{0:.2f} - {1:.2f}'.format(d1, d2)))
          
            
    def _canvas_hit_test(self, x, y, tolerance=5):
        r1 = self.d1_canvas.GetRect()   
        r2 = self.d2_canvas.GetRect() 
        if y >= r1.y - tolerance and y <= r1.y + r1.height + tolerance:
            return 1
        if y >= r2.y - tolerance and y <= r2.y + r2.height + tolerance:
            return 2        
        return -1    
        
   
    def _set_in_canvas(self, canvas_number):
        if canvas_number != self._in_canvas:
            ##print '_set_in_canvas({})'.format(canvas_number)
            if canvas_number != -1:
                ##print 'Entrou -', canvas_number
                self._in_canvas = canvas_number
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    self.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
                else:
                    # wxPython classic code
                    self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
            else:
                ##print 'Saiu -', self._in_canvas
                self._in_canvas = -1
                self.SetCursor(wx.STANDARD_CURSOR)
    
  
    def _on_canvas_mouse(self, event):
        if event.GetEventType() in [wx.wxEVT_MOTION, wx.wxEVT_LEFT_DOWN, 
                        wx.wxEVT_LEFT_UP, wx.wxEVT_MOTION|wx.wxEVT_LEFT_DOWN]:
            evt = wx.MouseEvent(event.GetEventType())
            pos = self.ScreenToClient(wx.GetMousePosition())
            evt.SetPosition(pos)
            self.GetEventHandler().ProcessEvent(evt) or evt.IsAllowed()
            

            
    def _create_dummy_axes(self):
        self.rect = [0.0, 0.0, 1.0, 1.0]
        self.dummy_ax = DummyAxes(self.figure, None, self.rect)
        self.figure.add_axes(self.dummy_ax)
        
        
            
    def set_dummy_spines_visibility(self, boolean):
        if self.dummy_ax is not None:
            self.dummy_ax.set_spines_visibility(boolean)
            
       
    # Overrides super class method
    def _draw_figure(self):
        if not self.dummy_ax:
            self._create_dummy_axes()

    
    def set_ylim(self, ylim):
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
        end = 12000
        locs = np.arange(start, end, step)
        for loc in locs:
            text = self.index_axes.text(0.5, loc, "%g" % loc, ha='center', 
                                        va='center',  fontsize=10
            )
            text.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))  
        self.draw()     


    def hide_index_curve(self):
        if not self.index_axes:
            return
        self.index_axes.texts = []
        self.draw() 

            
   