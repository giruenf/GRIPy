from collections import OrderedDict   

import numpy as np

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import FrameController
from classes.ui import RepresentationController

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
        #
        self._data = [] 
        #
        self._label = None
        #
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
        label = self.get_label()
        if label:
            label.destroy()

    def on_change_data_obj_uid(self, new_value, old_value):
        try:
            if old_value is not None:
                self.detach()   
            obj = self.get_data_object() 
            # Exclude any representation, if exists
            self.plottype = None
            if obj:
                self._init_data_mask()

                # TODO: Verificar isso
                # Setando datatype do eixo Z
                index_type = self.get_well_plot_index_type()
                self.set_dimension(dim_idx=-1, datatype=index_type)
                self.plottype = _PREFERRED_PLOTTYPES.get(obj.uid[0])
                self.attach(obj.uid)
        except Exception as e:
            print ('\nERROR on_change_obj_oid:', e)
            raise


    def on_change_plottype(self, new_value, old_value):
        UIM = UIManager()
        repr_ctrl = self.get_representation()
        label = self.get_label()
        #
        if repr_ctrl:
            UIM.remove(repr_ctrl.uid) 
        if label:
            label.destroy()
        #    
        if new_value is not None:
            repr_tid = _PLOTTYPES_REPRESENTATIONS.get(new_value)
            try:
                #
                track_ctrl_uid = UIM._getparentuid(self.uid)
                track_ctrl =  UIM.get(track_ctrl_uid)
                #
                if not track_ctrl.overview:
                    label = track_ctrl._append_track_label(
                                                        toc_uid=track_ctrl_uid
                    )
                    #
                    data_obj = self.get_data_object()
                    label.set_title(data_obj.name)
                    label.set_subtitle(data_obj.datatype)
                    #
                    self._label = label
                    #
                else:
                    self._label = None  
                #
                # TODO: rever linha abaixo
                state = self._get_log_state()                
                repr_ctrl = UIM.create(repr_tid, self.uid, **state)
                repr_ctrl.draw()
                #
            except Exception as e:
                print ('ERROR on_change_plottype', e)
                self.plottype = None    
                raise

    def get_representation(self):
        # Returns the real OM.object representation
        UIM = UIManager()
        children = UIM.list(None, self.uid)
        if len(children) == 0:
            return None
        for child in children:
            if isinstance(child, RepresentationController):
                return child

    def get_label(self):
        # Returns the real OM.object representation
        return self._label

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
        repr_ctrl = self.get_representation()
        if not repr_ctrl:
            return False
        return repr_ctrl.draw()

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
            PM = ParametersManager.get()
            parms = PM.get_datatypes_visual_props(obj.datatype)
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
    
    
    def get_data_info(self, event):
        repr_ctrl = self.get_representation()
        if not repr_ctrl:
            return None        
        return repr_ctrl.get_data_info(event)


    def is_valid(self):
        return self.get_representation() is not None


    # Os metodos abaixo se referem aos processos de data mask (data filter)
    # que foram integrados a esta classe. 
    def _init_data_mask(self):
        try:
            OM = ObjectManager()
            data_obj = OM.get(self.data_obj_uid)
            data_indexes = data_obj.get_data_indexes() 
            for dim_idx in range(len(data_indexes)):
                indexes_per_dim_uid = data_indexes[dim_idx]
                di_uid = indexes_per_dim_uid[0]  # Chosing the first one!
                di = OM.get(di_uid)  
                if (len(data_indexes) - dim_idx) <= 2:    
                    # Sempre exibe as 2 ultimas dimensoes do dado.
                    # Ex: sismica 3-d stacked (iline, xline, tempo) 
                    # serah exibido xline e tempo, em principio.
                    # (di_uid, is_ranged, start, stop)
                    self._data.append([di_uid, True, 0, len(di.data)])
                else:
                    self._data.append([di_uid, False, 0, len(di.data)])
        except Exception as e:
            print('ERROR _init_data_mask:', e)
            raise


    def get_data_object_uid(self):
        return self.data_obj_uid 

    def get_data_object(self):
        if not self.data_obj_uid:
            return None
        OM = ObjectManager()
        return OM.get(self.data_obj_uid)
    
    def get_data_name(self):
        """Convenience function."""
        data_obj = self.get_data_object()
        return data_obj.name
    
    def get_data_unit(self):
        """Convenience function."""
        data_obj = self.get_data_object()
        return data_obj.unit

    def get_data_type(self):
        """Convenience function."""
        data_obj = self.get_data_object()
        return data_obj.datatype

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
        data_obj = OM.get(self.data_obj_uid)        
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
     
    def get_filtered_data(self, dimensions_desired=None):
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
            raise Exception('get_filtered_data - Tratar isso.')
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

    @staticmethod
    def get_int_from_log(logdata, null=-1):
        if not np.equal(np.mod(logdata[np.isfinite(logdata)], 1), 0).all():
            print("Não é partição!")
            return
        codes = np.unique(logdata)
        tokeep = np.isfinite(codes) * (codes != null)
        codes = codes[tokeep]

        booldata = np.zeros((len(codes), len(logdata)), dtype=bool)
        for j in range(len(codes)):
            booldata[j][logdata == codes[j]] = True

        return booldata, codes