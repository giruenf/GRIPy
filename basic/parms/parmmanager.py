# -*- coding: utf-8 -*-

import os 
import json

import app

CURVETYPES_FILE='curvetypes.json'
PARAMETERS_FILE = 'parameters.json'
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
        self._curvetypes = app.app_utils.read_json_file(
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          CURVETYPES_FILE)
        )
        self._parametersdict = app.app_utils.read_json_file(
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          PARAMETERS_FILE)
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

           
    def get_datatypes(self):
        """Return valid Datatypes.
        """
        return self._parametersdict["DATATYPES"]
     
    def get_curvetypes(self, datatype):
        """Given a Datatype name (e.g. Log) return its curvetypes associated.
        """
        return self._parametersdict["CURVETYPES"].get(datatype)
 
    def get_all_curvetypes(self):
        ret_list = []
        for dt, cts in self._parametersdict["CURVETYPES"].items():
            ret_list += cts
        return ret_list    
  
    def get_curvetype_visual_props(self, curvetype_name):
        """Given a Curvetype name (e.g. GammaRay) return its visual properties.
        """
        return self._curvetypes.get(curvetype_name)
    
    def get_curvetype_from_mnemonic(self, mnem):
        """Given a mnemonic (e.g. GR), return its Curvetype (e.g. GammaRay)
        """
        key = _removetrailingdigits(mnem).lower()
        curvetype = self._parametersdict["MNEMONIC_TO_CURVETYPE"].get(key)
        if not curvetype:
            return None
        # Let's get most voted...
        curvetype = _getbestmatch(curvetype)
        return curvetype
          
    def get_datatype_from_mnemonic(self, mnem):
        """Given a mnemonic (e.g. GR), return its Datatype (e.g. Log)
        """
        curvetype = self.get_curvetype_from_mnemonic(mnem)
        if curvetype is None:
            msg = 'Unknown curvetype for mnemonic: {}'.format(mnem)
            raise Exception(msg)
        #
        for datatype, curvetypes in self._parametersdict["CURVETYPES"].items():
            if curvetype in curvetypes:
                return datatype
        msg = 'Unknown datatype for mnemonic: {}'.format(mnem)
        raise Exception(msg)  
   
    def vote_for_curvetype(self, mnem, curvetype):
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict["MNEMONIC_TO_CURVETYPE"].get(key) is None:
            print ('vote_for_curvetype criou key:', key)
            self._parametersdict["MNEMONIC_TO_CURVETYPE"][key] = {}
        if curvetype not in self._parametersdict["MNEMONIC_TO_CURVETYPE"][key]:
            self._parametersdict["MNEMONIC_TO_CURVETYPE"][key][curvetype] = 0
            print ('vote_for_curvetype criou curvetype:', key)
        self._parametersdict["MNEMONIC_TO_CURVETYPE"][key][curvetype] += 1


    """
    def votefordatatype(self, mnem, datatype):
        key = _removetrailingdigits(mnem).lower()
        if self._parametersdict['MNEMONIC_TO_CURVETYPE'].get(key) is None:
            print ('votefordatatype criou key:', key)
            self._parametersdict['MNEMONIC_TO_CURVETYPE'][key] = {}
        
        if self._parametersdict['MNEMONIC_TO_CURVETYPE'][key].get(datatype) is None:
            self._parametersdict['MNEMONIC_TO_CURVETYPE'][key][datatype] = 0 
            print ('votefordatatype criou datatype:', datatype)
        try:    
            self._parametersdict['MNEMONIC_TO_CURVETYPE'][key][datatype] += 1
        except KeyError:
            print (mnem, datatype, key)
            raise
    """        
           
    def register_votes(self):   
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           PARAMETERS_FILE), 'w') as jsonfile:
             json.dump(self._parametersdict, jsonfile, sort_keys=True, indent=4, separators=(',', ': '))
      
        
      
        
# Based on yapsy.PluginManagerSingleton
class ParametersManagerSingleton(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = ParametersManager()
        return cls.__instance


