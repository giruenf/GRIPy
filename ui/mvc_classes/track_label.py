# -*- coding: utf-8 -*-

import wx

from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 


from app import log

import numpy as np

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator


from ui.mvc_classes.extras import SelectablePanelMixin



# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40
VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']


# TODO: Parametros: levar para App.utils ou Parameters.manager
DEFAULT_LABEL_BG_COLOR  = '#B0C4DE' #LightSteelBlue  
SELECTION_WIDTH = 2
SELECTION_COLOR = 'green'









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
        l = Line2D([0.0, 1.0], [0.05, 0.05])
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


    def set_object_uid(self, object_uid):
        self._obj_uid = object_uid 


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
                line = Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
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
                line = Line2D([0.0, 1.0], [0.5, 0.5])
                self._mplot_objects['line'] = ax.add_line(line)
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
        
        
        if plottype == 'line':
            self._properties['title'] = {'x': 0.5, 'y':0.64, 
                            'ha':'center', 'fontsize':10
            }
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







class TrackLabelController(UIControllerObject):
    tid = 'track_label_controller'
    
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
        self._title = None
        self._visual_objects = []
        self.SetBackgroundColour('white')
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))  
        #
        self.Bind(wx.EVT_LEFT_DOWN, self._on_button_press)
        self.Bind(wx.EVT_MIDDLE_DOWN, self._on_button_press)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_button_press)
        #
        self._selected = False



    def _on_button_press(self, event):
        
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
            if isinstance(gui_evt.GetEventObject(), VisDataLabel):    
                visdl = gui_evt.GetEventObject()
                menu = wx.Menu()    
                id_ = wx.NewId() 
                menu.Append(id_, 'Remove from track')
                event.canvas.Bind(wx.EVT_MENU, lambda event: self._remove_object_helper((visdl._obj_uid)), id=id_)    
                event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
                menu.Destroy() # destroy to avoid mem leak
            #
        """    





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