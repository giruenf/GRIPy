import re
import os
import json
import importlib
import timeit
import inspect
import collections
from enum import Enum
from pathlib import Path

import numpy as np
from matplotlib.cm import cmap_d
import wx

import app
import fileio
from classes.om.base.manager import ObjectManager
from app import log


class GripyBitmap(wx.Bitmap):

    def __init__(self, path_to_bitmap=None):
        if path_to_bitmap is None:
            super().__init__()
            return
        if os.path.exists(path_to_bitmap):
            full_file_name = path_to_bitmap
        elif os.path.exists(os.path.join(app.ICONS_PATH, \
                                         path_to_bitmap)):
            full_file_name = os.path.join(app.ICONS_PATH, path_to_bitmap)
        else:
            raise Exception('ERROR: Wrong bitmap path [{}, {}].'.format( \
                app.ICONS_PATH, path_to_bitmap)
            )
        super().__init__(full_file_name)


class GripyIcon(wx.Icon):

    def __init__(self, path_to_bitmap=None, type_=wx.BITMAP_TYPE_ANY):

        # print(PurePath(app.ICONS_PATH, path_to_bitmap), 'r')

        if path_to_bitmap is not None:
            if Path(path_to_bitmap).exists():
                pass
            elif Path(app.ICONS_PATH, path_to_bitmap).exists():
                path_to_bitmap = Path(app.ICONS_PATH, path_to_bitmap)
            else:
                raise Exception('ERROR: Wrong bitmap path.')
        super().__init__(path_to_bitmap, type_)


def calc_well_time_from_depth(event, well_uid):
    OM = ObjectManager()
    well = OM.get(well_uid)
    vp = None
    for log_obj in OM.list('log', well.uid):
        if log_obj.datatype == 'Velocity':
            vp = log_obj
            break
    if vp is None:
        raise Exception('ERROR [calc_prof_tempo]: Vp log not found.')
    index_set = OM.get(vp.index_set_uid)
    md = index_set.get_z_axis_indexes_by_type('MD')[0]
    #
    if md.data[0] != 0.0:
        return
    owt = [0.0]
    #
    for idx in range(1, len(md.data)):
        if vp.data[idx - 1] == np.nan:
            raise Exception('ERROR [calc_prof_tempo]: Found np.nan on Vp[{}] '.format(idx - 1))
        diff_prof = md.data[idx] - md.data[idx - 1]
        value = (float(diff_prof) / vp.data[idx - 1]) * 1000.0  # To milliseconds
        value = owt[idx - 1] + value
        owt.append(value)
    #    
    owt = np.array(owt)
    twt = owt * 2.0
    #
    print('\nOWT:', owt)
    #
    owt_index = OM.new('data_index', 0, 'One Way Time', 'TIME', 'ms', data=owt)
    OM.add(owt_index, index_set.uid)
    #
    twt_index = OM.new('data_index', 0, 'Two Way Time', 'TWT', 'ms', data=twt)
    OM.add(twt_index, index_set.uid)
    #          


