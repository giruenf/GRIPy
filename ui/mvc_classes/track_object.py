from collections import OrderedDict   

import numpy as np
import wx

from classes.om import ObjectManager
from classes.ui import UIManager

from ui.mvc_classes.wxgripy import FrameController
from ui.mvc_classes.wxgripy import Frame

from classes.ui import UIControllerObject
from classes.ui import UIViewObject 

from ui.mvc_classes.representation import RepresentationController

# TODO: verificar se linhas abaixo devem ser mantidas
from basic.parms import ParametersManager

# TODO: Verificar se deve-se manter isso. 
# Colocado para pegar figure.py:98: MatplotlibDeprecationWarning
# Adding an axes using the same arguments as a previous axes currently reuses 
# the earlier instance.  In a future version, a new instance will always be 
# created and returned.  Meanwhile, this warning can be suppressed, and the 
# future behavior ensured, by passing a unique label to each axes instance.
import warnings
#with warnings.catch_warnings():                            # with version
#    warnings.simplefilter("error", module="matplotlib")
warnings.filterwarnings("error", module="matplotlib")       # full version

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


class TrackObjectController(FrameController):
    tid = 'track_object_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['data_obj_uid'] = {
            'default_value': None,
            'type': 'uid'
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
    
    def __init__(self, **state):
        super().__init__(**state)
        self._data = [] 
        
        self.subscribe(self.on_change_data_obj_uid, 'change.data_obj_uid')        
        self.subscribe(self.on_change_plottype, 'change.plottype')
        self.subscribe(self.on_change_picked, 'change.selected')
        #self.subscribe(self.on_change_pos, 'change.pos')


    def PostInit(self):
        UIM = UIManager()
        if self.pos == -1:
            track_ctrl_uid = UIM._getparentuid(self.uid)
            self.pos = len(UIM.list(self.tid, track_ctrl_uid))     

              
    def PreDelete(self):
        self.plottype = None


    def on_change_data_obj_uid(self, new_value, old_value):
        print('\n\non_change_data_obj_uid', new_value, old_value)
        OM = ObjectManager()
        try:
            if old_value is not None:
                self.detach()   
            obj = OM.get(new_value)  
            # Exclude any representation, if exists
            self.plottype = None
            if obj:
                self._init_data()
                
                # TODO: Verificar isso
                # Setando datatype do eixo Z
                index_type = self.get_well_plot_index_type()
                self.set_dimension(dim_idx=-1, datatype=index_type)
                self.plottype = _PREFERRED_PLOTTYPES.get(obj.uid[0])
                self.attach(obj.uid)
        except Exception as e:
            print ('\n\n\nERROR on_change_obj_oid:', e)
            raise


    def on_change_plottype(self, new_value, old_value):
        print('\n\non_change_plottype', new_value, old_value)
        UIM = UIManager()
        repr_ctrl = self.get_representation()
        if repr_ctrl:
            UIM.remove(repr_ctrl.uid) 
        if new_value is not None:
            repr_tid = _PLOTTYPES_REPRESENTATIONS.get(new_value)
            try:
                state = self._get_log_state()
                repr_ctrl = UIM.create(repr_tid, self.uid, **state)
                repr_ctrl.draw()
            except Exception as e:
                print ('ERROR on_change_plottype', e)
                self.plottype = None    
                raise


    def on_change_picked(self, new_value, old_value):
        self.get_representation().set_picked(new_value, old_value) 
              
    def is_picked(self):
        return self.picked

    # Picking with event that generates pick... 
    # Event(PickEvent) maybe useful in future
    def pick_event(self, event):
        """
        Quando o usuario clica em um objeto Representation, 
        ocorre o redirect para ca.
        """
        if event.mouseevent.button == 1:
            self.selected = not self.selected                             
                      
            
    def redraw(self):
        if not self.get_representation():
            return False
        return self.get_representation().redraw()


    def get_well_plot_index_type(self):
        UIM = UIManager()
        track_ctrl_uid = UIM._getparentuid(self.uid)
        well_plot_ctrl_uid = UIM._getparentuid(track_ctrl_uid)
        well_plot_ctrl = UIM.get(well_plot_ctrl_uid)
        return well_plot_ctrl.index_type


    def _get_log_state(self):
        # TODO: Rever necessidade de obj.name - ParametersManager
        state = {}
        OM = ObjectManager()
        obj = OM.get(self.data_obj_uid)
        
        if obj.tid == 'log':
            # TODO: Rever isso
            parms = ParametersManager.get().get_curvetype_visual_props(obj.datatype)     
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
        # Returns the real OM.object representation
        UIM = UIManager()
        children = UIM.list(None, self.uid)
        if len(children) == 0:
            return None
        return children[0]


    def is_valid(self):
        return self.get_representation() is not None

    def _init_data(self):
        print('\n_init_data:', self.data_obj_uid)
        try:
            OM = ObjectManager()
            data_obj = OM.get(self.data_obj_uid)
            # No need to get unit from data_obj if it not changed.
            self._data_name = data_obj.name
            self._data_unit = data_obj.unit 
            self._data_type = data_obj.datatype
            #
            data_indexes = data_obj.get_data_indexes() 
            for dim_idx in range(len(data_indexes)):
                indexes_per_dim_uid = data_indexes[dim_idx]
                di_uid = indexes_per_dim_uid[0]  # Chosing the first one!
                di = OM.get(di_uid)  
                if (len(data_indexes) - dim_idx) <= 2:    
                    # Sempre exibe as 2 ultimas dimensoes do dado.
                    # Ex: sismica 3-d stacked (iline, xline, tempo) serah exibido
                    # xline e tempo, em principio.
                    # (di_uid, is_ranged, start, stop)
                    self._data.append([di_uid, True, 0, len(di.data)])
                else:
                    self._data.append([di_uid, False, 0, len(di.data)])            
                # 
        except Exception as e:
            print('ERROR _init_data:', e)
            raise


    def get_data_name(self):
        return self._data_name
    
    def get_data_unit(self):
        return self._data_unit

    def get_data_type(self):
        return self._data_type

    def get_data_object_uid(self):
        return self.data_obj_uid 

    # TODO: rename to set_dimension_data
    def set_dimension(self, dim_idx=-1, **kwargs):
        """
        dim_idx here refers to object actual data indexes.
        """
        # TODO: make dimensions changeable with np.transpose.
        #"""
        #dim_idx here refers to DataMask current dimension, not object
        #data indexes.
        #"""      
        datatype = kwargs.pop('datatype', None)
        name = kwargs.pop('name', None)
        di_uid = kwargs.pop('di_uid', None)
        #
        if datatype is None and name is None and di_uid is None:
            raise Exception('Either di_uid, datatype or name must be informed.')
        #   
        OM = ObjectManager()
        data_obj = OM.get(self.data_obj_uid )        
        data_indexes = data_obj.get_data_indexes()
        dim_dis_uids = data_indexes[dim_idx] 
