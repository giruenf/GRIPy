# -*- coding: utf-8 -*-
from OM.Manager import ObjectManager
from OM.Objects import GenericObject
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 

from DT.DataTypes import Density

# TODO: verificar se linhas abaixo devem ser mantidas
import Parms
import numpy as np

from scipy.interpolate import interp1d

import numpy.ma as ma
import matplotlib.mlab as mlab
import matplotlib.collections as mcoll
import matplotlib.cbook as cbook 
import matplotlib
                                   
from matplotlib.patches import FancyBboxPatch
import collections                                      
                                          
from App.app_utils import MPL_COLORS, MPL_COLORMAPS


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
    'data_index': 'index',
    'seismic': 'density',
    'partition': 'patches',
    'scalogram': 'density',
    'gather_scalogram': 'density',
    'spectogram': 'density',
    'gather_spectogram': 'density',
    'velocity': 'density',
    'gather': 'density',
    'angle': 'contourf',
    'model1d': 'density'
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


class DataFilter(GenericObject):
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_filter'
    _TID_FRIENDLY_NAME = 'Data Filter'
    
    SHOW_ON_TREE = False
    
    
    def __init__(self, objuid):
        super(DataFilter, self).__init__()
        self.data = []
        self.track_obj_ctrls_uids = []
        self.append_objuid(objuid)

    
    def append_objuid(self, track_obj_ctrl_uid):
        if track_obj_ctrl_uid in self.track_obj_ctrls_uids:
            raise Exception('Object was added before.')
        try:
            UIM = UIManager()
            track_obj_ctrl = UIM.get(track_obj_ctrl_uid)
            obj = track_obj_ctrl.get_object()
            #if obj.tid == 'data_index':
            #    self.data.append((obj.uid, True, True, 0, len(obj.data)))
            #else:
            self.set_z_dimension_index(track_obj_ctrl_uid)
            #index_set = OM.get(obj.index_set_uid)
        #    print 'HERE:', obj.uid
            data_indexes = obj.get_data_indexes()
        #    print '\ndata_indexes:', data_indexes
            for dim_idx in range(1, len(data_indexes)):
                dim_idx_indexes = data_indexes[dim_idx]
                chosen_index = dim_idx_indexes[0]
                if dim_idx == 1:   
                    self.data.append((chosen_index.uid, True, True, 0, len(chosen_index.data)))
                else:
                    self.data.append((chosen_index.uid, False, False, 0, len(chosen_index.data)))
            #                
            self.track_obj_ctrls_uids.append(track_obj_ctrl_uid) 
        except Exception as e:
            print ('ERROR:', e)
            raise e     


    def set_z_dimension_index(self, track_obj_ctrl_uid):
        UIM = UIManager()
        track_obj_ctrl = UIM.get(track_obj_ctrl_uid)
        obj = track_obj_ctrl.get_object()

        track_ctrl_uid = UIM._getparentuid(track_obj_ctrl.uid)
        logplot_ctrl_uid = UIM._getparentuid(track_ctrl_uid)
        logplot_ctrl = UIM.get(logplot_ctrl_uid)
        
      #  print '\nobj.get_data_indexes() set_Z(181):', obj.uid
      #  print '\nobj.get_data_indexes():', obj.get_data_indexes(), '\n'
        z_axis_candidate_indexes = obj.get_data_indexes()[0]
        chosen_index = None
        
      #  for candidate_index in z_axis_candidate_indexes:
      #      print candidate_index
        
      #  print '\nFOIIII\n'
        
        for candidate_index in z_axis_candidate_indexes:
            if candidate_index.datatype == logplot_ctrl.model.index_type:
                chosen_index = candidate_index     
                break
        try:    
            if chosen_index is None:
                self.data[0] = (None, True, True, 0, 0)
            else:    
                self.data[0] = (chosen_index.uid, True, True, 0, len(chosen_index.data))     
        except IndexError as ie:
            if len(self.data) > 0:
                raise ie
            if chosen_index is None:
                self.data.append((None, True, True, 0, 0))
         #       print 'APPEND NONE'
                
            else:    
                self.data.append((chosen_index.uid, True, True, 0, len(chosen_index.data)))   
        #        print 'APPEND', chosen_index.uid

    def reload_z_dimension_indexes(self):  
        for track_obj_ctrl_uid in self.track_obj_ctrls_uids:
            self.set_z_dimension_index(track_obj_ctrl_uid)


    def reload_data(self):
       # print 'reload_data'
        UIM = UIManager()
        for toc_uid in self.track_obj_ctrls_uids:
            toc = UIM.get(toc_uid)
            toc._do_draw()
       # print 'reload_data end'    


