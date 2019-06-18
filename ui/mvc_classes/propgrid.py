# -*- coding: utf-8 -*-

from collections import OrderedDict

import wx
import wx.propgrid as pg 
from wx.adv import OwnerDrawnComboBox 

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject                                  
import app.pubsub as pub
from app.app_utils import MPL_COLORS, MPL_COLORMAPS


from ui.mvc_classes.wxgripy import FrameController
from ui.mvc_classes.wxgripy import Frame


from pubsub.core.topicexc import MessageDataSpecError

###############################################################################
###############################################################################


class GripyPgProperty(object):
    
    def __init__(self, obj_uid, obj_attr):
        self._obj_uid = obj_uid
        self._obj_attr = obj_attr
        
    def _get_object(self):
        app = wx.App.Get()
        Manager = app.get_manager_class(self._obj_uid[0])
        manager = Manager()
        obj = manager.get(self._obj_uid)
        return obj

    def _get_value(self):
        obj = self._get_object()
        return obj[self._obj_attr]

    def _set_value(self, value):
        try:
            obj = self._get_object()     
            obj[self._obj_attr] = value   
            return True
        except:
            return False

    def ValueToString(self, *args):
        return str(self._get_value())

    def StringToValue(self, variant, text, flag):
        return self._set_value(text)  



class StringProperty(pg.StringProperty, GripyPgProperty):    

    def __init__(self, obj_uid, obj_attr, 
                                 label=pg.PG_LABEL, name=pg.PG_LABEL):
        
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.StringProperty.__init__(self, label, name)
        
        

class IntProperty(pg.IntProperty, GripyPgProperty):    

    def __init__(self, obj_uid, obj_attr, 
                                 label=pg.PG_LABEL, name=pg.PG_LABEL):
        
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.IntProperty.__init__(self, label, name)


    """
    def ValueToString(self, *args):
        return str(self._get_value())

    def StringToValue(self, variant, text, flag):
        return self._set_value(text)  
    """
        #pg.Append( wxpg.IntProperty("IntWithSpin",value=256) )
        #pg.SetPropertyEditor("IntWithSpin", "SpinCtrl")    
    
    
class FloatProperty(pg.FloatProperty, GripyPgProperty):     

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL, name=pg.PG_LABEL):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.FloatProperty.__init__(self, label, name)


    def ValueToString(self, *args):
#        print('FloatProperty.ValueToString:', str(self._get_value()))
        return str(self._get_value())


    def StringToValue(self, variant, text, flag):
#        print('FloatProperty.StringToValue:', self._obj_attr, text)
        return self._set_value(text)  


    """
    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller[self._obj_attr]
        return str(value)


    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller[self._obj_attr] = text
        return True    

    """




class BoolProperty(pg.BoolProperty, GripyPgProperty):   

    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL, name=pg.PG_LABEL):
        GripyPgProperty.__init__(self, obj_uid, obj_attr)
        pg.BoolProperty.__init__(self, label, name)
        self.SetAttribute("UseCheckbox", 1)
        self.SetAttribute("UseDClickCycling", 1)
        value = self._get_value()
        self.SetValue(value)
        
    """
    def ValueToString(self, *args):
        value = self._get_value()
        return str(value)
    """
    
    def OnSetValue(self):
        self._set_value(self.GetValue())


            
    
class EnumProperty(pg.EnumProperty, GripyPgProperty):    
 
    
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL, name=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        
        if opt_labels is None:
            raise Exception('No options labels values found in: {} - model key: {}'.\
                            format(obj_uid, obj_attr)
            )   
            
            
#        print('\n\nCriando EnumProperty para:' + obj_attr)    
#        print('Prop label:', label, type(label))
#        print('Prop name:', name, type(name))
#        print('Opt labels:', opt_labels, type(opt_labels))
#        print('Opt values:', opt_values, type(opt_values))
#        print('Values:', values, type(values))
#        print('Value', value, type(value))
        
        
        
        if values is None:
            values = list(range(len(opt_labels)))
#            print('VALUES WAS NONE.')
#            print('NEW VALUES IS:' + str(values), type(values))
#        else:
#            print('VALUES OK.')
        
        
        try:
            
            GripyPgProperty.__init__(self, obj_uid, obj_attr)
            pg.EnumProperty.__init__(self, label, name, opt_labels, values, value=value)    
            
            
            #super(EnumProperty, self).__init__(label, name, labels, values, value=value)
            
            #pg.EnumProperty(label, name, labels, values, value)
            # EnumProperty(label, name, choice, value=0)  choice as wxPGChoices
            #              
            # EnumProperty(label, name, labels=[], values=[], value=0)
            # labels - list of strings
            # values - list of integers
            
            #wxEnumProperty(const  ::wxString& label,const  ::wxString& name, 
            #                ::wxPGChoices& choices,int value)
            
            #
            self._opt_labels = opt_labels
            self._opt_values = opt_values        
            if self._opt_values is None:
                self._opt_values = opt_labels
            #
            self._values = values
            #
            val = self._get_value()
            #
