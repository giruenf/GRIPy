# -*- coding: utf-8 -*-

from collections import OrderedDict
from LIS import LISFile
import numpy as np


class LISWells(object):
    
    def __init__(self, lis_file):
        if not isinstance(lis_file, LISFile):
            raise Exception()
        self.lis = lis_file
        self.data = []
        i = 0
        if self.lis.logical_records:
            well = None
            for lr in self.lis.logical_records:
                if lr.code == 128:
                    i += 1
                    #print 'I: ', i
                    if well is None:
                        well = LISWell()
                    elif not well.is_closed():
                        well.close()
                        self.data.append(well)   
                        well = LISWell()
                elif lr.code == 129:
                    well.close()
                    self.data.append(well)
                    well = None
                if lr.code not in [128, 129, 130, 131, 132, 133, 234]:
                    well.add_logical_register(lr)

                    

class LISWell(object):
    
    def __init__(self):
        self.registers = []
        self.infos = None
        self.logs = None
        self._closed = False
        
    def add_logical_register(self, lr):    
        self.registers.append(lr)
        
    def close(self):
        #print 'closing....'   
        #self.header = LISWellHeaderProperties()
        for lr in self.registers:
            if lr.code == 34:
                LISWellInfoFactory.add_logical_register(lr)
            if lr.code == 0 or lr.code == 64:
                LISWellLogsFactory.add_logical_register(lr)
        self.infos = LISWellInfoFactory.get_infos()
        self.logs = LISWellLogsFactory.get_logs()
        if self.logs[0]:
            if self.logs[0].data[0] > self.logs[0].data[-1]:
                for idx in range(len(self.logs)):
                    self.logs[idx].data = np.flipud(self.logs[idx].data)    
        self._closed = True
        # to optimize memory
        self.registers = None
       
    def is_closed(self):
        return self._closed
        
    def get_depth(self):
        if self.is_closed():
            if self.logs[0]:
                return self.logs[0]
        return None    
                         
    def get_start_depth(self):
        depth_data = self.get_depth().data
        if depth_data is not None:
            return depth_data[0]
        return None    

    def get_end_depth(self):
        depth_data = self.get_depth().data
        if depth_data is not None:
            return depth_data[-1]
        return None                
                    
    def get_depth_unit(self):
        return self.get_depth().unit
                
    def get_logs(self):
        return self.logs[1:]
        
        
class LISWellLogsFactory(object):
    entry_block = None
    datum_spec_block = None
    data = None
      
    @classmethod              
    def add_logical_register(cls, lr):
        if cls.entry_block is None:
            cls.entry_block = OrderedDict()
        if cls.datum_spec_block is None:
            cls.datum_spec_block = OrderedDict()
        if cls.data is None:        
            cls.data = OrderedDict()
        if lr.code == 0:
            frame = lr.registers.get('Frame')
            for od in frame:
                for k, values in od.items():       
                    if cls.data.get(k) is None:
                        cls.data[k] = values
                    else:
                        cls.data[k] = np.append(cls.data.get(k), values)
        elif lr.code == 64:        
            for entry in lr.registers.get('Entry Block'):
                cls.entry_block[entry.get('Entry Type')] = entry.get('Entry')   
            cls.datum_spec_block = lr.registers.get('Datum Spec Block')
        else:    
            raise Exception()   
      
    @classmethod       
    def get_logs(cls):
        curves = []
        if cls.data.get(-1) is not None:
            curves.append(LISWellLog('DEPT', cls.entry_block.get(14), cls.data.get(-1))) 
        for idx, curve in enumerate(cls.datum_spec_block):
            curves.append(LISWellLog(curve.get('Mnemonic'), curve.get('Units'), cls.data.get(idx)))
        # to optimize memory
        cls.data = None    
        cls.entry_block = None
        cls.datum_spec_block = None 
        return curves
          
          
# Just a wrapper to LISModel
class LISWellLog(object):
    def __init__(self, mnem, unit, data):
        self.mnem = mnem
        self.unit = unit
        self.data = data
        
    def get_first_occurence_pos(self):
        #print np.isnan(self.data)
        for idx, boolean in enumerate(np.isnan(self.data)):
            if not boolean:
                #print 'RETORNOU FIRST: ', idx
                return idx
                
    def get_last_occurence_pos(self):
        print '\nLISWellLog.get_last_occurence_pos'
        y = np.isnan(self.data)
        print y, len(y)
        for idx in range(len(y)-1, -1, -1):
            if not y[idx]:
                print 'RETORNOU LAST: ', idx
                return idx                
        print 'DEU RUIM' 
        
        
class LISWellInfoFactory(object):
    
    data = None
     
    @classmethod      
    def add_logical_register(cls, lr):
        if lr.code not in [34]:
            raise Exception()
        type_ = None
        info = OrderedDict()
        
        for component in lr.registers.get('Component Block'):
            if component.get('Component Mnemonic') == 'TYPE' and type_ is None:
                type_ = component.get('Component')
            else:    
                if info.get(component.get('Component Mnemonic')) is None:
                    info[component.get('Component Mnemonic')] = [component.get('Component')]
                else:
                    print '\nAAA:', component.get('Component Mnemonic')
                    print info
                    print 'III: ', info.get(component.get('Component Mnemonic'))
                    info.get(component.get('Component Mnemonic')).append(component.get('Component'))
        if cls.data is None:
            cls.data = OrderedDict()
        if cls.data.get(type_) is None:
            cls.data[type_] = info
        else:
            cls.data.get(type_).update(info)
            
   
    @classmethod     
    def get_infos(cls):
        infos = []
        for type_, values_dict in cls.data.items():
            lis_info = LISWellInfo(type_)
            lis_info.data = values_dict
            infos.append(lis_info)
        cls.data = None    
        return infos

            
# Just a wrapper to LISModel
class LISWellInfo(object):
    def __init__(self, type_=None):
        self.type = type_
        self.data = OrderedDict()
        
        
                    