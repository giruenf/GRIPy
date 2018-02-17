# -*- coding: utf-8 -*-
import wx

from workpage import WorkPageController
from workpage import WorkPageModel
from workpage import WorkPage

from App import log
from UI.uimanager import UIManager

# From Vis.Crossplot
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, NullLocator, NullFormatter
from matplotlib.colorbar import ColorbarBase
from matplotlib.colors import NoNorm, ListedColormap, Normalize

import numpy as np
from scipy import stats

from Basic import Colors
#




class CrossPlotController(WorkPageController):
    tid = 'crossplot_controller'
    
    def __init__(self):
        super(CrossPlotController, self).__init__()



class CrossPlotModel(WorkPageModel):
    tid = 'crossplot_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 
                'type': int
        }             
    }    
    _ATTRIBUTES.update(WorkPageModel._ATTRIBUTES)   
    
    def __init__(self, controller_uid, **base_state):   
        super(CrossPlotModel, self).__init__(controller_uid, **base_state)   
        
    
    
    
class CrossPlot(WorkPage):
    tid = 'crossplot'
    _FRIENDLY_NAME = 'Cross Plot'

    def __init__(self, controller_uid, **kwargs):
        super(CrossPlot, self).__init__(controller_uid)
        #
        self.set_own_name() # da mesma forma que o LogPlot
        #
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)                    
        self.crossplot_panel = CrossPlotPanel(self.center_panel) 
        self.hbox.Add(self.crossplot_panel, 1, wx.EXPAND)
        self.center_panel.SetSizer(self.hbox)
        self.hbox.Layout()
        
        self.tool_bar.AddSeparator()  
        self.tool_bar.Realize()  
             
        
    def set_own_name(self):
        UIM = UIManager()   
        controller = UIM.get(self._controller_uid)
        idx = 0
        lpcs = UIM.list('crossplot_controller')
        for lpc in lpcs:
            idx += 1
        controller.model.title = self._FRIENDLY_NAME + ' ['+ str(idx) + ']'    
        


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
    
    MAIN_AXES_WIDTH = 1.0 - 2*HORIZONTALMARGIN - 3*HORIZONTALPAD - YLABELWIDTH - COLORBARWIDTH - ZLABELWIDTH
    MAIN_AXES_HEIGHT = 1.0 - 2*VERTICALMARGIN - VERTICALPAD - XLABELHEIGHT
    
    #MAIN_AXES_BOTTOM = VERTICALMARGIN + XLABELHEIGHT + VERTICALPAD
    MAIN_AXES_BOTTOM = VERTICALMARGIN + XLABELHEIGHT
    MAIN_AXES_LEFT = HORIZONTALMARGIN + YLABELWIDTH + HORIZONTALPAD
    
    XLABELBOTTOM = VERTICALMARGIN
    
    YLABELLEFT = HORIZONTALMARGIN
    ZLABELLEFT = 1.0 - HORIZONTALMARGIN - ZLABELWIDTH
    COLORBARLEFT = ZLABELLEFT - HORIZONTALPAD - COLORBARWIDTH
    
    #TEXTFONTSIZE = 'medium'
    #NUMBERFONTSIZE = 'small'
    
    TEXTFONTSIZE = 11
    NUMBERFONTSIZE = 11
    
    #XLABELTEXTBOTTOM = 0.1
    XLABELTEXTBOTTOM = 0.4
    #XLABELTEXTTOP = 0.9
    XLABELTEXTTOP = 0.8
    #XLABELTEXTHMARGIN = 0.001
    XLABELTEXTHMARGIN = 0.005
    
    #YLABELTEXTLEFT = 0.1
    YLABELTEXTLEFT = 0.4
    #YLABELTEXTRIGHT = 0.9
    YLABELTEXTRIGHT = 0.9
    #YLABELTEXTVMARGIN = 0.002
    YLABELTEXTVMARGIN = 0.009
    
    ZLABELTEXTLEFT = 0.1
    #ZLABELTEXTLEFT = 0.3
    #ZLABELTEXTRIGHT = 0.9
    ZLABELTEXTRIGHT = 0.8
    
    
    def __init__(self, *args, **kwargs):
        super(CrossPlotPanel, self).__init__(*args, **kwargs)
        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)
        
        self.cmap = Colors.COLOR_MAP_RAINBOW
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
        self.xlabel_ax = None
        self.ylabel_ax = None
        self.zlabel_ax = None
        
        #self.colorbar_ax.yaxis.set_major_formatter(NullFormatter())
        self.collectionproperties = dict(linewidths=0.5, s=30)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(sizer)
        self.Fit()
        
        #self.canvas.mpl_connect('button_press_event', self.on_press)
        #self.canvas.mpl_connect('motion_notify_event', self.on_move)
    
    
    def create_xlabel(self):
        rect = [self.MAIN_AXES_LEFT, self.XLABELBOTTOM, self.MAIN_AXES_WIDTH, self.XLABELHEIGHT]
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

        print '\nself.xdata:', self.xdata, len(self.xdata)
        print 'self.ydata:', self.ydata, len(self.ydata)
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
            
        #"""    
        
        #self.colorbar_ax.yaxis.set_major_formatter(NullFormatter())
        
