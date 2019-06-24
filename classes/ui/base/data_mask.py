
from collections import OrderedDict

import numpy as np

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 



class DataMaskController(UIControllerObject):
    tid = 'data_mask_controller'

    _ATTRIBUTES = OrderedDict()
            
    _ATTRIBUTES['data_obj_uid'] = {
            'default_value': None,
            'type': 'uid'
    }             
  
   
    def __init__(self, **state):     
        super().__init__(**state)

        self._data = []
        
#        OM = ObjectManager()
#        data_obj = OM.get(self.data_obj_uid)  
        
        self._init_data()


    def _init_data(self):
        print('\n\n_init_data')
        try:
            OM = ObjectManager()
            data_obj = OM.get(self.data_obj_uid)
            print(data_obj)
            #
            # No need to get unit from data_obj if it not changed.
            self._data_name = data_obj.name
            self._data_unit = data_obj.unit 
            #
            print('b4 data_obj.get_data_indexes()')
            data_indexes = data_obj.get_data_indexes() 
            
            print('data_indexes:', data_indexes)
            
            for dim_idx in range(len(data_indexes)):
                print('dim_idx:', dim_idx)
                indexes_per_dim_uid = data_indexes[dim_idx]
#                print(dim_idx, indexes_per_dim_uid)
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
        
#        print('\nset_dimension:', kwargs)
#        print('self._data[dim_idx]:', self._data[dim_idx])
        
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
        
   



class DataMask(UIViewObject):
    tid = 'data_mask'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