def load_segy(event, filename, new_obj_name='', comparators_list=None,
              iline_byte=9, xline_byte=21, offset_byte=37, tid='seismic',
              datatype='amplitude', parentuid=None):
    OM = ObjectManager()
    disableAll = wx.WindowDisabler()
    wait = wx.BusyInfo("Loading SEG-Y file...")
    #
    try:
        print("\nLoading SEG-Y file...")
        segy_file = fileio.segy.SEGYFile(filename)
        # segy_file.print_dump()
        # """
        segy_file.read(comparators_list)
        segy_file.organize_3D_data(iline_byte, xline_byte, offset_byte)
        #
        print('segy_file.traces.shape:', segy_file.traces.shape)
        #

        #
        seis_like_obj = OM.new(tid, segy_file.traces, name=new_obj_name,
                               datatype=datatype
                               )
        if not OM.add(seis_like_obj, parentuid):
            raise Exception('Object was not added. tid={}'.format(tid))
        #

        #
        z_index = OM.new('data_index',
                         name='Time',
                         datatype='TWT',
                         unit='ms',
                         start=0.0,
                         step=(segy_file.sample_rate * 1000),
                         samples=segy_file.number_of_samples
                         )
        OM.add(z_index, seis_like_obj.uid)
        #

        try:
            offset_index = OM.new('data_index',
                                  segy_file.dimensions[2],
                                  name='Offset',
                                  datatype='OFFSET',
                                  unit='m'
                                  )
            OM.add(offset_index, seis_like_obj.uid)
            next_dim = 2
        except Exception as e:
            next_dim = 1

            #
        xline_index = OM.new('data_index',
                             segy_file.dimensions[1],
                             name='X Line',
                             datatype='X_LINE'
                             )
        if OM.add(xline_index, seis_like_obj.uid):
            next_dim += 1
        #

        iline_index = OM.new('data_index',
                             segy_file.dimensions[0],
                             name='I Line',
                             datatype='I_LINE'
                             )
        OM.add(iline_index, seis_like_obj.uid)
        #  
        seis_like_obj._create_data_index_map(
            [iline_index.uid],
            [xline_index.uid],
            [offset_index.uid],
            [z_index.uid]
        )

        print('seis_like_obj.traces.shape:', seis_like_obj.data.shape)

        # """
    except Exception as e:
        raise e
    finally:
        del wait
        del disableAll


#
# TODO: Verificar melhor opcao no Python 3.6
#   

CallerInfo = collections.namedtuple('CallerInfo',
                                    ['object_', 'class_', 'module', 'function_name',
                                     'filename', 'line_number', 'line_code'
                                     ]
                                    )


def get_callers_stack():
    """
        Based on: https://gist.github.com/techtonik/2151727 with some 
        changes.
    
        Get a list with caller modules, objects and functions in the stack
        with list index 0 being the latest call.
        
        Returns:
            list(collections.namedtuple('CallerInfo', 
                        ['object_', 'class_', 'module', 'function_name', 
                         'filename', 'line_number', 'line_code']))
    """

    ret_list = []

    print('app_utils.get_callers_stack')

    try:
        stack = inspect.stack()
        for i in range(1, len(stack)):
            fi = stack[i]
            module_ = None
            obj = fi.frame.f_locals.get('self', None)
            class_ = fi.frame.f_locals.get('__class__', None)
            if obj:
                module_ = inspect.getmodule(obj)
            if not class_ and obj:
                class_ = obj.__class__
            ret_list.append(
                CallerInfo(object_=obj, class_=class_, module=module_,
                           function_name=fi.function, filename=fi.filename,
                           line_number=fi.lineno, line_code=fi.code_context,
                           # index=fi.index,
                           # traceback=traceback, f_locals=fi.frame.f_locals
                           )
            )
            if fi.frame.f_locals.get('__name__') == '__main__':
                break
    except Exception as e:
        print(e)
        raise

    return ret_list


def get_class_full_name(obj):
    try:
        full_name = obj.__class__.__module__ + "." + obj.__class__.__name__
    except Exception as e:
        msg = 'ERROR in function app.app_utils.get_class_full_name().'
        log.exception(msg)
        raise e
    return full_name


def get_string_from_function(function_):
    if not callable(function_):
        msg = 'ERROR: Given input is not a function: {}.'.format(str(function_))
        log.error(msg)
        raise Exception(msg)
    return function_.__module__ + '.' + function_.__name__


def get_function_from_filename(full_filename, function_name):
    try:
        # print ('\nget_function_from_filename', full_filename, function_name)
        if function_name == '<module>':
            return None

        rel_path = os.path.relpath(full_filename, app.BASE_PATH)
        module_rel_path = os.path.splitext(rel_path)[0]
        # print (module_rel_path)
        module_str = '.'.join(module_rel_path.split(os.path.sep))
        # print (module_str)
        module_ = importlib.import_module(module_str)
        # print (module_, function_name)
        function_ = getattr(module_, function_name)
        return function_
    except:
        raise


