# -*- coding: utf-8 -*-
from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 

from matplotlib.transforms import (Bbox, BboxTransform)
                                   

#from matplotlib.transforms import (Affine2D, BboxBase, Bbox, BboxTransform,
#                                   IdentityTransform, TransformedBbox)


# TODO: verificar se linhas abaixo devem ser mantidas
import Parms
import numpy as np

#import sys

from scipy.interpolate import interp1d

import numpy.ma as ma
import matplotlib.mlab as mlab
import matplotlib.collections as mcoll
import matplotlib.cbook as cbook 
import matplotlib
                                   

from matplotlib.patches import FancyBboxPatch
import collections                                      
                                          
  
from App.utils import MPL_COLORS, MPL_COLORMAPS
import wx


###############################################################################
###############################################################################
                               
              
def calculate_extremes(obj, gap_percent=5):
    min_val = np.nanmin(obj.data)
    max_val = np.nanmax(obj.data)
    one_percent_gap = (max_val - min_val) / 100
    min_val = min_val - (gap_percent * one_percent_gap)
    max_val = max_val + (gap_percent * one_percent_gap)
    return np.round(min_val, 2), np.round(max_val, 2)


_PLOTTYPES_REPRESENTATIONS = {
    'line': 'line_representation_controller',
    'index': 'index_representation_controller',
    'density': 'density_representation_controller',
    'patches': 'patches_representation_controller',
    'contourf': 'contourf_representation_controller'
}

_PREFERRED_PLOTTYPES = {
    'log': 'line',
    'index_curve': 'index',
    'seismic': 'density',
    'partition': 'patches',
    'scalogram': 'density',
    'velocity': 'density',
    'gather': 'density',
    'angle': 'contourf'
}


###############################################################################
###############################################################################


def transform(value, left_scale, right_scale, scale=0):
    if left_scale is None or right_scale is None:
        raise Exception('Left or Right scales cannot be None.')
    if scale not in [0, 1]:
        raise Exception('Scale must be 0 or 1.')
    invalid_err = np.geterr().get('invalid')
    invalid_err = np.geterr().get('invalid')
    np.seterr(invalid='ignore')    
    if scale == 0:
        range_ = np.absolute(right_scale - left_scale)
        translated_value = np.abs(value - left_scale)    
        ret_val =  (translated_value / range_)
    else:
        if left_scale <= 0.0:
            raise Exception()
        ls = np.log10(left_scale)    
        rs = np.log10(right_scale)
        range_ = rs - ls
        translated_value = np.log10(value) - ls
        ret_val =  (translated_value / range_)
    np.seterr(invalid=invalid_err)
    return ret_val    
        

def inverse_transform(value, left_scale, right_scale, scale=0):
    if left_scale is None or right_scale is None:
        raise Exception('Left or Right scales cannot be None.')
    if scale not in [0, 1]:
        raise Exception('Scale must be 0 or 1.')
    invalid_err = np.geterr().get('invalid')
    np.seterr(invalid='ignore')    
    if scale == 0:
        range_ = np.absolute(right_scale - left_scale)
        translated_value = value * range_
        if (left_scale > right_scale):
            ret_val = left_scale - translated_value
        else:    
            ret_val = left_scale + translated_value
    else:
        ls = np.log10(left_scale)    
        rs = np.log10(right_scale)
        range_ = rs - ls
        translated_value = value * range_
        translated_value = np.round(translated_value, 3)
        translated_value = translated_value + ls
        ret_val = np.power(10, translated_value)
    np.seterr(invalid=invalid_err)
    return ret_val  


###############################################################################
###############################################################################




class TrackObjectController(UIControllerBase):
    tid = 'track_object_controller'
    
    
    def __init__(self):
        super(TrackObjectController, self).__init__()
        self.subscribe(self.on_change_objtid, 'change.obj_tid')        
        self.subscribe(self.on_change_objoid, 'change.obj_oid')
        self.subscribe(self.on_change_plottype, 'change.plottype')
        #
        #OM = ObjectManager(self) 
        #OM.subscribe(self.qqcoisa, 'pre_remove')
        #
        
    def PostInit(self):
        UIM = UIManager()
        if self.model.pos == -1:
            track_ctrl_uid = UIM._getparentuid(self.uid)
            self.model.pos = len(UIM.list(self.tid, track_ctrl_uid))     
        
        
    def PreDelete(self):
        print '\nTrackObjectController.PreDelete'
        self.model.plottype = None
        
    
    def get_object(self):
        # Get OM object from TrackObjectController
        # Returns None if there is no OM Object associate with it.    
        OM = ObjectManager(self) 
        try:
            obj = OM.get((self.model.obj_tid, self.model.obj_oid))
            if obj: 
                return obj
        except:
            pass
        return None


    def on_change_objtid(self, new_value, old_value):
        print '\non_change_objtid:', new_value
        if old_value is not None:
            if self.model.obj_tid:
                print 'detaching tid'
                self.detach((old_value, self.model.obj_oid))
            self.model.obj_oid = None
            # Exclude any representation, if exists
            #self.model.plottype = None


    def on_change_objoid(self, new_value, old_value):
        print '\non_change_objoid:', new_value, old_value
        # Exclude any representation, if exists
        if old_value is not None:
            print 'detaching oid'
            self.detach((self.model.obj_tid, old_value))
        self.model.plottype = None
        obj = self.get_object()
        if obj:
            plottype = _PREFERRED_PLOTTYPES.get(obj.tid)
            self.model.plottype = plottype       
            self.attach(obj.uid)
    
    
    def on_change_plottype(self, new_value, old_value):
        #print '\non_change_plottype:', new_value
        UIM = UIManager()
        representations = UIM.list(None, self.uid)
        if representations:
            repr_ctrl = representations[0]
            #repr_ctrl.unsubscribe(self._repr_change_prop, 'change')
            UIM.remove(repr_ctrl.uid)
            
        if new_value is not None:
            repr_tid = _PLOTTYPES_REPRESENTATIONS.get(new_value)
            try:
                state = self._get_log_state()
                repr_ctrl = UIM.create(repr_tid, self.uid, **state)
                track_uid = UIM._getparentuid(self.uid)
                logplot_uid = UIM._getparentuid(track_uid)
                logplot_ctrl = UIM.get(logplot_uid)
                
                #
                #print 'created_toc:' #, self.get_object().start, self.get_object().end
                #track_ctrl = UIM.get(track_uid)
                #print 'get start...'
                #start = track_ctrl.view.depth_to_wx_position(self.get_object().start)
                #print 'get end...'
                #end = track_ctrl.view.depth_to_wx_position(self.get_object().end)
                #print 'pixels:', start, end
                #
                
                logplot_ctrl.track_object_included(self.get_object().start, 
                                 self.get_object().end
                )
                
                
                self.model._redirects_to = repr_ctrl.model
                #repr_ctrl.subscribe(self._repr_change_prop, 'change')
            except:    
                #print '\non_change_plottype:', new_value
                raise
                self.model.plottype = None                


    def _get_log_state(self):
        # TODO: Rever necessidade de obj.name - ParametersManager
        state = {}
        obj = self.get_object()
        if obj.tid == 'log':
            # TODO: Rever isso
            parms = Parms.ParametersManager.get().get_curvetype_visual_props(obj.curvetype)     
            if parms is not None:
                #print 'parms: not None'
                state['left_scale'] = parms.get('LeftScale')
                state['right_scale'] = parms.get('RightScale')
                state['thickness'] = parms.get('LineWidth')
                state['color'] = parms.get('Color', 'Black')
                loglin = parms.get('LogLin')
                if loglin == 'Lin':
                    state['x_scale'] = 0
                elif loglin == 'Log':
                    state['x_scale'] = 1
                else:
                    raise ValueError('Unknown LogLin: [{}]'.format(loglin))  
            else:
                #print 'parms: None'
                if obj.name == 'LOG_TESTE_CURVE':
                    state['x_scale'] = 1
                    ls, rs = (0.01, 100000.0)
                else:    
                    state['x_scale'] = 0
                    ls, rs = calculate_extremes(obj)
                state['left_scale'] = ls
                state['right_scale'] = rs
        return state
            

    def get_data(self, event):
        repr_ctrl = self.get_representation()
        if not repr_ctrl:
            return None        
        return repr_ctrl.get_data(event)


    def get_representation(self):
        # Returns the real Ompl_object LogPlot representation
        UIM = UIManager()
        representations = UIM.list(None, self.uid)
        if len(representations) == 0:
            return None
        return representations[0]                

    def is_valid(self):
        return self.get_representation() is not None


    def redraw(self):
        if not self.get_representation():
            return False
        return self.get_representation().redraw()


    # TODO: Picking
    
    # TODO: Get data


    """
    def is_picked(self):
        return self.model.picked

    def on_change_picked(self, new_value, old_value):
        self.get_representation().view.set_picked(new_value) 
    """  
            
    # Picking with event that generates pick... 
    # Event(PickEvent) maybe useful in future
    def pick_event(self, event):
        print event
        self.model.selected = not self.model.selected 
      