#        print('dim_dis_uids:', dim_dis_uids)
        ret_datatypes = []
        #
        for dim_di_uid in dim_dis_uids:
            if dim_di_uid == di_uid:
                self._data[dim_idx][0] = di_uid
#                print('self._data[dim_idx] 2.1:', self._data[dim_idx])
                return True
            dim_di = OM.get(dim_di_uid)
#            print(dim_di.datatype, datatype)
            if dim_di.name == name:
                self._data[dim_idx][0] = dim_di_uid
#                print('self._data[dim_idx] 2.2:', self._data[dim_idx])
                return True                
            elif dim_di.datatype == datatype:
                ret_datatypes.append(dim_di_uid)
        if ret_datatypes:
            self._data[dim_idx][0] = ret_datatypes[0] # Sets with the first one
#            print('self._data[dim_idx] 2.3:', self._data[dim_idx])
            return True
#        print('set_dimension DEU FALSE')
        return False
    
    
    def _get_slicer(self):        
        slicer = []     
        for [di_uid, is_range, start, stop] in self._data:       
            if not is_range:                
                slicer.append(start)
            else:                
                slicer.append(slice(start, stop))            
        slicer = tuple(slicer)
        return slicer
    
    
    def get_data(self, dimensions_desired=None):
        if dimensions_desired is not None and dimensions_desired not in [1, 2]:
            raise Exception('Dimensions must be 1 or 2.')
        OM = ObjectManager()
        data_obj = OM.get(self.data_obj_uid )  
        #
        slicer = self._get_slicer()
        data = data_obj.data[slicer]
        #
