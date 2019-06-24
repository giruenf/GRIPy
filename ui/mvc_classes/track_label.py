from collections import OrderedDict

import numpy as np
import wx
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator

from app import log
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 
from ui.mvc_classes.extras import SelectablePanelMixin



# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40
VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']


# TODO: Parametros: levar para App.utils ou Parameters.manager
DEFAULT_LABEL_BG_COLOR  = '#B0C4DE' #LightSteelBlue  
SELECTION_WIDTH = 2
SELECTION_COLOR = 'green'



def create_and_prepare_axes(figure, extent, **kwargs):
    #import matplotlib.figure.Figure.text
    ax = Axes(figure, extent) #, label=kwargs.get('toc_uid', ''))
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
    vertical_alignment = props.get('va')
    if vertical_alignment:
        text.update({'va': vertical_alignment})
    return text
            
  
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





class TrackTitleCanvas(FigureCanvas):
    def __init__(self, parent, title=None, color=None, fontsize=10):
        height = 28.0/DPI
        fig = Figure(figsize=(1, height), dpi=DPI)
        super().__init__(parent, -1, fig)   
        l = Line2D([0.0, 1.0], [0.05, 0.05])
        l.set_linewidth(1)
        l.set_color('black')  
        fig._set_artist_props(l)
        fig.lines.append(l)
        l._remove_method = lambda h: self.lines.remove(h)
        fig.stale = True
        self._text = self.figure.text(0.5, 0.5, '', ha='center', va='center')
        self.update(title, color, fontsize)        
        
