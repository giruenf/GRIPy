"""
    Pyhton DLIS file reader
    Adriano Paulo - adrianopaulo@gmail.com
    July 2016
      
    
    PREFACE:
    
        American Petroleum Institute (API) Standard RP66 Version 1 (RP66 V1), 
        published in May 1991, specified a format for digital well log data, 
        called Digital Log Interchange Standard (DLIS). 
        RP66 V1 publication was under jurisdiction of API until June 1998, 
        when Petrotechnical Open Software Corporation (POSC) accepted its 
        stewardship.
        In November 2006, POSC re-brands itself as Energistics.
          
    PURPOSE:
    
        This software was created to read DLIS files.
        At this time only DLIS Version 1 (RP66 V1) is supported.


    SOURCES:

        This code was developed based on Energistics RP66 V1 standard:
            http://w3.energistics.org/RP66/V1/Toc/main.html
            
      
    USAGE:
        
        (1) To read a DLIS file into memory, just use:
        
            dlis = DLISFile()                 (mandatory) 
            dlis.read(filename)               (mandatory) 
                
        
        (2) An example of usage (just a example) can be shown with:
        
            dlis.print_logical_file()     (optional)        
            
            The function above is just a taste of this DLIS reader, it 
            produces some result like this:
            
            
            Logical File: 0
    
            1&0&B61441
    
               #1
                  0&0&INDEX :  1640.375 m
                  1&0&DT :  -999.25 us/ft
                  1&0&GR :  51.84400177 gAPI
                  1&0&ILD :  0.0189999993891 ohm.m
                  1&0&CALI :  12.3409996033 in
                  1&0&RHOB :  4.29400014877 g/cm3
                  1&0&NPHI :  0.675999999046 m3/m3
            
               #2
                  0&0&INDEX :  1640.5 m
                  1&0&DT :  -999.25 us/ft
                  1&0&GR :  55.9160003662 gAPI
                  1&0&ILD :  0.0189999993891 ohm.m
                  1&0&CALI :  12.3509998322 in
                  1&0&RHOB :  4.29400014877 g/cm3
                  1&0&NPHI :  0.65030002594 m3/m3
                 
                ...
                
               #n   
           
       
       
        (3) For a real usage, use these data structures:
       
            - dlis.data: a list of Logical Wells data. Each Logical Well data 
                         is an OrderedDict containing object name as key and 
                         another OrderedDict as object values, that values are
                         a OrderedDict too containing data index as key 
                         (e.g #1, #2, #n) and a list of values as a dict value.
                         This list of values are the real log data values.
                         The structure is illustrated below.
                
                -> Logical Well Data 1    
                -> Logical Well Data 2
                  --> (object_name_1, object_dict_1), where object_dict_1 is: 
                     ---> (data_index_1, list_of_values_1)
                     ---> (data_index_2, list_of_values_2)
                     ---> (data_index_n, list_of_values_n)
                  --> (object_name_2, object_dict_2)
                  --> (object_name_n, object_dict_n)
                -> Logical Well Data n    
                
                
            - dlis.data_props: a list of Logical Wells properties. Each Logical
                        Well properties is an OrderedDict containing object 
                        name as key and another OrderedDict as values 
                
   **** (????)         - dlis.SUL: a list of well parameters (header parameters).


            - dlis.file_header = None
            - dlis.origin = None
            - dlis.parameter = None
            - dlis.frame = None
            - dlis.channel = None    
   
"""

import os        
import struct
from collections import OrderedDict

import numpy as np

import app
#from multiprocessing import Process, Queue
#import threading
#import utils



def _get_value(data, format_, big_endian=True):
    big = ''   
    if big_endian:
        big = '>'
    format_ = big + format_ 
    try:
#        print()
#        print(data, type(data))
        n = struct.unpack(format_, data)
#        print(n)
#        print(n[0], type(n[0]))
#        print()
        return n[0]
    except Exception:
        raise

    
    
def get_from_list(data_list, start_offset, code, size=None):
    code_spec = RepresentationCodes.get_code(code)
