# -*- coding: utf-8 -*-

import numpy as np

import wx

from matplotlib.colorbar import ColorbarBase
from matplotlib import style as mstyle 
from matplotlib import axis
from matplotlib import rcParams

from ui.mvc_classes.workpage import WorkPageController
from ui.mvc_classes.workpage import WorkPageModel
from ui.mvc_classes.workpage import WorkPage

from ui.plotstatusbar import PlotStatusBar

from ui.uimanager import UIManager
from app import log

from app.app_utils import GripyBitmap  


#from ui.mvc_classes.mpl_base import PlotFigureCanvas




CP_NORMAL_TOOL = wx.NewId()        
CP_SELECTION_TOOL = wx.NewId()   


CP_FLOAT_PANEL = wx.NewId()  



class CrossPlotController(WorkPageController):
    tid = 'crossplot_controller'
    
    def __init__(self):
        super().__init__()

        
        

class CrossPlotModel(WorkPageModel):
    tid = 'crossplot_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        }             
    }    
        
    """    
        xlim=xlim, ylim=ylim, x_scale=x_scale, scale_lines=10, 
                     y_scale=y_scale,
                     x_label= 'X axis', y_label= 'Y axis', title='Title' 
    )
    """
    
    def __init__(self, controller_uid, **base_state):   
        super().__init__(controller_uid, **base_state)   

        
        
        
        
    
class CrossPlot(WorkPage):
    tid = 'crossplot'
    _FRIENDLY_NAME = 'Cross Plot'


    def __init__(self, controller_uid):   
        super().__init__(controller_uid) 

  
    def PostInit(self):
#        print ('CrossPlot.PostInit')

        try:

            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self._tool_bar =  wx.aui.AuiToolBar(self)
            self.sizer.Add(self._tool_bar, 0, flag=wx.TOP|wx.EXPAND)
            #     
            UIM = UIManager()   
            canvas_controller = UIM.create('canvas_controller', 
                    self._controller_uid
            )