###############################################################################
###############################################################################



class TrackObjectController(UIControllerBase):
    tid = 'track_object_controller'
    
    def __init__(self):
        super(TrackObjectController, self).__init__()
        self.subscribe(self.on_change_objtid, 'change.obj_tid')        
        self.subscribe(self.on_change_objoid, 'change.obj_oid')
        self.subscribe(self.on_change_plottype, 'change.plottype')
   
    
    def PostInit(self):
        UIM = UIManager()
        if self.model.pos == -1:
            track_ctrl_uid = UIM._getparentuid(self.uid)
            self.model.pos = len(UIM.list(self.tid, track_ctrl_uid))     

                 
    def PreDelete(self):
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
        if old_value is not None:
            if self.model.obj_tid:
                self.detach((old_value, self.model.obj_oid))
            self.model.obj_oid = None
            # Exclude any representation, if exists
            #self.model.plottype = None


    def on_change_objoid(self, new_value, old_value):
        # Exclude any representation, if exists
        if old_value is not None:
            self.detach((self.model.obj_tid, old_value))
        self.model.plottype = None
        obj = self.get_object()
        if obj:
            if obj.tid != 'partition':
                self.set_filter()
            plottype = _PREFERRED_PLOTTYPES.get(obj.tid)
            self.model.plottype = plottype       
            self.attach(obj.uid)


    def get_filter(self):
        try:
            OM = ObjectManager(self)
            return OM.get(('data_filter', self.model.data_filter_oid))
        except:
            return None


    def set_filter(self, filter_oid=None):
        if filter_oid is None:
            OM = ObjectManager(self)
            filter_ = OM.new('data_filter', self.uid)
            OM.add(filter_)
            self.model.data_filter_oid = filter_.oid
        else:
            if self.model.data_filter_oid:
                raise Exception('TRATAR EXCLUSAO FILTER')
            self.model.data_filter_oid = filter_oid    
    
    
    def on_change_plottype(self, new_value, old_value):
        #print 'on_change_plottype', new_value, old_value
        UIM = UIManager()
        repr_ctrl = self.get_representation()
        if repr_ctrl:
            UIM.remove(repr_ctrl.uid)  
        if new_value is not None:
            repr_tid = _PLOTTYPES_REPRESENTATIONS.get(new_value)
            try:
                state = self._get_log_state()
                UIM.create(repr_tid, self.uid, **state)
                self._do_draw()
            except Exception as e:    
                self.model.plottype = None    
                raise e
                            
                
    def _do_draw(self):
      #  print '\n\nTrackObjectController._do_draw'
        repr_ctrl = self.get_representation() 
        if self.get_object().tid != 'partition':
            repr_ctrl._prepare_data() 
      #  print 'CALL draw'    
        repr_ctrl.view.draw()       
      #  print 'CALL end'


    def _get_log_state(self):
        # TODO: Rever necessidade de obj.name - ParametersManager
        state = {}
        obj = self.get_object()
        if obj.tid == 'log':
            # TODO: Rever isso
            parms = Parms.ParametersManager.get().get_curvetype_visual_props(obj.datatype)     
            if parms is not None:
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
                if obj.name == 'LOG_TESTE_CURVE':
                    state['x_scale'] = 1
                    ls, rs = (0.01, 100000.0)
                else:    
                    state['x_scale'] = 0
                    ls, rs = calculate_extremes(obj)
                state['left_scale'] = ls
                state['right_scale'] = rs
        return state
    
    
    #'''
    #TODO: passar pelo navigator
    def get_data_info(self, event):
        repr_ctrl = self.get_representation()
        if not repr_ctrl:
            return None        
        return repr_ctrl.get_data_info(event)
    #'''
    

    def get_representation(self):
        # Returns the real Impl_object LogPlot representation
        UIM = UIManager()
        children = UIM.list(None, self.uid)
        if len(children) == 0:
            return None
        return children[0]


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
        print (event)
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

    _ATTRIBUTES['selected'] = {
            'default_value': False,
            'type': bool    
    } 
    
    _ATTRIBUTES['data_filter_oid'] = {
            'default_value': None,
            'type': int
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
        self._data = None
        #self._indexes = None
        self._fixed_indexes = None
        
        
    def get_object(self):
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid) 
        return toc.get_object()


    def _prepare_data(self):
        
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid)
        #
        filter_ = toc.get_filter()
        data_indexes = filter_.data[::-1]
        
        #print 'data_indexes[-1]:', data_indexes[-1]
        #
        if data_indexes[-1][0] is None:
            self._data = None
            return            
        #
        obj = toc.get_object() 
        data = obj.data
        
        #print '\nRepresentationController._prepare_data:', obj.uid
        
        slicer = collections.OrderedDict()
        for (di_uid, display, is_range, first, last) in data_indexes:
          #  print di_uid, display, is_range, first, last
            if not is_range:
                slicer[di_uid] = first
            else:
                slicer[di_uid] = slice(first,last)
        slicer = tuple(slicer.values())
        data = data[slicer]
        new_dim = 1
        if len(data.shape) == 1 and isinstance(obj, Density):
            data = data[np.newaxis, :]
        elif len(data.shape) > 2:
            for dim_value in data.shape[::-1][1::]:
                new_dim *= dim_value
            data = data.reshape(new_dim, data.shape[-1])
        """    
        try:
            if self.model.min_density is None:
                self.model.set_value_from_event('min_density', np.nanmin(data))
            if self.model.max_density is None:    
                self.model.set_value_from_event('max_density', np.nanmax(data))
            if self.model.min_wiggle is None:    
                self.model.set_value_from_event('min_wiggle', np.nanmin(data))
            if self.model.max_wiggle is None:     
                self.model.set_value_from_event('max_wiggle', np.nanmax(data))
        except:
            pass
        """
        self._data = data
        
       # print self._data
       # print



    def _get_z_index(self, ydata):   
        
        if self._data is None:
            # When we have differents z_axis (e.g. Wellplot as TVD e Log with data_axis as MD)
            return None
        #
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid) 
        #
        OM = ObjectManager(self)
        filter_ = toc.get_filter() #OM.get(('data_filter', toc.model.data_filter_oid))
        z_data = filter_.data[0]
        #
        
        #print 'filter_.data[0]:', z_data  
        
        di_uid, display, is_range, z_first, z_last = z_data
        z_data_index = OM.get(di_uid)
        z_data = z_data_index.data[z_first:z_last]
        z_index = (np.abs(z_data-ydata)).argmin()
        if z_index == 0:
            if np.abs(ydata - z_data[z_index]) > np.abs(z_data[1] - z_data[0]):
                return None
        if z_index == self._data.shape[-1]-1:
            if np.abs(ydata - z_data[z_index]) > np.abs(z_data[-1] - z_data[-2]):
                return None
            
        #print '\n_get_z_index:', ydata, z_index    
        return z_index

       
    def get_data_info(self, event):
        return self.view.get_data_info(event)

    #"""
    def redraw(self):
        if isinstance(self, LineRepresentationController):
            self.view.draw()
        else:
            return False
        #return self.view.draw_canvas()
    #"""    
        
    '''
    # TODO: rever esse nome horrivel
    # TODO: tirar a duplicidade de chamadas e substituir por esse metodo nas ocorrencias abaixo
    #       pesquisar por "argmin"
    def get_index_idx(self, value):
        obj = self.get_object()
        index_data = obj.get_index().data
        idx_index = (np.abs(index_data-value)).argmin()
        return idx_index 
    ''' 
       
    
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
        
    def get_data_info(self, event):
        raise NotImplemented('{}.get_data_info must be implemented.'.format(self.__class__))
    
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


    #'''
    def get_data_info(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        z_index = controller._get_z_index(event.ydata)
        if z_index is None:
            return None
        return str(controller._data[z_index])


    def on_change_xscale(self, new_value, old_value):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        if new_value == 1:
            if controller.model.left_scale is None or \
                                            controller.model.left_scale <= 0.0:
                controller.model.set_value_from_event('left_scale', 0.2)
        self.set_xscale(new_value) 

    def set_zorder(self, new_value, old_value):
        if len(self._mplot_objects.values()) == 1:
            self._mplot_objects['line'].set_zorder(new_value)
            self.draw_canvas()
                
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
      #  print '\nLineRepresentationView.draw()'
        
        if len(self._mplot_objects.values()) == 1:
            self.clear()
        #     
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        OM = ObjectManager(self)
        obj = controller.get_object()
        #
        if self.label:
            self.label.set_plot_type('line')
            self.label.set_xlim(
                (controller.model.left_scale, controller.model.right_scale)
            ) 
            self.label.set_color(controller.model.color)
            self.label.set_thickness(controller.model.thickness)    
        self.set_title(obj.name)
        self.set_subtitle(obj.unit)          
        #
        if controller._data is None:
            return
        #
        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)        
        #
        OM = ObjectManager(self)
        obj = controller.get_object()
        
        filter_ = toc.get_filter()
        z_data = filter_.data[0]
        di_uid, display, is_range, z_first, z_last = z_data
        
        z_data_index = OM.get(di_uid)
        z_data = z_data_index.data[z_first:z_last]
        #
        transformated_xdata = transform(controller._data, controller.model.left_scale, 
                    controller.model.right_scale, controller.model.x_scale)
        #
        self.interpolate = True
        if self.interpolate:
            f1 = interp1d(z_data, transformated_xdata)     
            depth_list = []
            for depth_px in range(track_controller.view.track.GetSize()[1]):
                depth = track_controller.view.track.get_depth_from_ypixel(depth_px)
                
                if depth > np.nanmin(z_data) and depth < np.nanmax(z_data): #obj.start and depth < obj.end:
                    depth_list.append(depth)
                    
            if not self._mplot_objects.get('line'):
                line = track_controller._append_artist('Line2D', f1(depth_list), 
                            depth_list, linewidth=controller.model.thickness,
                            color=controller.model.color
                )
            else:
                line = self._mplot_objects.get('line')   
                line.set_data(f1(depth_list), depth_list)
        else:
            if not self._mplot_objects.get('line'):
                line = track_controller._append_artist('Line2D', transformated_xdata, 
                            z_data, linewidth=controller.model.thickness,
                            color=controller.model.color
                )
            else:
                line = self._mplot_objects.get('line')   
                line.set_data(transformated_xdata, z_data)
        #        
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
        #

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
            'default_value': 50.0,
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
            
    def _draw(self, new_value, old_value):
        # Bypass function
       # print '\nIndexRepresentationView._draw (bypass)'
        self.draw()
       # print '\nIndexRepresentationView._draw (bypass) end'
        
        
    def get_data_info(self, event):
        OM = ObjectManager(self)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
                
        ### Z axis Conversion 
        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)
        filter_ = toc.get_filter()
        di_uid, display, is_range, z_first, z_last = filter_.data[0]
        z_data_index = OM.get(di_uid)
        position_data = z_data_index.data[z_first:z_last]    
        ### END - Z axis Conversion 
        
        y_pos_index = (np.abs(position_data - event.ydata)).argmin()
        return str(controller._data[y_pos_index])

           
    
    
    def draw(self):
       # print '\nIndexRepresentationView.draw'
        self.clear()
        self._mplot_objects['text'] = []
        OM = ObjectManager(self)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
                
        obj = controller.get_object()
        
        
        ### Z axis Conversion 
        filter_ = toc.get_filter()
        di_uid, display, is_range, z_first, z_last = filter_.data[0]
        z_data_index = OM.get(di_uid)
        position_data = z_data_index.data[z_first:z_last]    
        ### END - Z axis Conversion 
        
        
        
        y_min = controller._data[0] 
        y_max = controller._data[-1]  
        
        
        if y_min%controller.model.step:
            y_min = (y_min//controller.model.step + 1) * controller.model.step  
        y_values = np.arange(y_min, y_max, controller.model.step)


        for y_value in y_values:
            
            y_pos_index = (np.abs(controller._data - y_value)).argmin()
            
            #y_pos_index = controller._get_z_index(y_value)
            
            #print y_value, y_pos_index
            y_pos = position_data[y_pos_index]
            text = track_controller._append_artist('Text', 
                                    controller.model.pos_x, y_pos,
                                    "%g"%y_value,
                                    color=controller.model.color,
                                    horizontalalignment=controller.model.ha,
                                    verticalalignment=controller.model.va,
                                    fontsize=controller.model.fontsize
            )                        
            if controller.model.bbox:
                pad = 0.2
                boxstyle = controller.model.bbox_style
                boxstyle += ",pad=%0.2f" % pad
                text._bbox_patch = FancyBboxPatch(
                                    (0., 0.),
                                    1., 1.,
                                    boxstyle=boxstyle,
                                    color=controller.model.bbox_color,
                                    alpha=controller.model.bbox_alpha
                )                    
            #text.zorder = controller.model.zorder
            self._mplot_objects['text'].append(text)
        try:
            #obj = controller.get_object()
            self.set_title(obj.name)
            self.set_subtitle(obj.unit)
        except:
            pass
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
            print (msg)
            self.model.set_value_from_event('colormap', old_value)
        else:    
            self.view.set_colormap(new_value)     
            
                
class DensityRepresentationModel(UIModelBase):
    tid = 'density_representation_model'

    _ATTRIBUTES = collections.OrderedDict()
    
    _ATTRIBUTES['type'] = {
            'default_value': 'density', #'wiggle', #'density', 
            'type': str,
            'pg_property': 'EnumProperty',
            'label': 'Plot type',
            'labels': ['Density', 'Wiggle', 'Both'],  
            'values': ['density', 'wiggle', 'both']
    }    
    _ATTRIBUTES['colormap'] = {
            'default_value': 'spectral_r', #'gray',
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

            

    def PostInit(self):
        UIM = UIManager()
        controller =  UIM.get(self._controller_uid)
        #
        obj = controller.get_object()
        if obj.tid == 'gather' or obj.tid == 'seismic':
            controller.model.colormap = 'gray_r'
        
        #if self.label:
        #    self.label.set_plot_type(controller.model.type)    
            
            
        controller.subscribe(self._draw, 'change.type')    
        controller.subscribe(self.set_interpolation, 'change.interpolation')
        controller.subscribe(self._draw, 'change.min_density')   
        controller.subscribe(self._draw, 'change.max_density')  
        controller.subscribe(self.set_line_width, 'change.linewidth')   
        controller.subscribe(self.set_line_color, 'change.linecolor')   
        controller.subscribe(self.fill_between, 'change.fill') 
        controller.subscribe(self.fill_color_left, 'change.fill_color_left')
        controller.subscribe(self.fill_color_right, 'change.fill_color_right')
        controller.subscribe(self._draw, 'change.min_wiggle')   
        controller.subscribe(self._draw, 'change.max_wiggle')
        #
        #self.draw()
        
            
    def _draw(self, new_value, old_value):
        # Bypass function
        self.draw()  


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
            mpl_obj = self._mplot_objects['wiggle'][idx]
            if mpl_obj is not None:
                mpl_obj.set_alpha(alpha)
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


    def get_data_info(self, event):
        OM = ObjectManager(self)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if controller._data is None:
            return None
        #
        z_index = controller._get_z_index(event.ydata)
        if z_index is None:
            return None
        #
        xdata = inverse_transform(event.xdata, 0.0, controller._data.shape[0], 0)
        xdata = int(xdata)
        msg = ''
        #

        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)   
        OM = ObjectManager(self)
        filter_ = toc.get_filter() #OM.get(('data_filter', toc.model.data_filter_oid))
        #
        data_indexes = filter_.data
        x_index = 0
        x = xdata
        multiplier = 1
        #
        for (di_uid, display, is_range, first, last) in data_indexes[1:]:
            obj = OM.get(di_uid)
            if not display:
                value = obj.data[first] 
            else:
                if not is_range:
                    value = obj.data[first]
                else: 
                    values_dim = obj.data[slice(first,last)]
                    index = x % len(values_dim)
                    x_index += index * multiplier 
                    multiplier *= len(values_dim)
                    x = x // len(values_dim)
                    value = values_dim[index]
            obj_str = obj.name + ': ' + str(value)
            if msg:
                msg = obj_str + ', ' + msg
            else:    
                msg = obj_str      
        msg += ', Value: ' + str(controller._data[(x_index, z_index)])
        return '[' + msg +  ']'

        
    
    def draw(self):
        self.clear()     
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if controller._data is None:
            return
        #
        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #
        OM = ObjectManager(self)
        filter_ = toc.get_filter() #OM.get(('data_filter', toc.model.data_filter_oid))
        #
        """
        for filter_data in filter_.data:
            di_uid, display, is_range, z_first, z_last = filter_data
            di = OM.get(di_uid)
            print di.dimension, di.name, display, is_range, z_first, z_last
        """    
        #
        z_data = filter_.data[0]
        di_uid, display, is_range, z_first, z_last = z_data
        z_data_index = OM.get(di_uid)
        z_data = z_data_index.data[z_first:z_last]
        #
        x_data = filter_.data[1]
        di_uid, display, is_range, x_first, x_last = x_data
        x_data_index = OM.get(di_uid)
        x_data = x_data_index.data[z_first:z_last]
        #
        #print x_data_index.dimension, x_data_index.name, display, is_range, x_first, x_last, x_data
        #
        if self.label:
            #print '\n\n\n'
            self.label.set_plot_type(controller.model.type)
            self.set_title(controller.get_object().name)
            if controller.model.type == 'wiggle':
                self.label.set_zlabel(x_data_index.name)
                #self.set_subtitle(x_data_index.name)
                #self.label.set_offsets(x_data)
                self.label.set_xlim((x_data[0], x_data[-1]))

                
            #print '\n\n\n'
        #print 'controller.model.type:', controller.model.type    
        #
        #
        self._mplot_objects['density'] = None
        self._mplot_objects['wiggle'] = []
        #self.set_title(controller.get_object().name)
        #
        #print '\n\n\n'
        #print 'NOME:', controller.get_object().name
        #print '\n\n\n'
        """
        if self.label:
            self.label.set_plot_type('line')
            self.label.set_xlim(
                (controller.model.left_scale, controller.model.right_scale)
            ) 
            self.label.set_color(controller.model.color)
            self.label.set_thickness(controller.model.thickness)    
        self.set_title(obj.name)
        self.set_subtitle(obj.unit)   
        """
        #
        if controller.model.type == 'density' or controller.model.type == 'both':
            # 0,0 and 1.0 are our fixed Axes x_lim
            extent = (0.0, 1.0, np.nanmax(z_data), np.nanmin(z_data))   
            image = track_controller._append_artist('AxesImage',
                                            cmap=controller.model.colormap,
                                            interpolation=controller.model.interpolation,
                                            extent=extent
            )
            image.set_data(controller._data.T)
            image.set_label(self._controller_uid)            
            if image.get_clip_path() is None:
                # image does not already have clipping set, clip to axes patch
                image.set_clip_path(image.axes.patch)     
            self._mplot_objects['density'] = image
            if controller.model.min_density is None:
                controller.model.set_value_from_event('min_density', np.nanmin(controller._data))
            if controller.model.max_density is None:    
                controller.model.set_value_from_event('max_density', np.nanmax(controller._data))
            image.set_clim(controller.model.min_density, controller.model.max_density)
            self.set_density_alpha(controller.model.density_alpha)  
            
            if self.label:
                #self.label.set_plot_type('density')  
                self.label.set_colormap(controller.model.colormap)
                self.label.set_zlim((controller.model.min_density, 
                                                 controller.model.max_density)
                )
            #    
        else:
            self._mplot_objects['density'] = None
        #
        if controller.model.type == 'wiggle' or controller.model.type == 'both':    
            self._lines_center = []
            x_lines_position = transform(np.array(range(0, controller._data.shape[0])),
                                         0.0, controller._data.shape[0]
            )
            if len(x_lines_position) > 1:
                increment = (x_lines_position[0] + x_lines_position[1]) / 2.0 
            elif len(x_lines_position) == 1:
                increment = 0.5
            else:
                raise Exception('Error. x_lines_position cannot have lenght 0. Shape: {}'.format(controller._data.shape))
            if controller.model.min_wiggle == None:
                controller.model.set_value_from_event('min_wiggle',
                                                      (np.amax(np.absolute(controller._data))) * -1)  
            if controller.model.max_wiggle == None:
                controller.model.set_value_from_event('max_wiggle', 
                                                      np.amax(np.absolute(controller._data)))     
            data = np.where(controller._data<0, controller._data/np.absolute(controller.model.min_wiggle), controller._data)
            data = np.where(data>0, data/controller.model.max_wiggle, data)
    
            for idx, pos_x in enumerate(x_lines_position):
                self._lines_center.append(pos_x + increment) 
                xdata = data[idx]
                xdata = self._transform_xdata_to_wiggledata(xdata, pos_x, pos_x + 2*increment)
                line = track_controller._append_artist('Line2D', xdata, z_data,
                                            linewidth=controller.model.linewidth,
                                            color=controller.model.linecolor
                                            )
                #line.set_label(toc_uid)
                self._mplot_objects['wiggle'].append(line)   
                self._mplot_objects['wiggle'].append(None) # left fill
                self._mplot_objects['wiggle'].append(None) # right fill
            
            #if self.label:
                #self.label.set_plot_type('wiggle')   
            #    self.label.set_xlim((controller.model.min_wiggle, 
            #                                     controller.model.max_wiggle)
            #    )
            
        self.draw_canvas()
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

    #def PostInit(self):
    #    self.draw()


    def get_data_info(self, event):
        OM = ObjectManager(self)
        for part_uid, collection in self._mplot_objects.items():
            result, dict_ = collection.contains(event)
            if result:
                obj = OM.get(part_uid)
                return obj.name #OM._getparentuid(part_uid), obj.name #, dict_
 
    
    def draw(self):        
        self.clear()
        #
        OM = ObjectManager(self)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        toc_uid = UIM._getparentuid(self._controller_uid)
        track_controller_uid = UIM._getparentuid(toc_uid)
        track_controller =  UIM.get(track_controller_uid)
        #
        obj = controller.get_object()
        #
        index = obj.get_index()[0][0]
        
        
        for part in OM.list('part', obj.uid):
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



class ContourfRepresentationController(RepresentationController):
    tid = 'contourf_representation_controller'
    
    def __init__(self):
       # print '\n\nContourfRepresentationController'
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

       # print '\n\nContourfRepresentationView'
        
        if self.label:
            self.label.set_plot_type('density')    

    def PostInit(self):
        self.draw()        


    def get_data_info(self, event):
        pass
    
    
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
         
    def get_data_info(self, x, y):
        return None

    def get_data_info_array(self):
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
