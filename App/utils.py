# -*- coding: utf-8 -*-
import wx
import re
import os
import json
import importlib
import timeit
import inspect
import collections
from enum import Enum  
#from App import log



def is_wxPhoenix():
    return 'phoenix' in wx.version()

   
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
          
# Phoenix DropTarget code
class DropTarget(wx.DropTarget):
    
    def __init__(self, callback):
        wx.DropTarget.__init__(self)
        self.data = wx.CustomDataObject('obj_uid')
        self.SetDataObject(self.data)
        self.callback = callback
        
    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, d):
        if self.GetData(): 
            data = self.data.GetData().tobytes()
            if data:
                wx.CallAfter(self.callback, repr(data))
        return d   
        
# TODO: Remove it!
# wxPython classic DropTarget code        
class DropTargetClassic(wx.PyDropTarget):
    
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
        

class GripyEnum(Enum):

    def __repr__(self):
        #return '{} object, name: {}, value: {}'.format(self.__class__, self.name, self.value)
        return str(self.value)
        
    def __eq__(self, other):
        if type(other) is self.__class__:
            return self.value is other.value
        return self.value is other

    def __lt__(self, other):
        if type(other) is self.__class__:
            return self.value < other.value
        return self.value < other

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __gt__(self, other):
        if type(other) is self.__class__:
            return self.value > other.value
        return self.value > other

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)



class GripyEnumBitwise(GripyEnum):
 
    def __or__(self, other):
        if type(other) is self.__class__:
            return self.value | other.value 
        return self.value | other

    def __ror__(self, other):
        return self.__or__(other)    
        
        
class LogPlotState(GripyEnum):
    NORMAL_TOOL = 0
    SELECTION_TOOL = 1

class LogPlotDisplayOrder(GripyEnum):
    Z_ORDER_NONE = -1
    Z_ORDER_SEISMIC = 1000
    Z_ORDER_PARTITION = 2000
    Z_ORDER_SCALOGRAM = 3000
    Z_ORDER_WIGGLE = 4000
    Z_ORDER_VELOCITY = 5000
    Z_ORDER_LOG = 6000
    Z_ORDER_INDEX = 10000
    Z_ORDER_TRACKGRID = 100000
    
        
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL        
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)
WHITESPACE_STR = ' \t\n\r'
NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL)
)   


class GripyJSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, wx.Point):
            return 'wx.Point' + str(obj)    
        elif isinstance(obj, wx.Size):
            return 'wx.Size' + str(obj)   
        elif isinstance(obj, GripyEnum):
            return str(obj.value)
        elif callable(obj):
            return get_string_from_function(obj)    
        try:
            return str(obj)
        except:    
            return super(GripyJSONDecoder, self).default(self, obj)     


def clean_path_str(path):
    #path = path.replace('\\' ,'/')  
    path = path.encode('ascii', 'ignore') # in order to save unicode characters
    path = path.encode('string-escape')
    return path


def write_json_file(py_object, fullfilename):
    fullfilename = clean_path_str(fullfilename)
    fullfilename = os.path.normpath(fullfilename)
    directory = os.path.dirname(fullfilename)
    if not os.path.exists(directory):
        os.makedirs(directory)
        msg = 'App.utils.write_json_file has created directory: {}'.format(directory)
        #log.debug(msg)
        print msg
    f = open(fullfilename, 'w')
    f.write(json.dumps(py_object, indent=4, cls=GripyJSONEncoder))
    f.close()


class GripyJSONDecoder(json.JSONDecoder): 

    def decode(self, s, _w=WHITESPACE.match):
        self.scan_once = gripy_make_scanner(self)
        return super(GripyJSONDecoder, self).decode(s, _w)    


def gripy_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    encoding = context.encoding
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook

    def _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration
        if nextchar == '"':
            if string[idx:idx + 10] == '"wx.Point(':
                return GripyJSONParser((string, idx + 10), _scan_once, wx.Point)    
            elif string[idx:idx + 9] == '"wx.Size(':
                return GripyJSONParser((string, idx + 9), _scan_once, wx.Size)         
            return parse_string(string, idx + 1, encoding, strict)
        elif nextchar == '{':
            return parse_object((string, idx + 1), encoding, strict,
                _scan_once, object_hook, object_pairs_hook)
        elif nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        elif nextchar == 'n' and string[idx:idx + 4] == 'null':
            return None, idx + 4
        elif nextchar == 't' and string[idx:idx + 4] == 'true':
            return True, idx + 4
        elif nextchar == 'f' and string[idx:idx + 5] == 'false':
            return False, idx + 5
        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return res, m.end()
        elif nextchar == 'N' and string[idx:idx + 3] == 'NaN':
            return parse_constant('NaN'), idx + 3
        elif nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
            return parse_constant('Infinity'), idx + 8
        elif nextchar == '-' and string[idx:idx + 9] == '-Infinity':
            return parse_constant('-Infinity'), idx + 9
        else:
            raise StopIteration

    return _scan_once        
        

def GripyJSONParser(s_and_end, scan_once, _class, _w=WHITESPACE.match, _ws=WHITESPACE_STR):
    s, end = s_and_end
    values = []
    nextchar = s[end:end + 1]
    if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
    # Look-ahead for trivial empty array
    if nextchar == ']':
        return values, end + 1
    _append = values.append
    
    while True:
        try:
            value, end = scan_once(s, end)
        except StopIteration:
            raise ValueError("Expecting object {}, {}".format(s, end))
        _append(value)
        nextchar = s[end:end + 1]
        if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end:end + 1]
        end += 1
        if nextchar == ')' and s[end:end + 1] == '"':
            end += 1
            break
        elif nextchar != ',':
            raise ValueError("Expecting ',' delimiter {}, {}".format(s, end))
        try:
            if s[end] in _ws:
                end += 1
                if s[end] in _ws:
                    end = _w(s, end + 1).end()
        except IndexError:
            pass         
    return _class(int(values[0]), int(values[1])), end



def read_json_file(fullfilename):
    fullfilename = fullfilename.replace('\\' ,'/')  
    fullfilename = fullfilename.encode('ascii', 'ignore') # in order to save unicode characters
    fullfilename = fullfilename.encode('string-escape')
    f = open(fullfilename)
    state = json.load(f, cls=GripyJSONDecoder)
    f.close()
    return state
        




def parse_string_to_uid(obj_uid_string):
    """
    Parse a uid String (which may contains non uid characters like " and \) to
    a uid tuple in a format (tid, oid).
    
    Parameters
    ----------
    obj_uid_string : str
        The uid String.
    
    Returns
    -------
    tuple
        A pair (tid, oid) which can be a Gripy object identifier.
    """
    left_index = obj_uid_string.find('(')
    right_index = obj_uid_string.rfind(')')
    if left_index == -1 or right_index == -1:
        return None
    elif right_index < left_index:
        return None
    obj_uid_string = obj_uid_string[left_index+1:right_index]
    tid, oid = obj_uid_string.split(',')
    tid = tid.strip('\'\" ')
    oid = int(oid.strip('\'\" '))
    return tid, oid       