class TrackObjectModel(UIModelBase):
    tid = 'track_object_model'

    _ATTRIBUTES = collections.OrderedDict()
    _ATTRIBUTES['obj_tid'] = {
            'default_value': None,
            'type': str    
    }
    _ATTRIBUTES['obj_oid'] = {
            'default_value': None,
            'type': int    
    }    
    _ATTRIBUTES['plottype'] = {
            'default_value': None,
            'type': str    
    }  
    # TODO: pos
    _ATTRIBUTES['pos'] = {
            'default_value': -1,
            'type': int    
    }      

    _ATTRIBUTES['selected'] = {
            'default_value': False,
            'type': bool    
    }     
    
    # TODO: Check for _ATTRIBUTES['visible']  and _ATTRIBUTES['picked'] 

    def __init__(self, controller_uid, **base_state): 
        super(TrackObjectModel, self).__init__(controller_uid, **base_state) 
  
    
    def get_state(self, state_type=None):
        # This overrides UIModelBase.get_state
        # TODO: manter alinhado com o UIModelBase.get_state
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if not controller.is_valid():
            return None
        else:
            print 'NOT VALID'
            raise Exception()
        state = super(TrackObjectModel, self).get_state()        
        repr_ctrl = controller.get_representation()
        state.update(repr_ctrl.model.get_state())
        return state


###############################################################################
###############################################################################


class RepresentationController(UIControllerBase):
    tid = 'representation_controller'
    
    def __init__(self):
        super(RepresentationController, self).__init__()
         
    def get_data(self, event):
        return self.view.get_data(event)

    def get_object(self):
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid) 
        return toc.get_object()

    def redraw(self):
        if isinstance(self, LineRepresentationController):
            self.view.draw()
        else:
            return False
        #return self.view.draw_canvas()
 
    # TODO: rever esse nome horrivel
    # TODO: tirar a duplicidade de chamadas e substituir por esse metodo nas ocorrencias abaixo
    #       pesquisar por "argmin"
    def get_index_idx(self, value):
        obj = self.get_object()
        index_data = obj.get_index().data
        idx_index = (np.abs(index_data-value)).argmin()
        return idx_index 
        
    
class RepresentationView(UIViewBase):
    tid = 'representation_view'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid) 
        self._mplot_objects = {}
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        if not track_controller.model.overview:
            self.label = track_controller._append_track_label()
            self.label.set_object_uid(self._controller_uid)
        else:
            self.label = None
        
    def PreDelete(self):
        self.clear()
        if self.label:
            self.label.destroy()
        
    def get_data(self, event):
        return None
        #raise NotImplemented('{}.get_data must be implemented.'.format(self.__class__))
    
    def get_canvas(self):
        try:
            # Getting canvas from MPL.Artist
            # All _mplot_objects are on the same FigureCanvas
            # (TrackFigureCanvas.plot_axes)
            canvas = self._mplot_objects.values()[0].figure.canvas        
            return canvas
        except:
            # Getting from TrackController
            UIM = UIManager()
            toc_uid = UIM._getparentuid(self._controller_uid)
            track_controller_uid = UIM._getparentuid(toc_uid)
            track_controller =  UIM.get(track_controller_uid)
            return track_controller._get_canvas()
        
    def draw_canvas(self):     
        canvas = self.get_canvas()
        if canvas:
            canvas.draw()
            return True
        return False

    def draw_after(self, func, *args, **kwargs):
        if callable(func):
            func(*args, **kwargs)
            return self.draw_canvas()
        return False
    
    def clear(self):  
        self.draw_after(self._remove_all_artists)

    def _remove_all_artists(self):
        for value in self._mplot_objects.values():
            # String is a sequence too, but it will not be here
            if isinstance(value, collections.Sequence):
                for obj in value:
                    if obj:
                        obj.remove()  
            else:
                if value:
                    value.remove()
        self._mplot_objects = {}       
        
        
    def set_title(self, title):
        if self.label:
            self.label.set_title(title)
            
            
    def set_subtitle(self, unit):    
        if self.label:
           self.label.set_unit(unit)
            
  
    def _set_picking(self, mplot_obj, pickradius=3):
        # When we set picker to True (to enable line picking) function
        # Line2D.set_picker sets pickradius to True, 
        # then we need to set it again.
        mplot_obj.set_picker(True)
        mplot_obj.set_pickradius(pickradius)
        
        
###############################################################################
###############################################################################


class LineRepresentationController(RepresentationController):
    tid = 'line_representation_controller'
    
    def __init__(self):
        super(LineRepresentationController, self).__init__()


class LineRepresentationModel(UIModelBase):
    tid = 'line_representation_model'

    _ATTRIBUTES = collections.OrderedDict()
    _ATTRIBUTES['left_scale'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Left value'        
    }
    _ATTRIBUTES['right_scale'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Right value'
    }
    _ATTRIBUTES['thickness'] = {
            'default_value': 1, 
            'type': int,
            'pg_property': 'EnumProperty',
            'label': 'Width',
            'labels': ['0', '1', '2', '3', '4', '5'],
            'values': [0, 1, 2, 3, 4, 5 ]
    }
    _ATTRIBUTES['color'] = {
            'default_value': 'Black',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Color',
            'labels': MPL_COLORS.keys()                
    }
    _ATTRIBUTES['x_scale'] = {
            'default_value': 0, 
            'type': int,
            'pg_property': 'EnumProperty',
            'label': 'X axis scale',
            'labels': ['Linear', 'Logarithmic'],
            'values': [0, 1]
    }
    
    def __init__(self, controller_uid, **base_state): 
        super(LineRepresentationModel, self).__init__(controller_uid, **base_state)     
          
    
