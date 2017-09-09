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
TRACE_OFFSET_BYTE = 37
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
    header : list (of binary data)
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
        #self.filesize = None
        #self.text_header = None
        #self.binary_header = None
        self.headers = None
        self.traces = None
        #self.sample_rate = None
        #self.number_of_samples = None 
        #self.data_format_code = None
        #self.trace_data_size = None
        self._pre_read()
    
    
    def _pre_read(self):
        self.file = open(self.filename, mode='rb')
        self.filesize = os.fstat(self.file.fileno()).st_size
        self.text_header = self.file.read(SEGY_HEADER_TEXT_SIZE).decode('EBCDIC-CP-BE')
        self.binary_header = self.file.read(SEGY_HEADER_BINARY_SIZE)
        self.sample_rate = float(int16(self.binary_header, 17))/1000000  # from us to seconds 
        self.number_of_samples = int16(self.binary_header, 21)    # number of samples 
        self.data_format_code = int16(self.binary_header, 25)
        # At this time, only data format code 1 is accepted.
        if self.data_format_code != 1: # or self.data_format_code != 5:
            raise Exception('Data sample format code {} is not accepted.'.format(self.data_format_code))
        # TODO: Melhorar data_format
        #if self.data_format_code == 1:
        self.trace_data_size = 4
        self.file.close()     


    def __len__(self):
        return len(self.traces)
    

    def get_dump_data(self, samples=3000, start=0):
        self.file = open(self.filename, mode='rb')
        start_offset = SEGY_HEADER_TEXT_SIZE + SEGY_HEADER_BINARY_SIZE
        if start:
            start_offset += start * (TRACE_BINARY_HEADER_SIZE + 
                                self.number_of_samples * self.trace_data_size
            )
        if start_offset > self.filesize:
            raise Exception('Cannot start a dump beyond file size position.')
        dump_data = []    
        self.file.seek(start_offset)
        i = 1
        while self.file.tell() < self.filesize and i <= samples:
            trace_bin_header = self.file.read(TRACE_BINARY_HEADER_SIZE)
            self.file.seek(self.number_of_samples * self.trace_data_size, 1)
            dump_data.append(trace_bin_header)
            i += 1
        self.file.close()  
        return dump_data
    

    """ Se um dos comparadores satisfaz (OR), retorna True"""
    # TODO: implementar AND
    def _satisfies(self, trace_bin_header, comparators_list):
        if not comparators_list:
            return True
        #print 'satisfier:', comparators_list
        for (header_byte_pos, bytes_len, operator, value) in comparators_list:
            if operator == '>=':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) >= value
            elif operator == '<=':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) <= value                  
            elif operator == '>':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) > value
            elif operator == '<':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) < value     
            elif operator == '!=':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) != value
            elif operator == '==':
                ok = get_value(trace_bin_header, header_byte_pos, bytes_len) == value
            if ok:
                break 
        return ok    
     
 
    def read(self, comparators_list=None):
        #print '\nreading:', comparators_list
        self.headers = []
        self.traces = []
        self.file = open(self.filename, mode='rb')
        self.file.seek(SEGY_HEADER_TEXT_SIZE + SEGY_HEADER_BINARY_SIZE)
        while self.file.tell() < self.filesize:
            #print '{:.2f}'.format((float(self.file.tell()) / self.filesize) * 100)
            trace_bin_header = self.file.read(TRACE_BINARY_HEADER_SIZE)
            if self._satisfies(trace_bin_header, comparators_list):
                #print 'SATISFACTION', '{:.2f}'.format((float(self.file.tell()) / self.filesize) * 100)
                trace_data = self.file.read(self.number_of_samples * self.trace_data_size)            
                trace = get_trace_from_data(trace_data)
                self.headers.append(trace_bin_header)
                self.traces.append(trace)
            else:
                self.file.seek(self.number_of_samples * self.trace_data_size, 1)
        self.file.close()    
        self.traces = np.array(self.traces)
        #print '\n\nTRACES:', len(self.traces)


    def _get_dimensions(self, *args):
        #print '\n_get_dimensions'
        #print len(self), len(self.traces), len(self.headers), args
        if not args:
            raise Exception('')
        dims = []
        for arg in args:
            dims.append([])
        for idx in range(len(self)):
            #print 'idx:', idx
            for dim, bytes_pos in enumerate(list(args)):
                #print 'bytes_pos:', bytes_pos
                val = get_value(self.headers[idx], bytes_pos, 4)
                if val not in dims[dim]:
                    dims[dim].append(val)
        for list_ in dims:
            list_.sort()    
        return dims


    def organize_3D_data(self, *args): #iline_byte=9, xline_byte=21, offset_byte=37):
        # dimensions = self._get_dimensions(iline_byte, xline_byte, offset_byte)
        #print '\norganize_3D_data:', args, len(self.traces)
        dimensions = self._get_dimensions(*args)
        #print 'dimensions:', dimensions
        if len(dimensions) == 2 or (len(dimensions) == 3 and len(dimensions[2])==1):
            data = np.zeros((len(dimensions[0]), len(dimensions[1]), 
                             len(self.traces[0])), np.float32
            )
            if len(dimensions) == 3:    
                del dimensions[2]    
        elif len(dimensions) == 3:
            data = np.zeros((len(dimensions[0]), len(dimensions[1]), 
                             len(dimensions[2]), len(self.traces[0])), np.float32
            )
        else:
            raise Exception('Tratar isso seja lah o que isso for....')
        # 
        for idx, trace in enumerate(self.traces):
            idx_values_dim = []
            for j in range(len(dimensions)):
                value = get_value(self.headers[idx], args[j], 4)
                idx_values_dim.append(dimensions[j].index(value))
            #
            if len(data.shape) == 4:
                data[idx_values_dim[0]][idx_values_dim[1]][idx_values_dim[2]] = trace
            elif len(data.shape) == 3:
                data[idx_values_dim[0]][idx_values_dim[1]] = trace
            else:
                raise Exception('AAAAAAAAAAAAAAAAAA')
        #
        self.dimensions = [np.asarray(dim) for dim in dimensions] 
        self.traces = data    




    def print_dump(self, samples=3000, start=0):
        template_positions = [
            (1, 4), # trace number absolute
            (5, 4), # trace number absolute
            (9, 4), 
            (13, 4), # order in the shot (1-120)
            (17, 4), # shot record
            (21, 4),
            (25, 4),
            (27, 2),
            (29, 2),
            (31, 2),
            (33, 2),
            (35, 2),
            (37, 4),
            (41, 4),
            (45, 4),
            (49, 4),
            (53, 4),
            (57, 4),
            (61, 4),
            (65, 4),
            (69, 2),
            (71, 2),           
            (73, 4),
            (77, 4),
            (81, 4),
            (85, 4),
            (89, 4),
            (93, 4),
            (181, 4),
            (185, 4),
            (189, 4),
            (193, 4),
            (197, 4)            
        ]
        '''
        template_positions = [
            (1, 4), # trace number absolute
            (5, 4), # trace number absolute
            (9, 4), 
            (21, 4),
            (37, 4)
        ]
        '''
        for data in self.get_dump_data(samples, start):
            print
            for pos, nbytes in template_positions:
                print 'byte {}: {}'.format(pos, get_value(data, pos, nbytes))