#        print('get_data - len(data.shape):', len(data.shape), 
#                                  ' dimensions_desired:', dimensions_desired)
        if (dimensions_desired is None or 
                                    (dimensions_desired == len(data.shape))):
            return data
        #
        if dimensions_desired > len(data.shape):
            # Quando se deseja acrescentar dimensoes ao dado. Por exemplo,
            # exibindo dados 1-D em um grafico 2-D.
            redim_slicer = []
            for i in range(dimensions_desired-len(data.shape)):
                redim_slicer.append(np.newaxis)
            for i in range(len(data.shape)):
                # slice(None, None, None) equals ":" 
                redim_slicer.append(slice(None, None, None))
            data = data[tuple(redim_slicer)]
        #
        elif len(data.shape) > dimensions_desired and dimensions_desired == 2:
            # Flipa todas as dimensoes que sao exibidas, exceto a 
            # ultima (em geral o Z axis). Essas dimensoes farao a composicao
            # do eixo X. A ultima dimensao sera exibida no eixo Y do grafico.
            # Valido para uso em 2-D
            new_dim = 1
            for dim_value in data.shape[::-1][1::]:
                new_dim *= dim_value
            data = data.reshape(new_dim, data.shape[-1])            
        #    
        else:
            # Possivel uso alem 2-D ou algum erro nao mapeado.
            raise Exception('get_data - Tratar isso.')
        return data    


    def get_index_for_dimension(self, dim_idx=-1):
        """
        For some data dimension, returns the DataIndex uid and 
        its data filtered by mask values.
        """
        OM = ObjectManager()
        dim_data = self._data[dim_idx]     
        dim_di_uid = dim_data[0]
        di = OM.get(dim_di_uid)
        slicer = self._get_slicer()
        dim_di_data = di.data[slicer[dim_idx]]
        return dim_di_uid, dim_di_data 
        
    
    def get_index_data_for_dimension(self, dim_idx=-1):
        """
        Returns the DataIndex data being applied to some dimension. 
        """
        _, dim_di_data  = self.get_index_for_dimension(dim_idx)
        return dim_di_data
       
    def get_last_dimension_index(self):
        return self.get_index_for_dimension()
  
    def get_last_dimension_index_data(self):
        return self.get_index_data_for_dimension()
      
    def get_equivalent_index(self, datatype, dim_idx=-1):
        """
        Metodo usado para se obter um DataIndex de equivalencia (e.g. obter
        um TWT quando self.datatype == 'MD').
        
        Valido somente para dados de pocos, devido a busca por CurveSet.
        
        Retorna uma tupla onde o primeiro elemento informa se foi encontrado
        objeto equivalente diferente o DataIndex mask sendo aplicado. Em caso 
        afirmativo, o segundo elemento da tupla contem o objeto encontrado.
        Caso nao tenha sido obtido index equivalente, o segundo elemento 
        retornara o proprio objeto, se este tiver o datatype procurado. 
        Se o datatype desejado nao for encontrado, sera retornado (False, None).
        """
        dim_di_uid, _ = self.get_index_for_dimension(dim_idx)
        OM = ObjectManager()
        di = OM.get(dim_di_uid)
        
        if di.datatype == datatype:
            return False, di
        OM = ObjectManager()
        curve_set_uid = OM._getparentuid(di.uid)
        if curve_set_uid[0] != 'curve_set':
            msg = 'ERROR DataIndex.get_equivalent_data_index: curve_set not found.'
            raise Exception(msg)
        for possible_di in OM.list('data_index', curve_set_uid):
            if possible_di.uid == di.uid:
                continue
            if possible_di.datatype == datatype:
                # Found it!
                return True, possible_di
        return False, None


    def get_equivalent_index_data(self, datatype, dim_idx=-1):
        found, equivalent_di = self.get_equivalent_index(datatype, dim_idx)
        if equivalent_di is None:
            return None
        slicer = self._get_slicer()
        return equivalent_di.data[slicer[dim_idx]]   
        
   


