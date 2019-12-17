from collections import OrderedDict, Sequence

import wx
import wx.propgrid as pg
import matplotlib.colors as mcolors

from classes.ui import UIManager
from classes.ui import UIControllerObject
from classes.ui import UIViewObject
import app.pubsub as pub
from app.app_utils import MPL_COLORS, MPL_COLORMAPS


class GripyPgProperty(object):

    def __init__(self, obj_uid, obj_attr, getter_func=None, setter_func=None):
        self._obj_uid = obj_uid
        self._obj_attr = obj_attr
        self._getter_func = getter_func
        self._setter_func = setter_func

    def _get_object(self):
        app = wx.App.Get()
        Manager = app.get_manager_class(self._obj_uid[0])
        manager = Manager()
        obj = manager.get(self._obj_uid)
        return obj

    def _get_value(self):
        if self._getter_func:
            kwargs = {'obj_uid': self._obj_uid}
            return self._getter_func(self._obj_attr, **kwargs)
        obj = self._get_object()
        return obj[self._obj_attr]

    def _set_value(self, value):
        try:
            if self._setter_func:
                kwargs = {'obj_uid': self._obj_uid}
                return self._setter_func(self._obj_attr, value, **kwargs)
            obj = self._get_object()
            obj[self._obj_attr] = value
            return True
        except Exception as e:
            print('ERROR at GripyPgProperty._set_value:', e)
            #            raise
            return False

    def ValueToString(self, *args):
        return str(self._get_value())

    def StringToValue(self, text, flag=0):
        variant = self._set_value(text)
        if self._set_value(text):
            return True, variant
        return False, variant


class StringProperty(pg.StringProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.StringProperty.__init__(self, label, name=obj_attr)


class IntProperty(pg.IntProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.IntProperty.__init__(self, label, name=obj_attr)


class FloatProperty(pg.FloatProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 getter_func=None, setter_func=None):
        GripyPgProperty.__init__(self, obj_uid, obj_attr,
                                 getter_func, setter_func)
        pg.FloatProperty.__init__(self, label, name=obj_attr)


class BoolProperty(pg.BoolProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.BoolProperty.__init__(self, label, name=obj_attr)
        #
        self.SetAttribute("UseCheckbox", 1)
        self.SetAttribute("UseDClickCycling", 1)
        # Setting m_value with GripyPgProperty value
        value = self._get_value()
        self.SetValue(value)

    def OnSetValue(self):
        # Called after m_value was setted...
        # print('\nGripyPgProperty.OnSetValue')
        self._set_value(self.GetValue())


class EnumProperty(pg.EnumProperty, GripyPgProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None):

        if opt_labels is None:
            raise Exception('No options labels values found in: {} - model key: {}'. \
                            format(obj_uid, obj_attr)
                            )

        try:

            GripyPgProperty.__init__(self, obj_uid, obj_attr)
            pg.EnumProperty.__init__(self, label, obj_attr, opt_labels,
                                     values=list(range(len(opt_labels))), value=0)

            self._opt_labels = opt_labels
            self._opt_values = opt_values
            if self._opt_values is None:
                self._opt_values = opt_labels

            #
            val = self._get_value()
            #  
            idx = self._get_index(val)
            self.SetValue(idx)

        except Exception as e:
            print('\nDEU RUIM!!!! - {}\n\n\n'.format(e))
            raise

    def _get_index(self, val):

        try:
            return self._opt_values.index(val)
        except ValueError:
            try:
                return [key.lower() for key in self._opt_values].index(val)
            except:
                try:
                    return self._opt_labels.index(val)
                except:
                    print()
                    print('ERRO idx = self._opt_values.index(val)')
                    print(self._opt_values)
                    print(self._opt_labels)
                    print(val, type(val))
                    raise
                    #

    def IntToValue(self, int_value, flag=0):
        """Given a wx.Choice integer index, get its associated value 
        (from opt_values) and set the object attribute with this value.
        
        Parameters
        ----------
        variant : not used
            Default parameter from wx.propgrid.EnumProperty.
        int_value : int
            A wx.Choice integer index.    
        flag : not used
            Default parameter from wx.propgrid.EnumProperty.
            
        Returns
        -------
        ret_val : bool
            A value indicating operation was successful. 
        """

        opt_value = self._opt_values[int_value]
        ret_val = self._set_value(opt_value)
        return True, opt_value

    def ValueToString(self, value, flag=0):
        """Get object property value and returns a string associated with it.
        This string will be selected on wx.Choice container.
        
        Parameters
        ----------
        value : not used
            Default parameter from wx.propgrid.EnumProperty.
        flag : not used
            Default parameter from wx.propgrid.EnumProperty.
            
        Returns
        -------
        ret_str : str
            A string that will be selected on wx.Choice container. 
        """

        val = self._get_value()
        idx = self._get_index(val)
        ret_str = str(self._opt_labels[idx])
        return ret_str

    def GetIndexForValue(self, value):
        """Given a value, returns its associated index.
        
        Parameters
        ----------
        value : not used
            Default parameter from wx.propgrid.EnumProperty.

        Returns
        -------
        idx : int
            A integer index for given value. 
        """

        val = self._get_value()
        idx = self._get_index(val)
        return idx


class MPLColorsProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=list(MPL_COLORS.keys()))


class MPLColormapsProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=list(MPL_COLORMAPS))


class MPLScaleProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=["Linear", "Log", "Symlog", "Logit"],
                         opt_values=["linear", "log", "symlog", "logit"]
                         )


class MPLHAProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=["Center", "Right", "Left"],
                         opt_values=["center", "right", "left"]
                         )


class MPLVAProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=["Center", "Top", "Bottom",
                                     "Baseline", "Center baseline"],
                         opt_values=["center", "top", "bottom",
                                     "baseline", "center_baseline"]
                         )


class MPLFontWeightProperty(EnumProperty):

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        super().__init__(obj_uid, obj_attr, label=label,
                         opt_labels=["Normal", "Regular", "Light",
                                     "Ultralight", "Book", "Medium",
                                     "Roman", "Semibold", "Demibold",
                                     "Demi", "Bold", "Heavy", "Extra bold",
                                     "Black"],
                         opt_values=["normal", "regular", "light",
                                     "ultralight", "book", "medium",
                                     "roman", "semibold", "demibold",
                                     "demi", "bold", "heavy", "extra bold",
                                     "black"]
                         )


class SystemColourProperty(pg.SystemColourProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.SystemColourProperty.__init__(self, label, name=obj_attr,
                                         value=pg.ColourPropertyValue())


class ColourProperty(pg.ColourProperty, GripyPgProperty):
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):

        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.ColourProperty.__init__(self, label, name=obj_attr)
        #
        color = self._get_value()
        #
        if mcolors.is_color_like(color):
            color = tuple([255 * c for c in mcolors.to_rgb(color)])
        #
        self.SetValue(color)

    def OnSetValue(self):
        # Called after m_value was setted...
        val = self.GetValue()
        color = None
        if isinstance(val, Sequence):
            color = tuple([c / 255 for c in val])
            color = mcolors.to_hex(color)
        elif isinstance(val, wx.Colour):
            color = val.GetAsString(wx.C2S_HTML_SYNTAX)

        self._set_value(color)

    def ValueToString(self, value, flag):
        ret_str = ''
        mpl_colors_values_list = list(MPL_COLORS.values())
        if wx.Colour(value) in mpl_colors_values_list:
            idx = mpl_colors_values_list.index(wx.Colour(value))
            ret_str = list(MPL_COLORS.keys())[idx]
        #
        mpl_colors_od = OrderedDict(mcolors.get_named_colors_mapping())
        mpl_colors_values_list = list(mpl_colors_od.values())
        #
        if not ret_str:
            value = tuple(c / 255 for c in value)
            if value in mpl_colors_values_list:
                idx = mpl_colors_values_list.index(value)
                ret_str = list(mpl_colors_od.keys())[idx]
        #
        if not ret_str:
            value = mcolors.to_hex(value)
            if value in mpl_colors_values_list:
                idx = mpl_colors_values_list.index(value)
                ret_str = list(mpl_colors_od.keys())[idx]
            else:
                ret_str = value
        #        
        if ret_str == 'k':
            ret_str = 'Black'
        elif ret_str == 'w':
            ret_str = 'White'
        elif ret_str == 'b':
            ret_str = 'Blue'
        elif ret_str == 'g':
            ret_str = 'Green'
        elif ret_str == 'r':
            ret_str = 'Red'
        elif ret_str == 'c':
            ret_str = 'Cyan'
        elif ret_str == 'm':
            ret_str = 'Magenta'
        elif ret_str == 'w':
            ret_str = 'Yellow'
        elif ':' in ret_str:
            ret_str = ret_str.split(':')[-1]
        #    
        ret_str = ret_str.capitalize()
        #
        return ret_str