#    print()
#    print('\nget_from_list', start_offset, code, code_spec)
    if code_spec is None:
        msg = 'Code ' + str(code) + ' is not recognized.'
        raise Exception(msg)
    special = code_spec.get('special')
    if special is None:
        if code_spec.get('size') != "variable":
            return start_offset+code_spec.get('size'), \
                   _get_value(data_list[start_offset:start_offset+\
                                        code_spec.get('size')],\
                   code_spec.get('format')
            )
        else:
            raise Exception()
            
    if special:       
        if code == 1:
            raise Exception()
            '''
            v1 = ord(data_list[start_offset:start_offset+1])
            v2 = ord(data_list[start_offset+1:start_offset+2])
            result = bin(v1)[2:].zfill(8)  
            result += bin(v2)[2:].zfill(8)
            fraction = result[1:12]
            exponent = result[12:16]               
            if result[0] == '0':
                exponent = int(exponent, 2)
                fraction = int(fraction, 2) / 2. ** 23
                value = fraction * 2. ** (exponent)      
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
            return start_offset+2, value     
            '''    
        elif code == 2:
            values = [] 
            for i in range(4):
                v = ord(data_list[start_offset+i:start_offset+i+1])
                values.append(v) 
            result = ''    
            for value in values:
                result += bin(value)[2:].zfill(8)
            exponent = result[1:9]   
            mantissa = result[9:32]
            exponent = int(exponent, 2)
            mantissa = int(mantissa, 2) / 2. ** 23
            if result[0] == '1':
                value = -(1 + mantissa) * 2. ** (exponent - 127) 
            else:
                value = (1 + mantissa) * 2. ** (exponent - 127)                    
            return start_offset+4, value    
        elif code == 3:
            new_offset, V = get_from_list(data_list, start_offset, 2)           # FSINGL
            new_offset, A = get_from_list(data_list, new_offset, 2)             # FSINGL
            # V is a nominal value with a confidence interval of [V - A, V + A]
            return new_offset, V, A
        elif code == 4:
            new_offset, V = get_from_list(data_list, start_offset, 2)           # FSINGL
            new_offset, A = get_from_list(data_list, new_offset, 2)             # FSINGL
            new_offset, B = get_from_list(data_list, new_offset, 2)             # FSINGL
            # V is a nominal value with a confidence interval of [V - A, V + B]
            return new_offset, V, A, B
        elif code == 5:
            values = [] 
            for i in range(4):
                v = ord(data_list[start_offset+i:start_offset+i+1])
                values.append(v) 
            result = ''    
            for value in values:
                result += bin(value)[2:].zfill(8)
            exponent = result[1:8]   
            mantissa = result[8:32]
            exponent = int(exponent, 2)
            mantissa = int(mantissa, 2)
            if result[0] == '1':
                value = -1 * mantissa * 16. ** (exponent - 64) 
            else:
                value = mantissa * 16. ** (exponent - 64)            
            return start_offset+4, value    
        #
        elif code == 6:
            raise Exception('code == 6!!!')
            
        #    
        elif code == 7:    
            values = [] 
            for i in range(8):
                v = ord(data_list[start_offset+i:start_offset+i+1])
                values.append(v) 
            result = ''    
            for value in values:
                result += bin(value)[2:].zfill(8) 
            exponent = result[1:12]   
            mantissa = result[12:64]    
            exponent = int(exponent, 2)
            mantissa = int(mantissa, 2)
            if result[0] == '1':
                value = -1 * (1 + mantissa) * 2. ** (exponent - 1023) 
            else:
                value = (1 + mantissa) * 2. ** (exponent - 1023)          
            return start_offset+8, value
        elif code == 8:
            new_offset, V = get_from_list(data_list, start_offset, 7)           # FDOUBL
            new_offset, A = get_from_list(data_list, new_offset, 7)             # FDOUBL
            # V is a nominal value with a confidence interval of [V - A, V + A]
            return new_offset, V, A
        elif code == 9:
            new_offset, V = get_from_list(data_list, start_offset, 7)           # FDOUBL
            new_offset, A = get_from_list(data_list, new_offset, 7)             # FDOUBL
            new_offset, B = get_from_list(data_list, new_offset, 7)             # FDOUBL
            # V is a nominal value with a confidence interval of [V - A, V + B]          
            return new_offset, V, A, B
        elif code == 10:
            new_offset, R = get_from_list(data_list, start_offset, 2)           # FSINGL
            new_offset, I = get_from_list(data_list, new_offset, 2)             # FSINGL
            # Value = R + i* I,  i = (-1)1/2
            return new_offset, R, I
        elif code == 11:    
            new_offset, R = get_from_list(data_list, start_offset, 7)           # FDOUBL
            new_offset, I = get_from_list(data_list, new_offset, 7)             # FDOUBL
            # Value = R + i* I,  i = (-1)1/2
            return new_offset, R, I
        elif code == 18 or code == 22:
            #print data_list[start_offset:start_offset+1]
            try:
                bin_vec = bin(ord(data_list[start_offset:start_offset+1]))[2:].zfill(8)
            except Exception:
                print('start_offset:', start_offset, len(data_list))
                raise Exception('Verificar IndexError')
            if bin_vec[0] == '0':
                return start_offset+1, int(bin_vec, 2)
            else:
                if bin_vec[1] == '0':
                    bin_vec = '0' + bin_vec[1:]
                    bin_vec +=  bin(ord(data_list[start_offset+1:start_offset+2]))[2:].zfill(8)
                    return start_offset+2, int(bin_vec, 2)
                else:
                    bin_vec = '00' + bin_vec[2:]
                    bin_vec +=  bin(ord(data_list[start_offset+1:start_offset+2]))[2:].zfill(8)
                    bin_vec +=  bin(ord(data_list[start_offset+2:start_offset+3]))[2:].zfill(8)
                    bin_vec +=  bin(ord(data_list[start_offset+3:start_offset+4]))[2:].zfill(8)
                    return start_offset+4, int(bin_vec, 2)
        elif code == 19 or code == 27:
            new_offset, value = get_from_list(data_list, start_offset, 15)      # USHORT
            return new_offset+value, \
                   data_list[new_offset:new_offset+value].decode("utf-8")
        elif code == 20:  
            new_offset, value = get_from_list(data_list, start_offset, 18)      # UVARI
            return new_offset+value, \
                    data_list[new_offset:new_offset+value].decode("utf-8")
        elif code == 21:
            dtime = OrderedDict()
            new_offset, year = get_from_list(data_list, start_offset, 15)       # USHORT
            year = 1900 + year
            dtime['Y'] = year
            v1 = ord(data_list[new_offset:new_offset+1])
            new_offset += 1
            result = bin(v1)[2:].zfill(8)  
            tz = result[0:4]
            m = result[4:8]
            dtime['TZ'] = tz
            dtime['M'] = m
            new_offset, day = get_from_list(data_list, new_offset, 15)          # USHORT
            dtime['D'] = day
            new_offset, hours = get_from_list(data_list, new_offset, 15)        # USHORT
            dtime['H'] = hours
            new_offset, minutes = get_from_list(data_list, new_offset, 15)      # USHORT
            dtime['MN'] = minutes
            new_offset, seconds = get_from_list(data_list, new_offset, 15)      # USHORT
            dtime['S'] = seconds
            new_offset, milliseconds = get_from_list(data_list, new_offset, 16) # UNORM
            dtime['MS'] = milliseconds
            return new_offset, dtime
        elif code == 23:
            new_offset, O = get_from_list(data_list, start_offset, 22)          # ORIGIN
            new_offset, C = get_from_list(data_list, new_offset, 15)            # USHORT
            new_offset, I = get_from_list(data_list, new_offset, 19)            # IDENT
            return new_offset, (O, C, I)
            # O = Origin Reference
            # C = Copy Number
            # I = Identifier
        elif code == 24: 
            new_offset, T = get_from_list(data_list, start_offset, 19)          # IDENT
            new_offset, N = get_from_list(data_list, new_offset, 23)            # OBNAME
            objref = OrderedDict() 
            objref['T'] = T
            objref['N'] = N
            # T = obj type - N = obj name
            return new_offset, objref
        elif code == 25:
            new_offset, T = get_from_list(data_list, start_offset, 19)           # IDENT
            new_offset, N = get_from_list(data_list, start_offset, 23)           # OBNAME
            new_offset, T = get_from_list(data_list, start_offset, 19)           # IDENT
            raise Exception()
            # T = Object Type
            # N = Object Name
            # L = Attribute Label
        elif code == 26: 
             new_offset, value = get_from_list(data_list, start_offset, 15)      # USHORT
             if value == 0:
                 return False
             if value == 1:
                 return True
             raise Exception()
        elif code == 28:
            v1 = ord(data_list[start_offset:start_offset+1])
            result = bin(v1)[2:].zfill(8)   
            ret = []
            for i in range(len(result)):
                ret.append(int(result[i]))
            return start_offset+1, ret
            """
            0: Logical Record Structure
                0 = Indirectly Formatted Logical Record
                1 = Explicitly Formatted Logical Record
            
            1: Predecessor
                0 = This is the first segment of the Logical Record
                1 = This is not the first segment of the Logical Record
            
            2: Successor
                0 = This is the last Segment of the Logical Record.
                1 = This is not the last Segment of the Logical Record
            
            3: Encryption
                0 = No encryption.
                1 = Logical Record is encrypted
            
            4: Encryption Packet
                0 = No Logical Record Segment Encryption Packet
                1 = Logical Record Segment Encryption Packet is present
            
            5: Checksum
                0 = No checksum
                1 = A checksum is present in the LRST
            
            6: Trailing Length
                0 = No Trailing Length
                1 = A copy of the LRS lengt is present in the LRST
            
            7: Padding
                0 = No record padding
                1 = Pad bytes are present in LRST 
            """         
            