"""
class DataMask(UIViewObject):
    tid = 'data_mask'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
#        UIM = UIManager()
#        controller = UIM.get(self._controller_uid)

"""

###############################################################################
###############################################################################

"""
class NavigatorController(FrameController):
    tid = 'navigator_controller'
    
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['data_filter_oid'] = {
            'default_value': None,
            'type': int
    }  
    
    def __init__(self, **state):
        super().__init__(**state)
 
    def PostInit(self):
        OM = ObjectManager()
        df = OM.get(('data_filter', self.data_filter_oid))
        data_indexes = df.data[::-1]
        for (di_uid, display, is_range, first, last) in data_indexes:
            #obj = OM.get(di_uid)
            #print '\n', obj.name, display, is_range, first, last
            self.view.add_panel(di_uid, display, is_range, first, last)  
        self.view.add_bottom_panel()    


    def Set(self, results):
        print ('NavigatorController.Set:', results)
        OM = ObjectManager()
        df = OM.get(('data_filter', self.data_filter_oid))
        new_data = []
        for result in results[::-1]:
            new_data.append((result['uid'], result['display'], 
                            result['is_range'], result['start'], result['end'])
            ) 
            #print result
        df.data = new_data
        df.reload_data()
        print ('NavigatorController.Set ENDED')
        

"""



SLIDER_MARGIN = 5  # Default 6


class RangeSlider(wx.Slider):
    
    def __init__(self, *args, **kwargs):
        wx.Slider.__init__(self, *args, **kwargs)
        self.SetPageSize(1)
        self.calculate_rect()
        self.Bind(wx.EVT_SLIDER, self.on_event)

    def calculate_rect(self):
        self.rect = self.GetClientRect()
        self.rect.width -= 2*SLIDER_MARGIN
        self.rect.x += SLIDER_MARGIN

    def on_event(self, event):
        if event.GetEventType() == wx.EVT_LEFT_DOWN.typeId:
            if self.is_selrange():
                val = self.get_position(event) 
                if val < self.GetValue():
                    self.SetSelection(val, self.GetSelEnd())
                elif val > self.GetValue():    
                    self.SetSelection(self.GetSelStart(), val)
                self.send_change()    
            else:      
                event.Skip()
        elif event.GetEventType() == wx.EVT_SLIDER.typeId:
            self.send_change()

    def send_change(self):
        if self.is_selrange():
            #print 'send_change:', self.GetSelStart(), self.GetSelEnd()+1
            self.GetParent().GetParent().set_values(self.GetSelStart(), self.GetSelEnd()+1)
        else:    
            self.GetParent().GetParent().set_values(self.GetValue())
 
    def is_selrange(self):
        return (self.GetWindowStyle() & wx.SL_SELRANGE)
    
    def set_selrange(self, sel=True, selmin=None, selmax=None):
        if sel:
            self.SetWindowStyle(wx.SL_SELRANGE)
            if selmin is None or selmax is None:
                raise Exception()
            else:
                self.SetSelection(selmin, selmax)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_event)  
        else:
            self.ClearSel()
            if self.is_selrange():
                self.Unbind(wx.EVT_LEFT_DOWN, handler=self.on_event)
            self.SetWindowStyle(wx.SL_BOTTOM)       
            if selmin is None:
                raise Exception()
            super(RangeSlider, self).SetValue(selmin)
       
    def SetSelection(self, minsel, maxsel):
        #print 'Aqui'
        super(RangeSlider, self).SetSelection(minsel, maxsel)
        #print 'aqui nao'
        value = minsel + ((maxsel - minsel)/2)
        super(RangeSlider, self).SetValue(value)
          
    def SetValue(self, value):
        old_min_range = self.GetSelStart()
        old_max_range = self.GetSelEnd()
        old_med_range = old_min_range + ((old_max_range - old_min_range)/2)
        new_min_range = value - (old_med_range - old_min_range)
        new_max_range = value + (old_max_range - old_med_range) 
        if new_min_range < self.GetRange()[0] or \
                                        new_max_range > self.GetRange()[1]:                               
            return False   
        super(RangeSlider, self).SetSelection(new_min_range, new_max_range)
        super(RangeSlider, self).SetValue(value)
        return True
    
    def get_position(self, e):
        click_min = self.rect.x + (self.GetThumbLength()/2)
        click_max = (self.rect.x + self.rect.width) - (self.GetThumbLength()/2)
        click_position = e.GetX()
        result_min = self.GetMin()
        result_max = self.GetMax()
        if click_position > click_min and click_position < click_max:
            result = self.linapp(click_min, click_max,
                                 result_min, result_max,
                                 click_position)
        elif click_position <= click_min:
            result = result_min
        else:
            result = result_max    
        return result
    
    def linapp(self, x1, x2, y1, y2, x):
        proportion = float(x - x1) / (x2 - x1)
        length = y2 - y1
        return round(proportion*length + y1)