#        self.mpl_connect('button_press_event', self._on_press)
        #self.Bind(wx.EVT_PAINT, self.on_paint)

    #def on_paint(self, event):
    #    print 'TrackTitleCanvas.on_paint'
    #    event.Skip()
                
    def _on_press(self, event):
        self.GetParent()._on_press(event)        
              
    def update(self, title=None, color=None, fontsize=10):
        """
        Update TrackTitleCanvas properties.
        
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
          




class TitleDataLabel(FigureCanvas):
    _COLOR = 'lightgreen'
    
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        fig = Figure(figsize=(1, 0.30))
        super().__init__(self.parent, -1, fig)     
#        self.figure.set_facecolor(self._COLOR)
        #
        self._mplot_objects = {}
        self._properties = {}
        self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 'fontsize':9}
        self._properties['sub_title'] = {'x': 0.5, 'y':0.10, 'ha':'center', 'fontsize':9} 
        #
        self.title = None
        self.subtitle = None
        
    def set_title(self, title):
        if self.title == title:
            return
        title_text = self._mplot_objects.get('title_text', None)
        if not title_text:
            title_text = create_text(self.figure, title, self._properties['title'])
            self._mplot_objects['title_text'] = title_text
        else:
            title_text.set_text(title)
        self.draw()    
        self.title = title   

    def set_subtitle(self, subtitle):
        if self.subtitle == subtitle: 
            return
        subtitle = self._mplot_objects.get('subtitle', None)
        if not subtitle:
            subtitle = create_text(self.figure, '(' + str(subtitle) + ')', self._properties['sub_title'])
            self._mplot_objects['subtitle'] = subtitle
        else:
            subtitle.set_text('(' + subtitle + ')')
        self.draw()    
        self.subtitle = subtitle 



class LineDataLabel(FigureCanvas):
    _COLOR = 'lightblue'
    
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        fig = Figure(figsize=(1, 0.20))
        super().__init__(self.parent, -1, fig)     
#        self.figure.set_facecolor(self._COLOR)
        #
        self._mplot_objects = {}
        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        self._properties['min'] = {'x': self._properties['xleft'], 'y':0.33, 'ha':'left', 'va':'center', 'fontsize':9}     
        self._properties['max'] = {'x': self._properties['xright'], 'y':0.33, 'ha':'right', 'va':'center', 'fontsize':9}
        # rect : [left, bottom, width, height]
        self._properties['axes_bottom'] = 0.80
        self._properties['axes_height'] = 0.10
        self._properties['axes_extent'] = [self._properties['xleft'],
                         self._properties['axes_bottom'],
                         self._properties['xright']-self._properties['xleft'], 
                         self._properties['axes_height']
        ]
        #
        self.color = None
        self.thickness = None
        self.lim = None


    def _get_line(self):
        line = self._mplot_objects.get('line')  
        if line is None:
            ax = create_and_prepare_axes(self.figure, 
                                         self._properties['axes_extent']
            )        
            line = Line2D([0.0, 1.0], [0.5, 0.5])
            self._mplot_objects['line'] = ax.add_line(line)
        return line    


    def _get_min_text(self):
        min_text = self._mplot_objects.get('min_text')
        if min_text is None:
            min_text = create_text(self.figure, '', self._properties['min'])
        return min_text

    def _get_max_text(self):
        max_text = self._mplot_objects.get('max_text')
        if max_text is None:
            max_text = create_text(self.figure, '', self._properties['max'])
        return max_text


    def set_color(self, color):
        if self.color == color:
            return
        line = self._get_line()
        line.set_color(color) 
        self.draw()
        self.color = color

    def set_thickness(self, thickness):
        if self.thickness == thickness:
            return
        line = self._get_line()
        line.set_linewidth(thickness) 
        self.draw()
        self.thickness = thickness

    def set_lim(self, lim):
        if self.lim == lim:
            return
        min_, max_ = lim
        min_ = prepare_float_value(min_)
        max_ = prepare_float_value(max_)
        #
        min_text = self._get_min_text()
        min_text.set_text(min_)
        #
        max_text = self._get_max_text()
        max_text.set_text(max_)
        #
        self.draw()             
        self.lim == lim  





class ColormapDataLabel(FigureCanvas):
    _COLOR = 'lightblue'
    
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        fig = Figure(figsize=(1, 0.20))
        super().__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        #
        self._mplot_objects = {}
        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        self._properties['min'] = {'x': self._properties['xleft'], 'y':0.33, 'ha':'left', 'va':'center', 'fontsize':9}     
        self._properties['max'] = {'x': self._properties['xright'], 'y':0.33, 'ha':'right', 'va':'center', 'fontsize':9}
        # rect : [left, bottom, width, height]
        self._properties['axes_bottom'] = 0.80
        self._properties['axes_height'] = 0.10
        self._properties['axes_extent'] = [self._properties['xleft'],
                         self._properties['axes_bottom'],
                         self._properties['xright']-self._properties['xleft'], 
                         self._properties['axes_height']
        ]
        #
        self.cmap = None
        self.lim = None


    def _start_variables(self):
        self.plottype = None
        self.left_scale = None
        self.right_scale = None  

        self.zlabel = None        
        self.zlim = None
        self.xlabel = None  


    def _get_cmap_img(self):
        cmap_img = self._mplot_objects.get('cmap_img') 
        if not cmap_img:
            extent = self._properties.get('axes_extent')
            print(extent)
            ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)
            gradient = np.linspace(0, 1, 256)
            gradient = np.vstack((gradient, gradient))
            cmap_img = ax.imshow(gradient, aspect='auto')
            self._mplot_objects['cmap_img'] = cmap_img
        return cmap_img


    def set_colormap(self, cmap):
        if self.cmap == cmap:
            return
        cmap_img = self._get_cmap_img()
        cmap_img.set_cmap(cmap)        
        self.draw()
        self.cmap = cmap 
        
        
    def _get_min_text(self):
        min_text = self._mplot_objects.get('min_text')
        if min_text is None:
            min_text = create_text(self.figure, '', self._properties['min'])
        return min_text

    def _get_max_text(self):
        max_text = self._mplot_objects.get('max_text')
        if max_text is None:
            max_text = create_text(self.figure, '', self._properties['max'])
        return max_text


    def set_lim(self, lim):
        if self.lim == lim:
            return
        min_, max_ = lim
        min_ = prepare_float_value(min_)
        max_ = prepare_float_value(max_)
        #
        min_text = self._get_min_text()
        min_text.set_text(min_)
        #
        max_text = self._get_max_text()
        max_text.set_text(max_)
        #
        self.draw()             
        self.lim == lim  






class WiggleDataLabel(FigureCanvas):
    _COLOR = 'lightblue'
    
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        fig = Figure(figsize=(1, 0.20))
        super().__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        #
        self._mplot_objects = {}
        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        self._properties['min'] = {'x': self._properties['xleft'], 'y':0.33, 'ha':'left', 'va':'center', 'fontsize':9}     
        self._properties['max'] = {'x': self._properties['xright'], 'y':0.33, 'ha':'right', 'va':'center', 'fontsize':9}
        # rect : [left, bottom, width, height]
        self._properties['axes_bottom'] = 0.80
        self._properties['axes_height'] = 0.10
        self._properties['axes_extent'] = [self._properties['xleft'],
                         self._properties['axes_bottom'],
                         self._properties['xright']-self._properties['xleft'], 
                         self._properties['axes_height']
        ]
        #
        self.cmap = None
        self.lim = None


    def _start_variables(self):
        self.plottype = None
        self.left_scale = None
        self.right_scale = None  

        self.zlabel = None        
        self.zlim = None
        self.xlabel = None  


    def _get_cmap_img(self):
        cmap_img = self._mplot_objects.get('cmap_img') 
        if not cmap_img:
            extent = self._properties.get('cmap_axes_extent')
            ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)
            gradient = np.linspace(0, 1, 256)
            gradient = np.vstack((gradient, gradient))
            cmap_img = ax.imshow(gradient, aspect='auto')
            self._mplot_objects['cmap_img'] = cmap_img
        return cmap_img

    def _get_min_text(self):
        min_text = self._mplot_objects.get('min_text')
        if min_text is None:
            min_text = create_text(self.figure, '', self._properties['min'])
        return min_text

    def _get_max_text(self):
        max_text = self._mplot_objects.get('max_text')
        if max_text is None:
            max_text = create_text(self.figure, '', self._properties['max'])
        return max_text

    def set_lim(self, lim):
        if self.lim == lim:
            return
        min_, max_ = lim
        min_ = prepare_float_value(min_)
        max_ = prepare_float_value(max_)
        #
        min_text = self._get_min_text()
        min_text.set_text(min_)
        #
        max_text = self._get_max_text()
        max_text.set_text(max_)
        #
        self.draw()             
        self.lim == lim  




class NewDataLabel(wx.Panel, SelectablePanelMixin):
    
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        #
        self.tdl = None
        self._plot_type = None
        self.create_title()
        #
        self.ldl = None
        self.cdl = None
        self.wdl = None
        #
        
        print('\n\n\nNewDataLabel.__init__:', args, kwargs)        
        if args:
            self.set_plot_type(args[0])
        print('self.tdl:', self.tdl)
        print('self.ldl:', self.ldl)
        print('self.cdl:', self.cdl)
        print('self.wdl:', self.wdl)
        print('END NewDataLabel.__init__\n\n\n')


    def _remove_all_canvas(self):
        print('\nNewDataLabel._remove_all_canvas\n')
        if self.ldl:
            self.GetSizer().Detach(self.ldl)
            self.ldl.Destroy()
        if self.cdl:
            self.GetSizer().Detach(self.cdl)
            self.cdl.Destroy()    
        if self.wdl:
            self.GetSizer().Detach(self.wdl)
            self.wdl.Destroy()    
        #    
        self.ldl = None
        self.cdl = None
        self.wdl = None  
        #
        self.redraw()


    def redraw(self):
        self.GetParent().redraw()
        
        
    def destroy(self):
        wx.CallAfter(self.GetParent().remove_object, self)

    def set_plot_type(self, plot_type):
        
        if plot_type == self._plot_type:
            return
        
        print('\n\n\nNewDataLabel.set_plot_type:', 
              self._plot_type, 
              plot_type
        )
        if self._plot_type is not None:
            self._remove_all_canvas()
        self._plot_type = plot_type
        #if plot_type == 'index':
        #    pass
        if plot_type == 'line':
            self.create_line()
        if plot_type == 'density' or plot_type == 'both':    
            self.create_colormap()
        if plot_type == 'wiggle' or plot_type == 'both':    
            self.create_wiggle()
        self.redraw()    
        print('self.tdl:', self.tdl)
        print('self.ldl:', self.ldl)
        print('self.cdl:', self.cdl)
        print('self.wdl:', self.wdl)
        print('END NewDataLabel.set_plot_type\n\n\n')


    def create_title(self):
        self.tdl = TitleDataLabel(self)
        self.GetSizer().Add(self.tdl, 0,  wx.EXPAND)
        #self.Layout()
        
    def create_line(self):
        self.ldl = LineDataLabel(self)
        self.GetSizer().Add(self.ldl, 0,  wx.EXPAND)
        #self.Layout()

    def create_colormap(self):
        self.cdl = ColormapDataLabel(self)
        self.GetSizer().Add(self.cdl, 0,  wx.EXPAND)
        #self.Layout()

    def create_wiggle(self):
        self.wdl = WiggleDataLabel(self)
        self.GetSizer().Add(self.wdl, 0,  wx.EXPAND)
        #self.Layout()        

    def set_title(self, title):
        self.tdl.set_title(title)    
            
    def set_subtitle(self, subtitle):
        self.tdl.set_subtitle(subtitle)

    def set_color(self, color):
        self.ldl.set_color(color)

    def set_thickness(self, thickness):
        self.ldl.set_thickness(thickness)

    def set_xlim(self, xlim):
        self.ldl.set_lim(xlim)

    def set_colormap(self, cmap):
        self.cdl.set_colormap(cmap)
        
    def set_colormap_lim(self, lim):
        self.cdl.set_lim(lim)



    def set_zlabel(self, z_axis_label):
        return
    
    def set_zlim(self, zlim):
        return

    def set_xlabel(self, x_axis_label):
        return

    def set_offsets(self, offsets_list):
        return




class DataLabel(FigureCanvas):
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
    
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        #fig = Figure(figsize=(1, 0.35))
        fig = Figure(figsize=(1, 0.45))
        super().__init__(self.parent, -1, fig)     
        self.figure.set_facecolor(self._COLOR)
        #
        toc_uid = kwargs.get('toc_uid')
        if toc_uid is None:
            toc_uid = args[0]  
        self._toc_uid = toc_uid 
        #
        #self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_double_click)
        self._mplot_objects = {}
        self._properties = {}
        self._start_variables()
#        self.mpl_connect('button_press_event', self._on_press)


    def destroy(self):
        wx.CallAfter(self.parent.remove_object, self)
               
        
    def _on_press(self, event):
        self.GetParent()._on_press(event)


    def _start_variables(self):
        self.title = None 
        self.plottype = None
        self.left_scale = None
        self.right_scale = None
        self.subtitle = None
        self.thickness = None
        self.color = None
        self.cmap = None
        self.xlim = None
        self.zlabel = None        
        self.zlim = None
        self.xlabel = None        


    def set_title(self, title):
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


    def set_subtitle(self, subtitle):
        if self.subtitle == subtitle: 
            return
        props = self._properties.get('sub_title', None)
        if props:
            subtitle = self._mplot_objects.get('subtitle', None)
            if not subtitle:
                subtitle = create_text(self.figure, '(' + str(subtitle) + ')', props)
                self._mplot_objects['subtitle'] = subtitle
            else:
                subtitle.set_text('(' + subtitle + ')')
            self.draw()    
            self.subtitle = subtitle   
                                
            
    def set_color(self, color):
        return
        if self.plottype == 'line':
            if self.color == color:
                return
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)                    
                line = Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
            line.set_color(color) 
            self.draw()
            self.color = color


    def set_thickness(self, thickness):
        return
    
        if self.plottype == 'line':
            if self.thickness == thickness:
                return
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)        
                line = Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
            line.set_linewidth(thickness) 
            self.draw()
            self.thickness = thickness
            
            
    def set_colormap(self, cmap):
        return
    
        if self.plottype == 'density':
            if self.cmap == cmap:
                return
            cmap_img = self._mplot_objects.get('cmap_img', None) 
            if not cmap_img:
                extent = self._properties.get('cmap_axes_extent', None)
                ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)
                gradient = np.linspace(0, 1, 256)
                gradient = np.vstack((gradient, gradient))
                cmap_img = ax.imshow(gradient, aspect='auto')
                self._mplot_objects['cmap_img'] = cmap_img
            cmap_img.set_cmap(cmap)    
            self.draw()
            self.cmap = cmap


    def set_zlabel(self, z_axis_label):
        return
    
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
        return
    
        print('label.set_xlim:', xlim)
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
        return
    
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
        return
    
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
        return
    
        if self.plottype == 'wiggle':
            line = self._mplot_objects.get('line', None)  
            if not line:
                extent = self._properties.get('line_axes_extent', None)
                if not extent:
                    raise Exception()
                ax = create_and_prepare_axes(self.figure, extent) #, toc_uid=self._toc_uid)    
                ax.set_xlim((0, len(offsets_list)+1))
                ax.set_ylim((-1.0, 1.0))
                line = Line2D([0.0, 1.0], [0.5, 0.5])
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
        if plottype == self.plottype:
            return
        if plottype not in VALID_PLOT_TYPES:
            return

        self._remove_all_artists()

        self._start_variables()   

        self._properties = {}
        self._properties['xleft'] = 0.05
        self._properties['xright'] = 0.95
        #
        self._properties['title'] = {'x': 0.5, 'y':0.64, 'ha':'center', 'fontsize':9}
        self._properties['sub_title'] = {'x': 0.5, 'y':0.19, 'ha':'center', 'fontsize':9}       
        #
        self.plottype = plottype 
        
        return
        
    
        if plottype == 'line':
#            self._properties['title'] = {'x': 0.5, 'y':0.64, 
#                            'ha':'center', 'fontsize':10
#            }
            self._properties['sub_title'] = {'x': 0.5, 'y':0.19, 
                            'ha':'center', 'fontsize':9
            }        
            self._properties['xmin'] = {'x': self._properties['xleft'],
                             'y':0.33, 'ha':'left', 'va':'center', 
                             'fontsize':9
            }     
            self._properties['xmax'] = {'x': self._properties['xright'],
                             'y':0.33, 'ha':'right', 'va':'center', 
                             'fontsize':9
            }
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.05, 
                        self._properties['xright']-self._properties['xleft'],
                        0.15
            ]
            
            
        elif plottype == 'density':
            #
#            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
#                                                                'fontsize':10}            
            self._properties['cmap_axes_extent'] = [self._properties['xleft'],
                        0.10, 
                        self._properties['xright']-self._properties['xleft'],
                        0.22
            ]
            #
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
            #
            ypos = 0.18
            self._properties['xlabel'] = {'x': 0.5, 'y':ypos, 'ha':'center', 
                                                'va':'center', 'fontsize':10}   
            self._properties['xmin'] = {'x':self._properties['xleft'],
                         'y':ypos, 'ha':'left', 'va':'center', 'fontsize':9
            }
            self._properties['xmax'] = {'x': self._properties['xright'],
                        'y':ypos, 'ha':'right', 'va':'center', 'fontsize':9
            }                
            #
            self._properties['line_axes_extent'] = [self._properties['xleft'],
                        0.0, 
                        self._properties['xright']-self._properties['xleft'],
                        0.2
            ]

                  
            
        elif plottype == 'wiggle':  
#            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
#                                                                'fontsize':10}   
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
#            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
#                                                                'fontsize':10}            
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
        elif plottype == 'index':
#            self._properties['title'] = {'x': 0.5, 'y':0.55, 'ha':'center', 
#                                                                'fontsize':10}
            self._properties['sub_title'] = {'x': 0.5, 'y':0.2, 'ha':'center', 
                                                                'fontsize':9}
                                                                              
                                                               







###############################################################################
###############################################################################


class TrackLabelController(UIControllerObject):
    tid = 'track_label_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['title'] = {
            'default_value': None,
            'type': str      
    }
    _ATTRIBUTES['title_bgcolor'] = {
            'default_value': 'LightSteelBlue', # '#B0C4DE'
            'type': str
    }
    _ATTRIBUTES['title_fontsize'] = {
            'default_value': 10,
            'type': int
    } 
    _ATTRIBUTES['selected'] = {
            'default_value': False,
            'type': bool
    }    
    _ATTRIBUTES['plottype'] = {
            'default_value': 'line', 
            'type': str
    }    
    def __init__(self):
        super().__init__()
        


class TrackLabel(UIViewObject, wx.Panel, SelectablePanelMixin):  
    tid = 'track_label'
       
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self._controller_uid)
        parent_controller = UIM.get(parent_uid)        
        wx_parent = parent_controller._get_wx_parent(self.tid)
        wx.Panel.__init__(self, wx_parent)
        #
        self.track_view_object = wx_parent
        self._visual_objects = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))  
        #
        self.Bind(wx.EVT_LEFT_DOWN, self._on_button_press)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_button_press)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_button_press)
        #


    def PostInit(self):
        self.create_title()
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        controller.subscribe(self._on_change_title, 'change.title')    
        controller.subscribe(self._on_change_title, 'change.title_bgcolor') 
        controller.subscribe(self._on_change_title, 'change.title_fontsize') 
#        controller.subscribe(self._on_change_selected, 'change.selected') 

    def _on_change_title(self, new_value, old_value):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        self._title.update(controller.title, controller.title_bgcolor, 
                           controller.title_fontsize
        ) 
        self.Layout()         


    def create_title(self):
        self._title = TrackTitleCanvas(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)
                        
    def create_data_label(self):
        self._title = TrackTitleCanvas(self)
        self.GetSizer().Add(self._title, 0,  wx.EXPAND)


# TrackObjectController labels                 
    def append_object(self, *args, **kwargs):
        return self.insert_object(len(self._visual_objects), *args, **kwargs)
        
    def insert_object(self, pos, *args, **kwargs):
        """
        Insert a new visual object at given pos with properties informed.
        """
        dl = NewDataLabel(self, *args, **kwargs)
        self._visual_objects.insert(pos, dl)
        self.GetSizer().Add(dl, 0,  wx.EXPAND)
        self.Layout()
        return dl
    
    def remove_object(self, *args):
        """
        Removes the track is a given position. 
        """
        if not args[0]:
            return
        if isinstance(args[0], int):    
            vdl = self._visual_objects.pop(args[0])
        elif isinstance(args[0], NewDataLabel):   
            vdl = args[0]
            self._visual_objects.remove(vdl)
        else:
            raise Exception()            
        self.GetSizer().Detach(vdl)
        vdl.Destroy()
        self.Layout()  


    def redraw(self):
        self.Layout()

    def set_plot_type(self, plot_type):
        self._dl.set_plot_type(plot_type)
        self.Layout()
        
        
# Events         
    def _on_button_press(self, event):
        
        return
        
        UIM = UIManager()
        track_controller_uid = UIM._getparentuid(self._controller_uid)
        track_controller = UIM.get(track_controller_uid)
        track_controller._on_button_press(event)
        
        #self.track_view_object.process_event(event)

        """
        if isinstance(event, wx.MouseEvent):        
            gui_evt = event
        else:
            gui_evt = event.guiEvent
            print (gui_evt)
            
        if gui_evt.GetEventObject() and gui_evt.GetEventObject().HasCapture():            
            gui_evt.GetEventObject().ReleaseMouse()  
        #  
        """
       
    
        """
        gui_evt = event
        if event.button == 3: 
            if isinstance(gui_evt.GetEventObject(), DataLabel):    
                visdl = gui_evt.GetEventObject()
                menu = wx.Menu()    
                id_ = wx.NewId() 
                menu.Append(id_, 'Remove from track')
                event.canvas.Bind(wx.EVT_MENU, lambda event: self._remove_object_helper((visdl._toc_uid)), id=id_)    
                event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
                menu.Destroy() # destroy to avoid mem leak
            #
        """    




        