"""
    Given a Explicitly Formatted Logical Record (EFLR) code, returns its type,
    description and allowed set types.
        
"""
'''
def get_EFLR_for_code(EFLR_code):
    if not isinstance(EFLR_code, int):
        raise Exception('EFLR_code must be a int value.')
    if EFLR_code < 0 or EFLR_code > 127:
        raise Exception('EFLR code does not exist.')
    if EFLR_code > 11: 
        raise Exception('Undefined or reserved EFLR code are not available at this time.') 
    ret = {}    
    if EFLR_code == 0:    
        ret['type'] = 'FHLR'
        ret['desc'] = 'File Header'
        ret['allow'] = ['FILE-HEADER']
    elif EFLR_code == 1:
        ret['type'] = 'OLR'
        ret['desc'] = 'Origin'
        ret['allow'] = ['ORIGIN', 'WELL-REFERENCE']
    elif EFLR_code == 2:
        ret['type'] = 'AXIS'
        ret['desc'] = 'Coordinate Axis'
        ret['allow'] = ['AXIS']
    elif EFLR_code == 3:
        ret['type'] = 'CHANNL'
        ret['desc'] = 'Channel-related information'
        ret['allow'] = ['CHANNEL']
    elif EFLR_code == 4:
        ret['type'] = 'FRAME'
        ret['desc'] = 'Frame Data'
        ret['allow'] = ['FRAME', 'PATH']        
    elif EFLR_code == 5:
        ret['type'] = 'STATIC'
        ret['desc'] = 'Static Data'
        ret['allow'] = ['CALIBRATION', 'CALIBRATION-COEFFICIENT', \
            'CALIBRATION-MEASUREMENT', 'COMPUTATION', 'EQUIPMENT', 'GROUP',\
            'PARAMETER', 'PROCESS', 'SPICE', 'TOOL', 'ZONE']
    elif EFLR_code == 6:
        ret['type'] = 'SCRIPT'
        ret['desc'] = 'Textual Data'
        ret['allow'] = ['COMMENT']
    elif EFLR_code == 7:
        ret['type'] = 'UPDATE'
        ret['desc'] = 'Update Data'
        ret['allow'] = ['UPDATE']
    elif EFLR_code == 8:
        ret['type'] = 'UDI'
        ret['desc'] = 'Unformatted Data Identifier'
        ret['allow'] = ['NO-FORMAT']   
    elif EFLR_code == 9:
        ret['type'] = 'LNAME'
        ret['desc'] = 'Long Name'
        ret['allow'] = ['LONG-NAME']
    elif EFLR_code == 10:
        ret['type'] = 'SPEC'
        ret['desc'] = 'Specificfation'
        ret['allow'] = ['ATTRIBUTE', 'CODE', 'EFLR', 'IFLR', 'OBJECT-TYPE',\
            'REPRESENTATION-CODE', 'SPECIFICATION', 'UNIT-SYMBOL']
    elif EFLR_code == 11:
        ret['type'] = 'DICT'
        ret['desc'] = 'Dictionary'
        ret['allow'] = ['BASE-DICTIONARY', 'IDENTIFIER', 'LEXICON', 'OPTION']
    return ret    
'''



def get_objname_from_tuple(obj_name_tuple):
    """Given a O, C, I tuple, return its string full name 
    (e.g 0&0&DEFINING_ORIGIN).
    """
    O, C, I = obj_name_tuple
    return str(O) + '&' + str(C) + '&' + I


def get_actual_objname(full_object_name):
    """Given a object string full name (e.g 0&0&DEFINING_ORIGIN), returns
    its name (e.g DEFINING_ORIGIN).
    """
    return full_object_name.split('&')[2]


class RepresentationCodes(object):
    instance = None
    
    def __init__(self):
        # base_path == this floder
        base_path = os.path.dirname(os.path.abspath(__file__))
        rc_json_file = 'representation_codes.json'
        self.codes = app.app_utils.read_json_file(
                os.path.join(base_path, rc_json_file)
        )
        
    @classmethod    
    def start(cls):
        if cls.instance is None:
            cls.instance = RepresentationCodes()
           
    @classmethod    
    def get_code(cls, code):
        val = None
        if cls.instance:
            val = cls.instance.codes[code-1]
        return val