#                    x_scale=x_scale, scale_lines=10, y_scale=y_scale,
#                    x_label= 'X axis', y_label= 'Y axis', title='Titulo do Cross Plot'
#            )
            self._main_panel = canvas_controller.view
            self.sizer.Add(self._main_panel, 1, flag=wx.EXPAND)
            #
            self._status_bar =  PlotStatusBar(self)
            self.sizer.Add(self._status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)
            self.SetSizer(self.sizer)   
            #
            self._build_tool_bar()
            self.Layout()
    

        except Exception as e:
            print ('ERROR IN CrossPlot.PostInit:', e)
            raise


    def PreDelete(self):
        try:
            self.sizer.Remove(0)
            del self._tool_bar
        except Exception as e:
            msg = 'PreDelete ' + self.__class__.__name__ + \
                                            ' ended with error: ' + str(e)
            print (msg)                                
            pass       


    def _on_change_tool(self, event):
        print 
        if event.GetId() == CP_NORMAL_TOOL:
            print ('CP_NORMAL_TOOL')
        elif event.GetId() == CP_SELECTION_TOOL:  
            print ('CP_SELECTION_TOOL')



    def _on_change_float_panel(self, event):
        # TODO: Integrar binds de toggle buttons...
        if event.GetId() == CP_FLOAT_PANEL:
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            controller.model.float_mode = event.IsChecked()            


    def _build_tool_bar(self):

        self.fp_item = self._tool_bar.AddTool(CP_FLOAT_PANEL, 
                      wx.EmptyString,
                      GripyBitmap('restore_window-25.png'), 
                      wx.NullBitmap,
                      wx.ITEM_CHECK,
                      'Float Panel', 
                      'Float Panel',
                      None
        )
        self._tool_bar.ToggleTool(CP_FLOAT_PANEL, False)
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_float_panel, None,
                  CP_FLOAT_PANEL
        )        
        self._tool_bar.AddSeparator()
        
        #
        self._tool_bar.AddTool(CP_NORMAL_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self._tool_bar.ToggleTool(CP_NORMAL_TOOL, True) 
        #
        self._tool_bar.AddTool(CP_SELECTION_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_tool, None,
                  CP_NORMAL_TOOL, CP_SELECTION_TOOL
        )
        #
        self._tool_bar.AddSeparator()
        
        '''
        lib = mstyle.library
        for k, values in lib.items():
            print ('\n\nSTYLE: {}'.format(k))
            
            for key, value in values.items():
                print ('{}: {}'.format(key, value))
        '''        
   

        '''
        print ('\n')
            
        for key, value in rcParams.items():
#            for k in ['grid.', 'axes.', 'figure.', 'xtick.', 'ytick.']:
#                if key.startswith(k):
            if key not in mstyle.core.STYLE_BLACKLIST:
                print ('{}: {}'.format(key, value))

        print ('\n')
        '''
        
        
        #print ('axis._gridline_param_names:', axis._gridline_param_names)

        self._tool_bar.label_MC = wx.StaticText(self._tool_bar, 
                                                label='MPL Theme:  '
        )
        #self._tool_bar.label_MC.SetLabel('Multi cursor:')
        self._tool_bar.AddControl(self._tool_bar.label_MC, '')

        
        styles = ['default'] + mstyle.available[:]
        self._tool_bar.choice_Style = wx.Choice(self._tool_bar, choices=styles)
        self._tool_bar.choice_Style.SetSelection(0)
        #
        #controller = UIM.get(self._controller_uid)
        #idx_index_type = ['MD', 'TVD', 'TVDSS', 'TWT', 'TIME'].index(controller.model.index_type)
        #self._tool_bar.choice_IT.SetSelection(idx_index_type)
        self._tool_bar.choice_Style.Bind(wx.EVT_CHOICE , self._on_choice_style) 
        self._tool_bar.AddControl(self._tool_bar.choice_Style, '')
        
        self._tool_bar.AddSeparator()
        
        self._tool_bar.Realize()  


    
    def set_own_name(self):
        UIM = UIManager()   
        controller = UIM.get(self._controller_uid)
        idx = 0
        lpcs = UIM.list('crossplot_controller')
        for lpc in lpcs:
            idx += 1
        controller.model.title = self._FRIENDLY_NAME + ' ['+ str(idx) + ']'    
        



    def _on_choice_style(self, event):
        
        lib_name = event.GetString()
        print ('\n\nLoading Style:', lib_name)

        UIM = UIManager()  
        cc = UIM.list('canvas_controller', self._controller_uid)[0]
        cc.load_style(lib_name)



                
            
       


class CrossPlotPanel(wx.Panel):
    
    HORIZONTALMARGIN = 0#.01
    VERTICALMARGIN = 0#.02
    
    HORIZONTALPAD = 0#.005
    #VERTICALPAD = 0#.01
    VERTICALPAD = 0.03
    #
    #YLABELWIDTH = 0.02
    YLABELWIDTH = 0.1
    COLORBARWIDTH = 0.01
    #ZLABELWIDTH = 0.03
    ZLABELWIDTH = 0.1
    #XLABELHEIGHT = 0.03
    XLABELHEIGHT = 0.06
    
    MAIN_AXES_WIDTH = 1.0 - (2*HORIZONTALMARGIN + 3*HORIZONTALPAD + \
                                    YLABELWIDTH + COLORBARWIDTH + ZLABELWIDTH)
    MAIN_AXES_HEIGHT = 1.0 - (2*VERTICALMARGIN + VERTICALPAD + XLABELHEIGHT)
    
    #MAIN_AXES_BOTTOM = VERTICALMARGIN + XLABELHEIGHT + VERTICALPAD
    MAIN_AXES_BOTTOM = VERTICALMARGIN + XLABELHEIGHT
    MAIN_AXES_LEFT = HORIZONTALMARGIN + YLABELWIDTH + HORIZONTALPAD
    
    XLABELBOTTOM = VERTICALMARGIN
    
    YLABELLEFT = HORIZONTALMARGIN
    ZLABELLEFT = 1.0 - HORIZONTALMARGIN - ZLABELWIDTH
    COLORBARLEFT = ZLABELLEFT - HORIZONTALPAD - COLORBARWIDTH
    
    #TEXTFONTSIZE = 'medium'
    #NUMBERFONTSIZE = 'small'
    
    TEXTFONTSIZE = 14
    NUMBERFONTSIZE = 11
    
    #XLABELTEXTBOTTOM = 0.1
    XLABELTEXTBOTTOM = 0.1
    #XLABELTEXTTOP = 0.9
    XLABELTEXTTOP = 0.8
    #XLABELTEXTHMARGIN = 0.001
    XLABELTEXTHMARGIN = 0.005
    
    #YLABELTEXTLEFT = 0.1
    YLABELTEXTLEFT = 0.8
    #YLABELTEXTRIGHT = 0.9
    YLABELTEXTRIGHT = 0.9
    #YLABELTEXTVMARGIN = 0.002
    YLABELTEXTVMARGIN = 0.009
    
    ZLABELTEXTLEFT = 0.1
    #ZLABELTEXTLEFT = 0.3
    #ZLABELTEXTRIGHT = 0.9
    ZLABELTEXTRIGHT = 0.8
    
    
    
    def __init__(self, *args):
        
        
        super().__init__(args[0])
        
        
#        self.figure = Figure()
#        self.canvas = FigureCanvas(self, -1, self.figure)
        
        
#        self.SetBackgroundColour('green')
#        self.canvas.SetBackgroundColour('blue')    

        """
        super().__init__(wx_parent, 
                 track_view_object, size, **base_axes_properties
            )
        
        TrackFigureCanvas(self, None, size=wx.Size(300, 300),
                                y_major_grid_lines=controller.model.y_major_grid_lines,
                                y_minor_grid_lines=controller.model.y_minor_grid_lines,
                                **track.model._getstate()
        )        
        """
        
        """

        rect = [self.MAIN_AXES_LEFT, self.MAIN_AXES_BOTTOM, 
                self.MAIN_AXES_WIDTH, self.MAIN_AXES_HEIGHT
        ]
        
        """
        _MAIN_AXES_LEFT_RIGHT_SPACE = 0.1
        _MAIN_AXES_LEFT_BOTTOM_UP = 0.1
        
        
        rect = [_MAIN_AXES_LEFT_RIGHT_SPACE, _MAIN_AXES_LEFT_BOTTOM_UP,
                1.0-2*_MAIN_AXES_LEFT_RIGHT_SPACE,
                1.0-2*_MAIN_AXES_LEFT_BOTTOM_UP
        ]
#        """
        props = {#'y_major_grid_lines': 500.0, 'y_minor_grid_lines': 100.0, 
                 'pos': 0, 'label': '', 'plotgrid': True, 'x_scale': 0, 
                 'overview': False, 'depth_lines': 0, 'width': 160, 
                 'minorgrid': True, 'leftscale': 0.2, 'decades': 4, 
                 'scale_lines': 5, 'selected': False, 
                 'visible': True, 'name': '', 
                 'rect': rect, 'xlim': (0.0, 1.0), 'ylim': (0.0, 1.0),
                 'y_plotgrid': True, 'y_minorgrid': True,
                 'y_scale_lines': 5
        }
        
        UIM = UIManager()
        
        center_panel = self.GetParent()
        workpage = center_panel.GetParent()
        controller = UIM.get(workpage._controller_uid)
        
#        print ('\n\ncontroller.model._props:', controller.model._props)


        self.xlabel_ax = None
        self.ylabel_ax = None
        
        x_label = controller.model._props.pop('x_label', None)
        y_label = controller.model._props.pop('y_label', None)            
        title = controller.model._props.pop('title', None)

        for key, value in controller.model._props.items():
            props[key] = value
        
        self.canvas = PlotFigureCanvas(self, None, size=wx.Size(300, 300), 
                                       share_x=True, **props
        )
        
        self.canvas.base_axes.spines['right'].set_visible(True)
        self.canvas.base_axes.spines['left'].set_visible(True)
        self.canvas.base_axes.spines['bottom'].set_visible(True)
        self.canvas.base_axes.spines['top'].set_visible(True)
        
        
        self._COLOR = 'ivory' #'whitesmoke'#'lightyellow'
        #'aliceblue'#'paleturquoise' #'lightblue' #'white'
        
        if x_label is not None:
            self.set_xlabel(x_label)
        if y_label is not None:
            self.set_ylabel(y_label)

        if self._COLOR:
            self.canvas.figure.set_facecolor(self._COLOR)
            
        if title is not None:    
            self.canvas.figure.suptitle(title, y=0.95, fontsize=16)    

        '''
        self.crossplot_ax.xaxis.set_major_locator(MaxNLocator(5))
        self.crossplot_ax.xaxis.set_major_formatter(NullFormatter())
        self.crossplot_ax.yaxis.set_major_locator(MaxNLocator(5))
        self.crossplot_ax.yaxis.set_major_formatter(NullFormatter())
        self.crossplot_ax.grid(axis='x', which='major', linestyle='-.')
        self.crossplot_ax.grid(axis='y', which='major', linestyle='-.')        
        '''
        
        """
        
        self.cmap = colors.COLOR_MAP_RAINBOW
        self.colorbar = None
        self.collections = []
        self.xdata = None
        self.ydata = None
        self.zdata = None
        self.xlabel = ''
        self.ylabel = ''
        self.zlabel = ''
        self.xlocator = MaxNLocator(6).tick_values
        self.ylocator = MaxNLocator(6).tick_values
        self.zlocator = MaxNLocator(6).tick_values
        self.xlim = None
        self.ylim = None
        self.zlim = None
        self.zmode = 'continuous'
        self.classnames = {}
        self.classcolors = {}
        self.nullclass = np.nan
        self.parts = None
        self.shownparts = []
        
        
        #
        #
        rect = [self.MAIN_AXES_LEFT, self.MAIN_AXES_BOTTOM, self.MAIN_AXES_WIDTH, self.MAIN_AXES_HEIGHT]
        self.crossplot_ax = self.figure.add_axes(rect)
        self.crossplot_ax.xaxis.set_major_locator(MaxNLocator(5))
        self.crossplot_ax.xaxis.set_major_formatter(NullFormatter())
        self.crossplot_ax.yaxis.set_major_locator(MaxNLocator(5))
        self.crossplot_ax.yaxis.set_major_formatter(NullFormatter())
        self.crossplot_ax.grid(axis='x', which='major', linestyle='-.')
        self.crossplot_ax.grid(axis='y', which='major', linestyle='-.')
        #        

        self.zlabel_ax = None
        
        #self.colorbar_ax.yaxis.set_major_formatter(NullFormatter())
        self.collectionproperties = dict(linewidths=0.5, s=30)
        
        """
        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        
        #self.canvas.mpl_connect('button_press_event', self.on_press)
        #self.canvas.mpl_connect('motion_notify_event', self.on_move)
    
    
    def create_xlabel(self):
        rect = [0.1, 0.03, 0.8, 0.04]
        #
        self.xlabel_ax = self.canvas.figure.add_axes(rect)
        self.xlabel_ax.xaxis.set_major_locator(NullLocator())
        self.xlabel_ax.yaxis.set_major_locator(NullLocator())
        #
        self.xlabel_ax.text(0.5, self.XLABELTEXTBOTTOM, '', ha='center', va='bottom', fontsize=self.TEXTFONTSIZE)
        self.xlabel_ax.text(self.XLABELTEXTHMARGIN, self.XLABELTEXTTOP, '', ha='left', va='top', fontsize=self.NUMBERFONTSIZE)
        self.xlabel_ax.text(1.0 - self.XLABELTEXTHMARGIN, self.XLABELTEXTTOP, '', ha='right', va='top', fontsize=self.NUMBERFONTSIZE)
        #
        self.xlabel_ax.set_xlim(0.0, 1.0)
        self.xlabel_ax.set_ylim(0.0, 1.0)
        #
        self.xlabel_ax.spines['right'].set_visible(False)
        self.xlabel_ax.spines['top'].set_visible(False)
        self.xlabel_ax.spines['left'].set_visible(False)
        self.xlabel_ax.spines['bottom'].set_visible(False)
        #
        if self._COLOR:
            self.xlabel_ax.set_facecolor(self._COLOR)
        
    """   
    def create_xlabel(self):
        rect = [self.MAIN_AXES_LEFT, self.XLABELBOTTOM, 
                                    self.MAIN_AXES_WIDTH, self.XLABELHEIGHT]
        self.xlabel_ax = self.figure.add_axes(rect)
        self.xlabel_ax.xaxis.set_major_locator(NullLocator())
        self.xlabel_ax.yaxis.set_major_locator(NullLocator())
        #
        self.xlabel_ax.text(0.5, self.XLABELTEXTBOTTOM, '', ha='center', va='bottom', fontsize=self.TEXTFONTSIZE)
        self.xlabel_ax.text(self.XLABELTEXTHMARGIN, self.XLABELTEXTTOP, '', ha='left', va='top', fontsize=self.NUMBERFONTSIZE)
        self.xlabel_ax.text(1.0 - self.XLABELTEXTHMARGIN, self.XLABELTEXTTOP, '', ha='right', va='top', fontsize=self.NUMBERFONTSIZE)
        #
        self.xlabel_ax.set_xlim(0.0, 1.0)
        self.xlabel_ax.set_ylim(0.0, 1.0)   
    """
    
    def create_ylabel(self):
        rect = [0.01, 0.1, 0.04, 0.8]
        #        
        self.ylabel_ax = self.canvas.figure.add_axes(rect)
        self.ylabel_ax.xaxis.set_major_locator(NullLocator())
        self.ylabel_ax.yaxis.set_major_locator(NullLocator())
        #
        self.ylabel_ax.text(self.YLABELTEXTLEFT, 0.5, '', ha='left', va='center', fontsize=self.TEXTFONTSIZE, rotation=90)
        self.ylabel_ax.text(self.YLABELTEXTRIGHT, self.YLABELTEXTVMARGIN, '', ha='right', va='bottom', fontsize=self.NUMBERFONTSIZE)
        self.ylabel_ax.text(self.YLABELTEXTRIGHT, 1.0 - self.YLABELTEXTVMARGIN, '', ha='right', va='top', fontsize=self.NUMBERFONTSIZE)
        #
        self.ylabel_ax.set_xlim(0.0, 1.0)
        self.ylabel_ax.set_ylim(0.0, 1.0)
        #
        self.ylabel_ax.spines['right'].set_visible(False)
        self.ylabel_ax.spines['top'].set_visible(False)
        self.ylabel_ax.spines['left'].set_visible(False)
        self.ylabel_ax.spines['bottom'].set_visible(False) 
        #
        if self._COLOR:
            self.ylabel_ax.set_facecolor(self._COLOR)    
            
    """    
    def create_ylabel(self):
        rect = [self.YLABELLEFT, self.MAIN_AXES_BOTTOM, self.YLABELWIDTH, self.MAIN_AXES_HEIGHT]
        self.ylabel_ax = self.figure.add_axes(rect)
        self.ylabel_ax.xaxis.set_major_locator(NullLocator())
        self.ylabel_ax.yaxis.set_major_locator(NullLocator())
        #
        self.ylabel_ax.text(self.YLABELTEXTLEFT, 0.5, '', ha='left', va='center', fontsize=self.TEXTFONTSIZE, rotation=90)
        self.ylabel_ax.text(self.YLABELTEXTRIGHT, self.YLABELTEXTVMARGIN, '', ha='right', va='bottom', fontsize=self.NUMBERFONTSIZE)
        self.ylabel_ax.text(self.YLABELTEXTRIGHT, 1.0 - self.YLABELTEXTVMARGIN, '', ha='right', va='top', fontsize=self.NUMBERFONTSIZE)
        #
        self.ylabel_ax.set_xlim(0.0, 1.0)
        self.ylabel_ax.set_ylim(0.0, 1.0)    
    """
    
    def create_zlabel(self):
        rect = [self.ZLABELLEFT, self.MAIN_AXES_BOTTOM, self.ZLABELWIDTH, self.MAIN_AXES_HEIGHT]
        self.zlabel_ax = self.figure.add_axes(rect)
        self.clear_zlabel()
        #
        rect = [self.COLORBARLEFT, self.MAIN_AXES_BOTTOM, self.COLORBARWIDTH, self.MAIN_AXES_HEIGHT]
        self.colorbar_ax = self.figure.add_axes(rect, sharey=self.zlabel_ax)
        #
    
    def clear_zlabel(self):
        self.zlabel_ax.clear()
        self.zlabel_ax.xaxis.set_major_locator(NullLocator())
        self.zlabel_ax.yaxis.set_major_locator(NullLocator())
        self.zlabel_ax.text(self.ZLABELTEXTRIGHT, 0.5, self.zlabel, ha='right', va='center', fontsize=self.TEXTFONTSIZE, rotation=270)
        self.zlabel_ax.set_xlim(0.0, 1.0)
        self.zlabel_ax.set_ylim(0.0, 1.0)



    def set_xdata(self, xdata):
        self.xdata = xdata


    def set_xlabel(self, xlabel):
        if self.xlabel_ax is None:
            self.create_xlabel()
        self.xlabel_ax.texts[0].set_text(xlabel)
        self.xlabel = xlabel

    
    """
    def set_xlabel(self, xlabel):
        if self.xlabel_ax is None:
            self.create_xlabel()
        self.xlabel_ax.texts[0].set_text(xlabel)
        self.xlabel = xlabel
    """    
    
    def set_xlim(self, xlim):
        if self.xlabel_ax is None:
            self.create_xlabel()
        #self.xlabel_ax.texts[1].set_text("{:g}".format(xlim[0]))
        #self.xlabel_ax.texts[2].set_text("{:g}".format(xlim[1]))
        self.xlabel_ax.texts[1].set_text("{:4.2f}".format(xlim[0]))
        self.xlabel_ax.texts[2].set_text("{:4.2f}".format(xlim[1]))
        self.crossplot_ax.set_xlim(xlim)
        self.xlim = xlim
        #self.draw()    
    
    def set_ydata(self, ydata):
        self.ydata = ydata

    def set_ylabel(self, ylabel):
        if self.ylabel_ax is None:
            self.create_ylabel()
        self.ylabel_ax.texts[0].set_text(ylabel)
        self.ylabel = ylabel
        
    """    
    def set_ylim(self, ylim):
        if self.ylabel_ax is None:
            self.create_ylabel()     
      
        #self.ylabel_ax.texts[1].set_text("{:g}".format(ylim[0]))
        #self.ylabel_ax.texts[2].set_text("{:g}".format(ylim[1]))
        self.ylabel_ax.texts[1].set_text("{:4.2f}".format(ylim[0]))
        self.ylabel_ax.texts[2].set_text("{:4.2f}".format(ylim[1]))
        self.crossplot_ax.set_ylim(ylim)
        self.ylim = ylim
        #self.draw()    
    """
    
    def set_zdata(self, zdata):
        self.zdata = zdata

    def set_zlabel(self, zlabel):
        if self.zlabel_ax is None:
            self.create_zlabel()    
        self.zlabel_ax.texts[0].set_text(zlabel)
        self.zlabel = zlabel
    
    def set_zlim(self, zlim):
        self.zlim = zlim    
    
    def set_zmode(self, zmode):
        self.zmode = zmode    
    
    def set_xlocator(self, xlocator):
        self.xlocator = xlocator
     
    def set_ylocator(self, ylocator):
        self.ylocator = ylocator
     
    def set_zlocator(self, zlocator):
        self.zlocator = zlocator
    
    
    def set_classnames(self, classnames):
        self.classnames = classnames
    
    def set_classcolors(self, classcolors):
        self.classcolors = classcolors
    
    def set_nullclass(self, nullclass):
        self.nullclass = nullclass
    
    def set_nullcolor(self, nullcolor):
        self.nullcolor = nullcolor
    
    
    def set_parts(self, parts):
        self.parts = parts
        if self.parts is not None:
            self.shownparts = [True for a in self.parts]
    
    def show_part(self, i, show=True):
        self.shownparts[i] = show



    def plot(self):
        #print '\nCrossPlotPanel.plot'
        #print 'zmode:', self.zmode
        
        if self.zmode == 'classes':
            self._plot_zclasses()
            self.clear_zlabel()
            for tick in self.zticks:
                y = (tick - self.zlim[0])/(self.zlim[1] - self.zlim[0])
                classname = self.classnames[self.classes[tick]]
                self.zlabel_ax.text(self.ZLABELTEXTLEFT, y, classname, ha='left', va='center', fontsize=self.TEXTFONTSIZE, rotation=270)
                
        elif self.zmode == 'continuous':
            self._plot_zcontinuous()
            try:
                self.clear_zlabel()
                if self.zticks is not None:
                    for tick in self.zticks:
                        y = (tick - self.zlim[0])/(self.zlim[1] - self.zlim[0])
                        #print "{:g}".format(tick)
                        self.zlabel_ax.text(self.ZLABELTEXTLEFT, y, 
                                "{:g}".format(tick), ha='left', va='center', 
                                fontsize=self.NUMBERFONTSIZE
                        )
            except:
                pass
        else:
            self._plot_zsolid()
            self.clear_zlabel()
            
        #for collection, toshow in zip(self.collections, self.shownparts):
        #    collection.set_visible(toshow)
    

#        



    def _plot_zcontinuous(self):
#        print '\n\nCrossPlotPanel._plot_zcontinuous'
#        print 'self.parts:', self.parts
        if self.parts is None:
#            print 111
            parts = [np.ones_like(self.xdata, dtype=bool)]
        else:
#            print 222
            parts = self.parts
#        print    
#        print 'parts:', parts, len(parts)

        print ('\nself.xdata:', self.xdata, len(self.xdata))
        print ('self.ydata:', self.ydata, len(self.ydata))
        print
        
        good = np.sum(parts, axis=0, dtype=bool)
#        print 'good1:', good, len(good)
        good *= np.isfinite(self.xdata)
#        print 'good2:', good, len(good)
        good *= np.isfinite(self.ydata)
#        print 'good3:', good, len(good)
#        print
#        print 
        
        
        if self.zdata is not None:
#            print 'zdata Not None'
            good *= np.isfinite(self.zdata)  # TODO: Sem essa linha, onde não houver perfil z será plotado de ?preto? 
            zticks = self.zlocator(np.min(self.zdata[good]), np.max(self.zdata[good]))
            self.zlim = [zticks[0], zticks[-1]]
            self.zticks = zticks[1:-1]
            norm = Normalize(*self.zlim)
        else:
#            print 'zdata is None'
            self.zlim = None
            self.zticks = None
        
        """    
        print 
        print 'self.zdata:', self.zdata
            
        zticks = self.zlocator(np.min(self.zdata[good]), np.max(self.zdata[good]))
        self.zlim = [zticks[0], zticks[-1]]
        self.zticks = zticks[1:-1]
        
        norm = Normalize(*self.zlim)
        """
        #
        for part in parts:
            x = self.xdata[part*good]
            y = self.ydata[part*good]
            
            if self.zdata is None:
                #
                colors = ['blue', 'red', 'green', 'magenta', 'Teal', 
                          'Lime', 'Aqua', 'Yellow', 'Gray', 'Salmon']
                color = colors[len(self.collections)]
                #
                collection = self.crossplot_ax.plot(x, y, color=color)
                #
                if len(self.collections) == 0:
                    zero_line = np.zeros((len(x), ))
                    self.crossplot_ax.plot(x, zero_line, color='black')
            else:    
                c = self.zdata[part*good]
                collection = self.crossplot_ax.scatter(x, y, c=c, cmap=self.cmap, 
                                       norm=norm, zorder=-len(x), 
                                       **self.collectionproperties
                )
                
            #
            #print 'self.collectionproperties:', self.collectionproperties
            #
            """
            collection = self.crossplot_ax.scatter(x, y, c=c, cmap=self.cmap, 
                                                   norm=norm, zorder=-len(x), 
                                                   **self.collectionproperties
            )
            """
            #collection = self.crossplot_ax.plot(x, y)
            self.collections.append(collection)
        #  
        
        """
        xticks = self.xlocator(np.min(self.xdata[good]), np.max(self.xdata[good]))
        self.set_xlim([xticks[0], xticks[-1]])
        
        yticks = self.ylocator(np.min(self.ydata[good]), np.max(self.ydata[good]))
        self.set_ylim([yticks[0], yticks[-1]])
        """

#        print 'xlim:', xticks[0], xticks[-1]
#        print 'ylim:', yticks[0], yticks[-1]

#        print 'self.zticks:', self.zticks

        #"""
        if self.zticks is not None:
            self.colorbar = ColorbarBase(self.colorbar_ax, cmap=self.cmap, norm=norm, ticks=self.zticks)
            

    
    def draw(self):
        self.canvas.draw()
        

