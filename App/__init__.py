# -*- coding: utf-8 -*-
import os
import json
import logging
import wx
import matplotlib
#matplotlib.interactive(False)
#matplotlib.use('WXAgg')


_APP_INIT_FILE = '.gripy_app_config.json'

def _read_app_definitions():
    try:
        f = open(_APP_INIT_FILE, 'r')
        file_dict = json.load(f)
        f.close()
        return file_dict
    except Exception as e:
        print (e.args)

def start_logging(logging_dict):
    logging_level = logging_dict.get('logging_level', logging.DEBUG)
    log = logging.Logger('gripy', logging_level)
    logging_filename = logging_dict.get('logging_filename', '')
    logging_filename = os.path.normpath(logging_filename)
    if not os.path.exists(logging_filename):
        # Creates a new file and directory if no one was found
        dir_location, _ = os.path.split(logging_filename)
        if not os.path.isdir(dir_location):
            os.makedirs(dir_location)
        open(logging_filename, 'w').close() 
    logging_filemode = logging_dict.get('logging_filemode', 'a')
    hdlr = logging.FileHandler(logging_filename, logging_filemode)
    fs = '[%(asctime)s] [%(levelname)s] %(message)s '
    dfs = '%d/%m/%Y %H:%M:%S'
    fmt = logging.Formatter(fs, dfs)
    hdlr.setFormatter(fmt)
    log.addHandler(hdlr)
    return log

def check_platform():
    if os.name not in ['nt', 'posix']: 
        raise Exception('GriPy is not ready yet to this system platform. Sorry.')
   
def check_dependencies():
    if not 'phoenix' in wx.version():    
        raise Exception('Gripy works only with wxPython 4.')
    if not matplotlib.__version__.startswith('2.'):    
        raise Exception('Gripy works only with Matplotlib 2.')
        
#
check_platform()    
check_dependencies()
# App definitions
DEFS = _read_app_definitions()   
# Logging 
log = start_logging(DEFS.get('logging'))




      


        
        
        
        
        