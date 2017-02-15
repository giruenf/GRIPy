# -*- coding: utf-8 -*-
import wx
import importlib
import timeit
import inspect
import collections
from App import log


def get_caller_info():
    """
        It is a Python 2 hack for a feature only avaialable in Python 3.3+
        Based on: https://gist.github.com/techtonik/2151727 with some 
        changes.
    
        Get a list with caller modules, objects and functions in the stack
        with list index 0 being the latest call.
        
        Returns:
            list(collections.namedtuple('CallerInfo', 
                                   'module obj function_name traceback'))
       
    """
    stack = inspect.stack()
    if len(stack) < 3:
      return None
    ret_list = []
    CallerInfo = collections.namedtuple('CallerInfo', 
        'module obj function_name traceback'
    )
    for i in range(2, len(stack)):
        frame = stack[i][0]
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            module_ = inspect.getmodule(obj)
        else:
            obj = None
            module_ = None    
        traceback = inspect.getframeinfo(frame)    
        func_name = traceback[2]
        ret_list.append(CallerInfo(module=module_, obj=obj, 
                        function_name=func_name, traceback=traceback))
    return ret_list


def get_class_full_name(obj):
    try:
        full_name = obj.__class__.__module__ + "." + obj.__class__.__name__
    except Exception, e:
        msg = 'ERROR in function app.utils.get_class_full_name().'
        log.exception(msg)
        raise e
    return full_name    
    

def get_string_from_function(function_):
    if not callable(function_):
        msg = 'ERROR: Given input is not a function: {}.'.format(str(function_))
        log.error(msg)
        raise Exception(msg)
    return function_.__module__ + '.' + function_.__name__


def get_function_from_string(fullpath_function):
    try:
        module_str = '.'.join(fullpath_function.split('.')[:-1]) 
        function_str = fullpath_function.split('.')[-1]
        module_ = importlib.import_module(module_str)
        function_ = getattr(module_, function_str)
        return function_    
    except Exception, e:
        msg = 'ERROR in function app.utils.get_function_from_string({}).'.format(fullpath_function)
        log.exception(msg)
        raise e        
             

class Chronometer(object):
    
    def __init__(self):
        self.start_time = timeit.default_timer()
    
    def end(self):
        self.total = timeit.default_timer() - self.start_time
        return 'Execution in {:0.3f}s'.format(self.total)        
          
        
class DropTarget(wx.PyDropTarget):
    
    def __init__(self, callback):
        wx.PyDropTarget.__init__(self)
        self.data = wx.CustomDataObject('obj_uid')
        self.SetDataObject(self.data)
        self.callback = callback
        
    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, d):
        if self.GetData(): 
            data = self.data.GetData()
            if data:
                wx.CallAfter(self.callback, repr(data))
        return d        
        
        
        