#            print('val:', val)
            
            try:
                idx = self._opt_values.index(val)
            except ValueError:
                raise
            #    
#            print('idx:', idx)
            
#            self.SetValue(idx)
            self.SetValue(val)
            
        except Exception as e:
            print('\n\n\nDEU RUIM!!!! - {}\n\n\n'.format(e))
            raise
        
        
    def IntToValue(self, variant, int_value, flag):
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
#        print('\nIntToValue [{}]: {} - {}'.format(self._obj_attr, int_value, type(int_value)))

        #val = self._values[int_value]
        #print('val:', val, type(val))
        
        # This is the actual value
        opt_value = self._opt_values[int_value]
#        print('actual_value:', opt_value, type(opt_value))
        #
        ret_val = self._set_value(opt_value)
        return ret_val
        

    def ValueToString(self, value, flag):
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
        print('\nValueToString [{}]: {} - {}'.format(self._obj_attr, value, type(value)))
        val = self._get_value()
        
        print('val:', val, type(val))
        
        if isinstance(val, int):
            idx_val = self._opt_values.index(val)
            print('idx_val:', idx_val)
            ret_str = str(self._opt_labels[idx_val])
            #ret_str = str(self._opt_labels[val])
        elif isinstance(val, str): 
            ret_str = val
            
            
        print('Retornando String \"' + ret_str + '\" para Value: ' + str(val))
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
        
        
        print('\nGetIndexForValue [{}]: {} - {}'.format(self._obj_attr, value, type(value)))

#        idx = self._opt_values.index(value)
#        """

        val = self._get_value()
        
        print('val:', val, type(val))

       
        idx = self._opt_values.index(val)
        
        """
        try:
            print(1)
            idx = self._values.index(value)
        except ValueError:
            try:
                print(2)
                idx = self._opt_values.index(value)
            except:
                raise   
        """
        
#        """
        
        print('Retornando Index', idx, 'para Value:', value, 'para val:', val)
        
        return idx






class DynamicEnumProperty(pg.EnumProperty):    
 
    def __init__(self, callback, 
                 label=pg.PG_LABEL, name=pg.PG_LABEL, labels=[], 
                 values=None, value=0):
        if labels is None:
            raise Exception('No labels values found.')
        super(DynamicEnumProperty, self).__init__(label, name, labels, value=value)
        self._callback = callback
        self._labels = labels
        if not values:
            self._values = labels
        else:    
            self._values = values
        wx.CallAfter(self.IntToValue, None, value, None)
        
    def IntToValue(self, variant, int_value, flag):
        self._value = int_value
        value = self._values[self._value]
        self._callback(value)
        return True
        
    def ValueToString(self, value, flag):
        return self._labels[self._value]    
        


class MPLColorsProperty(EnumProperty):    
    
    def __init__(self, obj_uid, obj_attr, label=pg.PG_LABEL, name=pg.PG_LABEL,
                 opt_labels=[], opt_values=None, values=None, value=0):
        
        super().__init__(obj_uid, obj_attr, label=label, name=name,
                                            opt_labels=list(MPL_COLORS.keys()))





