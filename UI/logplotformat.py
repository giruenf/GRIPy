# -*- coding: utf-8 -*-

from collections import OrderedDict
from FileIO.PLT import PLTFile
from wx.lib.pubsub import pub

import copy
import numpy as np
import inspect

"""
TRACK_KEYS = OrderedDict([
    ('width', float),
    ('plotgrid', bool),
    ('x_scale', int),
    ('decades', int),
    ('leftscale', float),
    ('minorgrid', bool),
    ('overview', bool),
    ('scale_lines', int),
    ('depth_lines', int),
    ('show_track', bool),
    ('track_name', str),
    ('unidentified', int)
])
#
CURVE_KEYS = OrderedDict([
    ('curve_name', str),
    ('left_scale', float),
    ('right_scale', float),
    ('backup', str),
    ('thickness', int),
    ('color', str),
    ('x_scale', int),
    ('plottype', str),
    ('visible', bool),
    ('unidentified', bool)
])
"""
#
SHADE_KEYS = OrderedDict([
    ('left_curve_name', str),
    ('left_curve_value', float),
    ('right_curve_name', str),
    ('right_curve_value', float),
    ('visible', bool),
    ('color', str), 
    ('description', str)
])
#
OTHER_KEYS = ['GRID', 'PRINTOUT', 'HEADER', 'ANNO', 'HEADERREMARKS', 
              'PLOTSTYLE'
]    



###############################################################################


def caller():
    """
        It is a Python 2 hack for a feature only avaialable in Python 3.3+
        Based on: https://gist.github.com/techtonik/2151727    

        Changes by: Adriano Paulo    
    
        Get caller module, object and function

        Returns:
            A tuple (module, object, function)    
    
    """
    stack = inspect.stack()
    start = 2
    if len(stack) < start + 1:
      return None
    parentframe = stack[start][0]    
    module = inspect.getmodule(parentframe)
    if 'self' in parentframe.f_locals:
        obj = parentframe.f_locals['self']
    else:
        obj = None
    codename = parentframe.f_code.co_name
    return (module, obj, codename)
    

###############################################################################    


class UIPropertiesBase(object):
    __id = 0    
    KEYS = None        
        
    def __init__(self, **kwargs):
        self._id = self.__get_unique_label()
        if kwargs:
            for key, value in kwargs.items():
                if key in self.KEYS:
                    value_type = self.KEYS.get(key)
                    try:
                        value = value_type(value)
                        self.__dict__[key] = value
                    except:
                        pass    


    def __str__(self):
        return self.get_id() 
        
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_id() == other.get_id()
        return False  
                
                  
    def __call__(self):
        ret_val = dict(self.__dict__)
        del ret_val['_id']
        return ret_val

                    
    def set(self, key, value, caller_obj=None):
        old_value = copy.deepcopy(self.__dict__.get(key)) 
        #print 'old_value:', old_value
        if key in self.KEYS:
            value_type = self.KEYS.get(key)
            try:
                value = value_type(value)
            except:
                value = None
              
            self.__dict__[key] = value
            if caller_obj is None:
                caller_obj = caller()[1]
            pub.sendMessage(key, origin=caller_obj, old_value=old_value,
                            new_value=value, publisher=self)
                
    
    def get(self, key):
        #return copy.deepcopy(self.__dict__.get(key))
        return self.__dict__.get(key)
        
    def register_listener(self, key, function):
        #print 'REGISTRANDO:', key, str(function)
        pub.subscribe(function, key)
        #pub.subscribe(self.teste, key)
        
        
    def get_id(self):
        return self._id
            
    @classmethod
    def __get_unique_label(cls):
        label = '%s %i' % (cls.__name__, cls.__id)
        cls.__id += 1
        return label        



        
        
###############################################################################


class TrackUIProperties(UIPropertiesBase):

    KEYS = OrderedDict([
        ('width', int),
        ('plotgrid', bool),
        ('x_scale', int),
        ('decades', int),
        ('leftscale', float),
        ('minorgrid', bool),
        ('overview', bool),
        ('scale_lines', int),
        ('depth_lines', int),
        ('show_track', bool),
        ('track_name', str),
        ('curves', list)
        #('unidentified', int)
    ])
    
  