class LineRepresentationView(RepresentationView):
    tid = 'line_representation_view'
    _picked_color = 'MediumSpringGreen'

    def __init__(self, controller_uid):
        super(LineRepresentationView, self).__init__(controller_uid)
        self._used_scale = None
        self._used_left_scale = None
        self._used_right_scale = None

    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        controller.subscribe(self.set_xlim, 'change.left_scale')    
        controller.subscribe(self.set_xlim, 'change.right_scale') 
        controller.subscribe(self.set_thickness, 'change.thickness')
        controller.subscribe(self.set_color, 'change.color')
        controller.subscribe(self.set_zorder, 'change.zorder')
        controller.subscribe(self.on_change_xscale, 'change.x_scale')
        #
        parent_uid = UIM._getparentuid(self._controller_uid)
        parent = UIM.get(parent_uid)
        parent.subscribe(self.set_picked, 'change.selected') 
        #
        self.draw()


    def get_data(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        index_data = obj.get_index().data
        idx = (np.abs(index_data-event.ydata)).argmin()
        if not np.isfinite(obj.data[idx]):
            return None
        return obj.data[idx]


    def on_change_xscale(self, new_value, old_value):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        if new_value == 1:
            if controller.model.left_scale is None or \
                                            controller.model.left_scale <= 0.0:
                controller.model.set_value_from_event('left_scale', 0.2)
        self.set_xscale(new_value) 
    
    #def set_title(self, title):
    #    self.label.set_title(title)
            
    #def set_unit(self, unit):    
    #    self.label.set_unit(unit)

    def set_zorder(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_zorder(new_value)
            self.draw_canvas()
        

    #def set_selected(self, new_value, old_value):
    #    print 'set_selected:', new_value
        
        
    def set_picked(self, new_value, old_value):
        #print 'set_picked:', new_value
        if len(self._mplot_objects.values()) == 0:
            self.draw()
        if new_value:
            self._mplot_objects['line'].set_color(self._picked_color)    
        else:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            self._mplot_objects['line'].set_color(controller.model.color)
        self.draw_canvas()     
            
        
    def set_thickness(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_linewidth(new_value)
            self.draw_canvas()
            if self.label:
                self.label.set_thickness(new_value) 
        else:
            self.draw()
            
            
    def set_color(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_color(new_value)
            self.draw_canvas()   
            if self.label:
                self.label.set_color(new_value)
        else:
            self.draw()
                     
            
    def set_xscale(self, xscale):
        self.draw()

        
    def set_xlim(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        if not controller.get_object():
            return
        self.draw()

    
    def draw(self):
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)        
        #
        obj = controller.get_object()

        transformated_xdata = transform(obj.data, controller.model.left_scale, 
                    controller.model.right_scale, controller.model.x_scale)
        #
        if len(self._mplot_objects.values()) == 1:
            self.clear()
        #     

        """
        Line2D(xdata, ydata, linewidth=None, linestyle=None, color=None, 
               marker=None, markersize=None, markeredgewidth=None, 
               markeredgecolor=None, markerfacecolor=None, 
               markerfacecoloralt='none', fillstyle=None, antialiased=None, 
               dash_capstyle=None, solid_capstyle=None, dash_joinstyle=None, 
               solid_joinstyle=None, pickradius=5, drawstyle=None, 
               markevery=None, **kwargs)
        """
      
        
        # inicio - teste
        '''
        if not self._mplot_objects.get('line'):
            line = track_controller._append_artist('Line2D', transformated_xdata, 
                        obj.get_index().data, linewidth=controller.model.thickness,
                        color=controller.model.color
            )
        else:
            line = self._mplot_objects.get('line')
        
        '''

        f1 = interp1d(obj.get_index().data, transformated_xdata)
        #f2 = interp1d(obj.get_index().data, transformated_xdata, kind='cubic')        
        
        depth_list = []
        
        #print 'LineRepresentationView.draw()'
        for depth_px in range(track_controller.view.track.GetSize()[1]):
            depth = track_controller.view.track.get_depth_from_ypixel(depth_px)
            if depth > obj.start and depth < obj.end:
                depth_list.append(depth)
                #print depth
                
        if not self._mplot_objects.get('line'):
            line = track_controller._append_artist('Line2D', f1(depth_list), 
                        depth_list, linewidth=controller.model.thickness,
                        color=controller.model.color
            )
        else:
            line = self._mplot_objects.get('line')   
            line.set_data(f1(depth_list), depth_list)
            
        '''    
        if not self._mplot_objects.get('l1'):
            l1 = track_controller._append_artist('Line2D', f1(depth_list), 
                                                depth_list, linewidth=1, 
                                                color='blue'
            )
            self._mplot_objects['l1'] = l1
        else:
            l1 = self._mplot_objects.get('l1')
        l1.set_data(f1(depth_list), depth_list)
        '''
            
        #l2 = track_controller._append_artist('Line2D', f2(depth_list), 
        #            depth_list, linewidth=2, color='red' ,zorder=1000
        #)          
      
        
        
        #fim - teste
        
        
        line.set_label(toc_uid)

        # When we set picker to True (to enable line picking) function
        # Line2D.set_picker sets pickradius to True, 
        # then we need to set it again.
        self._set_picking(line)

        #
        self._used_scale = controller.model.x_scale
        self._used_left_scale = controller.model.left_scale
        self._used_right_scale = controller.model.right_scale
        #
        self._mplot_objects['line'] = line
        self.draw_canvas()    
        
        if self.label:
            self.label.set_plot_type('line')
            self.label.set_xlim(
                (controller.model.left_scale, controller.model.right_scale)
            ) 
            self.label.set_color(controller.model.color)
            self.label.set_thickness(controller.model.thickness) 
            
        
        self.set_title(obj.name)
        self.set_subtitle(obj.unit)   
        
        #self.view.set_thickness(self.model.thickness)
        #self.view.set_color(self.model.color)

        #print 'drawing line...', track_controller.view.track.GetSize()


###############################################################################
###############################################################################
    

class IndexRepresentationController(RepresentationController):
    tid = 'index_representation_controller'
    
    def __init__(self):
        super(IndexRepresentationController, self).__init__()
    
        
class IndexRepresentationModel(UIModelBase):
    tid = 'index_representation_model' 
    _ATTRIBUTES = collections.OrderedDict()
    _ATTRIBUTES['step'] = {
            'default_value': 500.0,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Step'        
    }
    _ATTRIBUTES['pos_x'] = {
            'default_value': 0.5, 
            'type': float,
            'pg_property': 'EnumProperty',
            'label': 'Horizontal Alignment',
            'labels': ['Left', 'Center', 'Right'],
            'values': [0.1, 0.5, 0.9]
    }
    _ATTRIBUTES['fontsize'] = {
            'default_value': 11, 
            'type': int,
            'pg_property': 'EnumProperty',
            'label': 'Font Size',
            'labels': ['7', '8', '9', '10', '11', '12', '13'],
            'values': [7, 8, 9, 10, 11, 12, 13]
    }
    _ATTRIBUTES['color'] = {
            'default_value': 'Black',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Color',
            'labels': MPL_COLORS.keys()
    }    
    _ATTRIBUTES['bbox'] = {
            'default_value': True ,
            'type': bool,
            'pg_property': 'BoolProperty',
            'label': 'Bbox',
    }   
    _ATTRIBUTES['bbox_style'] = {
            'default_value': 'round', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Bbox Style',
            'labels': ['Circle', 'DArrow', 'LArrow', 'RArrow', 
                       'Round', 'Round4', 'Roundtooth', 'Sawtooth',
                       'Square'
            ],
            'values': ['circle', 'darrow', 'larrow', 'rarrow',
                       'round', 'round4', 'roundtooth', 'sawtooth',
                       'square'
            ]
    }
    _ATTRIBUTES['bbox_color'] = {
            'default_value': 'White',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Bbox Color',
            'labels': MPL_COLORS.keys()
    }         
    _ATTRIBUTES['bbox_alpha'] = {
            'default_value': 0.5,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Bbox Alpha'      
    }    
    _ATTRIBUTES['ha'] = {
            'default_value': 'center',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Horizontal Alignment in the TextBox',
            'labels': ['Left', 'Center', 'Right'],
            'values': ['left', 'center', 'right']
    } 
    _ATTRIBUTES['va'] = {
            'default_value': 'center',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Vertical Alignment in the TextBox',
            'labels': ['Top', 'Center', 'Bottom', 'Baseline'],
            'values': ['top', 'center', 'bottom', 'baseline']
    }             
    
    def __init__(self, controller_uid, **base_state): 
        super(IndexRepresentationModel, self).__init__(controller_uid, **base_state)           
        
        
        
class IndexRepresentationView(RepresentationView):
    tid = 'index_representation_view'

    def __init__(self, controller_uid):
        super(IndexRepresentationView, self).__init__(controller_uid)    
        if self.label:
            self.label.set_plot_type('index')              


    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        controller.subscribe(self._draw, 'change.step')    
        controller.subscribe(self._draw, 'change.pos_x') 
        controller.subscribe(self._draw, 'change.ha')
        controller.subscribe(self._draw, 'change.va')
        controller.subscribe(self._draw, 'change.fontsize')
        controller.subscribe(self._draw, 'change.color') 
        controller.subscribe(self._draw, 'change.bbox')
        controller.subscribe(self._draw, 'change.bbox_style')
        controller.subscribe(self._draw, 'change.bbox_color')
        controller.subscribe(self._draw, 'change.bbox_alpha')
        controller.subscribe(self._draw, 'change.zorder')
        try:
            self.draw()
        except:
            raise
            
    def _draw(self, new_value, old_value):
        # Bypass function
        self.draw()

    def get_data(self, event):
        # TODO: Criar funcao considerando MD, TVD e TVDSS
        return None        
        
    def draw(self):
        self.clear()
        self._mplot_objects['text'] = []
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #
        obj = controller.get_object()
        y_min = obj.min
        y_max = obj.max
        #
        if y_min%controller.model.step: 
            y_min = (y_min//controller.model.step + 1) * controller.model.step

        y_positions = np.arange(y_min, y_max, controller.model.step)
        for pos_y in y_positions:
            """
            Text(x=0, y=0, text='', color=None, verticalalignment='baseline', 
            horizontalalignment='left', multialignment=None, 
            fontproperties=None, rotation=None, linespacing=None, 
            rotation_mode=None, usetex=None, wrap=False, **kwargs)
            """
            text = track_controller._append_artist('Text', 
                                    controller.model.pos_x, pos_y,
                                    "%g"%pos_y,
                                    color=controller.model.color,
                                    horizontalalignment=controller.model.ha,
                                    verticalalignment=controller.model.va,
                                    fontsize=controller.model.fontsize
            )                        
            if controller.model.bbox:
                pad = 0.2
                boxstyle = controller.model.bbox_style
                """
                if boxstyle in ['round', 'round4']: 
                    tail = ',rounding_size=None'
                elif boxstyle in ['roundtooth', 'sawtooth']:   
                    tail = ',tooth_size=None'
                else:
                    tail = ''
                """    
                boxstyle += ",pad=%0.2f" % pad
                text._bbox_patch = FancyBboxPatch(
                                    (0., 0.),
                                    1., 1.,
                                    boxstyle=boxstyle,
                                    #transform=mtransforms.IdentityTransform(),
                                    color=controller.model.bbox_color,
                                    alpha=controller.model.bbox_alpha
                )                    
                #                     **props)
                # def __init__(self, xy, width, height,
                #  boxstyle="round",
                #  bbox_transmuter=None,
                #  mutation_scale=1.,
                #  mutation_aspect=None,
                #  **kwargs):
                # text.set_bbox(dict(color=controller.model.bbox_color, 
                #                   alpha=controller.model.bbox_alpha)
                #)
            #text.zorder = controller.model.zorder
            self._mplot_objects['text'].append(text)
        
        self.set_title(obj.name)
        self.set_subtitle(obj.unit)    
        self.draw_canvas()   


###############################################################################
###############################################################################

    
class DensityRepresentationController(RepresentationController):
    tid = 'density_representation_controller'
    
    def __init__(self):
        super(DensityRepresentationController, self).__init__()
        
    def PostInit(self):    
        self.subscribe(self.on_change_colormap, 'change.colormap')   
        self.subscribe(self.on_change_density_alpha, 
                                                       'change.density_alpha'
        )
        self.subscribe(self.on_change_wiggle_alpha, 
                                                       'change.wiggle_alpha'
        )
    
    def on_change_density_alpha(self, new_value, old_value):    
        if new_value >= 0.0 and new_value <= 1.0:
            self.view.set_density_alpha(new_value)
        else:
            self.model.set_value_from_event('density_alpha', old_value)
            
    def on_change_wiggle_alpha(self, new_value, old_value):      
        if new_value >= 0.0 and new_value <= 1.0:
            self.view.set_wiggle_alpha(new_value)
        else:
            self.model.set_value_from_event('wiggle_alpha', old_value)   
    
    def on_change_colormap(self, new_value, old_value):
        if new_value not in MPL_COLORMAPS:
            msg = 'Invalid colormap. Valid values are: {}'.format(MPL_COLORMAPS)
            print msg
            self.model.set_value_from_event('colormap', old_value)
        else:    
            self.view.set_colormap(new_value)     



    def get_iline_idx(self):
        obj = self.get_object()
        idx_iline = obj.dimensions[0][1].index(self.model.iline)
        return idx_iline


    def get_xline_idx(self):
        obj = self.get_object()
        idx_xline = obj.dimensions[1][1].index(self.model.xline)
        return idx_xline
    
    
    # TODO: Rever este nome horrivel...
    def get_previous_next_line(self):
        #UIM = UIManager() 
        obj = self.get_object()
        idx_iline = obj.dimensions[0][1].index(self.model.iline)
        if self.model.xline is None:
            # Default values
            prev_ = idx_iline - 1
            iline_next = idx_iline + 1
            # 
            if idx_iline == 0:
                iline_prev = None
            elif idx_iline == len(obj.dimensions[0][1]) - 1:  
                iline_next = None
            return (iline_prev, ), (iline_next, )
            
        else:    
            idx_xline = obj.dimensions[1][1].index(self.model.xline)
            # Default values
            prev_ = (obj.dimensions[0][1][idx_iline], obj.dimensions[1][1][idx_xline-1])
            try:
                next_ = (obj.dimensions[0][1][idx_iline], obj.dimensions[1][1][idx_xline+1])
            except:
                # esse valor alterado logo a frente
                next_ = None
            #
            if idx_xline == 0:
                if idx_iline == 0:
                    prev_ = None
                else:
                    prev_ = (obj.dimensions[0][1][idx_iline-1], obj.dimensions[1][1][-1])       
            elif idx_xline == len(obj.dimensions[1][1]) - 1: 
                if idx_iline == len(obj.dimensions[0][1]) - 1: 
                    next_ = None
                else:
                    next_ = (obj.dimensions[0][1][idx_iline+1], obj.dimensions[1][1][0])
            return prev_, next_



class DensityRepresentationModel(UIModelBase):
    tid = 'density_representation_model'

    _ATTRIBUTES = collections.OrderedDict()
    """
    _ATTRIBUTES['dimensions'] = {
            'default_value': None,
            'type': int,
            'pg_property': None
    }    
    """
    _ATTRIBUTES['iline'] = {
            'default_value': None,
            'type': int,
            'pg_property': 'IntProperty',
            'label': 'Iline' 
    }    
    _ATTRIBUTES['xline'] = {
            'default_value': None,
            'type': int,
            'pg_property': 'IntProperty',
            'label': 'Xline' 
    }   
    _ATTRIBUTES['offset'] = {
            'default_value': None,
            'type': int,
            'pg_property': 'IntProperty',
            'label': 'Xline' 
    }   
    _ATTRIBUTES['type'] = {
            'default_value': 'density', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Plot type',
            'labels': ['Density', 'Wiggle', 'Both'],  
            'values': ['density', 'wiggle', 'both']
    }    
    _ATTRIBUTES['colormap'] = {
            'default_value': 'gray',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Colormap',
            'labels': MPL_COLORMAPS
    }      
    _ATTRIBUTES['interpolation'] = {
            'default_value': 'bicubic', #'none', #'bilinear',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Colormap interpolation',
            'labels': ['none', 'nearest', 'bilinear', 'bicubic',
                      'spline16', 'spline36', 'hanning', 'hamming',
                      'hermite', 'kaiser', 'quadric', 'catrom',
                      'gaussian', 'bessel', 'mitchell', 'sinc',
                      'lanczos'
            ]  
    }       
    _ATTRIBUTES['min_density'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap min value'     
    }
    _ATTRIBUTES['max_density'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap max value' 
    }
    _ATTRIBUTES['density_alpha'] = {
            'default_value': 1.0,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Colormap alpha'
    }
    _ATTRIBUTES['linewidth'] = {
            'default_value': 1, 
            'type': int,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle line width',
            'labels': ['0', '1', '2', '3'],
            'values': [0, 1, 2, 3]
    }   
    _ATTRIBUTES['linecolor'] = {
            'default_value': 'Black',
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle line color',
            'labels': MPL_COLORS.keys()
    }    
    _ATTRIBUTES['min_wiggle'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle min value'
    }
    _ATTRIBUTES['max_wiggle'] = {
            'default_value': None,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle max value'
    }  
    _ATTRIBUTES['wiggle_alpha'] = {
            'default_value': 1.0,
            'type': float,
            'pg_property': 'FloatProperty',
            'label': 'Wiggle alpha'
    }    
    _ATTRIBUTES['fill'] = {
            'default_value': None,
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle fill type',
            'labels': ['None', 'Left', 'Right', 'Both'],  
            'values': [None, 'left', 'right', 'both']
    }      
    _ATTRIBUTES['fill_color_left'] = {
            'default_value': 'Red', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle left fill color',
            'labels': MPL_COLORS.keys()
    }       
    _ATTRIBUTES['fill_color_right'] = {
            'default_value': 'Blue', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Wiggle right fill color',
            'labels': MPL_COLORS.keys()
    }         
    
    def __init__(self, controller_uid, **base_state): 
        super(DensityRepresentationModel, self).__init__(controller_uid, **base_state)      
    


class DensityRepresentationView(RepresentationView):
    tid = 'density_representation_view'

    def __init__(self, controller_uid):
        super(DensityRepresentationView, self).__init__(controller_uid)   
        if self.label:
            self.label.set_plot_type('density')    
            

    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        #
        obj = controller.get_object()
        
        print '\nDensityRepresentationView.PostInit'
        print 'obj.data.shape:', obj.data.shape
        
        
        if len(obj.data.shape) == 5 and obj.tid == 'scalogram':
            controller.model.iline = obj.dimensions[0][1][0]
            controller.model.xline = obj.dimensions[1][1][0]
            controller.model.offset = obj.dimensions[2][1][0]  
        elif len(obj.data.shape) == 4:
            controller.model.iline = obj.dimensions[0][1][0]
            controller.model.xline = obj.dimensions[1][1][0]
        elif len(obj.data.shape) == 3:
            controller.model.iline = obj.dimensions[0][1][0]
        else:
            raise Exception('')
        
        
        controller.subscribe(self.set_iline, 'change.iline')
        if controller.model.xline is not None:
            controller.subscribe(self.set_xline, 'change.xline')
        
        #
        #controller.model.min_density = np.nanmin(obj.data)
        #controller.model.max_density = np.nanmax(obj.data)
        #
        
        print 'after'
        
        
        controller.subscribe(self._draw, 'change.type')    
        controller.subscribe(self.set_interpolation, 
                                                       'change.interpolation'
        ) 
        controller.subscribe(self._draw, 'change.min_density')   
        controller.subscribe(self._draw, 'change.max_density')  
        controller.subscribe(self.set_line_width, 'change.linewidth')   
        controller.subscribe(self.set_line_color, 'change.linecolor')   
        controller.subscribe(self.fill_between, 'change.fill') 
        
        controller.subscribe(self.fill_color_left, 
                                                   'change.fill_color_left'
        ) 
        controller.subscribe(self.fill_color_right, 
                                                   'change.fill_color_right'
        ) 
        controller.subscribe(self._draw, 'change.min_wiggle')   
        controller.subscribe(self._draw, 'change.max_wiggle')  
        
        print 000
        
        self.draw()
        
        
        
    def _draw(self, new_value, old_value):
        # Bypass function
        self.draw()  


    

    def set_iline(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        try:
            # Dummy test
            idx_iline = obj.dimensions[0][1].index(controller.model.iline)
            self.draw()
        except ValueError:
            # Undo operation
            controller.model.iline = old_value


    def set_xline(self, new_value, old_value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        try:
            # Dummy test
            idx_xline = obj.dimensions[1][1].index(controller.model.xline)
            self.draw()
        except ValueError:
            # Undo operation
            controller.model.xline = old_value


    #def get_data(self, event):
    #    print event.xdata, event.xdata, event
    #    return ''
        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        index_data = obj.get_index().data
        idx = (np.abs(index_data-event.ydata)).argmin()
        if not np.isfinite(obj.data[idx]):
            return None
        return obj.data[idx]
        """
      
    def set_colormap(self, colormap):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_cmap(colormap)
            self.label.set_colormap(colormap)
        self.draw_canvas()       

    def set_interpolation(self, new_value, old_value):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_interpolation(new_value)
        self.draw_canvas()                

    def set_density_alpha(self, alpha):
        if self._mplot_objects['density']:
            self._mplot_objects['density'].set_alpha(alpha)
        self.draw_canvas()

    def set_wiggle_alpha(self, alpha):
        if len(self._mplot_objects['wiggle']) == 0:
            return
        for idx in range(0, len(self._mplot_objects['wiggle'])):    
            self._mplot_objects['wiggle'][idx].set_alpha(alpha)
        self.draw_canvas()

    def set_line_color(self, new_value, old_value):
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            line.set_color(new_value)
        self.draw_canvas()   

    def set_line_width(self, new_value, old_value):
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            line.set_linewidth(new_value)
        self.draw_canvas()    

    def fill_color_left(self, new_value, old_value):
        for idx_fill_obj in range(1, len(self._mplot_objects['wiggle']), 3):
            fill_mpl_obj = self._mplot_objects['wiggle'][idx_fill_obj]
            if fill_mpl_obj:
                fill_mpl_obj.set_color(new_value)
        self.draw_canvas()        

    def fill_color_right(self, new_value, old_value):
        for idx_fill_obj in range(2, len(self._mplot_objects['wiggle']), 3):
            fill_mpl_obj = self._mplot_objects['wiggle'][idx_fill_obj]
            if fill_mpl_obj:
                fill_mpl_obj.set_color(new_value)
        self.draw_canvas()   


    def get_data(self, event):
        xdata = inverse_transform(event.xdata, self._x_lim_min, self._x_lim_max, 0)
        dim_name, dim_values = self._x_dim
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        idx_iline = obj.dimensions[0][1].index(controller.model.iline)
        
        index_data = obj.get_index().data
        idx_index = (np.abs(index_data-event.ydata)).argmin()
        
        #if not np.isfinite(obj.data[idx]):
        #    return None
        #return obj.data[idx]
        
        if controller.model.xline is not None:
            idx_xline = obj.dimensions[1][1].index(controller.model.xline)
            msg = '[Iline: ' + str(controller.model.iline) + \
                ', Xline: ' + str(controller.model.xline) + \
                ', ' + dim_name + ': ' + str(dim_values[int(xdata)]) + \
                ', Amplitude: ' + str(obj.data[idx_iline][idx_xline][int(xdata)][idx_index]) + ']'
        else:
            msg = '[Iline: ' + str(controller.model.iline) + \
                ', ' + dim_name + ': ' + str(dim_values[int(xdata)]) + \
                ', Amplitude: ' + str(obj.data[idx_iline][int(xdata)][idx_index])  + ']'
        return msg
     
        
        
        
    def draw(self):
        print '\ndraw'
        self.clear()
        self._mplot_objects['density'] = None
        self._mplot_objects['wiggle'] = []
        #
        print 1
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        print 2
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        print 3
        #
        obj = controller.get_object()
        print 4
        index = obj.get_index()
        print 5
        #
        self.set_title(obj.name)
        #
        print 111, controller.model.iline
        print obj.dimensions[0][1]
        
        idx_iline = obj.dimensions[0][1].index(controller.model.iline)
        
        
        if controller.model.xline is not None:
            print 'if xline'
            idx_xline = obj.dimensions[1][1].index(controller.model.xline)
        
            if controller.model.offset is not None:
                print 'if offset'
                idx_offset = obj.dimensions[2][1].index(controller.model.offset)
                data = np.copy(obj.data[idx_iline][idx_xline][idx_offset])
                self._x_dim = obj.dimensions[3]
            else:
                data = np.copy(obj.data[idx_iline][idx_xline])
                self._x_dim = obj.dimensions[2]               
            
        else:    
            print 'else'
            data = np.copy(obj.data[idx_iline])
            self._x_dim = obj.dimensions[1]
            
        print 'fim ifelse'    
        #
        self._x_lim_min = 0.0
        self._x_lim_max = data.shape[0]
        #    
        print 222
        
        
        if controller.model.type == 'density' or controller.model.type == 'both':
            # 0,0 and 1.0 are our fixed Axes x_lim
            extent = (0.0, 1.0, index.max, index.min)   

            image = track_controller._append_artist('AxesImage',
                                            cmap=controller.model.colormap,
                                            interpolation=controller.model.interpolation,
                                            extent=extent
            )
            image.set_data(data.T)
            image.set_label(self._controller_uid)
            #
            #AxesImage(ax, cmap=None, norm=None, interpolation=None, 
                       #origin=None, extent=None, filternorm=1, 
                       #filterrad=4.0, resample=False, **kwargs)
            #
            #mpl_obj.set_label(toc_uid)
            #self.label.set_plot_type('density') 
            
            if image.get_clip_path() is None:
                # image does not already have clipping set, clip to axes patch
                image.set_clip_path(image.axes.patch)     
            self._mplot_objects['density'] = image
            if controller.model.min_density is None:
                controller.model.set_value_from_event('min_density', np.nanmin(data))
            if controller.model.max_density is None:    
                controller.model.set_value_from_event('max_density', np.nanmax(data))
            image.set_clim(controller.model.min_density, controller.model.max_density)
            self.set_density_alpha(controller.model.density_alpha)  
            #
            if self.label:
                self.label.set_colormap(controller.model.colormap)
                self.label.set_zlim((controller.model.min_density, 
                                                 controller.model.max_density)
                )
            #    
        else:
            self._mplot_objects['density'] = None
        #
        #
        if controller.model.type == 'wiggle' or controller.model.type == 'both':    
            self._lines_center = []
            x_lines_position = transform(np.array(range(0, self._x_lim_max)),
                                         self._x_lim_min, self._x_lim_max
            )
            print 'x_lines_position:', x_lines_position, len(x_lines_position)
            if len(x_lines_position) > 1:
                increment = (x_lines_position[0] + x_lines_position[1]) / 2.0 
            elif len(x_lines_position) == 1:
                increment = 0.5
            else:
                raise Exception('Error. x_lines_position cannot have lenght 0. Shape: {}'.format(data.shape))
    
            if controller.model.min_wiggle == None:
                controller.model.set_value_from_event('min_wiggle',
                                                      (np.amax(np.absolute(data))) * -1)  
            if controller.model.max_wiggle == None:
                controller.model.set_value_from_event('max_wiggle', 
                                                      np.amax(np.absolute(data)))     
                
            data = np.where(data<0, data/np.absolute(controller.model.min_wiggle), data)
            data = np.where(data>0, data/controller.model.max_wiggle, data)
    
            for idx, pos_x in enumerate(x_lines_position):
                self._lines_center.append(pos_x + increment) 
                xdata = data[idx]
                xdata = self._transform_xdata_to_wiggledata(xdata, pos_x, pos_x + 2*increment)
                line = track_controller._append_artist('Line2D', xdata, index.data,
                                            linewidth=controller.model.linewidth,
                                            color=controller.model.linecolor
                                            )
                #line.set_label(toc_uid)
                self._mplot_objects['wiggle'].append(line)   
                self._mplot_objects['wiggle'].append(None) # left fill
                self._mplot_objects['wiggle'].append(None) # right fill
            
            #self.label.set_zlim((controller.model.zmin, controller.model.zmax))      
            #self.draw_canvas()
            
        #self.set_zlim(controller.model.zmin, controller.model.zmax)
        self.draw_canvas()
        #
        self.fill_between(controller.model.fill, None)

    
    # Find a better name
    def _transform_xdata_to_wiggledata(self, values, axes_left, axes_right):
        # Normalizing values
        center = (axes_left + axes_right) / 2.0
        lim = axes_right - center
        return lim * values + center    


    def _remove_fillings(self, type_='both'):
        for idx in range(0, len(self._mplot_objects['wiggle']), 3):
            left_fill = self._mplot_objects['wiggle'][idx+1]
            right_fill = self._mplot_objects['wiggle'][idx+2]         
            if left_fill is not None and type_ in ['left', 'both']:
                left_fill.remove()
                self._mplot_objects['wiggle'][idx+1] = None         
            if right_fill is not None and type_ in ['right', 'both']:
                right_fill.remove()
                self._mplot_objects['wiggle'][idx+2] = None
        self.draw_canvas()
    
    
    def fill_between(self, new_value, old_value):
        fill_type = new_value
        self._remove_fillings()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        for idx_line in range(0, len(self._mplot_objects['wiggle']), 3):
            line = self._mplot_objects['wiggle'][idx_line]
            left_fill = self._mplot_objects['wiggle'][idx_line+1]
            right_fill = self._mplot_objects['wiggle'][idx_line+2]
            axis_center = self._lines_center[idx_line/3]
            left_fill = None
            if fill_type == 'left' or fill_type == 'both':
                left_fill = self._my_fill(line.axes,
                                                line.get_ydata(),                                     
                                                line.get_xdata(), 
                                                axis_center,
                                                where=line.get_xdata() <= axis_center,
                                                facecolor=controller.model.fill_color_left,
                                                interpolate=True
                )
                
            right_fill = None    
            if fill_type == 'right' or fill_type == 'both':
                right_fill = self._my_fill(line.axes,
                                                line.get_ydata(),                                      
                                                line.get_xdata(), 
                                                axis_center,
                                                where=line.get_xdata() >= axis_center,
                                                facecolor=controller.model.fill_color_right,
                                                interpolate=True
                )
            self._mplot_objects['wiggle'][idx_line+1] = left_fill
            self._mplot_objects['wiggle'][idx_line+2] = right_fill
        self.draw_canvas()    
    
    
    def _my_fill(self, axes, y, x1, x2=0, where=None, interpolate=False, step=None, **kwargs):
        
        if not matplotlib.rcParams['_internal.classic_mode']:
            color_aliases = mcoll._color_aliases
            kwargs = cbook.normalize_kwargs(kwargs, color_aliases)

            if not any(c in kwargs for c in ('color', 'facecolors')):
                fc = axes._get_patches_for_fill.get_next_color()
                kwargs['facecolors'] = fc
        
        # Handle united data, such as dates
        axes._process_unit_info(ydata=y, xdata=x1, kwargs=kwargs)
        axes._process_unit_info(xdata=x2)

        # Convert the arrays so we can work with them
        y = ma.masked_invalid(axes.convert_yunits(y))
        x1 = ma.masked_invalid(axes.convert_xunits(x1))
        x2 = ma.masked_invalid(axes.convert_xunits(x2))

        if x1.ndim == 0:
            x1 = np.ones_like(y) * x1
        if x2.ndim == 0:
            x2 = np.ones_like(y) * x2

        if where is None:
            where = np.ones(len(y), np.bool)
        else:
            where = np.asarray(where, np.bool)

        if not (y.shape == x1.shape == x2.shape == where.shape):
            raise ValueError("Argument dimensions are incompatible")

        mask = reduce(ma.mask_or, [ma.getmask(a) for a in (y, x1, x2)])
        if mask is not ma.nomask:
            where &= ~mask

        polys = []
        
        for ind0, ind1 in mlab.contiguous_regions(where):
            #i += 1
            #print i
            yslice = y[ind0:ind1]
            x1slice = x1[ind0:ind1]
            x2slice = x2[ind0:ind1]
            if step is not None:
                step_func = cbook.STEP_LOOKUP_MAP[step]
                yslice, x1slice, x2slice = step_func(yslice, x1slice, x2slice)

            if not len(yslice):
                continue

            N = len(yslice)
            Y = np.zeros((2 * N + 2, 2), np.float)
           
            if interpolate:
                def get_interp_point(ind):
                    im1 = max(ind - 1, 0)
                    y_values = y[im1:ind + 1]
                    diff_values = x1[im1:ind + 1] - x2[im1:ind + 1]
                    x1_values = x1[im1:ind + 1]

                    if len(diff_values) == 2:
                        if np.ma.is_masked(diff_values[1]):
                            return y[im1], x1[im1]
                        elif np.ma.is_masked(diff_values[0]):
                            return y[ind], x1[ind]

                    diff_order = diff_values.argsort()
                    diff_root_y = np.interp(0, diff_values[diff_order], y_values[diff_order])
                    diff_root_x = np.interp(diff_root_y, y_values, x1_values)
                    return diff_root_x, diff_root_y

                start = get_interp_point(ind0)
                end = get_interp_point(ind1)
            else:
                # the purpose of the next two lines is for when x2 is a
                # scalar like 0 and we want the fill to go all the way
                # down to 0 even if none of the x1 sample points do
                start = x2slice[0], yslice[0] #Y[0] = x2slice[0], yslice[0]
                end = x2slice[-1], yslice[-1] #Y[N + 1] = x2slice[-1], yslice[-1]

            Y[0] = start
            Y[N + 1] = end

            Y[1:N + 1, 0] = x1slice
            Y[1:N + 1, 1] = yslice
            Y[N + 2:, 0] = x2slice[::-1]
            Y[N + 2:, 1] = yslice[::-1]

            polys.append(Y)

        collection = mcoll.PolyCollection(polys, **kwargs)

        # now update the datalim and autoscale
        X1Y = np.array([x1[where], y[where]]).T
        X2Y = np.array([x2[where], y[where]]).T
        axes.dataLim.update_from_data_xy(X1Y, axes.ignore_existing_data_limits,
                                         updatex=True, updatey=True)
        axes.ignore_existing_data_limits = False
        axes.dataLim.update_from_data_xy(X2Y, axes.ignore_existing_data_limits,
                                         updatex=True, updatey=False)
        axes.add_collection(collection, autolim=False)
        axes.autoscale_view()
        return collection 

    

    # ATENCAO COM XLIM - TRANSFORM IT!!!!
    """
    def set_data(self, xdata, ydata):
        if len(xdata.shape) == 1:
            xdata = xdata[np.newaxis, :]
        if len(xdata.shape) == 2:
            xdata = xdata[np.newaxis, :]
            

            
        x, y, z = xdata.shape 
        data = xdata.reshape((x*y, z))
        
        ymin = np.nanmin(ydata)
        ymax = np.nanmax(ydata)
        # 0,0 and 1.0 are our fixed Axes x_lim
        extent = (0.0, 1.0, ymax, ymin)
       # print 'extent:', extent, data.shape
        
#        self._mplot_objects[0].axes.set_aspect('auto')
        self._mplot_objects[0].set_data(data.T)
#        self._mplot_objects[0].set_alpha(1.0)
        
        if self._mplot_objects[0].get_clip_path() is None:
            # image does not already have clipping set, clip to axes patch
            self._mplot_objects[0].set_clip_path(self._mplot_objects[0].axes.patch)
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)        
        if controller.model.zmin is None:
            controller.model.zmin = np.nanmin(xdata)
        if controller.model.zmax is None:    
            controller.model.zmax = np.nanmax(xdata)   
        self.set_zlim(controller.model.zmin, controller.model.zmax)
        
           
        self.draw_canvas()   
        self.label.set_zlim((controller.model.zmin, controller.model.zmax))   
    """    

    """
    def _get_data(self, x, y):
        # Based on AxesImage.get_cursor_data
        #'''Get the cursor data for given event xdata and ydata'''
        xmin, xmax, ymin, ymax = self._mplot_objects[0].get_extent()
        if self._mplot_objects[0].origin == 'upper':
            ymin, ymax = ymax, ymin
        # get_array is a cm.ScalarMappable function
        arr = self._mplot_objects[0].get_array()
        data_extent = Bbox([[ymin, xmin], [ymax, xmax]])
        array_extent = Bbox([[0, 0], arr.shape[:2]])
        trans = BboxTransform(boxin=data_extent,
                              boxout=array_extent)
        i, j = trans.transform_point([y, x]).astype(int)
        # Clip the coordinates at array bounds
        if not (0 <= i < arr.shape[0]) or not (0 <= j < arr.shape[1]):
            return None
        else:
            # returning X index, Y index and value(Z)
            return j, i, arr[i, j]
    """    


###############################################################################
###############################################################################


class PatchesRepresentationController(RepresentationController):
    tid = 'patches_representation_controller'
    
    def __init__(self):
        super(PatchesRepresentationController, self).__init__()

        
class PatchesRepresentationModel(UIModelBase):
    tid = 'patches_representation_model'
    
    _ATTRIBUTES = {}        
    
    #TODO: Retirar esse model???
    
    def __init__(self, controller_uid, **base_state): 
        super(PatchesRepresentationModel, self).__init__(controller_uid, **base_state)      
    


class PatchesRepresentationView(RepresentationView):
    tid = 'patches_representation_view'

    def __init__(self, controller_uid):
        super(PatchesRepresentationView, self).__init__(controller_uid)      
        if self.label:
            self.label.set_plot_type('partition')   

    def PostInit(self):
        self.draw()


    def get_data(self, event):
        OM = ObjectManager(self)
        for part_uid, collection in self._mplot_objects.items():
            result, dict_ = collection.contains(event)
            if result:
                obj = OM.get(part_uid)
                return obj.name #OM._getparentuid(part_uid), obj.name #, dict_
 
    
    def draw(self):        
        self.clear()
        #
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #
        obj = controller.get_object()
        index = obj.get_index()
        
        for part in obj.list('part'):
            vec = []        
            start = None
            end = None
            for idx, d in enumerate(part.data):
                if d and start is None:
                    start = index.data[idx]
                elif not d and start is not None:
                    end = index.data[idx-1]
                  #  print (start, end)
                    vec.append((start, end))
                    start = None
                    
            #color = colorConverter.to_rgba(part.color)
            #print color
            patches = [] 
            mpl_color = [float(c)/255.0 for c in part.color]
            for start, end in vec:
                patch = track_controller._append_artist('Rectangle',  (0.0, start),
                                    1.0, end-start,
                                    #color=mpl_color
                )
                patches.append(patch)
            
            collection = track_controller._append_artist('PatchCollection', 
                                                         patches, 
                                                         color=mpl_color
            )
            self._set_picking(collection, 0)
            self._mplot_objects[part.uid] = collection
           
        self.set_title(obj.name)    
        self.set_subtitle('partition')
        self.draw_canvas()

        #print part.name
        #print part.color
        #print part.data
        #print
        #print obj.getaslog()
        
        #track_controller._append_artist('Rectangle',  (0.0, 3000.0),
        #                                1.0, 2000.0,
        #                                color='red')


        #axes.add_collection(collection, autolim=False)
        
        
    
        # Rectangle(xy, width, height, angle=0.0, **patch_props)
        # Patch(edgecolor=None, facecolor=None, color=None, linewidth=None,
        #      linestyle=None, antialiased=None, hatch=None, fill=True,
        #      capstyle=None, joinstyle=None, **artist_props)
               





##  NOVA CLASSE


class ContourfRepresentationController(RepresentationController):
    tid = 'contourf_representation_controller'
    
    def __init__(self):
        print '\n\nContourfRepresentationController'
        super(ContourfRepresentationController, self).__init__()
        


    
class ContourfRepresentationModel(UIModelBase):
    tid = 'contourf_representation_model'

    _ATTRIBUTES = collections.OrderedDict() 

    
    def __init__(self, controller_uid, **base_state): 
        super(ContourfRepresentationModel, self).__init__(controller_uid, **base_state)      
    


class ContourfRepresentationView(RepresentationView):
    tid = 'contourf_representation_view'

    def __init__(self, controller_uid):
        super(ContourfRepresentationView, self).__init__(controller_uid)   

        print '\n\nContourfRepresentationView'
        
        if self.label:
            self.label.set_plot_type('density')    

    def PostInit(self):
        self.draw()        


    def get_data(self, event):
        pass
        #print event.xdata, event.ydata
        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        obj = controller.get_object()
        index_data = obj.get_index().data
        idx = (np.abs(index_data-event.ydata)).argmin()
        if not np.isfinite(obj.data[idx]):
            return None
        return obj.data[idx]
        """
    
    
    def draw(self):
        self.clear()
        self._mplot_objects['contourf'] = None
        #
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #

        obj = controller.get_object()
        index = obj.get_index()

        print 111
   
        '''
        x_axis = obj.attributes.get('frequencies')
        #x_axis = x_axis/x_axis[-1]
        y_axis = index.data
        mesh_y, mesh_x = np.meshgrid(y_axis, x_axis)
        '''
        
        '''
        x_axis = wa.fourier_frequencies
        y_axis = wa.time
        mesh_y, mesh_x = np.meshgrid(y_axis, x_axis)



        print x_axis
        print y_axis
        
        mesh_y, mesh_x = np.meshgrid(y_axis, x_axis)
        '''
        print 777
        
        #plt.contourf(mesh_x, mesh_y, to_plot, 20, cmap=plt.cm.jet)
        
        
        '''
        import matplotlib.pyplot as plt
        plt.subplot(1, 1, 1)
        plt.title("Theta_pp")
        CTPP = plt.contourf(np.rot90(obj.data, 1))
        
        print index.max*1000
        
        #plt.ylim(index.max*1000, 0)
        #plt.xlim(0, obj.data.shape[0]-1)
        plt.colorbar(CTPP, format='%.1f')
        
        plt.show()
        '''
        
        #print index.max, index.min
        extent = (0, obj.data.shape[0]-1, index.max*1000, index.min*1000) 
        #extent = (index.max*1000, index.min*1000, 0, obj.data.shape[0]-1) 
        
        data = obj.data
        data = np.rot90(data, 1)
        #data = data.T
        
        contourf = track_controller._append_artist('contourf', 
                                                   data, #, 20,
                                                   extent=extent
        )
                                        #cmap=controller.model.colormap
        #)

        contourf.ax.set_xlim(0, obj.data.shape[0]-1)
        #contourf.ax.set_ylim(0, obj.data.shape[0])
        #contourf.ax.set_xscale('log')
        
        '''
        corners = (x_axis[0], index.min), (x_axis[-1], index.max)
        
        ax.update_datalim(corners)
        ax.autoscale_view()
        '''
        
        self._mplot_objects['contourf'] = contourf    
        self.set_title(obj.name)
        self.draw_canvas()


    
#       
# My model for classes...       
#
"""
class DensityRepresentationController(RepresentationController):
    tid = 'density_representation_controller'
    
    def __init__(self):
        super(DensityRepresentationController, self).__init__()

    def _populate_model(self):
        pass
        #obj = self.get_object() 
        #self.view.label.set_data(obj.name, 'index', None, unit=obj.unit)
        #self.model.y_min = obj.min
        #self.model.y_max = obj.max
        
    def _do_display(self):  
        pass
        #self.view._show()
         
    def get_data(self, x, y):
        return None

    def get_data_array(self):
        return None

    def on_change_property(self, **kwargs):        
        pass
    
    
class DensityRepresentationModel(UIModelBase):
    tid = 'density_representation_model'

    _ATTRIBUTES = {               
    }
    
    def __init__(self, controller_uid, **base_state): 
        super(DensityRepresentationModel, self).__init__(controller_uid, **base_state)      
    


class DensityRepresentationView(RepresentationView):
    tid = 'density_representation_view'

    def __init__(self, controller_uid):
        super(DensityRepresentationView, self).__init__(controller_uid)        
        self.label.set_plot_type('index')   
        
"""        