#        UIM = UIManager()
#        controller = UIM.get(self._controller_uid)






        
'''        
# DataMaskController
class DataMask(OMBaseObject):
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_mask'

    def __init__(self, data_obj_uid):
        """
        track_object_controller.uid
        """
        super().__init__()
        self._data = []
        self._data_obj_uid = data_obj_uid
        self._data_unit = None
        self._data_name = None
        self._init_data()

 

    """
    def get_data_info(self, x_idx, y_idx, dimensions_plotted=None):
        #
        OM = ObjectManager()
        #
        x_index = 0
        multiplier = 1
        msg = ''
        #
        print()
        
        for dim_di_uid, is_range, start, stop in self._data[::-1][1::]:
            print('\nENTROU FOR')
            dim_di = OM.get(dim_di_uid)          
            if not is_range:
                value = dim_di.data[start]
            else: 
                values_dim = dim_di.data[slice(start, stop)]
                index = x_idx % len(values_dim)
                
                x_index += index * multiplier 
                
                print('\n', dim_di.name , ': ', x_idx, len(values_dim), 
                                                  index, multiplier, x_index)
                print('Adding', str(index + start), 'to value slicer.')

                # Prepare for next one...
                multiplier *= len(values_dim)
                x_idx = x_idx // len(values_dim)
                value = values_dim[index]
                
            obj_str = dim_di.name + ': ' + str(value)
                      
            if msg:
                msg = obj_str + ', ' + msg
            else:    
                msg = obj_str  
                
            print('msg:', msg)  
            
        print('\nSAIU FOR')    
 
        #
        last_dim_data = self._data[-1]      # last is always y_idx in the plot
        last_dim_di_uid = last_dim_data[0]
        last_dim_di = OM.get(last_dim_di_uid)  
        last_dim_di_start = last_dim_data[2] 
        y_idx += last_dim_di_start          # Adding range start        
        obj_str = last_dim_di.name + ': ' + str(last_dim_di.data[y_idx])
        #
        if msg:
            msg += ', ' + obj_str 
        else:    
            msg = obj_str  
        print('msg:', msg)                  
        #
        data = self.get_data(dimensions_plotted)
        print()
        print('data.shape:', data.shape, 'len(data.shape):', len(data.shape))

        if len(data.shape) == 1:
            value = data[y_idx]
            print(y_idx)
        elif len(data.shape) == 2:    
            value = data[x_index, y_idx]
            print(x_index, y_idx)
        #    
        msg = '[' + msg + ']'
        if self._data_unit:
            msg += ' ' + self._data_unit
        msg += ': ' + str(value)     
        return (msg, value)      
    """
    
    """
    # Gets info to be shown in WellPlot StatusBar
    def get_data_info(self, event):
        OM = ObjectManager()
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
        x = int(xdata)
        msg = ''
        #

        toc_uid = UIM._getparentuid(self._controller_uid)
        toc = UIM.get(toc_uid)   
        OM = ObjectManager()
        filter_ = toc.get_filter() #OM.get(('data_filter', toc.data_filter_oid))
        #
        data_indexes = filter_.data
        x_index = 0
        multiplier = 1
        #
        for (di_uid, display, is_range, start, stop) in data_indexes[1:]:
            obj = OM.get(di_uid)
            if not display:
                value = obj.data[start] 
            else:
                if not is_range:
                    value = obj.data[start]
                else: 
                    values_dim = obj.data[slice(start,stop)]
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

    """



#    def append_objuid(self, track_obj_ctrl_uid):    
#        print('DataMask.append_objuid:', track_obj_ctrl_uid)




    """

        filter_ = toc.get_filter() #OM.get(('data_filter', toc.data_filter_oid))
        #
        data_indexes = filter_.data
        x_index = 0
        x = xdata
        multiplier = 1
        #
        for (di_uid, display, is_range, start, stop) in data_indexes[1:]:
            obj = OM.get(di_uid)
            if not display:
                value = obj.data[start] 
            else:
                if not is_range:
                    value = obj.data[start]
                else: 
                    values_dim = obj.data[slice(start, stop)]
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

    """
    
    
    """
    def run(self, *objects):
        if not objects:
            return None
        slicer = self.get_slicer()
        ret_list = [obj.data[slicer] for obj in objects]
        if len(ret_list == 1):
            return ret_list[0]
        return ret_list
    """


        


"""

    def _prepare_data(self):
        
        print('\n\n_prepare_data')
        
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid)
        #
        
        try:
        
            filter_ = toc.get_filter()
            data_indexes = filter_.data[::-1]
            
            print('data_indexes[-1]:', data_indexes[-1])
            #
            if data_indexes[-1][0] is None:
                self._data = None
                return            
            #
            obj = toc.get_object() 
            data = obj._data
            
            #print '\nRepresentationController._prepare_data:', obj.uid
            
            slicer = OrderedDict()
            for (di_uid, display, is_range, start, stop) in data_indexes:
              #  print di_uid, display, is_range, start, stop
                if not is_range:
                    slicer[di_uid] = start
                else:
                    slicer[di_uid] = slice(start,stop)
            slicer = tuple(slicer.values())
            
            
            data = data[slicer]
            new_dim = 1
            if len(data.shape) == 1 and isinstance(obj, Density):
                data = data[np.newaxis, :]
            elif len(data.shape) > 2:
                for dim_value in data.shape[::-1][1::]:
                    new_dim *= dim_value
                data = data.reshape(new_dim, data.shape[-1])
                
                
            
            self._data = data
            
            
#            print (self._data)
           # print
#            print ('FIM _prepare_data\n\n')
           
           
        except Exception as e:
            print ('ERROR _prepare_data', e)
            raise



    def _get_z_index(self, ydata):   
        
        if self._data is None:
            # When we have differents z_axis (e.g. Wellplot as TVD e Log with data_axis as MD)
            return None
        #
        UIM = UIManager()
        toc_uid = UIM._getparentuid(self.uid)
        toc = UIM.get(toc_uid) 
        #
        OM = ObjectManager()
        filter_ = toc.get_filter() #OM.get(('data_filter', toc.data_filter_oid))
        z_data = filter_.data[0]
        #
        
        #print 'filter_.data[0]:', z_data  
        
        di_uid, display, is_range, z_start, z_stop = z_data
        z_data_index = OM.get(di_uid)
        z_data = z_data_index.data[z_start:z_stop]
        z_index = (np.abs(z_data-ydata)).argmin()
        if z_index == 0:
            if np.abs(ydata - z_data[z_index]) > np.abs(z_data[1] - z_data[0]):
                return None
        if z_index == self._data.shape[-1]-1:
            if np.abs(ydata - z_data[z_index]) > np.abs(z_data[-1] - z_data[-2]):
                return None
            
        #print '\n_get_z_index:', ydata, z_index    
        return z_index

"""



"""
class DataMask(OMBaseObject):
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_filter'
    _TID_FRIENDLY_NAME = 'Data Filter'
    

    def __init__(self, objuid):
        
        try:
            super(DataMask, self).__init__()
            self.data = []
            self.track_obj_ctrls_uids = []
            self.append_objuid(objuid)
        except Exception as e:
            print ('ERROR DataMask:', e)
            raise


    
    def append_objuid(self, track_obj_ctrl_uid):
        if track_obj_ctrl_uid in self.track_obj_ctrls_uids:
            raise Exception('Object was added before.')
        try:
            UIM = UIManager()
            track_obj_ctrl = UIM.get(track_obj_ctrl_uid)
            obj = track_obj_ctrl.get_object()
            
            #if obj.tid == 'data_index':
            #    self.data.append((obj.uid, True, True, 0, len(obj.data)))
            #                        (data_index_uid, display, is_range, start, stop)
            #else:
            
            self.set_z_dimension_index(track_obj_ctrl_uid)
            #index_set = OM.get(obj.index_set_uid)
            #print 'HERE:', obj.uid
        
            data_indexes = obj.get_data_indexes()
            #print '\ndata_indexes:', data_indexes
            
            
            # dim_idx=0 JAH FOI TRATADO NO self.set_z_dimension_index ACIMA
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
            print ('ERROR append_objuid:', e)
            raise e     



    def append_objuid(self, track_objuid):
        print '\nDataFilter.append_objuid:', track_objuid
        if track_objuid in self.tracks_objuids:
            raise Exception('Object was added before.')
        try:
            UIM = UIManager()
            track_obj_ctrl = UIM.get(track_objuid)
            obj = track_obj_ctrl.get_object()
            print obj.uid
            
            
            if obj.tid == 'data_index':
                self.data.append((obj.uid, True, True, 0, len(obj.data)))
            else:
                data_indexes = obj.get_index()
                print '\nlen(data_indexes):', len(data_indexes)
                
                for dim_idx in range(len(data_indexes)):
                    print 'dim_idx:', dim_idx
                    indexes = data_indexes[dim_idx]
                    index = indexes[0]
                    if dim_idx < 2:    
                        self.data.append((index.uid, True, True, 0, len(index.data)))
                    else:
                        self.data.append((index.uid, False, False, 0, len(index.data)))
                        
                        
            self.tracks_objuids.append(track_objuid)              
        except Exception as e:
            print 'ERROR:', e
            raise e     
        print 'DataMask.append_objuid ENDED\n'




    30-05-2019
    ==========
    O METODO ABAIXO SERVER PARA ESCOLHER O DATA INDEX QUE SERÁ UTILIZADO PARA 
    O EIXO Z. ISSO OCORRE QUANDO SE POSSUI VARIAS OPCOES (EXEMPLOS: MD, TVD, 
    TVDSS) E VAI SE PLOTAR O LOG EM UM WELLPLOT QUE ESTAH EM UM DETERMINADO 
    INDEX (MD,POR EXEMPLO).
    

    def set_z_dimension_index(self, track_obj_ctrl_uid):
        UIM = UIManager()
        track_obj_ctrl = UIM.get(track_obj_ctrl_uid)
        obj = track_obj_ctrl.get_object()

        track_ctrl_uid = UIM._getparentuid(track_obj_ctrl.uid)
        logplot_ctrl_uid = UIM._getparentuid(track_ctrl_uid)
        logplot_ctrl = UIM.get(logplot_ctrl_uid)
        
        z_axis_candidate_indexes = obj.get_data_indexes()[0]
        chosen_index = None
        
      #  for candidate_index in z_axis_candidate_indexes:
      #      print candidate_index
        
#        print ('\nFOIIII\n')
        
        for candidate_index in z_axis_candidate_indexes:
            if candidate_index.datatype == logplot_ctrl.index_type:
                chosen_index = candidate_index     
                break
#        print (chosen_index)    
        try:    
            if chosen_index is None:
                self.data[0] = (None, True, True, 0, 0)
            else: 
#                print ('la')
#                print (len(chosen_index._data))
#                print ('lala')
                self.data[0] = (chosen_index.uid, True, True, 0, len(chosen_index._data))    
#                print ('lalalalalala')
                
#            print ('\nFOIIII 2\n')        
                
        except IndexError as ie:
            if len(self.data) > 0:
                raise ie
            if chosen_index is None:
                self.data.append((None, True, True, 0, 0))
         #       print 'APPEND NONE'
                
            else:    
                self.data.append((chosen_index.uid, True, True, 0, len(chosen_index._data)))   
        #        print 'APPEND', chosen_index.uid
#        print ('\nFOIIII 3\n')
        
        
        
    def reload_z_dimension_indexes(self):  
        for track_obj_ctrl_uid in self.track_obj_ctrls_uids:
            self.set_z_dimension_index(track_obj_ctrl_uid)

       
       
"""   



'''

       