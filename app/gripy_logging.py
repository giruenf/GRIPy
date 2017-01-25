# -*- coding: utf-8 -*-

"""
    Based in Fang's code note obtained from
    http://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    
    Date: 14/12/2016
"""

import os
import json
import logging.config


def setup_logging(level, path, env_key='LOG_CFG'):
    """Setup logging configuration

    """
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        print config
        raise Exception()
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=level)
     
"""     
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
      
_levelNames = {
    CRITICAL : 'CRITICAL',
    ERROR : 'ERROR',
    WARNING : 'WARNING',
    INFO : 'INFO',
    DEBUG : 'DEBUG',
    NOTSET : 'NOTSET',
    'CRITICAL' : CRITICAL,
    'ERROR' : ERROR,
    'WARN' : WARNING,
    'WARNING' : WARNING,
    'INFO' : INFO,
    'DEBUG' : DEBUG,
    'NOTSET' : NOTSET,
}      
"""        