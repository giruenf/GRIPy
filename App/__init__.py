# -*- coding: utf-8 -*-
import os
import json
import logging
import wx
_APP_INIT_FILE = '.gripy_app_config.json'

def get():
    return wx.App.Get()

def _read_app_basic_config():
    try:
        f= open(_APP_INIT_FILE, 'r')
        file_dict = json.load(f)
        f.close()
        #for value in file_dict:
        #    print value
        return file_dict
    except Exception as e:
        print e.args
         
def start_logging(logging_dict):
    logging_level = logging_dict.get('logging_level', logging.DEBUG)
    log = logging.Logger('gripy', logging_level)
    logging_filename = logging_dict.get('logging_filename', '')
    if os.name == 'posix':
        logging_filename = logging_filename.replace('\\', '/')
    if not os.path.exists(logging_filename):
        # Creates a new file and directory if no one was found
        dir_location, _ = os.path.split(logging_filename)
        if not os.path.exists(dir_location):
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

if os.name not in ['nt', 'posix']: 
    raise Exception('GriPy is not ready yet to this system platform. Sorry.')       
_APP_BASIC_CONFIG = _read_app_basic_config()   
 
log = start_logging(_APP_BASIC_CONFIG.get('logging'))




      


        
        
        
        
        