class DLISObjectPool(object):
    current_file_number = -1
    current_lr = -1
    lrs = None
    objects = None
    lr_to_object = None
    object_to_lr = None

    @classmethod
    def init_pool(cls):
        """Init DLISObjectPool attributes.
        """
        cls.current_file_number = -1
        cls.current_lr = -1
        cls.lrs = OrderedDict()
        cls.objects = OrderedDict()
        cls.lr_to_object = OrderedDict()
        cls.object_to_lr = OrderedDict()    
    
    @classmethod
    def register_logical_record(cls, lr_structure_type, lr_type, lr_code):
        """Register a new Logical Record, with its structure type, LR type,
        LR code.
        """
        if lr_structure_type != 0 and lr_structure_type != 1:
            raise Exception('Logical Record Structure type invalid. ' + 
                'Valid types are 0 for IFLRs or 1 for EFLR.')        
        # Starting a new logical file    
        if lr_type == 'FILE-HEADER':
            if cls.lrs is None:
                cls.init_pool()
            cls.current_file_number += 1    
            cls.lrs[cls.current_file_number] = OrderedDict()
            cls.lr_to_object[cls.current_file_number] = OrderedDict()
            cls.object_to_lr[cls.current_file_number] = OrderedDict()
            cls.current_lr = 0
        else:
            cls.current_lr += 1
        new_set = OrderedDict()       
        new_set['type'] = lr_type
        new_set['code'] = lr_code
        new_set['structure_type'] = lr_structure_type
        new_set['template'] = []
        new_set['closed'] = False
        cls.lrs.get(cls.current_file_number)[cls.current_lr] = new_set
        cls.lr_to_object.get(cls.current_file_number)[lr_type] = []

    @classmethod
    def register_object(cls, object_name):
        """Register a new DLIS Object, with its name.
        """
        if not cls.get_logical_records()[-1].get('closed'):
            cls.get_logical_records()[-1]['closed'] = True
        if cls.objects.get(cls.current_file_number) is None:
            cls.objects[cls.current_file_number] = OrderedDict()
        cls.objects.get(cls.current_file_number)[object_name] = []
        current_lr = cls.get_logical_records()[-1]
        cls.object_to_lr.get(cls.current_file_number)[object_name] = current_lr.get('type')
        cls.lr_to_object.get(cls.current_file_number).get(current_lr.get('type')).append(object_name)

    @classmethod
    def get_logical_records(cls, file_number=None):
        if file_number is None:
            file_number = cls.current_file_number          
        return list(cls.lrs.get(file_number).values())
                       
    @classmethod
    def get_logical_record(cls, lr_type, file_number=None):
        for lr in cls.get_logical_records(file_number):
            if lr.get('type') == lr_type:
                return lr
        return None     

    @classmethod
    def get_objects_of_type(cls, lr_type, file_number=None):
        if file_number is None:
            file_number = cls.current_file_number
        obj_names = cls.lr_to_object.get(file_number).get(lr_type)  
        ret_map = OrderedDict()
        if not obj_names:
            return ret_map
        for obj_name in obj_names:
            ret_map[obj_name] = cls.objects.get(cls.current_file_number).get(obj_name)
        return ret_map 
       
    @classmethod
    def get_objects_dict_of_type(cls, lr_type, file_number=None):      
        if file_number is None:
            file_number = cls.current_file_number  
        ret_map = OrderedDict()    
        objects = cls.get_objects_of_type(lr_type, file_number)
        if not objects:
            return ret_map
        template_list = cls.get_logical_record(lr_type, file_number).get('template')       
        for obj_name, obj_values in objects.items():
            obj_map = OrderedDict()
            for idx, value in enumerate(obj_values):
                #print 'idx', idx, template_list[idx]
                obj_map[template_list[idx].get('name')] = value
            ret_map[obj_name] = obj_map    
        return ret_map
  
    @classmethod 
    def get_object_values_list(cls, object_name, file_number=None):
        """Given a object name (e.g 0&0&WN or 1&0&RHOB) return its values list.
        If file_number is not given, the latest one will be used. 
        """
        if file_number is None:
            file_number = cls.current_file_number
        obj_values_list = cls.objects.get(file_number).get(object_name)
        return obj_values_list
        
    @classmethod 
    def get_object_values_dict(cls, object_name, file_number=None):
        if file_number is None:
            file_number = cls.current_file_number        
        obj_values_list = cls.get_object_values_list(object_name, file_number)
        if obj_values_list is None:
            return None
        lr_type = cls.object_to_lr.get(file_number).get(object_name) 
        ret_map = OrderedDict()    
        for set_map in list(cls.lrs.get(file_number).values()):
            if set_map.get('type') == lr_type:
                for idx, template in enumerate(set_map.get('template')):
                    try:
                        ret_map[template.get('name')] = obj_values_list[idx]
                    except IndexError:
                        return ret_map
        return ret_map    
     
     
        
    
def _get_SUL(data):    
    # Getting Storage Unit Label (SUL)
    if len(data) != 80 and len(data) != 128:
        raise Exception('Input data size not according excepted (Excepted 80 or 120 bytes).')
    SUL = OrderedDict()
    SUL['Storage unit sequence number'] = data[0:4].decode("utf-8").strip() 
    SUL['RP66 version and format edition'] = data[4:9].decode("utf-8").strip() 
    SUL['Storage unit structure'] = data[9:15].decode("utf-8").strip() 
    if SUL.get('RP66 version and format edition').split('.')[0] == 'V1':
        SUL['Maximum visible record length'] = data[15:20].decode("utf-8").strip() 
        SUL['Storage set identifier'] = data[20:80].decode("utf-8").strip() 
    elif SUL.get('RP66 version and format edition').split('.')[0] == 'V2':
        if len(data) == 80:
            raise Exception('DLIS version 2 needs 128 bytes for Storage Unit Label (SUL).')
        SUL['Binding edition'] = data[15:19].decode("utf-8").strip()    
        SUL['Maximum visible record length'] = data[19:29].decode("utf-8").strip()  
        SUL['Producer organization code'] = data[29:39].decode("utf-8").strip() 
        SUL['Creation date'] = data[39:50].decode("utf-8").strip() 
        SUL['Serial number'] = data[50:62].decode("utf-8").strip()  
        SUL['reserved'] = data[62:68].decode("utf-8").strip() 
        SUL['Storage set identifier'] = data[68:128].decode("utf-8").strip() 
    return SUL

   
   