#        print '\n\n'
    


    """
    def _plot_zsolid(self):
        collection = self.crossplot_ax.plot(self.xdata, self.ydata, 'bo')
        self.collections.append(collection)
    """    

    
        
    """
    def _plot_zclasses(self):
        if self.parts is None:
            parts = [np.ones_like(self.xdata, dtype=bool)]
        else:
            parts = self.parts

        good = np.sum(parts, axis=0, dtype=bool)
        good *= np.isfinite(self.xdata)
        good *= np.isfinite(self.ydata)
        #good *= np.isfinite(self.zdata)  # TODO: Sem essa linha, onde não houver classificação será plotado de preto 

        classes = np.unique(self.zdata[good])
        self.classes = classes[classes != self.nullclass]
        
        n = self.zdata.shape[0]
        m = len(self.classes)
        ncc = len(self.classcolors.values()[0])
        
        zdata = np.full((n, ncc), np.nan)
        for cls in self.classes:
            zdata[self.zdata == cls] = self.classcolors[cls]
        zdata[self.zdata == self.nullclass] = self.nullcolor
        
        cmap = ListedColormap([self.classcolors[cls] for cls in self.classes])
        cmap.set_bad(self.nullcolor)
        self.zticks = range(m)
        self.zlim = [-0.5, m - 0.5]
        norm = NoNorm(*self.zlim)
        
        for part in parts:
            x = self.xdata[part*good]
            y = self.ydata[part*good]
            c = zdata[part*good]
            collection = self.crossplot_ax.scatter(x, y, c=c, cmap=cmap, zorder=-len(x), **self.collectionproperties)
            self.collections.append(collection)
            
        xticks = self.xlocator(np.min(self.xdata[good]), np.max(self.xdata[good]))
        self.set_xlim([xticks[0], xticks[-1]])
        
        yticks = self.ylocator(np.min(self.ydata[good]), np.max(self.ydata[good]))
        self.set_ylim([yticks[0], yticks[-1]])
        
        self.colorbar = ColorbarBase(self.colorbar_ax, cmap=cmap, norm=norm, ticks=self.zticks)
        #self.colorbar_ax.yaxis.set_major_formatter(NullFormatter())
        
    """    
        
    
    def draw(self):
        self.canvas.draw()
        
    
    
    """
    
    def on_move(self, event):
        return # TODO: tirar isso quando voltar a status_bar
        if event.inaxes == self.crossplot_ax:
            info = []
            info.append("{} = {:g}".format(self.xlabel, event.xdata))
            info.append("{} = {:g}".format(self.ylabel, event.ydata))
            self.status_bar.SetStatusText("        ".join(info))
        elif event.inaxes == self.xlabel_ax:
            pass
        elif event.inaxes == self.ylabel_ax:
            pass
        elif event.inaxes == self.zlabel_ax:
            pass
        elif event.inaxes == self.colorbar_ax:
            pass
    
    
    def on_press(self, event):
        pass

    """


        