"""        
if __name__=='__main__':
    #filename = 'D:\Sergio_Adriano\NothViking\Mobil_AVO_Viking_pstm_16_CIP_stk.sgy'
    filename = 'D:\\repo\\AVO_INVTRACE_FUNCIONANDO\\data\\finais\\pp_curvr_curv_curvr2_wrmo_qfilter_mute_sg2.sgy'
    #filename = 'D:\\Sergio_Adriano\\NothViking\\Mobil_AVO_Viking_pstm_16_stk.sgy'
    sgf = SEGYFile(filename)    


    #dump = sgf.get_dump_data(200000)
    
    sgf.read()
    
    print 'fim read'
    
    sgf.organize_3D_data()
    
    
    '''
    sgf.read()
    
    old_il = None
    old_xl = None
    
    for idx, data in enumerate(sgf.header):


        print    
        print idx
        il = get_value(data, 9, 4)
        xl = get_value(data, 21, 4)
        offset = get_value(data, 37, 4)     

        if il != old_il:
            print '\nTROCOU ILINE\n'
        
        if xl != old_xl:
            print '\nTROCOU XLINE\n'
            
        
        #
        print 'iline:', il
        print 'xline:', xl
        print 'offset:', offset
        #
    
        old_il = il
        old_xl = xl
    '''    
    
    #sgf.read([(21, 4, '==', 808), (21, 4, '==', 1572)])
    

    #dump_data = sgf.get_dump_data(samples=1000000)

    for idx, data in enumerate(sgf.header):
        #'''
        #if get_value(data, 21, 4) == 808:
        print    
        print idx
        print 'cip:', get_value(data, 21, 4)
        print 'idx:', get_value(data, 5, 4)
        print 'offset:', get_value(data, 37, 4)
        #'''    
        #
        '''
        if get_value(data, 193, 4) == 1572:
            print '\nb1:', get_value(data, 1, 4) # trace number absolute
            print 'b5:', get_value(data, 5, 4) # trace number absolute
            print 'b9:', get_value(data, 9, 4)
            print 'b13:', get_value(data, 13, 4) # order in the shot (1-120)
            print 'b17:', get_value(data, 17, 4) #shot record
            print 'b21:', get_value(data, 21, 4)
            print 'b25:', get_value(data, 25, 4)
            print 'b27:', get_value(data, 27, 2)
            print 'b29:', get_value(data, 29, 2)
            print 'b31:', get_value(data, 31, 2)
            print 'b33:', get_value(data, 33, 2)
            print 'b35:', get_value(data, 33, 2)
            print 'b37:', get_value(data, 37, 4)
            print 'b41:', get_value(data, 41, 4)
            print 'b45:', get_value(data, 45, 4)  
            print 'b49:', get_value(data, 49, 4)
            print 'b53:', get_value(data, 53, 4)
            print 'b57:', get_value(data, 57, 4)
            print 'b61:', get_value(data, 61, 4)
            print 'b65:', get_value(data, 65, 4)
            print 'b69:', get_value(data, 69, 2)
            print 'b71:', get_value(data, 71, 2)            
            print 'cdp_x:', get_value(data, 73, 4)
            print 'cdp_y:', get_value(data, 77, 4)
            print 'cdp_x:', get_value(data, 81, 4)
            print 'cdp_y:', get_value(data, 85, 4)
            print 'b89:', get_value(data, 89, 4)
            print 'b93:', get_value(data, 93, 4)
            print 'b181:', get_value(data, 181, 4)
            print 'b185:', get_value(data, 185, 4)
            print 'b189:', get_value(data, 189, 4)
            print 'b193:', get_value(data, 193, 4)
            print 'b197:', get_value(data, 197, 4)
        '''
    #print i, 100*(self.file.tell() / float(self.filesize))
    #i += 1
    #
    #'''
    #print get_value(data, 37, 4)
     
    print 

    print len(sgf.header)
"""