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



# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40


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



###############################################################################  
###
###############################################################################

'''

 
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
        self.update(title, plot_type, object_id, **kwargs)
        self.obj_id = object_id    
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        
   
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click to self.parent. 
        """
        print self.obj_id
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
        

'''
 


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
       



        
class PlotLabel(wx.Panel):
 
    def __init__(self, wx_parent, view_object):
        super(PlotLabel, self).__init__(wx_parent)
        self._view = view_object
        self._title = None
        self._visual_objects = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))  
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
        self._title = PlotLabelTitle(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
            
            
    def update_title(self, text='', bgcolor='yellow', fontsize=10):
        if self._title is None:
            self.create_title()
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
    _COLOR = 'lightblue' #'white'
    
    def __init__(self, parent):
        self.parent = parent
        fig = Figure(figsize=(1, 0.5))
        super(VisDataLabel, self).__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        #self.update(title, plot_type, object_id, **kwargs)
        self.obj_id = None  
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        
   
    def _on_left_double_click(self, event):
        """
        A method just for propagate left double click to self.parent. 
        """
        print 'Obj_id:', self.obj_id
        #wx.PostEvent(self.parent, event)



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

        print '\n\nVisDataLabel.set_data:', data_title, plot_type, object_id, kwargs

        if data_title is None or plot_type is None:
            return
        if plot_type not in VALID_PLOT_TYPES:
            return
            
        self.obj_id = object_id     
             
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
                self.figure.text(0.5, ypos, str(data_title), ha='center', fontsize=11)
                ypos -= 0.30
                unit = '(' + unit + ')'
                self.figure.text(0.5, ypos, unit, ha='center', fontsize=9)
            else:
                ypos -= 0.30
                self.figure.text(0.5, ypos, str(data_title), ha='center', fontsize=11)
                
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
        

            
 
    