###############################################################################
  
  
class CurveUIProperties(UIPropertiesBase):

    KEYS = OrderedDict([
        ('curve_name', str),
        ('left_scale', float),
        ('right_scale', float),
        ('unit', str),
        ('backup', str),
        ('thickness', int),
        ('color', str),
        ('x_scale', int),
        ('plottype', str),
        ('visible', bool),
        ('step', int),
        ('cmap', str)
        
        #('unidentified', bool)
    ])

    @staticmethod
    def from_IP_parameters(parms):
        cp = CurveUIProperties()
        cp.set('curve_name', parms.get('Name'))
        cp.set('left_scale', parms.get('LeftScale'))
        cp.set('right_scale', parms.get('RightScale'))
        cp.set('unit', parms.get('Units'))
        cp.set('backup', parms.get('Backup'))        
        cp.set('thickness', parms.get('LineWidth'))
        
        color = parms.get('Color', 'black')
        if color == 'DkGray':
            color = 'darkgray'
        cp.set('color', color)
        loglin = parms.get('LogLin')
        if loglin == 'Lin':
            cp.set('x_scale', 0)
        elif loglin == 'Log':
            cp.set('x_scale', 1)
        else:
            raise ValueError('Unknown LogLin: [{}]'.format(loglin))            
        cp.set('plottype', parms.get('LineStyle'))        
        cp.set('visible', True)
        return cp  
        

    @staticmethod
    def from_object(obj):
        cp = CurveUIProperties()
        if obj.tid == 'partition':
            cp.set('plottype', 'Partition')
            return cp
        elif obj.tid == 'depth':    #curve.set_value('plottype', 'Partition')
            cp.set('plottype', 'Index')
            cp.set('thickness', 9)
            cp.set('left_scale', 0.0)
            cp.set('right_scale', 1.0)
        elif obj.tid == 'log': 
            cp.set('plottype', 'Solid')    
            cp.set('thickness', 1)
            ls, rs = CurveUIProperties.get_extremes_from_object(obj)
            cp.set('left_scale', ls)
            cp.set('right_scale', rs)
        elif obj.tid == 'velocity':
            cp.set('plottype', 'density')
            cp.set('cmap', 'rainbow')
            return cp            
        elif obj.tid == 'seismic':
            #cp.set('plottype', 'wiggle')
            cp.set('plottype', 'density')
            cp.set('cmap', 'gray')#'gray')#')
            return cp
        elif obj.tid == 'scalogram':
            cp.set('plottype', 'density')
            cp.set('cmap', 'Paired') #'nipy_spectral')#cp.set('cmap', 'rainbow')
            return cp    
  
 
        cp.set('curve_name', obj.name)
        cp.set('unit', obj.unit)
        cp.set('backup', 0)        
        cp.set('color', 'black')
        cp.set('x_scale', 0)                
        cp.set('visible', True)
        return cp          


    @staticmethod
    def get_extremes_from_object(obj, gap_percent=5):
        left = np.nanmin(obj.data)
        right = np.nanmax(obj.data)
        unit = (right - left) / (100-gap_percent*2)
        left = left - (gap_percent*unit)
        right = right + (gap_percent*unit)
        return np.round(left, 2), np.round(right, 2)