class DLISFile(object):
    
    def __init__(self):
        RepresentationCodes.start()
        # base_path == this floder
        base_path = os.path.dirname(os.path.abspath(__file__))
        mapping_file = 'DLIS_RP66V1_MAPPING.json'
        self.mapping = app.app_utils.read_json_file(
                os.path.join(base_path, mapping_file)
        )
        #
        self._clear()


    def _clear(self):
        #
        DLISObjectPool.init_pool()
        #
        self.SUL = None    
        self.file_size = -1
        self.data = None
        self.data_props = None
        #
        self.file_header = None
        self.origin = None
        self.parameter = None
        self.frame = None
        self.channel = None
        #
        #self.queue = Queue()
        #
        


    def get_file_read_percent(self):
        if self.file_size == -1:
            return 0
        return float(self.file.tell())*100/self.file_size            
          
    @staticmethod      
    def is_DLIS_file(filename):  
        try:
            file_ = open(filename, mode='rb')
            # Getting Storage Unit Label (SUL)
            SUL = _get_SUL(file_.read(128))
            file_.close()
            if SUL.get('RP66 version and format edition').split('.')[0] != 'V1' \
            and SUL.get('RP66 version and format edition').split('.')[0] != 'V2':
                return False
            return True    
        except Exception:
            return False
        
        
    def print_logical_file(self, file_index=None, limit=None):
        if file_index is None:
            file_index = range(len(self.data))
        elif file_index == -1:
            file_index = range(len(self.data)-1, len(self.data), 1)
        elif file_index >= 0 and file_index < len(self.data):
            file_index = range(file_index, file_index+1, 1)
        else:
            raise Exception()
        if limit is not None:
            counter = 1
        for idx in file_index:
            datum = self.data[idx]
            print('\n\nLogical File:', idx)                
            for object_name, object_dict in datum.items():
                 print('\n', object_name)
                 for data_idx, data_values in object_dict.items():
                     print('\n  ', data_idx)
                     for i, v in enumerate(data_values): 
                         print('     ', list(self.data_props[idx].get(object_name).keys())[i], \
                             ': ', v, list(self.data_props[idx].get(object_name).values())[i].get('UNITS'))
                     if limit is not None:
                         if counter == limit:
                             msg = '\nLimit of ' + str(limit) + ' registers was reached. End of print.'
                             print(msg)
                             return
                         else:    
                             counter += 1
        print('\nEnd of print.')
                         
    '''                     
    def read(self, filename, callback=None, threading_stop_event=None):
        #t = threading.Thread(target=self._read, args=(filename, callback))                     
        #t.start()
        #t.join()
        p = Process(target=self._read, args=(filename, callback))                     
        p.start()
        p.join()    
    '''    
        
    def read(self, filename, callback=None, threading_stop_event=None):
        # Clear DLISObjectPool
        DLISObjectPool.init_pool()
        #
        self.filename = filename
        #self.callback = callback
        self.file = open(self.filename, mode='rb')
        self.file_size = os.fstat(self.file.fileno()).st_size
        # Getting Storage Unit Label (SUL)
        self.SUL = _get_SUL(self.file.read(128))
        
#        print()
#        print(self.SUL)
#        print()
        
        if self.SUL.get('RP66 version and format edition').split('.')[0] == 'V1':
            self.file.seek(80)
        elif self.SUL.get('RP66 version and format edition').split('.')[0] != 'V2': 
            raise Exception('This is not a DLIS File.')
        #     
        self._read_Logical_Records(callback, threading_stop_event)
        #self._reading_process = Process(target=self._read_Logical_Records, 
        #                                args=(stop_event, 'task'))                 
        #print 'a', self.file.tell() 
        #self._reading_process.start()
        #print 'b', self.file.tell(), self._reading_process.is_alive() 
        #self._reading_process.join()   
        #print 'c', self.file.tell(), self._reading_process.is_alive()  
        #
        self.file.close()
        #
        self._load_file_header_props()
        self._load_origin_props()
        self._load_parameter_props()
        self._load_frame_props()
        self._load_channel_props()
        #
        if threading_stop_event:
            if threading_stop_event.is_set():
                print('File reading canceled by user.')
            else:    
                self.print_logical_file(-1, 1)
        else:    
            self.print_logical_file(-1, 1)           
        #
        print('\n\nself.data_props')
        print(self.data_props)
        
        
        
        # TODO: rever self._curves_info
        self._curves_info = OrderedDict()
        for item_od in self.data_props:
            for curve_set_name in list(item_od.keys()):
                curve_info_od = item_od[curve_set_name]
                curve_set_name = get_actual_objname(curve_set_name)
                self._curves_info[curve_set_name] = []
                for curve_name, curve_props_od in curve_info_od.items():
                    curve_actual_name = get_actual_objname(curve_name)
                    curve_unit = curve_props_od['UNITS'].lower()
                    self._curves_info[curve_set_name].append(
                                                (curve_actual_name, curve_unit)
                    )
        #
        print('\n\nself._curves_info')
        print(self._curves_info)
        #
#        print('\n\nself.data')
#        print(self.data)
        #
        
#        """
        # TODO: rever self._curves_data
        self._curves_data = OrderedDict()
        for curve_set_name, curves_info_list in self._curves_info.items():
            self._curves_data[curve_set_name] = []
            for idx in range(len(curves_info_list)):
                self._curves_data[curve_set_name].append([])
        #    
        for item_od in self.data:
            for iflr_descriptor in list(item_od.keys()):
                curve_data_od = item_od[iflr_descriptor]
                curve_set_name = get_actual_objname(iflr_descriptor)
                
                for curves_data_list in list(curve_data_od.values()):
                    for idx, value in enumerate(curves_data_list):
#                        print('idx val:', idx, value)
                        self._curves_data[curve_set_name][idx].append(value)
        #
        for curves_data_list in list(self._curves_data.values()):
            for idx in range(len(curves_data_list)):
                curves_data_list[idx] = np.asarray(curves_data_list[idx])

        """
        print('\n\nself._curves:')
        for curve_set_name, curves_data_list in self._curves_data.items():
            print()
            print('CURVE_SET:', curve_set_name)
            print()
            for idx in range(len(curves_data_list)):
                print()
                print(self._curves_info[curve_set_name][idx])
                print(self._curves_data[curve_set_name][idx]) 
        """    


    def _load_file_header_props(self):
        self.file_header = self._get_logical_record_props('FILE-HEADER')



    def _load_origin_props(self): 
        self.origin = OrderedDict()
        origin_od = self._get_logical_record_props('ORIGIN')
        # id = 0 have all info we really need. Other are used when there are
        # copies as stated by RP66 V1.
        if not origin_od:
            return        
        