def get_function_from_string(fullpath_function):
    try:
        # print ('\nget_function_from_string:', fullpath_function)
        module_str = '.'.join(fullpath_function.split('.')[:-1])
        function_str = fullpath_function.split('.')[-1]
        # print ('importing module:', module_str)
        module_ = importlib.import_module(module_str)
        # print ('getting function:', function_str, '\n')
        function_ = getattr(module_, function_str)
        return function_
    except Exception as e:
        msg = 'ERROR in function app.app_utils.get_function_from_string({}).'.format(fullpath_function)
        log.exception(msg)
        print(msg)
        raise e


class Chronometer(object):

    def __init__(self):
        self.start_time = timeit.default_timer()

    def end(self):
        self.total = timeit.default_timer() - self.start_time
        return 'Execution in {:0.3f}s'.format(self.total)

    # Phoenix DropTarget code


class DropTarget(wx.DropTarget):

    def __init__(self, _test_func, callback=None):
        wx.DropTarget.__init__(self)
        self.data = wx.CustomDataObject('obj_uid')
        self.SetDataObject(self.data)
        self._test_func = _test_func
        self._callback = callback

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, defResult):
        obj_uid = self._get_object_uid()
        if self._callback:
            wx.CallAfter(self._callback, obj_uid)
        return defResult

    def OnDragOver(self, x, y, defResult):
        obj_uid = self._get_object_uid()
        if obj_uid:
            if self._test_func(obj_uid):
                return defResult
        return wx.DragNone

    def _get_object_uid(self):
        if self.GetData():
            obj_uid_bytes = self.data.GetData().tobytes()
            obj_uid_str = obj_uid_bytes.decode()
            if obj_uid_str:
                obj_uid = parse_string_to_uid(obj_uid_str)
                return obj_uid
        return None


class GripyEnum(Enum):

    def __repr__(self):
        # return '{} object, name: {}, value: {}'.format(self.__class__, self.name, self.value)
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


class WellPlotState(GripyEnum):
    NORMAL_TOOL = 0
    SELECTION_TOOL = 1


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
    # path = path.replace('\\' ,'/')
    path = path.encode('ascii', 'ignore')  # in order to save unicode characters
    path = path.encode('string-escape')
    return path


def write_json_file(py_object, fullfilename):
    fullfilename = clean_path_str(fullfilename)
    fullfilename = os.path.normpath(fullfilename)
    directory = os.path.dirname(fullfilename)
    if not os.path.exists(directory):
        os.makedirs(directory)
        msg = 'App.app_utils.write_json_file has created directory: {}'.format(directory)
        # log.debug(msg)
        print(msg)
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
    # encoding = context.encoding
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
            return parse_string(string, idx + 1, strict)
        elif nextchar == '{':
            return parse_object((string, idx + 1), strict,
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


def read_json_file(full_filename):
    # print ('\nread_json_file:', fullfilename, type(fullfilename))
    # fullfilename = fullfilename.replace('\\' ,'/')
    # fullfilename = fullfilename.encode('ascii', 'ignore') # in order to save unicode characters
    # fullfilename = fullfilename.encode('string-escape')
    json_file = open(full_filename, 'r')
    state = json.load(json_file, cls=GripyJSONDecoder)
    json_file.close()
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
    try:
        #        print ('parse_string_to_uid:', obj_uid_string)
        left_index = obj_uid_string.find('(')
        right_index = obj_uid_string.rfind(')')
        if left_index == -1 or right_index == -1:
            return None
        elif right_index < left_index:
            return None
        obj_uid_string = obj_uid_string[left_index + 1:right_index]
        tid, oid = obj_uid_string.split(',')
        tid = tid.strip('\'\" ')
        oid = int(oid.strip('\'\" '))
        return tid, oid
    except:
        raise


def get_wx_colour_from_seq_string(seq_str):
    # tuple or list
    if seq_str.startswith('(') or seq_str.startswith('['):
        seq_str = seq_str[1:-1]
        val = tuple([int(c.strip()) for c in seq_str.split(',')])
        color = wx.Colour(val)
        print('_get_wx_colour:', color,
              color.GetAsString(wx.C2S_HTML_SYNTAX))
        return color
    return None


# Have colormaps separated into categories:
# http://matplotlib.org/examples/color/colormaps_reference.html
"""
# MPL 1.4/1.5 COLORS

MPL_CATS_CMAPS = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]
"""

# MPL 2.0 COLORS
MPL_CATS_CMAPS = [
    ('Perceptually Uniform Sequential',
     ['viridis', 'inferno', 'plasma', 'magma']
     ),
    ('Sequential',
     ['Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys',
      'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples',
      'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'
      ]
     ),
    ('Sequential (2)',
     ['afmhot', 'autumn', 'bone', 'cool', 'copper', 'gist_heat',
      'gray', 'hot', 'pink', 'spring', 'summer', 'winter'
      ]
     ),
    ('Diverging',
     ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
      'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 'seismic'
      ]
     ),
    ('Qualitative',
     ['Accent', 'Dark2', 'Paired', 'Pastel1', 'Pastel2', 'Set1',
      'Set2', 'Set3', 'Vega10', 'Vega20', 'Vega20b', 'Vega20c'
      ]
     ),
    ('Miscellaneous',
     ['gist_earth', 'terrain', 'ocean', 'gist_stern', 'brg',
      'CMRmap', 'cubehelix', 'gnuplot', 'gnuplot2', 'gist_ncar',
      'nipy_spectral', 'jet', 'rainbow', 'gist_rainbow', 'hsv',
      'flag', 'prism'
      ]
     )
]