###############################################################################
"""
class CurveFormat(BaseFormat):
    USE_DEFAULT_CURVE_VALUE = -99999.99
    SCALE_MAPPING = {
        0: 'Linear',
        1: 'Logarithmic'
    }
    NUMERIC_BACKUP_MAPPING = {
         0: '0',
         1: '270',
         2: '90'
    }    
    LINE_BACKUP_MAPPING = {
         0: 'None',
         1: 'RBU',
         2: 'LBU',
         3: 'x10',
         4: 'Wrap'
    }    
    
    def __init__(self, values_map=None):
        BaseFormat.__init__(self)
        self._map = OrderedDict()
        self.set_values(values_map)

    def __str__(self):
        return self.get_id() + ': ' + str(self.get_values())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_id() == other.get_id() and self._map == other._map 
        return False

    def __ne__(self, other):
        return not self == other
    
    def set_values(self, values_map):
        if values_map is None:
            return
        try :
            for key, value in values_map.items():
                self.set_value(key, value)
        except Exception:
            raise            

    def set_value(self, key, value):
        if key in LogPlotFormat.CURVE_KEYS.keys():
            type_ = LogPlotFormat.get_curve_key_type(key)
            try:
                value = type_(value)
                self._map[key] = value
                return True
            except Exception:
                if key == 'left_scale' or key == 'right_scale':  
                    if value == '*':        
                        self._map[key] = self.USE_DEFAULT_CURVE_VALUE
                        return True
                return False
        else:
            return False

    def get_values(self):
        return self._map

    def get_value(self, key):
        if key in LogPlotFormat.CURVE_KEYS.keys():
            return self._map.get(key)
        else:
            return None

            
###############################################################################
            
            
class ShadeFormat(BaseFormat): 
    CURVE_VALUE_ID = -99999.99
    def __init__(self, values_map):
        BaseFormat.__init__(self)   
        self._map = values_map
        self.set_values(values_map)
        
        
    def __str__(self):
        return self.get_id() + ': ' + str(self.get_values())
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_id() == other.get_id() and self._map == other._map
        return False
     
    def __ne__(self, other):
        return not self == other
        
    def set_values(self, values_map):
        if values_map is None:
            return
        try :
            for key, value in values_map.items():
                
                self.set_value(key, value)
        except Exception:
            raise            

    def set_value(self, key, value):
        if key in LogPlotFormat.SHADE_KEYS.keys():
            type_ = LogPlotFormat.get_shade_key_type(key)
            try:
                if key == 'left_curve_value' or key == 'right_curve_value':
                    if value.lower() == 'curve':
                        self._map[key] = self.CURVE_VALUE_ID 
                        return True
                value = type_(value)
                self._map[key] = value
                return True
            except Exception:
                raise
        else:
            return False
    
    def get_values(self):
        return self._map     
     
    def get_value(self, key):
        if key in LogPlotFormat.SHADE_KEYS.keys():
            return self._map.get(key)
        else:
            return None       
 

###############################################################################

       
# OrderFormat is just for convinience, because this 'order' is an "IP Thing"
# Probabily it will be excluded soon (maybe)
class OrderFormat(BaseFormat):
        
    def __init__(self, values_list):
        BaseFormat.__init__(self)  
        self.data = values_list
        
    def __str__(self):
        return self.get_id() + ': ' + str(self.get_values())
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_id() == other.get_id() and self.data == other.data
        return False

    def __ne__(self, other):
        return not self == other
        
    def get_values(self):
        return self.data
        
 
###############################################################################
 
       
class TrackFormat(BaseFormat):
    
    DEPTH_LINES_MAPPING = {
        0: 'Full',
        1: 'Left',
        2: 'Right',
        3: 'Center',
        4: 'Left & Right',
        5: 'None'
    }
    SCALE_MAPPING = {
        0: 'Linear',
        1: 'Logarithmic',
        2: 'Sine',
        3: 'Cosine'
    }
    

    def __init__(self, **kwargs):
        BaseFormat.__init__(self)
        self._map = OrderedDict()
        print kwargs
        self.set_values(**kwargs)
        self._curves = []
        self._shades = []
        self._order = None
        

    def __str__(self):
        _str = self.get_id() + ': ' + str(self.get_values()) + '\n'
        for curve in self.get_curves():
            _str += str(curve) + '\n'
        for shade in self.get_shades():
            _str += str(shade) + '\n'               
        _str += str(self._order) 
        return _str

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.get_id() != other.get_id():
                return False
            if self._map != other._map:
                return False    
            if not self._order == other._order:
                return False    
            if len(self._curves) != len(other._curves):
                return False
            if len(self._shades) != len(other._shades):
                return False    
            for i in range(len(self._curves)):
                if self._curves[i] != other._curves[i]:
                    return False
            for i in range(len(self._shades)):
                if self._shades[i] != other._shades[i]:
                    return False                   
            return True 
        return False

    def __ne__(self, other):
        return not self == other
            
    def set_values(self, **kwargs):
        if kwargs is None:
            return
        try :
            for key, value in kwargs.items():
                self.set_value(key, value)
        except Exception:
            raise            

    def set_value(self, key, value):
        if key in TRACK_KEYS.keys():
            type_ = LogPlotFormat.get_track_key_type(key)
            try:
                value2 = type_(value)
                self._map[key] = value2
                return True
            except Exception:
                return False
        else:
            return False
        
    def get_values(self):
        return self._map     
     
    def get_value(self, key):
        if key in LogPlotFormat.TRACK_KEYS.keys():
            return self._map.get(key)
        else:
            return None   
            
    def change_all_curves(self, new_curves_list):

        self.remove_all_curves()
        self._curves = new_curves_list

        
    def add_curve(self, curve):
        if not isinstance(curve, CurveFormat):
            raise Exception('Only CurveFormat objects can be added as TrackFormat curves ')
        self._curves.append(curve)
        
    def remove_curve_idx(self, curve_index):
        if curve_index >= 0 and curve_index < len(self._curves):
            del self._curves[curve_index]  
            
    def remove_curve(self, curve):
        if not isinstance(curve, CurveFormat):
            raise Exception('Cannot remove a object different from CurveFormat.')
        if curve in self._curves:
            pos = self._curves.index(curve)
            self._curves.remove(curve)
            return pos
        return -1
        
    def pop_curve(self, idx=None):
        if idx is None:
            return self._curves.pop()
        else:
            return self._curves.pop(idx)    
            
    def remove_all_curves(self):
        del self._curves[:]        
        
    def get_curve(self, curve_index):
        if curve_index >= 0 and curve_index < len(self._curves):
            return self._curves[curve_index]        
        
    def get_curves(self):
        return self._curves
        
    def get_curve_index(self, curve):
        if not isinstance(curve, CurveFormat):
            raise Exception('Must give a CurveFormat object.')
        return self._curves.index(curve)        
        
    def add_shade(self, shade):
        if not isinstance(shade, ShadeFormat):
            raise Exception('Only ShadeFormat objects can be added as TrackFormat shades.')
        self._shades.append(shade)
        
    def remove_shade(self, shade_index):
        if shade_index >= 0 and shade_index < len(self._shades):
            del self._shades[shade_index]  
            
    def remove_all_shades(self):
        del self._shades[:]        
        
    def get_shade(self, shade_index):
        if shade_index >= 0 and shade_index < len(self._shades):
            return self._shades[shade_index]        
        
    def get_shades(self):
        return self._shades      
        
    def set_order(self, order):
        self._order = order
        
    def get_order(self):
        return self._order
 



###############################################################################
  
    
class HeaderObjectFormat(BaseFormat):
        
    def __init__(self, name, data):
        BaseFormat.__init__(self)
        self.name = name
        self.data = data
        
    def __str__(self):
        return self.name + ': ' + str(self.get_values())
        
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.get_id() == other.get_id():
                return self.name == other.name and self.data == other.data
        return False
     
    def __ne__(self, other):
        return not self == other
        
    def get_values(self):
        return self.data   
 
       
###############################################################################

        
class LogPlotFormat(BaseFormat):
    #tid = 'logplotformat'
    DEFAULT_TRACK_WIDTH = 2.0
    #
    TRACK_KEYS = OrderedDict()
    TRACK_KEYS['width'] = float
    TRACK_KEYS['plotgrid'] = bool
    TRACK_KEYS['x_scale'] = int
    TRACK_KEYS['decades'] = int
    TRACK_KEYS['leftscale'] = float
    TRACK_KEYS['minorgrid'] = bool
    TRACK_KEYS['overview'] = bool
    TRACK_KEYS['scale_lines'] = int
    TRACK_KEYS['depth_lines'] = int
    TRACK_KEYS['show_track'] = bool
    TRACK_KEYS['track_name'] = str
    TRACK_KEYS['unidentified'] = int
    #
    CURVE_KEYS = OrderedDict()
    CURVE_KEYS['curve_name'] = str  
    CURVE_KEYS['left_scale'] = float
    CURVE_KEYS['right_scale'] = float
    CURVE_KEYS['backup'] = str
    CURVE_KEYS['thickness'] = int
    CURVE_KEYS['color'] = str
    CURVE_KEYS['x_scale'] = int
    CURVE_KEYS['plottype'] = str 
    CURVE_KEYS['visible'] = bool
    CURVE_KEYS['unidentified'] = bool
    # 
    SHADE_KEYS = OrderedDict()
    SHADE_KEYS['left_curve_name'] = str
    SHADE_KEYS['left_curve_value'] = float
    SHADE_KEYS['right_curve_name'] = str
    SHADE_KEYS['right_curve_value'] = float
    SHADE_KEYS['visible'] = bool
    SHADE_KEYS['color'] = str
    SHADE_KEYS['description'] = str 
    #
    OTHER_KEYS = ['GRID', 'PRINTOUT', 'HEADER', 'ANNO', 'HEADERREMARKS',
                'PLOTSTYLE']      
    
                    
    def __init__(self):
        BaseFormat.__init__(self)
        self.name = None
        self._tracks = []
        self._headers = []
        
    def __str__(self):
        _str = 'LogPlotFormat: [{}, {}]'.format(self.get_id(), self.name) + '\n'
        for track in self._tracks:
            _str += str(track) + '\n'
        for header in self._headers:
            _str += str(header) + '\n'    
        return _str   
        
    def __eq__(self, other):
        if isinstance(other, self.__class__): 
            if self.get_id() != other.get_id():
                return False
            if len(self._tracks) != len(other._tracks):
                return False
            for i in range(len(self._tracks)):
                if not self._tracks[i] == other._tracks[i]:
                    return False
            if len(self._headers) != len(other._headers):          
                return False
            for i in range(len(self._headers)):
                if self._headers[i] != other._headers[i]:
                    return False      
            return True 
        return False    
            
    def __ne__(self, other):
        return not self == other            
            
    def __len__(self):
        return len(self._tracks)        

    def insert_track(self, pos, track):
        if not isinstance(track, TrackFormat):
            raise Exception('Only TrackFormat objects can be inserted as LogPlotFormat tracks.') 
        self._tracks.insert(pos, track)    
        
    def append_track(self, track):
        if not isinstance(track, TrackFormat):
            raise Exception('Only TrackFormat objects can be appended as LogPlotFormat tracks.')
        self._tracks.append(track)

    def remove_track_idx(self, track_index):
        if track_index >= 0 and track_index < len(self._tracks):
            del self._tracks[track_index]  
    
    def remove_tracks_indexes(self, track_indexes):
        sorted(track_indexes, key=int, reverse=True)
        for idx in track_indexes:    
            self.remove_track_idx(idx)
    
    def remove_track(self, track):
        if not isinstance(track, TrackFormat):
            raise Exception('Cannot remove a object different from TrackFormat.')
        if track in self._tracks:
            pos = self._tracks.index(track)
            self._tracks.remove(track)
            return pos
        return -1
        
    def pop_track(self, idx=None):
        if idx is None:
            return self._tracks.pop()
        else:
            return self._tracks.pop(idx)
            
    def remove_all_tracks(self):
        del self._tracks[:]        
        
    def change_track_positions(self, track1, track2):
        if track1 not in self._tracks or track2 not in self._tracks:
            raise ValueError ('One of the tracks does not belong to this LogPlotFormat.')
        idx1, idx2 = self.get_track_index(track1), self.get_track_index(track2)
        self._tracks[idx1], self._tracks[idx2] = self._tracks[idx2], self._tracks[idx1]


    def change_curve_parent_track(self, curve, new_parent_track):
        if not isinstance(new_parent_track, TrackFormat):
            raise Exception('Must associate a CurveFormat to a TrackFormat object.')
        if not new_parent_track in self._tracks:
            raise Exception('new_track_parent does not belong to this LogPlotFormat.')
        old_parent_track = self.get_curve_parent(curve)    
        if old_parent_track == new_parent_track:
            return False
        #idx = old_parent_track.get_curve_index(curve)    
        #old_parent_track.pop_curve(idx)    
        old_parent_track.remove_curve(curve)
        new_parent_track.add_curve(curve)
        return True

    def set_track_new_position(self, track, new_pos):
        if track not in self._tracks:
            raise ValueError ('This track does not belong to this LogPlotFormat.')
        if new_pos < 0 and new_pos >= len(self._tracks):
            raise ValueError ('This position cannot be used. [0 <= pos < len(tracks)]')           
        old_pos = self.get_track_index(track)
        if new_pos == old_pos:
            return
        self.pop_track(old_pos)
        self.insert_track(new_pos, track)
        
    def get_track(self, idx):
        if idx >= 0 and idx < len(self._tracks):
            return self._tracks[idx]
        return None
        
    def get_tracks(self):
        return self._tracks

    def get_track_index(self, track):
        if not isinstance(track, TrackFormat):
            raise Exception('Cannot get a track position of non TrackFormat object.')
        return self._tracks.index(track)        
        
    def get_curves(self):        
        curves = []
        for track in self.get_tracks(): 
            curves.extend(track.get_curves())
        return curves    

    def get_curve_parent(self, curve):   
        if not isinstance(curve, CurveFormat):
            raise Exception('Cannot get a curve parent of non CurveFormat object.') 
        for track in self.get_tracks(): 
            if curve in track.get_curves():
                return track
        return None  # Informed curve does not belong this LogPlotFormat
        
    def remove_curve(self, curve):
        if not isinstance(curve, CurveFormat):
            raise Exception('Cannot remove a object different from CurveFormat.')
        if not curve in self.get_curves():        
            raise ValueError('This curve does not belong to this LogPlotFormat.')
        track_parent = self.get_curve_parent(curve)    
        track_parent.remove_curve(curve)        
        
    def add_header_object(self, header_object):        
        if not isinstance(header_object, HeaderObjectFormat):
            raise Exception('Only HeaderObjectFormat objects can be added as LogPlotFormat headers.')
        self._headers.append(header_object)      
        
    def get_header_object(self, header_object_name):
        for header in self._headers:
            if header.name == header_object_name:
                return header
        return None            
        
    def get_headers_objects(self):
        return self._headers
        
    def remove_header_object(self, header_object_name):
        for header in self._headers:
            if header.name == header_object_name:
                self._headers.remove(header)
                return True
        return False         
            
    def remove_all_headers(self):
        del self._headers[:]                
                     
    def get_track_header_color(self):    
        return self.get_header_object('GRID').data[46]    
        
    @staticmethod    
    def get_default_track_header_color(): 
        return '#B0C4DE' #LightSteelBlue
        
    def set_track_header_color(self, color):    
        self.get_header_object('GRID').data[46] = color                    
                
    @staticmethod
    def get_track_key(index):
        if index >= 0 and index < len(LogPlotFormat.TRACK_KEYS):
            return LogPlotFormat.TRACK_KEYS.keys()[index]            
        else:
            return None
    
    @staticmethod
    def get_track_key_type(key):
        if LogPlotFormat.TRACK_KEYS.get(key):
            return LogPlotFormat.TRACK_KEYS.get(key)          
        else:
            return None  
            
    @staticmethod
    def get_curve_key(index):
        if index >= 0 and index < len(LogPlotFormat.CURVE_KEYS):
            return LogPlotFormat.CURVE_KEYS.keys()[index]            
        else:
            return None
    
    @staticmethod
    def get_curve_key_type(key):
        if LogPlotFormat.CURVE_KEYS.get(key):
            return LogPlotFormat.CURVE_KEYS.get(key)          
        else:
            return None     
            
    @staticmethod
    def get_shade_key(index):
        if index >= 0 and index < len(LogPlotFormat.SHADE_KEYS):
            return LogPlotFormat.SHADE_KEYS.keys()[index]            
        else:
            return None
    
    @staticmethod
    def get_shade_key_type(key):
        if LogPlotFormat.SHADE_KEYS.get(key):
            return LogPlotFormat.SHADE_KEYS.get(key)          
        else:
            return None                
            
    @staticmethod
    def create_from_PLTFile(PLTfile):
        if not isinstance(PLTfile, PLTFile):
            raise Exception('A PLTFile instance must be given.')
        lpf = LogPlotFormat()  
        # Each row is an OrderedDict
        for row in PLTfile.get_main_parms():
            print '\nrow: ', row
            # track_value is an OrderedDict too
            track_value = row.get('TRACK')
            # Some adjusts
            if track_value.get('track_name') == '-':
                del track_value['track_name']
            track_value['width'] = float(track_value.get('width'))  
            if track_value.get('show_track') is None:
                track_value['show_track'] = 'Yes'
            # Axis X scale   
            if isinstance(track_value.get('x_scale'), int):    
                track_value['x_scale'] = track_value.get('x_scale')
            else:    
                if track_value.get('x_scale').lower() == 'no':
                    track_value['x_scale'] = 0
                elif track_value.get('x_scale').lower() == 'yes':
                    track_value['x_scale'] = 1
                elif  track_value.get('x_scale').lower() == 'lin':
                    track_value['x_scale'] = 0    
                elif track_value.get('x_scale').lower() == 'log':
                    track_value['x_scale'] = 1   
                elif  track_value.get('x_scale').lower() == 'sin':
                    track_value['x_scale'] = 2    
                elif track_value.get('x_scale').lower() == 'cos':
                    track_value['x_scale'] = 3       
            #       
            if track_value.get('depth_lines') is None:
                track_value['depth_lines'] = 0
            elif track_value.get('depth_lines') == 'Yes':
                track_value['depth_lines'] = 0
            elif track_value.get('depth_lines') == 'No':    
                track_value['depth_lines'] = 5
            else:
                track_value['depth_lines'] = int(track_value.get('depth_lines'))  
            track_value['scale_lines'] = int(track_value.get('scale_lines'))
            track_value['decades'] = int(track_value.get('decades'))
            track_value['leftscale'] = float(track_value.get('leftscale')) 
            for key in ['plotgrid', 'minorgrid', 'overview', 'show_track']:
                if isinstance(track_value.get(key), str):
                    if track_value.get(key).lower() == 'yes':
                        track_value[key] = True
                    elif track_value.get(key).lower() == 'no':
                        track_value[key] = False    
            # Some Adjusts (End)    
            tf = TrackFormat(track_value)
            # curves_values is list of OrderedDict
            curves_values = row.get('CURVE')
            for curve_value in curves_values:
                # Curves Adjusts
                if curve_value.get('visible') is None:
                    curve_value['visible'] = True
                if isinstance(curve_value.get('x_scale'), str):    
                    if curve_value.get('x_scale').lower() == 'lin':
                        curve_value['x_scale'] = 0    
                    elif curve_value.get('x_scale').lower() == 'log':
                        curve_value['x_scale'] = 1  
                #       
                cf = CurveFormat(curve_value)
                tf.add_curve(cf)
            shades_values = row.get('SHADE')
            for shade_value in shades_values:
                sf = ShadeFormat(shade_value)
                tf.add_shade(sf)
            order_value = row.get('ORDER')
            of = OrderFormat(order_value)
            tf.set_order(of)
            lpf.append_track(tf)
        for key, value in PLTfile.get_header_parms().items():
            if value is not None:
                hof = HeaderObjectFormat(key, value)        
                lpf.add_header_object(hof)
        return lpf
        
        


"""

