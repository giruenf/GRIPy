# -*- coding: utf-8 -*-
"""
PLT
===

This file defines the classes and functions necessary to read and write 
Senergy's Interactive Petrophysics (IP) PLT files.
Based on observations of ASCii PLT files placed in IP's Default Plot 
directory.
 


References
----------
.. [1] Interactive Petrophysics version 4.1:
    Interactive Petrophysics is a trademark of Senergy Software Limited
"""


import time
from datetime import date    
import utils  
import os, os.path
from collections import OrderedDict



class PLTFile(object):
    MAIN_KEY = 'MAIN'                    
    MAIN_SUBKEYS = ['TRACK', 'CURVE', 'SHADE', 'ORDER']      
    OTHER_KEYS = ['GRID', 'PRINTOUT', 'HEADER', 'ANNO', 'HEADERREMARKS', 'PLOTSTYLE']    
    TRACK_KEYS = OrderedDict()
    TRACK_KEYS['width'] = float
    TRACK_KEYS['plotgrid'] = bool
    TRACK_KEYS['x_scale'] = int
    TRACK_KEYS['decades'] = int
    TRACK_KEYS['leftscale'] = float
    TRACK_KEYS['minorgrid'] = bool
    TRACK_KEYS['overview'] = bool
    TRACK_KEYS['scale_lines'] = int
    TRACK_KEYS['depth_lines'] = int
    TRACK_KEYS['show_track'] = bool
    TRACK_KEYS['track_name'] = str
    TRACK_KEYS['unidentified'] = int
    #
    CURVE_KEYS = OrderedDict()
    CURVE_KEYS['curve_name'] = str  
    CURVE_KEYS['left_scale'] = float
    CURVE_KEYS['right_scale'] = float
    CURVE_KEYS['backup'] = str
    CURVE_KEYS['thickness'] = int
    CURVE_KEYS['color'] = str
    CURVE_KEYS['x_scale'] = int
    CURVE_KEYS['point_plotting'] = str 
    CURVE_KEYS['visible'] = bool
    CURVE_KEYS['unidentified'] = bool
    # 
    SHADE_KEYS = OrderedDict()
    SHADE_KEYS['left_curve_name'] = str
    SHADE_KEYS['left_curve_value'] = float
    SHADE_KEYS['right_curve_name'] = str
    SHADE_KEYS['right_curve_value'] = float
    SHADE_KEYS['visible'] = bool
    SHADE_KEYS['color'] = str
    SHADE_KEYS['description'] = str 
    #    
    
    def __init__(self):
        self.filename = None
        self._map = OrderedDict()
        #self._tracks = []
        self._map[self.MAIN_KEY] = []
        for other in self.OTHER_KEYS:
            self._map[other] = []

    def get_main_parms(self):
        return self._map.get(self.MAIN_KEY)   
        
    def get_header_parms(self):
        _map = {}
        for key in self.OTHER_KEYS:
            _map[key] = self._map.get(key) 
        return _map

    @property
    def name(self):
        if not self.filename:
            return None
        head, tail = os.path.split(self.filename)        
        name, ext = os.path.splitext(tail)    
        return name    


    @property
    def data(self):
        return self._map        
    
# TODO: isso está repetido com LogPlotFormat - corrigir no futuro

    @staticmethod
    def get_track_key(index):
        if index >= 0 and index < len(PLTFile.TRACK_KEYS):
            return PLTFile.TRACK_KEYS.keys()[index]            
        else:
            return None
    
            
    @staticmethod
    def get_curve_key(index):
        if index >= 0 and index < len(PLTFile.CURVE_KEYS):
            return PLTFile.CURVE_KEYS.keys()[index]            
        else:
            return None
            
    @staticmethod
    def get_shade_key(index):
        if index >= 0 and index < len(PLTFile.SHADE_KEYS):
            return PLTFile.SHADE_KEYS.keys()[index]            
        else:
            return None
            
