# -*- coding: utf-8 -*-

import struct
import os
import numpy as np
    

def ibm2ieee2(ibm_float):
    """
    ibm2ieee2(ibm_float)
    Used by permission
    (C) Secchi Angelo
    with thanks to Howard Lightstone and Anton Vredegoor. 
    """
    dividend=float(16**6)
    
    if ibm_float == 0:
        return 0.0
    istic,a,b,c=struct.unpack('>BBBB',ibm_float)
    if istic >= 128:
        sign= -1.0
        istic = istic - 128
    else:
        sign = 1.0
    mant= float(a<<16) + float(b<<8) +float(c)
    return sign* 16**(istic-64)*(mant/dividend)

    
def int16(buffer, byte): 
    """Retorna o valor inteiro de 2 bytes da posição byte, contido em buffer"""
    return( int(buffer[(byte-1):(byte-1)+2].encode('hex'),16))	   
    
   
def int32(buffer, byte): 
    """Retorna o valor inteiro de 4 bytes da posição byte, contido em buffer"""
    return( int(buffer[(byte-1):(byte-1)+4].encode('hex'),16)  )


def get_value(buffer, start_pos, bytes):
    if bytes == 2:
        return int16(buffer, start_pos)
    elif bytes == 4:
        return int32(buffer, start_pos)    
    else:
        raise NotImplementedError('Not implemented.')
        
        
def get_trace_from_data(buffer):
    """Retorna traco de numero trace_n em forma de lista (ja convertido para float)"""
    trace = []
    for i in range(0, len(buffer), 4):
        trace.append(ibm2ieee2(buffer[i:i+4]))
    return np.array(trace)


SEGY_HEADER_TEXT_SIZE = 3200
SEGY_HEADER_BINARY_SIZE = 400
TRACE_BINARY_HEADER_SIZE = 240
#TRACE_OFFSET_BYTE = 37
#TRACE_DATA_BYTES_SIZE = 4


class SEGYFile(object):    
    """
    A SEG-Y file object.
    
    Parameters
    ----------
    filename : str
        File name

    Attributes
    ----------
    filename : str
        File name.
    filesize : int 
        File size in bytes.    
    text_header : str
        SEG-Y EDCDIC text header of the file, located at its 3200's first bytes.     
    binary_header : list (of binary data)
        SEG_Y file binary header. From bytes 3201-3600.
    data : list
        A list of tuples (trace_bin_header, trace) where trace_bin_header is
        the 240 bytes (raw data) and trace is a np.array of float values.
    sample_rate : float
        The Z Axis difference between two consecutive data samples.
    number_of_samples : int
        Number of samples of each trace
    data_format_code : int    
        SEG-Y Data sample format code. 
            1 = 4-byte, IBM floating-point
            2 = 4-byte, two's complement integer
            3 = 2-byte, two's complement integer         
            4 = 4-byte fixed-point with gain (obsolete)
            5 = 4-byte IEEE floating-point
            6 = Not currently used
            7 = Not currently used
            8 = 1-byte, two's complement integer 
    """ 
    
    def __init__(self, filename):
        self.filename = filename
        self.filesize = None
        self.text_header = None
        self.binary_header = None
        self.header = []
        self.data = []
        self.sample_rate = None
        self.number_of_samples = None 
        self.data_format_code = None
        
    def read(self):
        self.file = open(self.filename, mode='rb')
        self.filesize = os.fstat(self.file.fileno()).st_size
        self.text_header = self.file.read(SEGY_HEADER_TEXT_SIZE).decode('EBCDIC-CP-BE')
        self.binary_header = self.file.read(SEGY_HEADER_BINARY_SIZE)
        self.sample_rate = float(int16(self.binary_header, 17))/1000000  # from us to seconds 
        self.number_of_samples = int16(self.binary_header, 21)    # number of samples 
        self.data_format_code = int16(self.binary_header, 25)
        if self.data_format_code == 1:
            trace_data_size = 4
        else:
            raise Exception('Data sample format code {} is not accepted.'.format(self.data_format_code))
        while self.file.tell() < self.filesize:
            trace_bin_header = self.file.read(TRACE_BINARY_HEADER_SIZE)
            trace_data = self.file.read(self.number_of_samples * trace_data_size)            
            trace = get_trace_from_data(trace_data)
            self.header.append(trace_bin_header)
            self.data.append(trace)
        self.file.close()    
        self.data = np.array(self.data)
        