############################################################################### 
 
 
TF_DEFAULT_YLIM = (0, 6000)
TF_DEFAULT_PLOTGRID = False
TF_DEFAULT_SCALE = 0  # Linear
TF_DEFAULT_YMAJOR_LINES = True
TF_DEFAULT_YMINOR_LINES = False
TF_DEFAULT_DEPTH_LINES = True
TF_DEFAULT_WIDTH = 160 #2.0
TF_DEFAULT_LOG_DECADES = 4
TF_DEFAULT_LOG_LEFTSCALE = 0.2
TF_DEFAULT_LOG_MINORGRID = False 

TF_DEFAULT_PROPS = {
    'ylim': TF_DEFAULT_YLIM, 
    'plotgrid': TF_DEFAULT_PLOTGRID, 
    'x_scale': TF_DEFAULT_SCALE,
    'y_major_grid_lines': TF_DEFAULT_YMAJOR_LINES, 
    'y_minor_grid_lines': TF_DEFAULT_YMINOR_LINES,
    'depth_lines': TF_DEFAULT_DEPTH_LINES,
    'width': TF_DEFAULT_WIDTH #,
    #'curves': []    
}     


def TF_DEFAULT_TRACK_FORMAT():
    return TrackUIProperties(**TF_DEFAULT_PROPS)

#TF_DEFAULT_TRACK_FORMAT = TrackFormat(**TF_DEFAULT_PROPS)


############################################################################### 