#        print('\n\n\norigin_od:', origin_od)
#        print('\n\n\n')
        try:
            obj_name, obj_map = list(origin_od.items())[0]
            print(obj_name)
            print(obj_map)
            for key, value in obj_map.items():
#                print('kv:', key, value)
                self.origin[key] = value
        except:
            raise
#        print('FIM _load_origin_props')    
        
    def _load_parameter_props(self):
        self.parameter = OrderedDict()
        params_od = self._get_logical_record_props('PARAMETER')
        if not params_od:
            return
        for obj_name, obj_dict in params_od.items():
            self.parameter[get_actual_objname(obj_name)] = obj_dict['VALUES']


    def _load_frame_props(self): 
        self.frame = OrderedDict()
        frame_od = self._get_logical_record_props('FRAME')    
        if not frame_od:
            return
        for obj_name, obj_dict in frame_od.items():
            frame_obj_od = OrderedDict()
            self.frame[get_actual_objname(obj_name)] = frame_obj_od
            frame_obj_od['CHANNELS'] = []
            for chan_obj_name in obj_dict.pop('CHANNELS'):
                frame_obj_od['CHANNELS'].append(get_actual_objname(chan_obj_name))
            for key, value in obj_dict.items():
                frame_obj_od[key] = value


    def _load_channel_props(self): 
        self.channel = OrderedDict()
        channel_od = self._get_logical_record_props('CHANNEL')
        if not channel_od:
            return
        for obj_name, obj_dict in channel_od.items():        
            self.channel[get_actual_objname(obj_name)] = obj_dict['UNITS']
            
            
            
    def _get_logical_record_props(self, lr_type): 
        try:
            lr_props = OrderedDict()
            lr_od = DLISObjectPool.get_objects_dict_of_type(lr_type)
            if not lr_od:
                return lr_props
            for obj_name, obj_map in lr_od.items():
                obj_lr_od = OrderedDict()
                lr_props[obj_name] = obj_lr_od
                for key, value in obj_map.items():
                    if isinstance(value, list) and len(value) == 1:
                        obj_lr_od[key] = value[0]
                    else:
                        obj_lr_od[key] = value    
        except Exception as e:
            print('ERROR:', e)
            lr_props = OrderedDict()
        #
#        print()
#        print(lr_type)
#        for obj_name, obj_map in lr_props.items():
#            print('    ', obj_name)
#            for key, value in obj_map.items():
#                print('        ', key, value)

#        print()
        #   
        #
        return lr_props
        
        

    '''    
    def stop_reading(self):
        if self._reading_process.is_alive():
            self._reading_process.terminate()
        self._clear    
        self.file.close()    
    '''    
    
    def _read_Logical_Records(self, callback=None, threading_stop_event=None):
        
        print('\n\n\nENTROU _read_Logical_Records')
        print('self.data_props:', self.data_props)
        print('\n\n\n')
        
        lr_data = b''
        current_obj_name = None
        i = 0
        while self.file.tell() < self.file_size:
            if threading_stop_event:
                if threading_stop_event.is_set():
                    break
            #i += 1
            if callback:
                callback(self.get_file_read_percent())  
            # "Visible Record consists of Visible Envelope Data plus one 
            #  or more Logical Record Segments"
            #  VED - Visible Envelope Data
            VED = OrderedDict()
            ved_data = self.file.read(self.mapping.get('VED').get('size'))
            vr_offset = 0
            for item in self.mapping.get('VED').get('data'):
                vr_offset, value = get_from_list(ved_data, vr_offset, item.get('code'))
                #value = value.decode("utf-8") 
                if item.get('name') == 'The value FF16':
                    if value != 255:
                        msg = 'Expected value FF16 on byte ' + str(self.file.tell()-2)
                        raise Exception(msg)
                else:
                   VED[item.get('name')] = value 
                #elif item.get('name') == 'Format version':
                #    if str(value) != self.SUL.get('RP66 version and format edition').split('.')[0].split('V')[1]:
                #        raise Exception('Version on Visible Record is not the same on Storage Unit Label.')
                   
            # Obtaing Visible Record end offset      
            end_vr_offset = self.file.tell() + VED.get('Visible Record Length') - 4  
            
            # Getting Logical Record Segments from Visible Record
            # A Logical Record Segment is composed of four mutually disjoint parts:
            # (1) a Logical Record Segment Header,
            # (2) an optional Logical Record Segment Encryption Packet,
            # (3) a Logical Record Segment Body, and
            # (4) an optional Logical Record Segment Trailer.

            print('\n\n\n002 _read_Logical_Records')
            print('self.data_props:', self.data_props)
            print('\n\n\n')


            while self.file.tell() < end_vr_offset:                
                # (1) Logical Record Segment Header
                lrs_header = OrderedDict()
                lrs_header_data = self.file.read(self.mapping.get('LRSH').get('size'))
                lrs_header_offset = 0
                for item in self.mapping.get('LRSH').get('data'):    
                    lrs_header_offset, value = get_from_list(lrs_header_data, lrs_header_offset, item.get('code'))
                    #value = value.decode("utf-8")
                    lrs_header[item.get('name')] = value
                lrs_body_size = lrs_header.get('Logical Record Segment Length') - 4
                # Calculating Logical Record Segment Trailer (LRST) size
                lrst_size = 0         
                # Trailing Length                
                if lrs_header.get('Logical Record Segment Attributes')[6]:
                    lrst_size += 2                            
                # Checksum    
                if lrs_header.get('Logical Record Segment Attributes')[5]:
                    lrst_size += 2   
                # Padding                
                if lrs_header.get('Logical Record Segment Attributes')[7]:
                    tmp_offset = self.file.tell()
                    self.file.seek(self.file.tell()+lrs_body_size-(lrst_size+1))
                    _, pad_count = get_from_list(self.file.read(1), 0, 15)
                    self.file.seek(tmp_offset)
                else:
                    pad_count = 0  
                lrst_size += pad_count                    
                    
                # (2) Logical Record Segment Encryption Packet (LRSEP)
                if lrs_header.get('Logical Record Segment Attributes')[3] or \
                        lrs_header.get('Logical Record Segment Attributes')[4]:
                    raise Exception('Logical Record is encrypted')       
                #    
             
                # (3) Logical Record Segment Body (LRSB)           
                lr_data += self.file.read(lrs_body_size - lrst_size) 
                # If LRSB has not Successor than the Logical Record (LR)
                # is ready to be processed. Otherwise another LRSB  
                # will be appended to LR.   
                if not lrs_header.get('Logical Record Segment Attributes')[2]: 
                    # It's time to work on logical record
                    lr_data_offset = 0
                    
                    
                    
                    while lr_data_offset < len(lr_data):
                        
                        # Explicitly Formatted Logical Records (EFLR)
                        if lrs_header.get('Logical Record Segment Attributes')[0] == 1:
