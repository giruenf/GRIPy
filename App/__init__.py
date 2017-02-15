# -*- coding: utf-8 -*-
import os
import logging
import wx
from FileIO.utils import AsciiFile
_APP_INIT_FILE = '.gripy_app_ini.json'


def get():
    return wx.App.Get()


def load_app_state():
    try:
        file_dict = AsciiFile.read_json_file(_APP_INIT_FILE)
        return file_dict
    except Exception as e:
        print e.args
                     
                     
def start_logging(logging_dict):
    logging_level = logging_dict.get('logging_level', logging.DEBUG)
    log = logging.Logger('gripy', logging_level)
    logging_filename = logging_dict.get('logging_filename', None)
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
    
    
_APP_STATE = load_app_state()    
log = start_logging(_APP_STATE.get('logging'))