# -*- coding: utf-8 -*-
import wx
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from App import log


# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40


VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']





def prepare_float_value(value):
    value = "{0:.3f}".format(value)#str(value)
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
        
        l = matplotlib.lines.Line2D([0, 1], [0, 1])
        l.set_linewidth(1)
        l.set_color('black')  
        fig._set_artist_props(l)
        
        super(PlotLabelTitle, self).__init__(parent, -1, fig)
        self._text = self.figure.text(0.5, 0.5, '', ha='center', va='center')
        self.update(title, color, fontsize)        

        self.mpl_connect('button_press_event', self._on_press)

                
    def _on_press(self, event):
        print 'PlotLabelTitle._on_press'
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
        fig = Figure(figsize=(1, 0.5))
        super(VisDataLabel, self).__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        self._obj_uid = None  
        #self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        self._mplot_objects = {}
        self._properties = {}
        self._start_variables()
        
        self.mpl_connect('button_press_event', self._on_press)

                
    def _on_press(self, event):
        print 'VisDataLabel._on_press'
        self.GetParent()._on_press(event)
       
   
    #def _on_left_double_click(self, event):
    #    """
    #    A method just for propagate left double click to self.parent. 
    #    """
    #    print 'Obj_id:', self._obj_uid
    #    #wx.PostEvent(self.parent, event)


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
        print '\nVisDataLabel.set_object_uid', object_uid
        self._obj_uid = object_uid 


    def set_title(self, title):
        print '\nVisDataLabel.set_title:', title
        if self.title == title:
            return
        props = self._properties.get('title', None)
        if props:
            title_text = self._mplot_objects.get('title_text', None)
            if not title_text:
                title_text = create_text(self.figure, title, props)
                self._mplot_objects['title_text'] = title_text
            else:
                title_text.set_text(title)
            self.draw()    
            self.title = title   
        else:
            raise Exception()    


    def set_unit(self, unit):
        print '\nVisDataLabel.set_unit'
        if self.unit == unit:
            return
        props = self._properties.get('sub_title', None)
        if props:
            unit_text = self._mplot_objects.get('unit_text', None)
            if not unit_text:
                unit_text = create_text(self.figure, unit, props)
                self._mplot_objects['unit_text'] = unit_text
            else:
                unit_text.set_text(unit)
            self.draw()    
            self.unit = unit   
        else:
            raise Exception()  
            
                         
    def set_color(self, color):
        print '\nVisDataLabel.set_color'
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
        print '\nVisDataLabel.set_thickness'
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
        print '\nVisDataLabel.set_colormap'
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
        print '\nVisDataLabel.set_zlabel:', z_axis_label
        if self.plottype == 'density' or self.plottype == 'wiggle':
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
        print '\nVisDataLabel.set_xlim'
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
        print '\nVisDataLabel.set_zlim:', zlim
        if self.zlim == zlim:
            return
        zmin, zmax = zlim
        props = self._properties.get('zmin', None)
        if props:
            zmin_text = self._mplot_objects.get('zmin_text', None)
            zmin = prepare_float_value(zmin)
            if not zmin_text:                
                self._mplot_objects['xmin_text'] = create_text(self.figure, 
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
        print '\nVisDataLabel.set_xlabel:', x_axis_label
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



#
    """
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
    """        


    def set_plot_type(self, plottype):
        print '\nVisDataLabel.set_plotype: ', plottype
        if plottype == self.plottype:
            return
        if plottype not in VALID_PLOT_TYPES:
            return
        self._start_variables()   
        """
        if plottype == 'wiggle':
            self.height = float(60)/DPI
        elif plottype == 'density':
            self.height = float(60)/DPI          
        else:
            self.height = float(LABEL_TITLE_HEIGHT)/DPI   
        w, _ = self.figure.get_size_inches()     
        self.figure.set_size_inches(w, self.height, forward=True)    
        """
        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        
        if plottype == 'line':
            self._properties['title'] = {'x': 0.5, 'y':0.6, 'ha':'center', 'fontsize':11}
            self._properties['sub_title'] = {'x': 0.5, 'y':0.3, 'ha':'center', 'fontsize':9}        
            self._properties['xmin'] = {'x': self._properties['xleft'],
                             'y':0.3, 'ha':'left', 'va':'center', 'fontsize':9
            }     
            self._properties['xmax'] = {'x': self._properties['xright'],
                             'y':0.3, 'ha':'right', 'va':'center', 'fontsize':9
            }
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.05, 
                        self._properties['xright']-self._properties['xleft'],
                        0.25
            ]
        elif plottype == 'density':
            self._properties['title'] = {'x': 0.5, 'y':0.75, 'ha':'center', 
                                                                'fontsize':11}            
            self._properties['cmap_axes_extent'] = [self._properties['xleft'],
                        0.35, 
                        self._properties['xright']-self._properties['xleft'],
                        0.15
            ]
            ypos = 0.6
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
            self._properties['title'] = {'x': 0.5, 'y':0.75, 'ha':'center', 
                                                                'fontsize':11}  
            self._properties['zlabel'] = {'x': 0.5, 'y':0.58, 'ha':'center', 
                                                'va':'center', 'fontsize':9
            }                                                    
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
        
        elif plottype == 'partition':
            print 'entrou partition'
            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
                                                                'fontsize':11}
            self._properties['sub_title'] = {'x': 0.5, 'y':0.3, 'ha':'center', 
                                                                'fontsize':9}
        #self.draw()                                                                    
        self.plottype = plottype                                                        


    def set_data(self, data_title, plot_type, object_id, **kwargs):
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
        >>> plt.set_data(name='DEPTH', plottype='index', units='m')
        >>> plt.set_data(name='RHOZ', plottype='solid', units='g/cm3', 
                       xmin='1.95', xmax='2.95', linecolor='red', linewidth=1)
        >>> plt.set_data(name='LITO', plottype='partition')
        
        """

        #print '\n\nVisDataLabel.set_data:', data_title, plot_type, object_id, kwargs

        if data_title is None or plot_type is None:
            return
        if plot_type not in VALID_PLOT_TYPES:
            return
            
        #self.obj_id = object_id     
             
        if plot_type == 'wiggle':
            h = float(60)/DPI
        elif plot_type == 'density':
            h = float(60)/DPI          
        else:
            h = float(LABEL_TITLE_HEIGHT)/DPI             
        w, _ = self.figure.get_size_inches()            
        self.figure.set_size_inches(w, h, forward=True)
            
            
        if plot_type == 'line':
            xleft = 0.05
            xright = 0.95
            ypos = 0.6
            unit = kwargs.get('x_unit', None)
            if unit is not None:
                title_text = self.figure.text(0.5, ypos, str(data_title), ha='center', fontsize=11)
                self._mplot_objects['title_text'] = title_text
                
                ypos -= 0.30
                unit = '(' + unit + ')'
                unit_text = self.figure.text(0.5, ypos, unit, ha='center', fontsize=9)
                self._mplot_objects['unit_text'] = unit_text
            else:
                ypos -= 0.30
                self._mplot_objects['title_text'] = self.figure.text(0.5, 
                            ypos, str(data_title), ha='center', fontsize=11
                )
                
            xmin = prepare_float_value(kwargs.get('x_min', ''))                
            xmax = prepare_float_value(kwargs.get('x_max', '')) 
            
            self._mplot_objects['xmin_text'] = self.figure.text(xleft, ypos,
                                     xmin, ha='left', va='center', fontsize=9
            )
            self._mplot_objects['xmax_text'] = self.figure.text(xright, ypos, 
                                    xmax, ha='right', va='center', fontsize=9
            )
            
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
            self._mplot_objects['line'] = ax.add_line(line)    


        elif plot_type == 'index':
            self.figure.text(0.5, 0.55, str(data_title), ha='center', fontsize=11)
            if kwargs.get('unit') is not None:
                str_unit = '(' + str(kwargs.get('unit')) + ')'
                self.figure.text(0.5, 0.3, str_unit, ha='center', va='center', fontsize=9)
                
                
        elif plot_type == 'partition':
            self.figure.text(0.5, 0.55, str(data_title), ha='center', fontsize=11)
            self.figure.text(0.5, 0.3, '(partition)', ha='center', va='center', fontsize=9)        



        elif plot_type == 'density':
            self.figure.text(0.5, 0.75, str(data_title), ha='center', fontsize=11)
            ax0 = Axes(self.figure, [0.05, 0.35, 0.9, 0.15])
            ax0.spines['right'].set_visible(False)
            ax0.spines['top'].set_visible(False)
            ax0.spines['left'].set_visible(False)
            ax0.spines['bottom'].set_visible(False)
            ax0.xaxis.set_major_locator(NullLocator())
            ax0.yaxis.set_major_locator(NullLocator()) 
            gradient = np.linspace(0, 1, 256)
            gradient = np.vstack((gradient, gradient))
            self.ax0.imshow(gradient, aspect='auto', cmap=kwargs.get('colormap'))
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
            self.figure.text(0.5, 0.75, str(data_title), ha='center', fontsize=11)   
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
                print '\n\nx_lim:', ax1.get_xlim(),'\n\n'
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
                    """
                    t = ax1.text(i+1, 0.0, str(kwargs.get('x_range')[i]), 
                                 fontsize=9 #, horizontalalignment='left'
                    )                    
                    """
                   # bb = t.get_window_extent(r)
                   # width = bb.width
                   # height = bb.height
                   # print width, height
                  
            ax1.add_line(l1)   
            #else:
            #self._axes.text(0.5, 0.3, '(Wiggle)', ha='center', va='center', fontsize=10)    
            #self.parent.GetSizer().Fit(self)#Layout()#.Refresh()self.Layout()
        

            
 
class PlotLabel(wx.Panel):
    
    DEFAULT_BG_COLOR  = '#B0C4DE' #LightSteelBlue  
    
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
        # TODO: VER ISSO ABAIXO, POIS ESTÁ ESTRANHO
        self.selectedCanvas = []


                
    def _on_press(self, event):
        self.track_view_object.process_event(event)

    # por enquanto não vou colocar esse metodo no TrackFigureCanvas (em teste)
    #def _has_changed_position_to(self, new_pos):
    #    self.track_view_object._has_changed_position_to(new_pos)


    def is_selected(self):
        return self._selected
        
        
        
    def _do_select(self):
        self._selected = not self._selected
        self.GetParent()._draw_window_selection(self)
    

    def create_title(self):
        self._title = PlotLabelTitle(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
            
            
    def update_title(self, text='', bgcolor=None, fontsize=10):
        if self._title is None:
            self.create_title()
        if not bgcolor:
            bgcolor = PlotLabel.DEFAULT_BG_COLOR
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
        
        
    def remove_object(self, pos):
        """
        Removes the track is a given position. 
        """
        vdl = self._visual_objects.pop(pos)
        self.GetSizer().Remove(vdl)
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
    text = figure.text(props.get('x'), props.get('y'), str(to_print),
                       ha=props.get('ha'), fontsize=props.get('fontsize')
    )
    vertical_alignment = props.get('va', None)
    if vertical_alignment:
        text.update({'va': vertical_alignment})
    return text
        