#                            print("EFLR")
                            role, definition = self.get_EFLR_process_descriptor(lr_data[lr_data_offset:lr_data_offset+1])
                            lr_data_offset += 1
                            
                            if role == 'ABSATR':
                                if not DLISObjectPool.get_logical_records()[-1].get('closed'):
                                    DLISObjectPool.get_logical_records()[-1].get('template').append(None)
                                else:
                                    DLISObjectPool.get_object_values_list(current_obj_name).append(None)
                                continue    
                            
                            map_ = OrderedDict()
                            
                            for key, (has_key, code) in definition.items():
                                 if has_key:
                                     
                                     if code:
                                        lr_data_offset, value = get_from_list(lr_data, lr_data_offset, code)
                                        #value = value.decode("utf-8") 
#                                        print('code:', key, value, role)
#                                        print()
                                        map_[key] = value
                                        
                                     else:
                                        # Reading Value
                                        if key == 'V':
                                            if not map_.get('C'):
                                                map_['C'] = 1
                                            values = []        
                                            # Firstly, trying to use value code
                                            if map_.get('R') is not None:
                                                code = map_.get('R')
                                            else:
                                                pos = len(DLISObjectPool.get_object_values_dict(current_obj_name))
                                                template = DLISObjectPool.get_logical_records()[-1].get('template')[pos]
                                                # Secondly, trying to use template code for value
                                                if template.get('code') is not None:
                                                    code = template.get('code')
                                                # Otherwise, use default code recommended by RP66_V1            
                                                else:
                                                    code = 19 
                                            for i in range(map_.get('C')):
                                                lr_data_offset, value = get_from_list(lr_data, lr_data_offset, code)
                                                if isinstance(value, str):
                                                    value = value.strip() 
                                                elif code == 23:
                                                    value = get_objname_from_tuple(value)   
                                                values.append(value)
#                                            print('not code: V', values, role)      
                                            map_['V'] = values    
                                        else:        
                                            raise Exception()           
                            
                            
                            if role == 'SET':
                                # Reseting data_props used in IFLR Frame Data                                  
                                if map_.get('T') == 'FILE-HEADER':
                                    
                                    #print('FILE-HEADER')
                                    
                                    if self.data_props is None:
                                        self.data_props = [] 
                                    if self.data is None:
                                        self.data = []
                                        
                                    print('FILE-HEADER:', len(self.data_props))    
                                    
                                    # Appending new 'spaces' for log properties
                                    # and for log data. We will have one list
                                    # of properties and one dict of data for 
                                    # each DLIS Logical File.
                                    # Frame Data Prop list will be compiled 
                                    # at logical file first IFLR.
                                    # Data dict will be constructed on every IFLR frame data    
#                                    """
                                    self.data_props.append(None)    
#                                    """
                                    self.data.append(OrderedDict())    
                                DLISObjectPool.register_logical_record(
                                        1, 
                                        map_.get('T'), 
                                        lrs_header.get('Logical Record Type')
                                )
                                current_obj_name = None
                            
                            elif role == 'ATTRIB':
                                if not DLISObjectPool.get_logical_records()[-1].get('closed'):
                                    new_template = OrderedDict()
                                    new_template['name'] = map_.get('L')
                                    new_template['unit'] = map_.get('U')
                                    new_template['code'] = map_.get('R')
                                    DLISObjectPool.get_logical_records()[-1].get('template').append(new_template)
                                else:
#                                    print('current_obj_name:', current_obj_name, map_.get('V'))
                                    DLISObjectPool.get_object_values_list(current_obj_name).append(map_.get('V'))
                                    
                            elif role == 'OBJECT':
                                current_obj_name = get_objname_from_tuple(map_.get('N'))
                                DLISObjectPool.register_object(current_obj_name)     
                            
                            else:
                                #DLISObjectPool.printa()
#                                print()
#                                print(role, definition, current_obj_name, self.file.tell())
                                raise Exception()
                            
                            
                        # Indirectly Formatted Logical Records (IFLR)        
                        else:
