

from collections import OrderedDict

from classes.om import OMBaseObject



class DataFilter(OMBaseObject):
    
    _NO_SAVE_CLASS = True   # TODO: Melhorar isso! @ObjectManager.save
    tid = 'data_filter'

    
    def __init__(self, objuid):
        try:
            super().__init__()
            self.data = []
            self.track_obj_ctrls_uids = []
            self.append_objuid(objuid)
        except Exception as e:
            print ('ERROR DataFilter:', e)
            raise


    def _is_tree_tid_node_needed(self):
        __doc__ = super()._is_tree_tid_node_needed.__doc__
        return False




    def get_slicer(self):
        
        slicer = OrderedDict()
        
        data_indexes = self.data[::-1]
        
        for (di_uid, display, is_range, first, last) in data_indexes:
          
            #  print di_uid, display, is_range, first, last
          

            if not is_range:
                
                slicer[di_uid] = first
                
                
            else:
                
                slicer[di_uid] = slice(first, last)
                
        slicer = tuple(slicer.values())
        #data = data[slicer]
        return slicer
    

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
    
    
    def run(self, *objects):
        if not objects:
            return None
        slicer = self.get_slicer()
        ret_list = [obj.data[slicer] for obj in objects]
        if len(ret_list == 1):
            return ret_list[0]
        return ret_list
    

    def append_objuid(self, track_obj_ctrl_uid):    
        print('DataFilter.append_objuid:', track_obj_ctrl_uid)
        


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
                                    (data_index_uid, display, is_range, first, last)
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
            print ('ERROR append_objuid:', e)
            raise e     


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


    def reload_data(self):
       # print 'reload_data'
        UIM = UIManager()
        for toc_uid in self.track_obj_ctrls_uids:
            toc = UIM.get(toc_uid)
            toc._do_draw()
       # print 'reload_data end'    
       
       
"""   
       