# MPL_COLORMAPS = [value for (key, values) in MPL_CATS_CMAPS for value in values]


MPL_COLORMAPS = sorted(cmap_d)

"""
MPL_COLORMAPS = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 
                 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r',
                 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 
                 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r',
                 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r',
                 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBu_r',
                 'PuBuGn', 'PuBuGn_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r',
                 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 
                 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r',
                 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 
                 'Set3', 'Set3_r', 'Spectral', 'Spectral_r', 'Vega10', 'Vega10_r',
                 'Vega20', 'Vega20_r', 'Vega20b', 'Vega20b_r', 'Vega20c', 'Vega20c_r',
                 'Wistia', 'Wistia_r', 'YlGn', 'YlGn_r', 'YlGnBu', 'YlGnBu_r',
                  'YlOrBr', 'YlOrBr_r', 'YlOrRd', 'YlOrRd_r', 
                  'afmhot', 'afmhot_r', 'autumn', 'autumn_r', 'binary', 'binary_r',
                  'bone', 'bone_r', 'brg', 'brg_r', 'bwr', 'bwr_r', 
                  'cool', 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r',
                  'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 
                  'gist_earth', 'gist_earth_r', 'gist_gray', 'gist_gray_r',
                  'gist_heat', 'gist_heat_r', 'gist_ncar', 'gist_ncar_r',
                  'gist_rainbow', 'gist_rainbow_r', 'gist_stern', 'gist_stern_r',
                  'gist_yarg', 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r',
                  'gnuplot_r', 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r',
                  'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 'magma_r', 
                  'nipy_spectral', 'nipy_spectral_r', 'ocean', 'ocean_r', 
                  'pink', 'pink_r', 'plasma', 'plasma_r', 'prism', 'prism_r', 
                  'rainbow', 'rainbow_r', 'seismic', 'seismic_r', 
                  'spectral', 'spectral_r', 'spring', 'spring_r', 
                  'summer', 'summer_r', 'terrain', 'terrain_r', 
                  'viridis', 'viridis_r', 'winter', 'winter_r']
  
"""

###############################################################################
###############################################################################  

