

from collections import OrderedDict

import numpy as np

from classes.om import OMBaseObject
from classes.om import ObjectManager



class DataFilter(OMBaseObject):
    
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_filter'

    
    def __init__(self, data_obj_uid):
        """
        track_object_controller.uid
        """

        super().__init__()
        self._data = []
        self._data_obj_uid = data_obj_uid
#        self.track_obj_ctrls_uids = []
#        self.append_objuid(toc_uid)
        self._prepare_data()


    # It will not be shown in Tree
    def _get_tree_object_node_properties(self):    
        return None
       
        
    def _prepare_data(self):
        OM = ObjectManager()
        data_obj = OM.get(self._data_obj_uid)
        data_indexes = data_obj.get_data_indexes()        
        for dim_idx in range(len(data_indexes)):
            indexes_uid = data_indexes[dim_idx]
            index_uid = indexes_uid[0]
            index = OM.get(index_uid)
            if (len(data_indexes) - dim_idx) <= 2:    
                # Sempre exibe as 2 ultimas dimensoes do dado.
                # Ex: sismica 3-d stacked (iline, xline, tempo) serah exibido
                # xline e tempo, em principio.
                # (di_uid, display, is_range, first, last)
                self._data.append([index_uid, True, True, 0, len(index.data)])
            else:
                self._data.append([index_uid, False, False, 0, len(index.data)])
                

    def _get_slicer(self):        
        slicer = []     
        for [di_uid, display, is_range, first, last] in self._data:       
            if not display:
                slicer.append(0)
            elif not is_range:                
                slicer.append(first)
            else:                
                slicer.append(slice(first, last))            
        slicer = tuple(slicer)
        print('_get_slicer:', slicer)
        return slicer
    
    
    def get_data(self, dimensions_desired=None):
        OM = ObjectManager()
        data_obj = OM.get(self._data_obj_uid)     
        slicer = self._get_slicer()
        data = data_obj.data[slicer]
        #
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
    

    def get_data_info(self, x_idx, y_idx, dimensions_plotted=None):
        #
        OM = ObjectManager()
        data_obj = OM.get(self._data_obj_uid)     
        slicer = self._get_slicer()
        data = data_obj.data[slicer]
        #
        
        slicer = self._get_slicer()
        
        OM = ObjectManager()
        x_index = 0
        multiplier = 1
        msg = ''
        #
        for [di_uid, display, is_range, first, last] in self._data[::-1][1::]:
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

    """



    def append_objuid(self, track_obj_ctrl_uid):    
        print('DataFilter.append_objuid:', track_obj_ctrl_uid)




        """

        filter_ = toc.get_filter() #OM.get(('data_filter', toc.data_filter_oid))
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
                    values_dim = obj.data[slice(first, last)]
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
                
                
            '''    
            try:
                if self.min_density is None:
                    self.set_value_from_event('min_density', np.nanmin(data))
                if self.max_density is None:    
                    self.set_value_from_event('max_density', np.nanmax(data))
                if self.min_wiggle is None:    
                    self.set_value_from_event('min_wiggle', np.nanmin(data))
                if self.max_wiggle is None:     
                    self.set_value_from_event('max_wiggle', np.nanmax(data))
            except:
                pass
            '''
            
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

"""



"""
class DataFilter(OMBaseObject):
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_filter'
    _TID_FRIENDLY_NAME = 'Data Filter'
    

    def __init__(self, objuid):
        
        try:
            super(DataFilter, self).__init__()
            self.data = []
            self.track_obj_ctrls_uids = []
            self.append_objuid(objuid)
        except Exception as e:
            print ('ERROR DataFilter:', e)
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
            #                        (data_index_uid, display, is_range, first, last)
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
        print 'DataFilter.append_objuid ENDED\n'




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
       