def _get_pg_property(obj_uid, obj_attr, obj_attr_props):
    if obj_attr_props.get('label') is None:
        obj_attr_props['label'] = obj_attr

    getter_func = obj_attr_props.get('getter_func')
    setter_func = obj_attr_props.get('setter_func')
    #
    enable = obj_attr_props.get('enabled', True)
    prop = None
    #

    if obj_attr_props.get('pg_property') == 'IntProperty' or \
            obj_attr_props.get('type') == int:
        prop = IntProperty(obj_uid, obj_attr,
                           label=obj_attr_props.get('label')
                           )

    elif obj_attr_props.get('pg_property') == 'FloatProperty' or \
            obj_attr_props.get('type') == float:
        prop = FloatProperty(obj_uid, obj_attr,
                             label=obj_attr_props.get('label'),
                             getter_func=getter_func,
                             setter_func=setter_func
                             )

    elif obj_attr_props.get('pg_property') == 'EnumProperty':
        prop = EnumProperty(obj_uid, obj_attr,
                            label=obj_attr_props.get('label'),
                            opt_labels=obj_attr_props.get('options_labels'),
                            opt_values=obj_attr_props.get('options_values')
                            )

    elif obj_attr_props.get('pg_property') == 'MPLColorsProperty':
        prop = MPLColorsProperty(obj_uid, obj_attr,
                                 label=obj_attr_props.get('label')
                                 )

    elif obj_attr_props.get('pg_property') == 'MPLColormapsProperty':
        prop = MPLColormapsProperty(obj_uid, obj_attr,
                                    label=obj_attr_props.get('label')
                                    )

    elif obj_attr_props.get('pg_property') == 'MPLScaleProperty':
        prop = MPLScaleProperty(obj_uid, obj_attr,
                                label=obj_attr_props.get('label')
                                )

    elif obj_attr_props.get('pg_property') == 'MPLHAProperty':
        prop = MPLHAProperty(obj_uid, obj_attr,
                             label=obj_attr_props.get('label')
                             )

    elif obj_attr_props.get('pg_property') == 'MPLVAProperty':
        prop = MPLVAProperty(obj_uid, obj_attr,
                             label=obj_attr_props.get('label')
                             )

    elif obj_attr_props.get('pg_property') == 'SystemColourProperty':
        prop = SystemColourProperty(obj_uid, obj_attr,
                                    label=obj_attr_props.get('label')
                                    )

    elif obj_attr_props.get('pg_property') == 'ColourProperty':
        prop = ColourProperty(obj_uid, obj_attr,
                              label=obj_attr_props.get('label')
                              )


    elif obj_attr_props.get('pg_property') == 'BoolProperty' or \
            obj_attr_props.get('type') == bool:
        prop = BoolProperty(obj_uid, obj_attr,
                            label=obj_attr_props.get('label')
                            )

    elif obj_attr_props.get('pg_property') == 'StringProperty' or \
            obj_attr_props.get('type') == str:
        prop = StringProperty(obj_uid, obj_attr,
                              label=obj_attr_props.get('label')
                              )

    elif isinstance(obj_attr_props.get('type'), tuple) and \
            obj_attr_props.get('type')[0] == tuple:
        prop = StringProperty(obj_uid, obj_attr,
                              label=obj_attr_props.get('label')
                              )

    if prop is not None:
        prop.Enable(enable)
        return prop
    else:
        raise Exception(' ERROR at _get_pg_property:', obj_uid, obj_attr, obj_attr_props)


# BLUE_COLORS_SCALE = ['#030C54', '#022F8E', '#1C70C8', '#51A2D5']
# BLUE_COLORS_SCALE = ['#022F8E', '#1C70C8', '#51A2D5']
BLUE_COLORS_SCALE = ['#0A619A', '#406A97', '#1974D2']