#                            print("IFLR")
                            lr_data_offset, obj_name =  get_from_list(lr_data, lr_data_offset, 23)
                            iflr_descriptor = get_objname_from_tuple(obj_name)
                            # If LRT for IFLR is 127, then we have a EOD -> Nothing to do!
                            if lrs_header.get('Logical Record Type') == 127:
                                if lr_data_offset == len(lr_data):
                                    break
                                else:
                                    raise Exception('ERROR: Found a IFLR EOD with LR data to be read.')                            
                            
                            if self.data_props[-1] is None:
                                print('\n\n\n')
                                print('self.data_props[-1] is None')
                                print('\n\n\n')
                                print('self.data_props:', self.data_props)
                                print('\n\n\n')
                                channel_objects = DLISObjectPool.get_objects_dict_of_type('CHANNEL')
                                print('\nchannel_objects:', channel_objects)
                                frame_objects = DLISObjectPool.get_objects_dict_of_type('FRAME')
                                print('\nframe_objects:', frame_objects)
                                frame_data_prop = OrderedDict() 
                                self.data_props[-1] = frame_data_prop
                                print('\n\nself.data_props[-1]:', self.data_props[-1])
                                print('\n\n\n')
                                #
                                for frame_obj_name, frame_obj_props in frame_objects.items():
                                    frame_props = OrderedDict()
                                    frame_data_prop[frame_obj_name] = frame_props
                                    for idx, channel_name in enumerate(frame_obj_props.get('CHANNELS')):
                                        channel_props = OrderedDict()
                                        frame_props[channel_name] = channel_props
                                        for frame_key, frame_value in frame_obj_props.items():
                                            if frame_key != 'CHANNELS': # No need to insert channel again
                                                try:
                                                    frame_value = frame_value[idx]
                                                except Exception:
                                                    frame_value = None
                                                channel_props[frame_key] = frame_value    
                                        for channel_key, channel_value in channel_objects.get(channel_name).items():
                                            if channel_key == 'AXIS' and channel_value is not None:
                                                axis_props = OrderedDict()
                                                axis_objects = DLISObjectPool.get_objects_dict_of_type('AXIS')
                                                print('\naxis_objects:', axis_objects)
                                                for axis_object_name in channel_value:
                                                    axis_props[axis_object_name] = OrderedDict()
                                                    for axis_key, axis_value in axis_objects.get(axis_object_name).items():
                                                        if isinstance(axis_value, list):
                                                            if len(axis_value) == 1:
                                                                axis_value = axis_value[0]
                                                        axis_props.get(axis_object_name)[axis_key] = axis_value
                                                channel_value = axis_props        
                                            elif isinstance(channel_value, list):
                                                if len(channel_value) == 1:
                                                    channel_value = channel_value[0]
                                            channel_props[channel_key] = channel_value        
                            
                            # TODO: Rever abaixo, reordenando o self.data
                            while lr_data_offset < len(lr_data):  
                                if self.data[-1].get(iflr_descriptor) is None:
                                    self.data[-1][iflr_descriptor] = OrderedDict()           
                                lr_data_offset, idx = get_from_list(lr_data, lr_data_offset, 18)
                                list_ = []
                                self.data[-1].get(iflr_descriptor)['#' + str(idx)] = list_    
                                if self.data_props[-1].get(iflr_descriptor):
                                    for channel_name, channel_props in self.data_props[-1].get(iflr_descriptor).items():
                                        code = channel_props.get('REPRESENTATION-CODE')
                                        if channel_props.get('DIMENSION') == 1:
                                            lr_data_offset, value = get_from_list(lr_data, lr_data_offset, code)
                                        else:
                                            value = []
                                            for i in range(channel_props.get('DIMENSION')):
                                                lr_data_offset, v = get_from_list(lr_data, lr_data_offset, code) 
                                                value.append(v)
                                        list_.append(value)
                        # End of IFLR
                        
                    # End of Logical Record processing - Clearing lr_data               
                    lr_data = b''                

                # (4) Logical Record Segment Trailer (LRST)
                # Bypassing pad bytes
                if pad_count:
                    self.file.seek(pad_count, 1)
                # Bypassing checksum    
                if lrs_header.get('Logical Record Segment Attributes')[5]:
                    self.file.seek(2, 1)
                # Bypassing trailing length     
                if lrs_header.get('Logical Record Segment Attributes')[6]:
                    self.file.seek(2, 1)                        
  
        else:
            if callback:
                callback(self.get_file_read_percent())
            #percent = float("{0:.2f}".format(self.get_file_read_percent()))
            #msg = 'Read: ' + str(percent) + '%'
            #print msg   



      
#        for fileno, map_ in DLISObjectPool.objects.items():
            
            
            
#            print()
#            print('file number:', fileno)
#            lrs = DLISObjectPool.get_logical_records(fileno)
#            print()
#            for lr in lrs:
#                type_name = lr.get('type')
#                print('    ', type_name)
#                objs = DLISObjectPool.get_objects_dict_of_type(type_name)
#                for obj_name, obj_map in objs.items():
#                    print('        ', obj_name)
#                    for k, v in obj_map.items():
#                        print('            ', k, v)
#            print()
#            print()
#            print()
#            print('ending...')
#            for k, v in map_.items():
#                print('        ', k, v)
            
        
        
    def get_EFLR_process_descriptor(self, descriptor_data):   
        if len(descriptor_data) != 1:
            raise Exception()
        v1 = ord(descriptor_data)
        result = bin(v1)[2:].zfill(8)
        if result[0:3] == '000':
            role = 'ABSATR'
        elif result[0:3] == '001':
            role = 'ATTRIB'   
        elif result[0:3] == '010':
            role = 'INVATR'
        elif result[0:3] == '011':
            role = 'OBJECT'     
        elif result[0:3] == '100':
            role = 'reserved'
        elif result[0:3] == '101':
            role = 'RDSET'   
        elif result[0:3] == '110':
            role = 'RSET'
        elif result[0:3] == '111':
            role = 'SET'
        attr = OrderedDict()    
        if role in ['SET', 'RSET', 'RDSET']:
            if result[3:4] == '1':
                attr['T'] = (True, 19)
            else:
                attr['T'] = (False, None)
            if result[4:5] == '1':
                attr['N'] = (True, 19)
            else:
                attr['N'] = (False, None)    
        elif role == 'OBJECT':   
            if result[3:4] == '1':
                attr['N'] = (True, 23)
            else:
                attr['N'] = (False, None)
        
        elif role in ['ATTRIB', 'INVATR']:
            if result[3:4] == '1':
                attr['L'] = (True, 19)
            else:
                attr['L'] = (False, None)
            if result[4:5] == '1':
                attr['C'] = (True, 18)
            else:
                attr['C'] = (False, None)   
            if result[5:6] == '1':
                attr['R'] = (True, 15)
            else:
                attr['R'] = (False, 19)
            if result[6:7] == '1':
                attr['U'] = (True, 27)
            else:
                attr['U'] = (False, None)      
            if result[7:8] == '1':
                attr['V'] = (True, None)
            else:
                attr['V'] = (False, None)               
        return role, attr    
        
        #  Definition of Characteristics and Component Format for Set, 
        #  Redundant Set, and Replacement Set Components            
            
        """
        000	ABSATR	Absent Attribute
        001	ATTRIB	Attribute
        010	INVATR	Invariant Attribute
        011	OBJECT	Object
        100	reserved	-
        101	RDSET	Redundant Set
        110	RSET	Replacement Set
        111	SET	Set
        """
        

         
if __name__ == '__main__':    
    #app = wx.App(False)
    filename = 'DLISOut_TMT001D.dlis'
    #filename = 'qqcoisa.dlis'
    #filename = 'Sample2.dlis'
    #filename = '57-438A_1_1.dlis'
    #filename = '311-U1325A_ecoscope.dlis'

    dlis = DLISFile()
    dlis.read(filename)

      