class DimensionPanel(wx.Panel):
    
    def __init__(self, data_index_uid, display, is_range, min_idx, max_idx, *args, **kwargs):
        super(DimensionPanel, self).__init__(*args, **kwargs)
        self.SetSize(300, 50)
        #
        self.data_index_uid = data_index_uid
        OM =  ObjectManager()
        obj = OM.get(data_index_uid)
        #
        main_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, obj.name)
        #
        self.top_panel = wx.Panel(self)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.check_display = wx.CheckBox(self.top_panel, -1, label='Display')  
        self.check_display.Bind(wx.EVT_CHECKBOX, self._on_check_display)                  
        self.top_sizer.Add(self.check_display, 1, wx.ALIGN_CENTER|wx.LEFT, 30)
        #
        self.check_range = wx.CheckBox(self.top_panel, -1, label='Range')
        self.check_range.Bind(wx.EVT_CHECKBOX, self._on_check_range)   
        self.top_sizer.Add(self.check_range, 1, wx.ALIGN_CENTER|wx.RIGHT, 30)
        self.top_panel.SetSizer(self.top_sizer)
        #
        main_sizer.Add(self.top_panel, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)
        #
        self.label = obj.name
        self.vec = obj.data
        self.display = display
        self.is_range = is_range
        #
        self.bottom_panel = wx.Panel(self)
        self.bottom_sizer = wx.BoxSizer(wx.VERTICAL)
        self.slider = RangeSlider(self.bottom_panel)
        self.bottom_sizer.Add(self.slider, 0, wx.EXPAND)
        self.text_value = wx.StaticText(self.bottom_panel, -1)
        self.bottom_sizer.Add(self.text_value, 0, wx.ALIGN_CENTER)
        self.bottom_panel.SetSizer(self.bottom_sizer)
        #
        main_sizer.Add(self.bottom_panel, 0, wx.EXPAND)
        #
        self.slider.SetRange(0, len(self.vec)-1)
        self.min_idx = min_idx
        self.max_idx = max_idx
        #
        if self.display:
            self.set_check_display(1)
        else:
            self.set_check_display(0)
        # 
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.SetSizer(main_sizer)
        main_sizer.Layout()

    def _on_paint(self, event):
        self.slider.calculate_rect()
        event.Skip()

    def _on_check_display(self, event):
        self.set_check_display(event.GetSelection())

    def _on_check_range(self, event):
        self.set_check_range(event.GetSelection())
        
    def set_check_display(self, value=0):
        self.check_display.SetValue(value)
        if value:
            self.display = True
            self.set_check_range(1)
            self.check_range.Enable()
            
        else:
            self.display = False
            self.set_check_range(0)
            self.check_range.Disable()
               
    def set_check_range(self, value=0):
        #print 'set_check_range:', value
        if self.min_idx > self.max_idx:
            temp = self.min_idx
            self.min_idx = self.max_idx
            self.max_idx = temp
        if value:  
            self.is_range = True
            #self.slider.set_selrange(True, self.min_idx, self.max_idx)
            #self.set_values(self.min_idx, self.max_idx)
        else:
            self.is_range = False
            #self.slider.set_selrange(False, self.min_idx, self.max_idx)
            #self.set_values(self.min_idx, self.max_idx)
        self.slider.set_selrange(self.is_range, self.min_idx, self.max_idx)
        self.set_values(self.min_idx, self.max_idx)            
        self.check_range.SetValue(value)    
        
    
    def set_values(self, min_idx, max_idx=None):
        self.min_idx = min_idx
        if max_idx is not None:
            self.max_idx = max_idx
            from_str = 'From: {}'.format(self.vec[min_idx])
            # TODO: max_idx-1 to max_idx !!!
            to_str = '   To: {}'.format(self.vec[max_idx-1])
            self.text_value.SetLabel(from_str + to_str)
        else:
            val_str = 'Selected: {}'.format(self.vec[min_idx])
            self.text_value.SetLabel(val_str)
        #print 'set_values:', self.min_idx, self.max_idx    
        self.bottom_sizer.Layout()    
           
    
    def get_result(self):
        ret = {}
        ret['uid'] = self.data_index_uid
        ret['display'] = self.display
        ret['is_range'] = self.is_range
        #if self.display:
        ret['start'] = self.min_idx
        ret['end'] = self.max_idx
        #else:
        #    ret['start'] = self.slider.GetValue()
        #    ret['end'] = None
        return ret
    



