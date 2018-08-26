# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 14:21:15 2018

@author: Adriano
"""


from collections import OrderedDict

from classes.om import DataObject
from classes.om import ObjectManager



class WellData1D(DataObject):                             
    tid = "data1d"
    
    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['index_uid'] = {
        'default_value': None,
        'type': str       
    }  
    
    
    def __init__(self, data, **attributes):
#        print ('\nattributes:', attributes)
        """
        index_set_uid = attributes.get('index_set_uid')
        try:    
            tid, oid = index_set_uid 
        except:
            print (index_set_uid, type(index_set_uid))										
            raise Exception('Object attribute \"index_set_uid\" must be a \"uid\" tuple.')    
        if tid != 'index_set':
            raise Exception('Object attribute \"index_set_uid\" must have its first argument as \"index_set\".')
        """
        super().__init__(data, **attributes)

#        OM = ObjectManager()        
#        OM.subscribe(self._on_OM_add, 'add')

    """
    def _on_OM_add(self, objuid):
        if objuid != self.uid:
            return
        #print 'WellData1D._on_OM_add:', objuid
        OM = ObjectManager()
        try:
            OM.unsubscribe(self._on_OM_add, 'add')     
        except Exception as e:
            print ('Deu ruim no unsub:', e)
        try:
            parent_uid = OM._getparentuid(self.uid)
            # TODO: remover esse armengue
            if self.tid == 'part':
                parent_well_uid = OM._getparentuid(parent_uid)
            else:
                parent_well_uid = parent_uid
            # FIM - Armengue    
        #    print 'parent_well_uid:', parent_well_uid
            my_index_set = OM.get(self.index_set_uid)
        #    print 'my_index_set:', my_index_set
        #    print 'list:'
        #    for obj_is in OM.list('index_set', parent_well_uid):
        #        print obj_is
            if my_index_set not in OM.list('index_set', parent_well_uid):
                print ('DEU RUIM')
                raise Exception('Invalid attribute \"index_set\"={}'.format(self.index_set_uid))
        except:
            raise

    @property
    def index_set_uid(self):
        return self.attributes['index_set_uid']
    """

    def get_data_indexes(self):
        ret_dict = OrderedDict()
        OM = ObjectManager()
#        print (self.__dict__)
        
        index_uid = parse_string_to_uid(self.index_uid)
        index = OM.get(index_uid)

        ret_dict[0] = [index]
        return ret_dict  

    """
    def get_data_indexes(self):
        OM = ObjectManager()    
        
        
        try:
            index_set = OM.get(self.index_set_uid)
            return index_set.get_data_indexes()
        except:
            return None
    """    
        
    def get_indexes(self):
        raise Exception('Invalid METHOD')   
    
    def get_friendly_name(self):
        OM = ObjectManager()
        parent_well_uid = OM._getparentuid(self.uid)
        parent_well = OM.get(parent_well_uid)         
        return self.name + '@' + parent_well.name



    