# -*- coding: utf-8 -*-


import wx
import logging

from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 



import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np
from matplotlib.colors import colorConverter



import Parms


FLOAT_NULL_VALUE = -9999.25




class TrackObjectController(UIControllerBase):
    tid = 'track_object_controller'
    
    def __init__(self):
        super(TrackObjectController, self).__init__()
        
        
    def on_change_objuid(self, **kwargs):    
        print '\non_change_objuid: ', kwargs.get('new_value')
        self.update_model(kwargs.get('new_value'))


    def update_model(self, obj_uid):
        _OM = ObjectManager(self)
        obj = _OM.from_string(obj_uid)
        
        print '\nupdate_model:', obj.name

        # TODO: Rever isso
        parms = Parms.ParametersManager.get().get_curve_parms(obj.name)     
        print 'parms:', parms
        
        if parms is not None:
            plottype = parms.get('LineStyle')
            if plottype.lower() == 'solid':
                plottype = 'line'
            self.model.plottype = plottype
            self.model.left_scale = parms.get('LeftScale')
            self.model.right_scale = parms.get('RightScale')
            self.model.unit = parms.get('Units')
            self.model.backup = parms.get('Backup') 
               
            self.model.thickness = parms.get('LineWidth')
            
            color = parms.get('Color', 'black')
            if color == 'DkGray':
                color = 'darkgray'
            self.model.color = color
            loglin = parms.get('LogLin')
            if loglin == 'Lin':
                self.model.x_scale = 0
            elif loglin == 'Log':
                self.model.x_scale = 1
            else:
                raise ValueError('Unknown LogLin: [{}]'.format(loglin))            
      
        else:    
            if obj.tid == 'partition':
                self.model.plottype = 'partition'
            elif obj.tid == 'log': 
                self.model.plottype = 'line'
                self.model.thickness = 1
                ls, rs = get_extremes_from_object(obj)
                self.model.left_scale = ls
                self.model.right_scale = rs  
                ###
                self.model.unit = obj.unit
                self.model.backup = 0        
                self.model.x_scale = 0                 
                ###
            elif obj.tid == 'velocity':
                self.model.plottype = 'density'
                self.model.cmap = 'rainbow'
            elif obj.tid == 'seismic':
                self.model.plottype = 'density'
                self.model.cmap = 'gray' #'gray')#')
            elif obj.tid == 'scalogram':
                self.model.plottype = 'density'
                self.model.cmap = 'Paired' #'nipy_spectral')#cp.set('cmap', 'rainbow')           
                
        print '\n\nDICT: ', self.model.__dict__
        
        
        
     
    def set_data(self, *args):
        print '\n\nTrackObjectController.set_data:', args
        
        if not self.model.obj_uid or not self.model.plottype:              
            return        
        if not args:
            return

        x_data = args[0]    
        y_data = args[1]
               

        self.view.eixo.set_xlim((self.model.left_scale, self.model.right_scale))
        
        if self.model.x_scale == 0:    
            self.view.eixo.set_xscale('linear')               
        elif self.model.x_scale == 1:    
            self.view.eixo.set_xscale('log')  
        else:
            raise Exception()
         
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self.uid)
        parent_controller =  _UIM.get(parent_controller_uid)        
        ylim = parent_controller.view.track.dummy_ax.get_ylim()        
        self.view.eixo.set_ylim(ylim)
       
        if len(self.view.eixo.lines) > 0: # never should be greater than 1 
            print '\nIF',len(self.view.eixo.lines) > 0
            self.view.eixo.lines[0].set_color(self.model.color)
            self.view.eixo.lines[0].set_linewidth(self.model.thickness)
            self.view.eixo.lines[0].set_zorder(10000)  
            self.view.eixo.lines[0].set_data(x_data, y_data)      
        else: 
            print '\nELSE'                       
            line = matplotlib.lines.Line2D(x_data, y_data, 
                    linewidth=self.model.thickness, 
                    color=self.model.color
            )
            self.view.eixo.add_line(line)       
        parent_controller.view.track.draw()    
        
        _OM = ObjectManager(self)
        obj = _OM.from_string(self.model.obj_uid)
        if not obj:
            print '\n\nDEU RUIM'
        self.view.cima.set_data(obj.name, self.model.plottype, 
                                self.model.obj_uid, x_unit=self.model.unit,
                                x_min=self.model.left_scale,
                                x_max=self.model.right_scale,
                                linecolor=self.model.color, 
                                linewidth=self.model.thickness
                                
        )