class PropertyGridController(UIControllerObject):
    tid = 'property_grid_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['obj_uid'] = {
        'default_value': None,
        'type': 'uid'
    }

    def __init__(self, **state):
        super().__init__(**state)
        #        self._properties = OrderedDict()
        #        self._fake_properties = OrderedDict()
        self.subscribe(self.on_change_obj_uid, 'change.obj_uid')

        # def PostInit(self):

    #    if self.obj_uid is not None:
    #        self.on_change_obj_uid(self.obj_uid, None)

    def _get_object(self, obj_uid=None):
        if obj_uid is None:
            obj_uid = self.obj_uid
        app = wx.App.Get()
        Manager = app.get_manager_class(obj_uid[0])
        manager = Manager()
        obj = manager.get(obj_uid)
        return obj

    def _create_pg_categories(self, categories, start_with=None,
                              blue_color_level=1):
        if start_with is None:
            start_with = self._root_category
        for name, data in categories.items():
            cat = pg.PropertyCategory(data['label'], name=name)
            # cat.SetBackgroundColour(wx.Colour(0, 128, blue_color))
            # self.view.SetCaptionBackgroundColour(wx.Colour(0, 128, blue_color))
            cell = cat.GetCell(0)
            cell.SetFgCol('white')
            # cell.SetBgCol(BLUE_COLORS_SCALE[blue_color_level])
            cell.SetBgCol(BLUE_COLORS_SCALE[2])
            self.view.AppendIn(start_with, cat)
            if data.get('children'):
                self._create_pg_categories(data['children'], cat,
                                           blue_color_level + 1)

    def on_change_obj_uid(self, new_value, old_value):
        # print('\n\non_change_obj_uid:', new_value, old_value)
        if old_value is not None:
            self.remove_properties(old_value)
        obj = self._get_object()
        title = obj.get_friendly_name()
        #
        self._root_category = pg.PropertyCategory(title, name='root')
        self.view.Append(self._root_category)
        #
        try:
            categories = obj._get_pg_categories()
            self._create_pg_categories(categories)
        except NotImplementedError:
            print('NotImplementedError: obj._get_pg_categories()')
            print(obj, obj.uid)
            categories = None
            #
        try:
            properties = obj._get_pg_properties()
        except NotImplementedError:
            print('NotImplementedError: obj._get_pg_properties()')
            print(obj, obj.uid)
            properties = obj._ATTRIBUTES
            # for key, key_props in od.items():
            #    property_ = _get_pg_property(obj.uid, key, key_props)
            #    self.view.Append(property_)

        #

        #
        for key, key_props in properties.items():
            try:
                property_ = _get_pg_property(obj.uid, key, key_props)

                if property_ is None:
                    print('property_ is None:', key, key_props)

                if key_props.get('category'):
                    category = self.view.GetProperty(key_props['category'])
                    if category is None:
                        raise Exception('Category not found:', key_props['category'])
                    self.view.AppendIn(category, property_)
                else:
                    self.view.Append(property_)
                #

                """
                if key_props.get('getter_func') and \
                                                key_props.get('listening'):
                    for obj_uid, obj_key in key_props.get('listening'):
                        print('\nobj_uid:', obj_uid)
                        print('obj_key:', obj_key)
                        obj = self._get_object(obj_uid)     
                        obj.subscribe(self.refresh_property, 
                                  'change.' + obj_key)
                        #self._fake_properties[key] = property_
                else:
                """
                # self._properties[key] = property_
                obj.subscribe(self.refresh_property, 'change.' + key)

            except Exception as e:
                print('\nERRO loading properties:', obj, key, key_props, e)
                raise

    def remove_properties(self, obj_uid):
        #        print('\n\n\nRemoving ALL properties for:', obj_uid)
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.uid)
        parent_controller = UIM.get(parent_controller_uid)
        # TODO: Retirar isso daqui...
        if parent_controller.view.splitter.IsSplit():
            parent_controller.view.splitter.Unsplit(self.view)
            #
        #        if self._properties:
        obj = self._get_object(obj_uid)

        # print('self.view.GetPropertyValues():', self.view.GetPropertyValues())

        for key, value in self._properties.items():
            obj.unsubscribe(self.refresh_property, 'change.' + key)

        #        self._properties.clear()
        self.view.Clear()

    #        print('Removed properties for:', obj_uid, ' OK!')

    def refresh_property(self, new_value, old_value, topicObj=pub.AUTO_TOPIC):
        """
        Refresh a property, when it is changed.
        """
        key = topicObj.getName().split('.')[-1]
        prop = self.view.GetPropertyByName(key)
        # print('refresh_property:', new_value, old_value, key, topicObj, prop)
        # print('self.view.GetPropertyKeys():', self.view.GetPropertyValues().keys())
        self.view.RefreshProperty(prop)


class PropertyGridView(UIViewObject, pg.PropertyGrid):
    tid = 'property_grid_view'

    def __init__(self, controller_uid):
        try:
            UIViewObject.__init__(self, controller_uid)
            UIM = UIManager()
            parent_controller_uid = UIM._getparentuid(self._controller_uid)
            parent_controller = UIM.get(parent_controller_uid)
            wx_parent = parent_controller._get_wx_parent(self.tid)
            pg.PropertyGrid.__init__(self, wx_parent,
                                     style=pg.PG_SPLITTER_AUTO_CENTER  # |\
                                     # pg.PG_HIDE_MARGIN
                                     )
            self.SetMarginColour('white')
            self.SetCaptionBackgroundColour(BLUE_COLORS_SCALE[2])
            self.SetCaptionTextColour('white')


        except Exception as e:
            print('ERRO PropertyGridView.__init__:', e)
