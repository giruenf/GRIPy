# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 11:02:27 2016

@author: Adriano
"""

import wx
import os
import struct
import App
from collections import OrderedDict
import numpy as np
from TIF import TIFFile


PRA = {
    "Physical Record Type": (1, 1),
    "Checksum Type": (2, 2),
    "File Number Presence": (5, 1),
    "Record Number Presence": (6, 1),
    "Parity Error": (9, 1),
    "Checksum Error": (10, 1),
    "Predecessor Continuation Attribute": (14,1),
    "Sucessor Continuation Attribute": (15, 1)
}


def _get_code_default_size(code):    
    if not isinstance(code, int):
        return ValueError('code needs to be a int value.')   
    if code == 56:
        return 1    
    elif code == 65:
        return -1
    elif code == 66:
        return 1
    elif code == 68:
        return 4       
    elif code == 73:
        return 4
    elif code == 79:
        return 2
    elif code == 77:
        return -1
    elif code == 1001:
        return 1
    else:
        msg = 'Codigo ' + str(code) + ' nao reconhecido, ainda....'
        raise Exception(msg)    
        
        
def get(data, code):
    if _get_code_default_size(code) != -1 and _get_code_default_size(code) != len(data):
        msg = 'Data must have ' + str(_get_code_default_size(code)) + ' bytes. Found ' + str(len(data)) + ' bytes. (code=' + str(code) + ')'
        raise ValueError(msg)
         
   #     size = _get_code_default_size(code)
   # if size < 0:
   #     raise Exception('Size must be greater than -1.')
   # if size == 0:
   #     return None   
    if code == 56:
        return _get_value(data, 'b', True)    
    elif code == 65:
        #print 'offset: ', offset
        #print 'size: ', size
        return _get_string(data)
    elif code == 66:
        return _get_value(data, 'b', False)
    
    elif code == 68:
        values = [] 
        for i in range(len(data)):
            start = i
            end = start+1
            v = ord(data[start:end])
            values.append(v)
            
        result = ''    

        for value in values:
            result += bin(value)[2:].zfill(8)
        exponent = result[1:9]   
        fraction = result[9:32]
        
        if result[0] == '0':
            exponent = int(exponent, 2)
            fraction = int(fraction, 2) / 2. ** 23
            value = fraction * 2. ** (exponent - 128)            
        else: 
            converted_exponent = ''
            for i in range(8):
                if exponent[i] == '0':
                    converted_exponent += '1'
                else:
                    converted_exponent += '0'       
            exponent = int(converted_exponent, 2) 
            converted_fraction = ''
            achou = False
            for i in range(22, -1, -1):
                if achou:
                    if fraction[i] == '0':
                        converted_fraction = '1' + converted_fraction
                    else:
                        converted_fraction = '0' + converted_fraction  
                else:
                    converted_fraction = fraction[i] + converted_fraction
                if fraction[i] == '1':
                    achou = True                
            fraction = int(converted_fraction, 2) / 2. ** 23 
            fraction = fraction * (-1)
            value = fraction * 2. ** (exponent - 128) 
        return value        
    
    elif code == 73:
        return _get_value(data, 'l', True)
    
    elif code == 79:
        return _get_value(data, 'h', False, True)
    
    elif code == 77:
        values = []     
        for i in range(len(data)):
            values.append(ord(data[i:i+1]))
        result = ''    
        for value in values:
            result += bin(value)[2:].zfill(8)
        return  result  
    # for 'LRA'    
#    elif code == 1001:
#        self.set_offset(self.get_offset() + 1)
#        return None 
    else:
        msg = 'Codigo ' + str(code) + ' no offset nao reconhecido, ainda....'
        raise Exception(msg)       



def _get_value(data, mode, signed=True, big_endian=True):
    big = ''   
    if big_endian:
        big = '>'
    if signed is False:    
        mode = mode.upper()
    format_ = big + mode 
    n = struct.unpack(format_, data)
    return n[0]       


def _get_string(data):
    string = ''
    for i in range(len(data)):
        string += struct.unpack('s', data[i])[0]
    return string.strip()


def decode_PRA(PRA_raw_data):
    map_ = {}
    for key, value in PRA.items():
        map_[key] =  int(PRA_raw_data[value[0]:value[0]+value[1]])
    return map_    





class LogicalRegister(object):

    def __init__(self):
        self.code = -1
        self.registers = OrderedDict()

    def __str__(self):
        ret_val = 'CODIGO: ' + str(self.code) + '\n'
        ret_val += 'DATA: ' + str(self.registers) + '\n'
        return ret_val
        
    
        
        
        
class PhysicalRegister(object):

    def __init__(self):
        #self.lenght = 0
        self.attr = {}
        self.lr_data = None
        self.trailer = None

    def __str__(self):
        raise Exception()
        #return str(self.body)        




def _get_trailer_size(PRA):
    size = 0
    if PRA.get('Record Number Presence'):
       size += 2
    if PRA.get('File Number Presence'):
        size += 2
    if PRA.get('Checksum Type'):
        size += 2  
    return size    



class LISFile(object):
    
    def __init__(self):
        self.physical_records = None
        self.logical_records = None
        json_file = 'LIS_MAPPING.json'
        fullpath_json = wx.App.Get().get_app_dir() + os.sep + \
                            self.__module__.split('.')[0] + os.sep + json_file
        #print 'fullpath_json:', fullpath_json
        self._json = App.app_utils.read_json_file(fullpath_json)
        
        
    def read_file(self, file_name):
        self.file_name = file_name
        file_ = open(self.file_name, mode='rb')
        self.input_data = file_.read()
        file_.close()
        
        
    def read_physical_records(self):
        prs_data = []
        # Reading file
        result, new_data = TIFFile.desencapsulate(self.input_data)
        if result:
            self.input_data = str('')
            for d in new_data:
                self.input_data += d
        offset = 0
        while offset < len(self.input_data):
            pr_lenght_data = self.input_data[offset:offset+_get_code_default_size(79)]
            offset += _get_code_default_size(79)
            if not pr_lenght_data:
                break
            pr_lenght = get(pr_lenght_data, 79)
            pr_data = self.input_data[offset:offset+(pr_lenght-len(pr_lenght_data))]
            offset += pr_lenght-len(pr_lenght_data)
            if not pr_data:
                break
            prs_data.append(pr_data) 
        self.input_data = None    
        # Creating Physical Records, but not processing Logical Records
        self.physical_records = []        
        for pr_data in prs_data:          
            # PRA - Physical Record Attributes
            pos = 0
            PRA_data = get(pr_data[pos:pos+2], 77)
            pos += 2            
            attr = decode_PRA(PRA_data)             
            lr_data = pr_data[pos:(len(pr_data) - _get_trailer_size(attr))]
            trailer_data = pr_data[len(pr_data) - _get_trailer_size(attr):]
            trailer_pos = 0 
            trailer = {}
            if attr.get('Record Number Presence'):
                value = get(trailer_data[trailer_pos:trailer_pos+_get_code_default_size(79)], 79)
                trailer_pos += _get_code_default_size(79)
                trailer['Record Number'] = value
            if attr.get('File Number Presence'):
                value = get(trailer_data[trailer_pos:trailer_pos+_get_code_default_size(79)], 79)
                trailer_pos += _get_code_default_size(79)    
                trailer['File Number'] = value
            if attr.get('Checksum Type'):
                value = get(trailer_data[trailer_pos:trailer_pos+_get_code_default_size(79)], 79) 
                trailer['Checksum'] = value
            # If there is some continuation records, joint then    
            if attr.get('Predecessor Continuation Attribute'):
                self.physical_records[-1].lr_data = self.physical_records[-1].lr_data + lr_data    
            else:    
                pr = PhysicalRegister()  
                pr.attr = attr
                pr.lr_data = lr_data
                pr.trailer  = trailer
                self.physical_records.append(pr)
            
            
            
    def read_logical_records(self):
        self.logical_records = []        
        
        for pr in self.physical_records:
            try:
                lr = LogicalRegister()
                pos = 0
                new_pos = _get_code_default_size(66)
                lr.code = get(pr.lr_data[pos:(pos+new_pos)], 66)
                pos = new_pos
                # LRA (1 byte) is not used 
                pos += 1
                json_obj = self._json.get(str(lr.code))
                if json_obj.get('data') is None:   
                    
                    if lr.code == 0:
                        list_ = []
                        lr.registers['Frame'] =  list_
                        lr_data_format = None
                        for i in range(len(self.logical_records)-1, -1, -1):
                            if self.logical_records[i].code == 64:
                                lr_data_format = self.logical_records[i]
                                break    
                        entry_block = OrderedDict()    
                        for entry in lr_data_format.registers.get('Entry Block'):
                            value = entry.get('Entry')
                            if isinstance(value, float):
                                value = float("{0:.4f}".format(value))
                            entry_block[entry.get('Entry Type')] = value
                        curves = OrderedDict()
                        # Only one depth register per frame [entry_block.get(13)==1]                        
                        if entry_block.get(13) == 1:
                            code = entry_block.get(15)
                            size = _get_code_default_size(code)
                            depth = get(pr.lr_data[2:pos+size], code)
                            pos += size
                            depth = float("{0:.4f}".format(depth))
                            curves[-1] = depth
                        
                        # Initializing logs curves dict
                        for idx in range(len(lr_data_format.registers.get('Datum Spec Block'))):
                            curves[idx] = []                    
                        if entry_block.get(12) is not None:
                            absent_value = entry_block.get(12)
                        else:
                            absent_value = -999.25
                        while pos < len(pr.lr_data):
                            for idx, entry_dict in enumerate(lr_data_format.registers.get('Datum Spec Block')):   
                                #item_name = entry_dict.get('Mnemonic')
                                item_size = entry_dict.get('Size')
                                item_code = entry_dict.get('Representation Code')
                                item_samples = entry_dict.get('Number Samples')    
                                item_inc = item_size/item_samples                              
                                for i in range(item_samples):                                
                                    value = get(pr.lr_data[pos:pos+item_inc], item_code)
                                    value = float("{0:.6f}".format(value))
                                    curves.get(idx).append(value)
                                    pos += item_inc
                                        
                        if curves.get(-1) is not None:
                            bigger_size = 0
                            for idx in range(len(lr_data_format.registers.get('Datum Spec Block'))):
                                if len(curves.get(idx)) > bigger_size:
                                    bigger_size = len(curves.get(idx))
                            if entry_block.get(4) == 1:
                                step = entry_block.get(8) * (-1)
                            else:
                                step = entry_block.get(8)  
                            depth = []
                            for i in range(bigger_size):
                                depth.append(curves.get(-1)+i*step)
                            curves[-1] = depth    
                                
                        new_curves = OrderedDict()        
                        for idx, curve in curves.items(): 
                            new_curve = np.asarray(curve)                                
                            where = (new_curve == absent_value)
                            new_curve[where] = np.nan    
                            new_curves[idx] = new_curve
                        curves = None  
                        list_.append(new_curves)
                        self.logical_records.append(lr)
                        continue    
                         
                         
                    elif lr.code == 34:
                        json_obj = self._json.get('Component Block')
                        
                    elif lr.code == 64:
                        json_obj = self._json.get('Entry Block')
                        list_ = []
                        lr.registers['Entry Block'] =  list_
                        item = None                    
                        while item == None or item.get('Entry Type') != 0:
                            if item is not None:
                                list_.append(item) 
                            item = OrderedDict()                            
                            for d in json_obj.get('data'):
                                if d.get('name') == 'Entry':
                                    if item.get('Entry Type') == 0:
                                        pos += item.get('Entry Size')
                                        break
                                    code = item.get('Entry Repr Code Nb')
                                    value = get(pr.lr_data[pos:(pos+item.get('Entry Size'))], code)
                                    item[d.get('name')] = value
                                    pos += item.get('Entry Size')    
                                elif d.get('name') != '':
                                    value = get(pr.lr_data[pos:(pos+d.get('size'))], d.get('code'))
                                    item[d.get('name')] = value 
                                    pos += d.get('size')
                                else:
                                    pos += d.get('size')
                                    
                        json_obj = self._json.get('Datum Spec Block')
                        datum_spec_block_option = -1
                        for entry_dict in list_:
                            if entry_dict.get('Entry Type') == 1:
                                datum_spec_block_option = entry_dict.get('Entry')
                                break
                        if datum_spec_block_option == 0:
                            json_obj = self._json.get('Datum Spec Block 0')
                        elif datum_spec_block_option == 1:
                            json_obj = self._json.get('Datum Spec Block 1')
                        else:
                            raise Exception()
                    elif lr.code == 234:
                        continue                    
                        #raise Exception() 
                    else: 
                        #continue
                        raise Exception()                
                list_ = []        
                lr.registers[json_obj.get('name')] = list_    
                item = None
                while pos < len(pr.lr_data):
                    if item is not None:
                        list_.append(item)
                    item = OrderedDict()
                    for d in json_obj.get('data'):
                        if lr.code == 34 and d.get('name') == 'Component':
                            code = item.get('Component Repr Code')
                            size = item.get('Component Size')
                            value = get(pr.lr_data[pos:(pos+size)], code)         
                            pos += size
                            item[d.get('name')] = value 
                        elif d.get('name'):
                            code = d.get('code')
                            size = _get_code_default_size(code)
                            if size == -1:
                                if d.get('size') is not None:
                                    size = d.get('size')
                                else:
                                    size = len(pr.lr_data)-pos
                            #print
                            #print 'pos: ', pos
                            #print 'lr.code: ', lr.code
                            #print 'code: ', code
                            #print 'size: ', size
                            value = get(pr.lr_data[pos:(pos+size)], code)
                            pos += size
                            item[d.get('name')] = value
                        else:
                            pos += d.get('size')
                else:
                    if item is not None:
                        list_.append(item)
                self.logical_records.append(lr)
            except Exception:
                continue
           

      
    