class TrackObjectModel(UIModelBase):
    tid = 'track_object_model'
    
    _ATTRIBUTES = {
        'obj_uid': {'default_value': wx.EmptyString, 
                    'type': str, 
                    'on_change': TrackObjectController.on_change_objuid
        },
        'left_scale': {'default_value': FLOAT_NULL_VALUE, 'type': float},
        'right_scale': {'default_value': FLOAT_NULL_VALUE, 'type': float},
        'unit': {'default_value': wx.EmptyString, 'type': str},
        'backup': {'default_value': wx.EmptyString, 'type': str},
        'thickness': {'default_value': 1, 'type': int},
        'color': {'default_value': 'black', 'type': str},
        'x_scale': {'default_value': 0, 'type': int},
        'plottype': {'default_value': wx.EmptyString, 'type': str},
        'visible': {'default_value': True, 'type': bool},
        'cmap': {'default_value': 'rainbow', 'type': str},
    }      


    def __init__(self, controller_uid, **base_state): 
        super(TrackObjectModel, self).__init__(controller_uid, **base_state) 
        print '\n\n', self.__dict__
  



def get_extremes_from_object(obj, gap_percent=5):
    left = np.nanmin(obj.data)
    right = np.nanmax(obj.data)
    unit = (right - left) / (100-gap_percent*2)
    left = left - (gap_percent*unit)
    right = right + (gap_percent*unit)
    return np.round(left, 2), np.round(right, 2)
  
  
    
    
    