# TODO: Fim
    
    @staticmethod
    def _list_to_trackdata(datalist): 
        map_ = OrderedDict()
        if datalist:
            for i in range(len(datalist)):
                map_[PLTFile.get_track_key(i)] = datalist[i]
        return map_
           
        
    @staticmethod
    def _list_to_curve(datalist):    
        map_ = OrderedDict()
        if datalist:
            for i in range(len(datalist)):
                map_[PLTFile.get_curve_key(i)] = datalist[i]
        return map_    
        
        
    @staticmethod
    def _list_to_shade(datalist):    
        map_ = OrderedDict()
        try:
            if datalist:
                for i in range(len(datalist)):
                    map_[PLTFile.get_shade_key(i)] = datalist[i]
        except IndexError:
            raise             
        return map_    
            
        
    @staticmethod
    def _trackdata_to_str(trackdata_dict):
        if trackdata_dict:
            line = 'TRACK '
            for i in range(len(trackdata_dict)):
                line += trackdata_dict[PLTFile.get_track_key(i)] + ' '        
        return line + '\n'  
            
            
    @staticmethod
    def _curvesdata_to_str(curvesdata_list):
        if curvesdata_list:
            str_ = ''
            for curvemap in curvesdata_list:
                line = 'CURVE '
                for i in range(len(curvemap)):
                    line += curvemap[PLTFile.get_curve_key(i)] + ' '
                str_ += line + '\n'    
        return str_         


    @staticmethod
    def _shadesdata_to_str(shadesdata_list):
        if shadesdata_list:
            str_ = ''
            for shademap in shadesdata_list:
                line = 'SHADE '
                for i in range(len(shademap)):
                    line += shademap[PLTFile.get_shade_key(i)] + ' '
                str_ += line + '\n'    
        return str_     


    @staticmethod
    def _orderdata_to_str(orderdata_list):
        return PLTFile._listdata_to_str('ORDER', orderdata_list)
           

    @staticmethod
    def _listdata_to_str(list_name, list_):
        if list_:
            line = list_name + ' '
            for item in list_:
                line += item + ' '        
        return line + '\n'    
        

    def _get_text_comment(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
        str_ = '$ File auto genereted by GRIPy - '     + date.today() + ' - ' +  \
            st + '\n\n'
        return str_    
        
        
    def _get_text_lines(self):
        text = ''            
        for heat in self._map[self.MAIN_KEY]:
            text += self._trackdata_to_str(heat['TRACK'])
            if heat['CURVE']:
                text += self._curvesdata_to_str(heat['CURVE'])
            if heat['SHADE']:
                text += self._shadesdata_to_str(heat['SHADE'])
            if heat['ORDER']:
                text += self._orderdata_to_str(heat['ORDER'])
        for other in self.OTHER_KEYS:
            if self._map[other]:
                text += self._listdata_to_str(other, self._map[other])
        return text        
            
            
    def write(self, filename):
        fileobject = AsciiFile.empty_file(filename)   
        fileobject.write(self._get_text_comment())
        fileobject.write(self._get_text_lines())
        fileobject.close()
        return True

    
def Reader(filename):
    pltfile = PLTFile()        
    pltfile.filename = filename.encode('string-escape')
    content = utils.read_file_as_list(pltfile.filename)        
    if not content:
        return None
    maindatum = OrderedDict()
    for line in content:
        if line and line[0] == 'TRACK':
            if maindatum:
                pltfile._map[pltfile.MAIN_KEY].append(maindatum)   
                maindatum = OrderedDict()   
            maindatum['TRACK'] = PLTFile._list_to_trackdata(line[1:])
            maindatum['CURVE'] = []
            maindatum['SHADE'] = []
            maindatum['ORDER'] = None
        elif line and line[0] == 'CURVE':
            maindatum['CURVE'].append(PLTFile._list_to_curve(line[1:]))
        elif line and line[0] == 'SHADE':
            try:
                maindatum['SHADE'].append(PLTFile._list_to_shade(line[1:]))
            except IndexError:
                print 'ERROR: SHADE - ' + pltfile.name
        elif line and line[0] == 'ORDER':
            maindatum['ORDER'] = line[1:]
        elif line and line[0] in PLTFile.OTHER_KEYS:
            if maindatum:
                pltfile._map[pltfile.MAIN_KEY].append(maindatum)
                maindatum = None
            pltfile._map[line[0]] = line[1:]    
    return pltfile    
    

        
def Writer(pltfile, filename):
    if not isinstance(pltfile, PLTFile):
        raise TypeError('pltfile should be a PLTFile instance.')
    return pltfile.write(filename)    
    
    
def getPLTFiles(dict_to_return, dirname):
    dirname = dirname.encode('string-escape')
    for filename in os.listdir(dirname):
        if filename.endswith(".plt") or filename.endswith(".PLT"): 
            if filename not in dict_to_return.keys():              
                fullname = os.path.join(dirname, filename)   
                plt = Reader(fullname)
                dict_to_return[plt.name] = plt
    return dict_to_return        
            
            
            
            
            