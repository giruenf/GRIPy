# -*- coding: utf-8 -*-
from collections import OrderedDict
import FileIO
import App
import os 

CURVE_DICT_FILE='CPARMDEF.json'
GRIPY_DEFAULT_PLOT='Gripy Default.plt_'
# Based on yapsy.PluginManager
class ParametersManager(object):
    
    def __init__(self):
        self.PLTs = OrderedDict()
        # For read first Gripy Default Plot
        dirname = os.path.dirname(os.path.abspath(__file__))
        dirname = dirname.encode('string-escape')
        fullname = os.path.join(dirname, GRIPY_DEFAULT_PLOT) 
        self.PLTs['GRIPy Default Plot'] = FileIO.PLT.Reader(fullname)
        # End - Gripy Default Plot
        self.PLTs['No Tracks Plot'] = None
        self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))
        self.curve_dict = App.utils.read_json_file(
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          CURVE_DICT_FILE)
        )
        
    def getPLTs(self):
        self.check_and_reload_PLTs()
        return self.PLTs

    def getPLT(self, PLT_name):
        self.check_and_reload_PLTs()
        return self.PLTs.get(PLT_name)
        
    def get_PLTs_names(self):
        return self.getPLTs().keys()
            
    def get_curve_parms(self, curve_name):
        return self.curve_dict.get(curve_name)

    def check_and_reload_PLTs(self):
        self.PLTs = FileIO.PLT.getPLTFiles(self.PLTs, os.path.dirname(os.path.abspath(__file__)))
        
        
# Based on yapsy.PluginManagerSingleton
class ParametersManagerSingleton(object):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = ParametersManager()
        return cls.__instance