def _get_pg_property(obj_uid, obj_attr, obj_attr_props):

    if obj_attr_props.get('label') is None:
        obj_attr_props['label'] = obj_attr
        #raise Exception('No label found in: {} - model key: {}'.format(obj_uid, \
        #                                                            obj_attr))  
    #if obj_attr_props.get('pg_property') is None:
    #    return None

    enable = obj_attr_props.get('enabled', True)
    prop = None
    if obj_attr_props.get('pg_property') == 'IntProperty':
        prop = IntProperty(obj_uid, obj_attr, 
                                           label=obj_attr_props.get('label')
        )
    elif obj_attr_props.get('pg_property') == 'FloatProperty':
        prop = FloatProperty(obj_uid, obj_attr, 
                                             label=obj_attr_props.get('label')
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
    elif obj_attr_props.get('pg_property') == 'BoolProperty':
        prop = BoolProperty(obj_uid, obj_attr, 
                            label=obj_attr_props.get('label')
        )   
        
    elif obj_attr_props.get('pg_property') == 'StringProperty' or \
                                            obj_attr_props.get('type') == str:
        prop = StringProperty(obj_uid, obj_attr, 
                                           label=obj_attr_props.get('label')
        )
    if prop is not None:
        prop.Enable(enable)
        return prop
    else:             
        raise Exception(' _get_pg_property:', obj_uid, obj_attr, obj_attr_props)





class PropertyGridController(UIControllerObject):
    tid = 'property_grid_controller'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['obj_uid'] = {
        'default_value': None,
        'type': 'uid'
    }      

    def __init__(self, **state):
        super().__init__(**state)  
        print('\n\nPropertyGridController.__init__:', state)
        self._properties = OrderedDict()
        self.subscribe(self.on_change_obj_uid, 'change.obj_uid') 
       
    def PostInit(self):
        if self.obj_uid is not None:
            self.on_change_obj_uid(self.obj_uid, None)
                   
    def _get_object(self, obj_uid=None):
        if obj_uid is None:
            obj_uid = self.obj_uid
        app = wx.App.Get()
        Manager = app.get_manager_class(obj_uid[0])
        manager = Manager()
        obj = manager.get(obj_uid)
        return obj
        

    def on_change_obj_uid(self, new_value, old_value):
        if old_value is not None:
            self.remove_properties(old_value)
        obj = self._get_object() 
        title = obj.get_friendly_name()
        self.view.Append(pg.PropertyCategory(title, name='title'))
        #
        try:
            od = obj._get_pg_properties_dict()
        except:
            od = obj._ATTRIBUTES
        #    
        #print('on_change_obj_uid:', od)
        #
        for key, key_props in od.items():
            try:
                property_ = _get_pg_property(obj.uid, key, key_props)
                self._properties[key] = property_
                self.view.Append(property_)
                obj.subscribe(self.refresh_property, 'change.' + key)     
            except Exception as e:
                print ('\nERRO loading properties:', obj.name, 
                       key, key_props, e
                )
                pass        


    def remove_properties(self, obj_uid):        
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self.uid)
        parent_controller =  UIM.get(parent_controller_uid)
        if parent_controller.view.splitter.IsSplit():  
            parent_controller.view.splitter.Unsplit(self.view)  
        #             
        if self._properties: 
            obj = self._get_object(obj_uid)
            for key in self._properties.keys():
                obj.unsubscribe(self.refresh_property, \
                                          'change.' + key
                )                     
        self._properties.clear()
        self.view.Clear()
       
        
    """    
    def set_object_uid(self, toc_obj_uid): 
        if toc_obj_uid == self.obj_uid:
            self.view.Refresh()
            return
        UIM = UIManager()    
        if toc_obj_uid[0] != 'track_object_controller':
            raise Exception('Cannot set an object with tid != "track_object_controller"')
        toc = UIM.get(toc_obj_uid)
        if not toc.is_valid():
            return  
    
        self.clear()
        
        OM = ObjectManager()
        obj = OM.get(toc.obj_uid)
        title = obj.get_friendly_name()
        #title = toc.get_object()._get_tid_friendly_name() + ': ' + \
        #                                            toc.get_object().name
        self.view.Append(
            pg.PropertyCategory(title, name='title')
        )
        
        repr_ctrl = toc.get_representation()

        print()
        print(repr_ctrl._ATTRIBUTES.items(), type(repr_ctrl._ATTRIBUTES.items()))
        print()
        
        for key, key_props in repr_ctrl._ATTRIBUTES.items():
            print('\n', repr_ctrl.uid, key, key_props)
            
            try:
                property_ = _get_pg_property(repr_ctrl.uid, key, key_props)

                self._properties[key] = property_
                self.view.Append(property_)
                repr_ctrl.subscribe(self.refresh_property, 'change.' + key)
                
            except:
                pass

        self.obj_uid = toc_obj_uid
    """
        
        
    #def refresh_property(self, topicObj=pub.AUTO_TOPIC, new_value=None, old_value=None):
    def refresh_property(self, new_value, old_value, topicObj=pub.AUTO_TOPIC):
        """
        Refresh a property, when it is changed.
        """
        key = topicObj.getName().split('.')[-1]
        prop = self._properties[key]
        self.view.RefreshProperty(prop)



class PropertyGridView(UIViewObject, pg.PropertyGrid):
    tid = 'property_grid_view'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)      
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        wx_parent = parent_controller._get_wx_parent(self.tid)
        #
        pg.PropertyGrid.__init__(self, wx_parent, 
                        style=pg.PG_SPLITTER_AUTO_CENTER|pg.PG_HIDE_MARGIN
        )
        #
        self.SetCaptionBackgroundColour(wx.Colour(0, 128, 192))
        self.SetCaptionTextColour('white')       