class TrackObjectView(UIViewBase):
    tid = 'track_object_view'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid) 
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        
        
        self.cima = parent_controller.view.label.append_object()
        
        self.eixo = Axes(parent_controller.view.track.figure, 
             parent_controller.view.track.dummy_ax.get_position(True),
             sharey=parent_controller.view.track.dummy_ax,
             frameon=False
        )
        self.eixo.xaxis.set_visible(False)
        self.eixo.yaxis.set_visible(False)
        parent_controller.view.track.figure.add_axes(self.eixo)
        


    #def PostInit(self):
    #    self.do_it()


    '''
    


import wx
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
#from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
#from matplotlib.figure import Figure
#import numpy as np


VALID_PLOT_TYPES = ['index', 'line', 'partition', 'density', 'wiggle']

# Constants
DPI = 80
LABEL_TITLE_HEIGHT = 40
     
    
    def draw(self):
        
        _UIM = UIManager()
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        parent_controller.view.track.draw()
    ''' 
     
        
    '''          
    def do_it(self):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if not controller.model.obj_uid or not controller.model.plottype:              
            return
       
        self.view.set_xlim((controller.model.left_scale, controller.model.right_scale))
        
        if controller.model.
        self.view.set_xscale()
                

        print 4
        print ax.get_xscale()  
        print

        xs = kwargs.get('x_scale', None) 
        if xs is not None:
            if ax.get_xscale() == 'linear' and xs == 1:    
                ax.set_xscale('log')
            elif ax.get_xscale() == 'log' and xs == 0:  
                ax.set_xscale('linear')    
        ax.set_ylim(ylim)
        
        if controller.model.plottype == 'line': 
            linewidth = kwargs.get('thickness')
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)
            
            if x_data is not None and y_data is not None:           
                
                if len(ax.lines) > 0: # never should be greater than 1 
                    print '\n',len(ax.lines) > 0
                    ax.lines[0].set_color(controller.model.color)
                    ax.lines[0].set_linewidth(controller.model.thickness)
                    ax.lines[0].set_zorder(10000)  
                    ax.lines[0].set_data(x_data, y_data)      
                else: 
                    print '\nELSE'                       
                    line = matplotlib.lines.Line2D(x_data, y_data, 
                            linewidth=controller.model.thickness, 
                            color=controller.model.color
                    )
                    ax.add_line(line)             
        
    '''

    
    '''    
    @staticmethod
    def from_IP_parameters(parms):
        cp = CurveUIProperties()
        cp.set('curve_name', parms.get('Name'))
        cp.set('left_scale', parms.get('LeftScale'))
        cp.set('right_scale', parms.get('RightScale'))
        cp.set('unit', parms.get('Units'))
        cp.set('backup', parms.get('Backup'))        
        cp.set('thickness', parms.get('LineWidth'))
        
        color = parms.get('Color', 'black')
        if color == 'DkGray':
            color = 'darkgray'
        cp.set('color', color)
        loglin = parms.get('LogLin')
        if loglin == 'Lin':
            cp.set('x_scale', 0)
        elif loglin == 'Log':
            cp.set('x_scale', 1)
        else:
            raise ValueError('Unknown LogLin: [{}]'.format(loglin))            
        cp.set('plottype', parms.get('LineStyle'))        
        cp.set('visible', True)
        return cp  
        
    '''    
       

    def append_object(self, plot_type, object_id, **kwargs):
        print '\n\n\nAPPEND_OBJECT'
        self.insert_curve(len(self.axes)-1, plot_type, object_id, **kwargs)
   

    def insert_object(self, pos, plot_type, object_id, **kwargs):  
        print '\n\n\nINSERT_OBJECT'
        ax = self.figure.add_axes(self.dummy_ax.get_position(True),
                          sharey=self.dummy_ax, 
                          frameon=False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        self.axes.append(ax)
        self.update_curve(pos, plot_type, object_id, **kwargs)
        

    def update_curve(self, pos, plot_type, object_id, **kwargs):
        #ax = self.axes[pos]
        
        #ls = kwargs.get('x_min', None)
        #rs = kwargs.get('x_max', None) 
        print '\n\n\nUPDATE_CURVE'
        
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        print 'x_lim:', controller.model.left_scale, controller.model.right_scale        

                
        
        if controller.model.left_scale != FLOAT_NULL_VALUE and \
                        controller.model.right_scale != FLOAT_NULL_VALUE:
            print 1
            if self.get_xlim() != (ls, rs):
                print 2
                self.set_xlim((ls, rs)) 
            else:
                print 3, self.get_xlim()
        print 4
        print self.get_xscale()  
        print

        xs = kwargs.get('x_scale', None) 
        if xs is not None:
            if self.get_xscale() == 'linear' and xs == 1:    
                self.set_xscale('log')
            elif self.get_xscale() == 'log' and xs == 0:  
                self.set_xscale('linear')    
          
      
                    
        if plot_type == 'line': 
            
            #x_smooth = np.linspace(kwargs.get('x_data').min(), kwargs.get('x_data').max(), 200)
            #y_smooth = spline(kwargs.get('x_data'), kwargs.get('y_data'), x_smooth)

            '''
            idx  = np.arange(0, len(kwargs.get('y_data')), 1000, dtype=np.int)            

            # Pegar pixels dos y no axis e espaçar de acordo com isso                
            
            x_smooth = np.array([kwargs.get('x_data')[i] for i in idx])
            y_smooth = np.array([kwargs.get('y_data')[i] for i in idx])
            #idx = np.linspace(0, len(kwargs.get('y_data')), 200)
            print '\nidx:', len(idx)
            '''
            linecolor = kwargs.get('linecolor', 'black')
            linewidth = kwargs.get('thickness')
            x_data = kwargs.get('x_data', None)
            y_data = kwargs.get('y_data', None)
            
            if x_data is not None and y_data is not None:           
                
                if len(ax.lines) > 0: # never should be greater than 1 
                    print '\n',len(ax.lines) > 0
                    ax.lines[0].set_color(linecolor)
                    ax.lines[0].set_linewidth(linewidth)
                    ax.lines[0].set_zorder(10000)  
                    ax.lines[0].set_data(x_data, y_data)      
                else: 
                    print '\nELSE'                       
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
            
            print 'x_data.shape:', x_data.shape
            print 'max_x_data:', max_x_data
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
                print vmin, vmax
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
          #      print 'format_coord:', col, row
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
            #print (xmin, xmax, ymax, ymin)
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
        print '\nSetting... ', ylim 
        ax.set_ylim(ylim)       
        self.draw()        
            
            
               
    def remove_curve(self, curve_number):       
        ax = self.axes.pop(curve_number)
        self.figure.delaxes(ax)
        self.draw()





            
    def curves_changed(self, origin, old_value, new_value, publisher): 
        if publisher != self.track_props:
            return
            
               
        if len(new_value) > len(old_value):
            # Curves added
            list_ = [item for item in new_value if item not in old_value]
            
            
            
            for item in list_:
                
                new_obj_pos = new_value.index(item)  # Position in a track
                new_obj_uid, new_obj_props = item
                new_obj = self._OM.from_string(new_obj_uid)
                
                            
                if new_obj.tid == 'index_curve':                    
                    self.view._label.insert_object(new_obj_pos, new_obj.name, 
                        'index', new_obj.uid, unit=new_obj.unit
                    )
                    self.view._track.insert_object(new_obj_pos, 'index', new_obj.uid) 

                
                elif new_obj.tid == 'log':  
                    index_obj = self._OM.get(new_obj.index_uid)
                    self.view._label.insert_object(new_obj_pos, new_obj.name, 
                        'line', new_obj.uid, 
                        x_unit = new_obj.unit,
                        x_min = new_obj_props.get('left_scale'),
                        x_max = new_obj_props.get('right_scale'),
                        linecolor = new_obj_props.get('color'), 
                        linewidth = new_obj_props.get('thickness')
                    )
                    self.view._track.insert_object(new_obj_pos, 'line', new_obj.uid, 
                        x_min = new_obj_props.get('left_scale'),
                        x_max = new_obj_props.get('right_scale'),
                        linecolor = new_obj_props.get('color'), 
                        linewidth = new_obj_props.get('thickness'),
                        x_data = new_obj.data,
                        y_data = index_obj.data            
                    )
                 
                elif new_obj.tid == 'partition':    
                    index_obj = self._OM.get(new_obj.index_uid)
                    part_dict = {}
                    for part in new_obj.list('part'): 
                        part_dict[part.code] = (part.color, part.data)

                    self.view._label.insert_object(new_obj_pos, new_obj.name, 
                        'partition', new_obj.uid
                    )
               
                    self.view._track.insert_object(new_obj_pos, 'partition', new_obj.uid,
                        x_data = part_dict,
                        y_data = index_obj.data              
                    )                        

                elif new_obj.tid == 'velocity':    
                    
                    start = new_obj.attributes.get('datum', 0)
                    step = new_obj.attributes.get('sample_rate')
                    stop = start + new_obj.attributes.get('samples') * step
                    y_data = np.arange(start, stop, step) 
                    max_x_data = np.amax(new_obj.data) 
                    min_x_data = np.amin(new_obj.data)
                    
                    
                    cmap = new_obj_props.get('cmap') #cm.get_cmap('brg')#cm.get_cmap('Greys')
                    
                    # Setting values
                    self.view._label.insert_object(new_obj_pos, new_obj.name, 
                        'density', new_obj.uid, z_label='Velocity', 
                        z_min=min_x_data, z_max=max_x_data, 
                        colormap=cmap,
                        x_label='Trace', x_min=1, x_max=int(new_obj.data.shape[0])
                    )  

                    self.view._track.insert_object(new_obj_pos, 'density', new_obj.uid,
                        min_value = min_x_data,
                        max_value = max_x_data, 
                        colormap=cmap,
                        x_data = new_obj.data,
                        y_data = y_data, 
                        alpha=0.3
                    )  
                            
                            
                            
                elif new_obj.tid == 'seismic':    
                    stacked = new_obj.attributes.get('stacked', False)
                    
                    if stacked:
                        start = new_obj.attributes.get('datum', 0)
                        step = new_obj.attributes.get('sample_rate')
                        stop = start + new_obj.attributes.get('samples') * step
                        y_data = np.arange(start, stop, step) 
                        max_x_data = np.amax(new_obj.data) 
                        min_x_data = np.amin(new_obj.data)
                        
                        print '\n\n1718: ', max_x_data, min_x_data
                        
                        cmap = new_obj_props.get('cmap') #cm.get_cmap('brg')#cm.get_cmap('Greys')
                        
                        # Setting values
                        self.view._label.insert_object(new_obj_pos, new_obj.name, 
                            'density', new_obj.uid, z_label='Amplitude', 
                            z_min=min_x_data, z_max=max_x_data, 
                            colormap=cmap,
                            x_label='Trace', x_min=1, x_max=int(new_obj.data.shape[0])
                        )  
    
                        self.view._track.insert_object(new_obj_pos, 'density', new_obj.uid,
                            min_value = min_x_data,
                            max_value = max_x_data, 
                            colormap=cmap,
                            x_data = new_obj.data,
                            y_data = y_data,
                            alpha=0.9
                        )  
                        
                    else: #new_obj_props.get('plottype') == 'wiggle':                  
                        x_data = new_obj.data
                        start = new_obj.attributes.get('datum', 0)
                        step = new_obj.attributes.get('sample_rate')
                        stop = start + new_obj.attributes.get('samples') * step
                        y_data = np.arange(start, stop, step) 
                        traces = new_obj.attributes.get('traces')
                                      
                        self.view._label.insert_object(new_obj_pos, new_obj.name, 
                            'wiggle', new_obj.uid, z_label='Amplitude', 
                            z_min='-1.0', z_max='1.0', 
                            x_label='Offsets',
                            x_range= range(1,traces+1),
                            x_unit = 'meters'  
                        )
                        
                        self.view._track.insert_object(new_obj_pos, 'wiggle', new_obj.uid,
                            x_min = new_obj_props.get('left_scale'),
                            x_max = new_obj_props.get('right_scale'),
                            x_data = x_data,
                            y_data = y_data            
                        )       
                        
                elif new_obj.tid == 'scalogram':
                    # Preparing values
                    
                    start = new_obj.attributes.get('datum', 0)
                    step = new_obj.attributes.get('sample_rate')
                    stop = start + new_obj.attributes.get('samples') * step
                    y_data = np.arange(start, stop, step) 
                    max_x_data = np.amax(new_obj.data) 
                    min_x_data = np.amin(new_obj.data)
                    cmap = new_obj_props.get('cmap') #cm.get_cmap('brg')#cm.get_cmap('Greys')
                    
                    # Setting values
                    self.view._label.insert_object(new_obj_pos, new_obj.name, 
                        'density', new_obj.uid, z_label='Amplitude power', 
                        z_min=min_x_data, z_max=max_x_data, 
                        colormap=cmap,
                        x_label='Trace', x_min=1, x_max=int(new_obj.data.shape[0])
                    )  

                    self.view._track.insert_object(new_obj_pos, 'density', new_obj.uid,
                        min_value = min_x_data,
                        max_value = max_x_data, 
                        colormap=cmap,
                        x_data = new_obj.data,
                        y_data = y_data            
                    )  
                else:
                    print new_obj.uid
                    raise Exception('ELSE')       
                    
                    


        elif len(new_value) < len(old_value):
            # Curve removed
            print
        else:
            # Curves changed position
            print       
        #print '\n\ncurves_changed:', 
        #print 'old_value'
        #for idx, (uid, cp) in enumerate(old_value): 
        #    print idx, uid, cp#.get_id()
        #print '\nnew_value'    
        #for idx, (uid, cp) in enumerate(new_value): 
        #    print idx, uid, cp#.get_id()   
            
            
            

 