MPL_COLORS = collections.OrderedDict()
MPL_COLORS['Black'] = None
MPL_COLORS['Maroon'] = None
MPL_COLORS['Green'] = wx.Colour(0, 100, 0)  # Dark Green
MPL_COLORS['Olive'] = wx.Colour(128, 128, 0)
MPL_COLORS['Navy'] = None
MPL_COLORS['Purple'] = None
MPL_COLORS['Teal'] = wx.Colour(0, 128, 128)
MPL_COLORS['Gray'] = None
MPL_COLORS['Silver'] = wx.Colour(192, 192, 192)
MPL_COLORS['Red'] = None
MPL_COLORS['Lime'] = wx.Colour(0, 255, 0)  # Green
MPL_COLORS['Yellow'] = None
MPL_COLORS['Blue'] = None
MPL_COLORS['Fuchsia'] = wx.Colour(255, 0, 255)
MPL_COLORS['Aqua'] = wx.Colour(0, 255, 255)
MPL_COLORS['White'] = None
MPL_COLORS['SkyBlue'] = wx.Colour(135, 206, 235)
MPL_COLORS['LightGray'] = wx.Colour(211, 211, 211)
MPL_COLORS['DarkGray'] = wx.Colour(169, 169, 169)
MPL_COLORS['SlateGray'] = wx.Colour(112, 128, 144)
MPL_COLORS['DimGray'] = wx.Colour(105, 105, 105)
MPL_COLORS['BlueViolet'] = wx.Colour(138, 43, 226)
MPL_COLORS['DarkViolet'] = wx.Colour(148, 0, 211)
MPL_COLORS['Magenta'] = None
MPL_COLORS['DeepPink'] = wx.Colour(148, 0, 211)
MPL_COLORS['Brown'] = None
MPL_COLORS['Crimson'] = wx.Colour(220, 20, 60)
MPL_COLORS['Firebrick'] = None
MPL_COLORS['DarkRed'] = wx.Colour(139, 0, 0)
MPL_COLORS['DarkSlateGray'] = wx.Colour(47, 79, 79)
MPL_COLORS['DarkSlateBlue'] = wx.Colour(72, 61, 139)
MPL_COLORS['Wheat'] = None
MPL_COLORS['BurlyWood'] = wx.Colour(222, 184, 135)
MPL_COLORS['Tan'] = None
MPL_COLORS['Gold'] = None
MPL_COLORS['Orange'] = None
MPL_COLORS['DarkOrange'] = wx.Colour(255, 140, 0)
MPL_COLORS['Coral'] = None
MPL_COLORS['DarkKhaki'] = wx.Colour(189, 183, 107)
MPL_COLORS['GoldenRod'] = None
MPL_COLORS['DarkGoldenrod'] = wx.Colour(184, 134, 11)
MPL_COLORS['Chocolate'] = wx.Colour(210, 105, 30)
MPL_COLORS['Sienna'] = None
MPL_COLORS['SaddleBrown'] = wx.Colour(139, 69, 19)
MPL_COLORS['GreenYellow'] = wx.Colour(173, 255, 47)
MPL_COLORS['Chartreuse'] = wx.Colour(127, 255, 0)
MPL_COLORS['SpringGreen'] = wx.Colour(0, 255, 127)
MPL_COLORS['MediumSpringGreen'] = wx.Colour(0, 250, 154)
MPL_COLORS['MediumAquamarine'] = wx.Colour(102, 205, 170)
MPL_COLORS['LimeGreen'] = wx.Colour(50, 205, 50)
MPL_COLORS['LightSeaGreen'] = wx.Colour(32, 178, 170)
MPL_COLORS['MediumSeaGreen'] = wx.Colour(60, 179, 113)
MPL_COLORS['DarkSeaGreen'] = wx.Colour(143, 188, 143)
MPL_COLORS['SeaGreen'] = wx.Colour(46, 139, 87)
MPL_COLORS['ForestGreen'] = wx.Colour(34, 139, 34)
MPL_COLORS['DarkOliveGreen'] = wx.Colour(85, 107, 47)
MPL_COLORS['DarkGreen'] = wx.Colour(1, 50, 32)
MPL_COLORS['LightCyan'] = wx.Colour(224, 255, 255)
MPL_COLORS['Thistle'] = None
MPL_COLORS['PowderBlue'] = wx.Colour(176, 224, 230)
MPL_COLORS['LightSteelBlue'] = wx.Colour(176, 196, 222)
MPL_COLORS['LightSkyBlue'] = wx.Colour(135, 206, 250)
MPL_COLORS['MediumTurquoise'] = wx.Colour(72, 209, 204)
MPL_COLORS['Turquoise'] = None
MPL_COLORS['DarkTurquoise'] = wx.Colour(0, 206, 209)
MPL_COLORS['DeepSkyBlue'] = wx.Colour(0, 191, 255)
MPL_COLORS['DodgerBlue'] = wx.Colour(30, 144, 255)
MPL_COLORS['CornflowerBlue'] = wx.Colour(100, 149, 237)
MPL_COLORS['CadetBlue'] = wx.Colour(95, 158, 160)
MPL_COLORS['DarkCyan'] = wx.Colour(0, 139, 139)
MPL_COLORS['SteelBlue'] = wx.Colour(70, 130, 180)
MPL_COLORS['RoyalBlue'] = wx.Colour(65, 105, 225)
MPL_COLORS['SlateBlue'] = wx.Colour(106, 90, 205)
MPL_COLORS['DarkBlue'] = wx.Colour(0, 0, 139)
MPL_COLORS['MediumBlue'] = wx.Colour(0, 0, 205)
MPL_COLORS['SandyBrown'] = wx.Colour(244, 164, 96)
MPL_COLORS['DarkSalmon'] = wx.Colour(233, 150, 122)
MPL_COLORS['Salmon'] = None
MPL_COLORS['Tomato'] = wx.Colour(255, 99, 71)
MPL_COLORS['Violet'] = wx.Colour(238, 130, 238)
MPL_COLORS['HotPink'] = wx.Colour(255, 105, 180)
MPL_COLORS['RosyBrown'] = wx.Colour(188, 143, 143)
MPL_COLORS['MediumVioletRed'] = wx.Colour(199, 21, 133)
MPL_COLORS['DarkMagenta'] = wx.Colour(139, 0, 139)
MPL_COLORS['DarkOrchid'] = wx.Colour(153, 50, 204)
MPL_COLORS['Indigo'] = wx.Colour(75, 0, 130)
MPL_COLORS['MidnightBlue'] = wx.Colour(25, 25, 112)
MPL_COLORS['MediumSlateBlue'] = wx.Colour(123, 104, 238)
MPL_COLORS['MediumPurple'] = wx.Colour(147, 112, 219)
MPL_COLORS['MediumOrchid'] = wx.Colour(186, 85, 211)

