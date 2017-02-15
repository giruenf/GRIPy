# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 10:53:59 2016

@author: Adriano
"""

"""

    Tape Image Format (TIF) Encapsulation
    
    This encapsulation format is more common for well logs rather than seismic 
    traces and, indeed, was developed by Dresser Atlas for disk storage of well
    logs. Each record is preceded by three 4 byte little endian integers, the 
    first being a 0 (normal record) or a 1 (file mark), the second the byte
    offset of the start of the previous record and the third the byte offset of
    the start of the next record. Because it uses absolute offsets into the 
    file, it is limited to datasets with a maximum size of 4GB. To extend TIF 
    to larger files, a TIF8 has been proposed which uses a 24 byte prefix with
    the ASCII characters “TIF8” followed by the 4 byte record type and the two 
    file offsets now each 8 bytes long instead of 4. Again, little endian byte 
    ordering is used for the record type and file offsets. 
    
    Source: http://www.oilit.com/papers/levin.pdf (page 2)
    
"""


import struct



def _get_tif_register(data):
    """
    TIF values are 4 bytes unsigned long and written in little endian format.
    """
    if len(data) != 4:
        raise ValueError('TIF register must have 4 bytes.')
    n = struct.unpack('L', data)
    return n[0]      
        
        
        
class TIFFile(object):
       
    @staticmethod
    def get_TIF_registers(data):
        registers = []
        offset = 0
        while offset < len(data):
            tif_register = []
            record_type = _get_tif_register(data[offset:offset+4])
            if record_type not in [0, 1]:
                return None
            offset += 4
            previous_record = _get_tif_register(data[offset:offset+4])
            offset += 4
            next_record = _get_tif_register(data[offset:offset+4])
            offset += 4
            if offset == next_record:
                encapsulated_data = None
            else:    
                encapsulated_data = data[offset:next_record]
            offset = next_record
            tif_register.append(record_type)
            tif_register.append(previous_record)
            tif_register.append(next_record)
            tif_register.append(encapsulated_data)
            registers.append(tif_register)
        return registers        

       
    
    @staticmethod
    def desencapsulate(data):
        registers = TIFFile.get_TIF_registers(data)
        # Not a TIF data, returning False and input data        
        if registers is None:
            return False, data
        return_data = []    
        tif_file = ''
        for register in registers:
            if register[0] == 1:
                return_data.append(tif_file)
                tif_file = str('')
            else:
                tif_file += register[3]
        # Returning True for success        
        return True, return_data