class TrackObject(Frame):
    tid = 'track_object'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
        self.basepanel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.basepanel.SetSizer(self.sizer)
        self.panels = []

    def PostInit(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #self._data.append([di_uid, True, 0, len(di.data)])
        is_range = True
        for (di_uid, display, first, last) in controller._data:
            self.view.add_panel(di_uid, display, is_range, first, last)  
        self.view.add_bottom_panel()    

    def add_panel(self, data_index_uid, display, is_range, start, end):
        panel = DimensionPanel(data_index_uid, display, is_range, start, end, self.basepanel)
        self.panels.append(panel)
        self.sizer.Add(panel, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5) #wx.ALIGN_CENTER
        self.sizer.Layout()
           
    def add_bottom_panel(self):
        buttons_panel = wx.Panel(self.basepanel)
        #buttons_panel.SetBackgroundColour('yellow')
        buttons_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.ok_button = wx.Button(buttons_panel, label='Ok')
        self.ok_button.Bind(wx.EVT_BUTTON, self.onOk)
        self.apply_button = wx.Button(buttons_panel, label='Apply')
        self.apply_button.Bind(wx.EVT_BUTTON, self.onApply)
        self.cancel_button = wx.Button(buttons_panel, label='Cancel')
        self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
        #
        buttons_panel_sizer.Add(self.ok_button, 0,
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        buttons_panel_sizer.Add(self.apply_button, 0, 
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        buttons_panel_sizer.Add(self.cancel_button, 0, 
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        #
        buttons_panel.SetSizer(buttons_panel_sizer)
        #buttons_panel.Layout()
        self.sizer.Add(buttons_panel, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5) #wx.ALIGN_CENTER
        self.sizer.Layout()
        #

    def onOk(self, event):
        self._doOK()

    def onApply(self, event):
        self._doApply()
        
    def onCancel(self, event):
        self._doCancel()  

    def _doOk(self):
        self._doApply()
        self._doCancel()

    def _doApply(self):
        print ('\n_doApply')
        results = []
        for panel in self.panels:
            results.append(panel.get_result())
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)    
        #controller.Set(results)
        #self._data.append([di_uid, True, 0, len(di.data)])
        controller._data = results
        print ('_doApply:', results)
        
        
    def _doCancel(self):
        self.Close()  

     
    