MPL_COLORS = collections.OrderedDict(sorted(MPL_COLORS.items()))

###############################################################################
###############################################################################        

# Based on https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html
# 10/September/2019 - Adriano Santana

MPL_LINESTYLES = collections.OrderedDict()
MPL_LINESTYLES['Solid'] = (0, ())
MPL_LINESTYLES['Dotted'] = (0, (1, 1))
MPL_LINESTYLES['Loosely dotted'] = (0, (1, 10))
MPL_LINESTYLES['Densely dotted'] = (0, (1, 1))
MPL_LINESTYLES['Dashed'] = (0, (5, 5))
MPL_LINESTYLES['Loosely dashed'] = (0, (5, 10))
MPL_LINESTYLES['Densely dashed'] = (0, (5, 1))
MPL_LINESTYLES['Dashdotted'] = (0, (3, 5, 1, 5))
MPL_LINESTYLES['Loosely dashdotted'] = (0, (3, 10, 1, 10))
MPL_LINESTYLES['Densely dashdotted'] = (0, (3, 1, 1, 1))
MPL_LINESTYLES['Dashdotdotted'] = (0, (3, 5, 1, 5, 1, 5))
MPL_LINESTYLES['Loosely dashdotdotted'] = (0, (3, 10, 1, 10, 1, 10))
MPL_LINESTYLES['Densely dashdotdotted'] = (0, (3, 1, 1, 1, 1, 1))