class PdfsMixin(object):
    _FAC = 0.1

    def __init__(self):
        self.x_pdfs = []
        self.y_pdfs = []
        self.z_pdfs = []
        self.xy_pdfs = []


    def create_x_pdf(self, where=None, color=None):
        if where is None:
            where = self.good
        if color is None:
            color = '#bbbbbb'

        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        x = np.linspace(xmin, xmax, 100)

        x_kde = stats.gaussian_kde(self.x[where])
        x_pdf = x_kde(x)
        x_pdf_n = x_pdf/np.nanmax(x_pdf)*(ymax - ymin)*self._FAC + ymin
        """
        x_pdf = self.crossplot_ax.fill_between(x, x_pdf_n, ymin,
                                               color=color, lw=0,
                                               alpha=alpha, zorder=-1)
        """
        x_pdf, = self.crossplot_ax.plot(x, x_pdf_n, color=color[:3],
                                        alpha=color[-1], zorder=-1)
        #"""
        self.x_pdfs.append(x_pdf)

        self.crossplot_ax.set_xlim(*self.xlim)
        self.crossplot_ax.set_ylim(*self.ylim)


    def create_y_pdf(self, where=None, color=None):
        if where is None:
            where = self.good
        if color is None:
            color = '#bbbbbb'

        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        y = np.linspace(ymin, ymax, 100)

        y_kde = stats.gaussian_kde(self.y[where])
        y_pdf = y_kde(y)
        y_pdf_n = y_pdf/np.nanmax(y_pdf)*(xmax - xmin)*self._FAC + xmin
        """
        y_pdf = self.crossplot_ax.fill_betweenx(y, y_pdf_n, xmin,
                                                color=color, lw=0,
                                                alpha=alpha, zorder=-1)
        """
        y_pdf, = self.crossplot_ax.plot(y_pdf_n, y, color=color[:3],
                                        alpha=color[-1], zorder=-1)
        #"""
        self.y_pdfs.append(y_pdf)

        self.crossplot_ax.set_xlim(*self.xlim)
        self.crossplot_ax.set_ylim(*self.ylim)


    def create_xy_pdf(self, where=None, color=None):
        if where is None:
            where = self.good
        if color is None:
            color = '#bbbbbb'

        xmin, xmax = self.xlim
        ymin, ymax = self.ylim

        X, Y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]

        positions = np.vstack([X.ravel(), Y.ravel()])
        values = np.vstack([self.x[where], self.y[where]])
        xy_kde = stats.gaussian_kde(values)
        xy_pdf = np.reshape(xy_kde(positions), X.shape)

        """
        vmin = np.nanmin(xy_pdf)
        vmax = np.nanmax(xy_pdf)
        cmap = matplotlib.cm.gray_r
        xy_pdf = self.crossplot_ax.contourf(X, Y, xy_pdf, 20, cmap=cmap,
                                            vmin=vmin, vmax=2*vmax, alpha=alpha,
                                            zorder=-2)
        """
        xy_pdf = self.crossplot_ax.contour(X, Y, xy_pdf, 5, colors=color[:3],
                                           alpha=color[-1], zorder=-2)
        #"""
        self.xy_pdfs.append(xy_pdf)

        self.crossplot_ax.set_xlim(*self.xlim)
        self.crossplot_ax.set_ylim(*self.ylim)

    def show_x_pdf(self, i, visible=True):
        self.x_pdfs[i].set_visible(visible)

    def show_y_pdf(self, i, visible=True):
        self.y_pdfs[i].set_visible(visible)

#    def show_z_pdf(self, visible=True):
#        self.z_pdf.set_visible(visible)

    def show_xy_pdf(self, i, visible=True):
        #self.xy_pdfs[i].set_visible(visible)
        for lc in self.xy_pdfs[i].collections:
            lc.set_visible(visible)



class FaciesMixin(object):
    def __init__(self):
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)

    def on_press(self, event):
        if event.inaxes == self.colorbar_ax:# and self.z_is_facies:
            z = event.ydata
            i = int(z*len(self.crossplots))

            isVisible = self.crossplots[i].get_visible()

            self.crossplots[i].set_visible(not isVisible)

            if self.x_pdfs:
                self.x_pdfs[i].set_visible(not isVisible)
            if self.y_pdfs:
                self.y_pdfs[i].set_visible(not isVisible)
            if self.xy_pdfs:
                for lc in self.xy_pdfs[i].collections:
                    lc.set_visible(not isVisible)

            self.canvas.draw()


class Panel(CrossPlotPanel, PdfsMixin, FaciesMixin):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)
        PdfsMixin.__init__(self)
        FaciesMixin.__init__(self)
