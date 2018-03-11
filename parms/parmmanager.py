# -*- coding: utf-8 -*-
#from collections import OrderedDict
#import FileIO
import App
import os 
import json

CURVETYPES_FILE='CurvetypesVis.json'
PARAMETERS2_FILE = 'parameters2.json'
#GRIPY_DEFAULT_PLOT='Gripy Default.plt_'

def _removetrailingdigits(text):
    count = 0
    for character in reversed(text):
        if not character.isdigit():
            break
        count += 1  
    if count == len(text) or count == 0:
        return text
    return text[:-count]

def _getbestmatch(dictionary):
    maxcount = -1
    bestmatch = ''
    for type_, count in dictionary.items():
        if count > maxcount:
            maxcount = count
            bestmatch = type_  
    return bestmatch


# Based on yapsy.PluginManager
class ParametersManager(object):
    
    def __init__(self):
        """
        self.PLTs = OrderedDict()
        # For read first Gripy Default Plot
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = dirname.encode('string-escape')
        fullname = os.path.join(dirname, GRIPY_DEFAULT_PLOT) 
        self.PLTs['GRIPy Default Plot'] = FileIO.PLT.Reader(fullname)
        # End - Gripy Default Plot
        self.PLTs['No Tracks Plot'] = None
        self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))
        """
        self._curvetypes = App.app_utils.read_json_file(
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          CURVETYPES_FILE)
        )
        self._parametersdict = App.app_utils.read_json_file(
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          PARAMETERS2_FILE)
        )   
                 
    #def getPLTs(self):
    #    self.check_and_reload_PLTs()
    #    return self.PLTs

    #def getPLT(self, PLT_name):
    #    self.check_and_reload_PLTs()
    #    return self.PLTs.get(PLT_name)
        
    #def get_PLTs_names(self):
    #    return self.getPLTs().keys()
 
    #def check_and_reload_PLTs(self):
    #    self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))
           
    def get_curvetype_visual_props(self, curvetype_name):
        return self._curvetypes.get(curvetype_name)

    def getcurvetypefrommnem(self, mnem):
        key = _removetrailingdigits(mnem).lower()
        value = self._parametersdict['mnemtocurvetype'].get(key)
        if not value:
            return ''    
        return _getbestmatch(value)
   
    def voteforcurvetype(self, mnem, curvetype):
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict['mnemtocurvetype'].get(key) is None:
            print ('voteforcurvetype criou key:', key)
            self._parametersdict['mnemtocurvetype'][key] = {}
        if curvetype not in self._parametersdict['mnemtocurvetype'][key]:
            self._parametersdict['mnemtocurvetype'][key][curvetype] = 0
            print ('voteforcurvetype criou curvetype:', key)
        self._parametersdict['mnemtocurvetype'][key][curvetype] += 1
    
    def getcurvetypes(self):
        return self._parametersdict['curvetypes']
    
    def getdatatypefrommnem(self, mnem):
        key = _removetrailingdigits(mnem).lower()
        value = self._parametersdict['mnemtodatatype'].get(key)
        if not value:
            return ''   
        return _getbestmatch(self._parametersdict['mnemtodatatype'].get(key))
    
    def votefordatatype(self, mnem, datatype):
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict['mnemtodatatype'].get(key) is None:
            print ('votefordatatype criou key:', key)
            self._parametersdict['mnemtodatatype'][key] = {}
        
        if self._parametersdict['mnemtodatatype'][key].get(datatype) is None:
            self._parametersdict['mnemtodatatype'][key][datatype] = 0 
            print ('votefordatatype criou datatype:', datatype)
        try:    
            self._parametersdict['mnemtodatatype'][key][datatype] += 1
        except KeyError:
            print (mnem, datatype, key)
            raise
            
            
    def getdatatypes(self):
        return ['Index', 'Log', 'Partition']

    def register_votes(self):   
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           PARAMETERS2_FILE), 'w') as jsonfile:
             json.dump(self._parametersdict, jsonfile, sort_keys=True, indent=4, separators=(',', ': '))
      
        
# Based on yapsy.PluginManagerSingleton
class ParametersManagerSingleton(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = ParametersManager()
        return cls.__instance


