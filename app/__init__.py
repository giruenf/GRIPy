# -*- coding: utf-8 -*-

import sys
from pathlib import Path
from pathlib import PurePath
import json
import logging

import wx
import matplotlib


INIT_FILE = '.gripy_app_config.json'
ICONS_REL_PATH = 'basic/icons'

BASE_PATH = PurePath(__file__).parent.parent
ICONS_PATH = BASE_PATH.joinpath(BASE_PATH, ICONS_REL_PATH)


def _read_app_definitions():
    try:
        init_file = open(PurePath(BASE_PATH, INIT_FILE), 'r')
        init_dict = json.load(init_file)
        init_file.close()
        return init_dict
    except Exception as e:
        msg = 'Fatal error while loading GRIPy init file: ' \
                            + str(PurePath(BASE_PATH, INIT_FILE)) \
                            + 'ERROR: ' + str(e)
        raise Exception(msg)

def start_logging(logging_dict):
    logging_level = logging_dict.get('logging_level', logging.DEBUG)
    log = logging.Logger('gripy', logging_level)
    logging_filename = logging_dict.get('logging_filename', '')
    logging_filename = Path(logging_filename)
    # Creates app log directory and file it was not found
    if not logging_filename.parent.exists():
        Path(logging_filename.parent).mkdir(parents=True, exist_ok=True) 
        open(logging_filename, 'w').close()    
    #    
    logging_filemode = logging_dict.get('logging_filemode', 'a')
    hdlr = logging.FileHandler(logging_filename, logging_filemode)
    fs = '[%(asctime)s] [%(levelname)s] %(message)s '
    dfs = '%d/%m/%Y %H:%M:%S'
    fmt = logging.Formatter(fs, dfs)
    hdlr.setFormatter(fmt)
    log.addHandler(hdlr)
    #
    return log

def check_platform():
    if sys.platform not in ['win32', 'linux']: 
        raise Exception('GriPy is not ready yet to this system platform. Sorry.')
   
def check_dependencies():
    if not 'phoenix' in wx.version():    
        raise Exception('Gripy works only with wxPython 4.')
    if not matplotlib.__version__.startswith('3.'):    
        raise Exception('Gripy works only with Matplotlib 3.')
        
#
check_platform()    
check_dependencies()
# App definitions
DEFS = _read_app_definitions()   
# Logging 

log = start_logging(DEFS.get('logging'))
#print (logging.getLogger().getEffectiveLevel())



      


        
        
        
        
        