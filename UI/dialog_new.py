# -*- coding: utf-8 -*-

import wx
import weakref
from wx.lib.pubsub import pub

from collections import OrderedDict

GRIPY_ICON_PATH = 'icons/logo-transp.ico'


"""
Add(self, item, int proportion=0, int flag=0, int border=0,
    PyObject userData=None) -> wx.SizerItem

Appends a child item to the sizer.
"""
item_sizer_keys = ['proportion', 'flag', 'border', 'userData']
#
"""
__init__(self, Window parent, int id=-1, String label=EmptyString, 
    Point pos=DefaultPosition, Size size=DefaultSize, 
    long style=0, String name=StaticBoxNameStr) -> StaticBox
"""
static_box_keys =  ['id', 'label', 'pos', 'size', 'style', 'name']
#
"""
__init__(self, Window parent, int id=-1, Point pos=DefaultPosition, 
    Size size=DefaultSize, long style=wxTAB_TRAVERSAL|wxNO_BORDER, 
    String name=PanelNameStr) -> Panel
"""
panel_keys =  ['id', 'pos', 'size', 'style', 'name']
#
staticboxsizer_keys =  ['orient']
boxsizer_keys =  ['orient']
gridsizer_keys = ['rows', 'cols', 'vgap', 'hgap']
flexgridsizer_keys = ['rows', 'cols', 'vgap', 'hgap']
gridbagsizer_keys = ['vgap', 'hgap']
#
wx_statictext_keys =  ['label']
wx_spinctrl_keys = ['id', 'value', 'pos', 'size', 'style', 'min', 'max', 
                    'initial', 'name']
wx_textctrl_keys = ['id', 'value', 'pos', 'size', 'style', 'validator', 'name']
wx_choice_keys = ['id', 'value', 'pos', 'size', 'choices', 'style', 
                  'validator', 'name']
wx_listbox_keys = ['id', 'value', 'pos', 'size', 'choices', 'style', 
                   'validator', 'name']

wx_filepickerctrl_keys = ['id', 'path', 'message', 'wildcard', 'pos', 'size', 
                          'style', 'validator', 'name']



registered_widgets = {
    wx.StaticText: wx_statictext_keys,
    wx.SpinCtrl: wx_spinctrl_keys,
    wx.TextCtrl: wx_textctrl_keys,
    wx.Choice: wx_choice_keys,
    wx.ListBox: wx_listbox_keys,
    wx.FilePickerCtrl: wx_filepickerctrl_keys
}



widget_special_keys = ['initial', 'listening', 'widget_name']

#
def get_control_keys(control_class):
    if registered_widgets.has_key(control_class):
        return registered_widgets.get(control_class)
    raise Exception('Unregistered class')   
#
def pop_registers(keys, kwargs):
    ret = {}
    for key in keys:
        if kwargs.get(key) is not None:
            ret[key] = kwargs.pop(key)
    #for key in special_keys:        
    #    if kwargs.get(key) is not None:
    #        ret[key] = kwargs.pop(key)             
    return ret, kwargs


def pop_widget_registers(keys, kwargs):
    ctrl_dict = {}
    special_dict = {}
    for key in keys:
        if kwargs.get(key) is not None:
            ctrl_dict[key] = kwargs.pop(key)
    for key in widget_special_keys:        
        if kwargs.get(key) is not None:
            special_dict[key] = kwargs.pop(key)             
    return ctrl_dict, special_dict, kwargs


class DialogPool(object):
    _objects = weakref.WeakValueDictionary()
    _dialog_controls = weakref.WeakKeyDictionary()
    
    @classmethod
    def register(cls, dialog, enc_control):
        if not isinstance(dialog, Dialog):
            raise Exception('Must inform a Dialog instance.')
        if not isinstance(enc_control, EncapsulatedControl):
            raise Exception('Cannot register a non EncapsulatedControl object.')
        if cls._objects.get(enc_control.name) is not None:
            raise Exception('Object already registered.')
        cls._objects[enc_control.name] = enc_control
        if cls._dialog_controls.get(dialog) is None:
            cls._dialog_controls[dialog] = []
        cls._dialog_controls.get(dialog).append(enc_control)    
        
    @classmethod
    def get_object(cls, object_name):        
        return cls._objects.get(object_name)

    @classmethod
    def get_dialog_objects(cls, dialog):
        return cls._dialog_controls.get(dialog)
        
    @classmethod
    def reset(cls):
        cls._objects = weakref.WeakValueDictionary()
        cls._dialog_controls = weakref.WeakKeyDictionary()


class EncapsulatedControl(object):
    
    def __init__(self, *args, **kwargs):
        parent = args[0]
        if not self._control_class in registered_widgets.keys():   
            raise Exception('Unregistered class')  
            
        #print '\n\nargs:', args    
        special_kw = args[1]    
        #print '\nkwargs:', kwargs    
        
        if special_kw.get('widget_name') is not None:
            self.name = special_kw['widget_name']
        else:
            self.name = None #DialogPool.generate_name(self)
            
        if special_kw.get('initial'):
            initial = special_kw['initial']
        else:
            initial = None      
            
        print initial, self._control_class    
            
        if special_kw.get('listening') is not None:
            self.listening = special_kw['listening']
        else:
            self.listening = None        
        self.control = self._control_class(parent, **kwargs)   
        pub.subscribe(self.check_change, 'widget_changed')    
        
        if initial is not None:
            self.set_value(initial)
                      
        
    def check_change(self, name):
        if not self.listening: return
        names, _function = self.listening    
        if name not in names: return           
        kwargs = {}
        for name in names:
            enc_control = DialogPool.get_object(name)
            try:
                kwargs[enc_control.name] = enc_control.get_value()
            except:
                raise
        _function(**kwargs)
      
        
    def on_change(self, event):
        pub.sendMessage('widget_changed', name=self.name)      
      
    def set_value(self, value):
        raise NotImplementedError()         
  
    def get_value(self):
        raise NotImplementedError()
        

class EncapsulatedChoice(EncapsulatedControl):
    _control_class = wx.Choice    
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedChoice, self).__init__(*args, **kwargs)            
        self.control.Bind(wx.EVT_CHOICE, self.on_change)

    def set_value(self, value):
        self.control.Clear()
        if not value:
            self._map = None
        else:
            self._map = value
            self.control.AppendItems(self._map.keys())       
        # To force on_change                  
        self.on_change(None)           

    def get_value(self):
        if not self._map:
            return None
        if self.control.GetSelection() == -1:
            return None
        return self._map[self.control.GetString(self.control.GetSelection())]    
            

class EncapsulatedTextCtrl(EncapsulatedControl):
    _control_class = wx.TextCtrl
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedTextCtrl, self).__init__(*args, **kwargs)           

    def set_value(self, value):
        if value is None:
            self.control.SetValue(wx.EmptyString)
        else:
            self.control.SetValue(str(value))
   
    def get_value(self):
        return self.control.GetValue()
        


class EncapsulatedFilePickerCtrl(EncapsulatedControl):
    _control_class = wx.FilePickerCtrl
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedFilePickerCtrl, self).__init__(*args, **kwargs)    
        
    def set_value(self, value):
        self.control.SetPath(value)

    def get_value(self):
        return self.control.GetPath()



class EncapsulatedSpinCtrl(EncapsulatedControl):
    _control_class = wx.SpinCtrl
    
    def __init__(self, *args, **kwargs):
        #if kwargs.get('initial'):
        #    if kwargs.get('initial') > 100:
        #        kwargs['max'] = kwargs.get('initial')
        super(EncapsulatedSpinCtrl, self).__init__(*args, **kwargs)      
        print self.control.GetValue()
        self.control.Bind(wx.EVT_SPINCTRL, self.on_change)

    def set_value(self, value):
        if value is not None:
            #print 'spin =', value, type(value)
            self.control.SetValue(value)
   
    def get_value(self):
        #print 'spin:', self.control.GetValue()
        return self.control.GetValue()
   
     
class EncapsulatedStaticText(EncapsulatedControl):
    _control_class = wx.StaticText
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedStaticText, self).__init__(*args, **kwargs)            

    def set_value(self, value):
        if value is not None:
            self.control.SetLabel(str(value))
   
    def get_value(self):
        return self.control.GetLabel()


class EncapsulatedListBox(EncapsulatedControl):
    _control_class = wx.ListBox 
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedListBox, self).__init__(*args, **kwargs)             
        self.control.Bind(wx.EVT_LISTBOX, self.on_change)

    def set_value(self, value):
        self.control.Clear()
        if not value:
            self._map = None
        else:
            self._map = value
            print '\nself.control.AppendItems:', self._map.keys(), type(self._map.keys()), self.control, '\n'
            self.control.AppendItems(self._map.keys())       
            #self.control.Set(self._map.keys())       
        # To force on_change                  
        self.on_change(None)           

    def get_value(self):
        if not self._map:
            return None
        if not self.control.GetSelections():
            return None
        return [self._map.get(self.control.GetString(sel)) for sel in self.control.GetSelections()]   


class Dialog(wx.Dialog):   

    def __init__(self, *args, **kwargs): 
        flags = wx.OK|wx.CANCEL
        if kwargs.get('flags') is not None:
            flags = kwargs.pop('flags')
        super(Dialog, self).__init__(*args, **kwargs)
        try:
            self.SetIcon(wx.Icon(GRIPY_ICON_PATH, wx.BITMAP_TYPE_ICO))
        except:
            pass
        dialog_box = wx.BoxSizer(wx.VERTICAL) 
        self.SetSizer(dialog_box) 
        self.mainpanel = self.AddBoxSizerContainer(self, proportion=1, 
                            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10
        )
        button_sizer = self.CreateButtonSizer(flags)
        dialog_box.Add(button_sizer, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)    
        dialog_box.Layout()         

    def _AddContainer(self, container_class, *args, **kwargs):
        if not args:
            parent = self.mainpanel
        else:
            parent = args[0]
        item_sizer_kw, kwargs = pop_registers(item_sizer_keys, kwargs)
        container = container_class(parent, **kwargs)
        if container_class == StaticBoxContainer:
            parent.GetSizer().Add(container.GetSizer(), **item_sizer_kw)
        else:    
            parent.GetSizer().Add(container, **item_sizer_kw)
        parent.GetSizer().Layout()
        return container

    def AddBoxSizerContainer(self, *args, **kwargs):
        return self._AddContainer(BoxSizerContainer, *args, **kwargs)
        
    def AddGridSizerContainer(self, *args, **kwargs):
        return self._AddContainer(GridSizerContainer, *args, **kwargs)     

    def AddFlexGridSizerContainer(self, *args, **kwargs):
        return self._AddContainer(FlexGridSizerContainer, *args, **kwargs)
        
    def AddGridBagSizerContainer(self, *args, **kwargs):
        return self._AddContainer(GridBagSizerContainer, *args, **kwargs)    

    def AddStaticBoxContainer(self, *args, **kwargs):
        return self._AddContainer(StaticBoxContainer, *args, **kwargs)
                 
    def AddWarpSizerContainer(self, *args, **kwargs):
        return self._AddContainer(WarpSizerContainer, *args, **kwargs)                 
                 
    def CreateControl(self, enc_class, container, **kwargs):
        # Create and Add a new control.
        keys = get_control_keys(enc_class._control_class)
        controlkw, specialkw, kwargs = pop_widget_registers(keys, kwargs)
        #print '\ncontrolkw:', controlkw
        #print 'specialkw:', specialkw
        #print 'kwargs:', kwargs
        print enc_class
        enc_control = enc_class(container, specialkw, **controlkw)
        if enc_control.name:
            DialogPool.register(self, enc_control)
        container.GetSizer().Add(enc_control.control, **kwargs)
        container.GetSizer().Layout()

    def AddChoice(self, *args, **kwargs):
        self.CreateControl(EncapsulatedChoice, args[0], **kwargs)

    def AddTextCtrl(self, *args, **kwargs):
        self.CreateControl(EncapsulatedTextCtrl, args[0], **kwargs)

    def AddFilePickerCtrl(self, *args, **kwargs):
        self.CreateControl(EncapsulatedFilePickerCtrl, args[0], **kwargs)

    def AddSpinCtrl(self, *args, **kwargs):
        self.CreateControl(EncapsulatedSpinCtrl, args[0], **kwargs)
        
    def AddStaticText(self, *args, **kwargs):
        self.CreateControl(EncapsulatedStaticText, args[0], **kwargs)        

    def AddListBox(self, *args, **kwargs):
        self.CreateControl(EncapsulatedListBox, args[0], **kwargs)        

    def Destroy(self):
        DialogPool.reset()
        super(Dialog, self).Destroy()

    def get_results(self):
        ret = {}
        if not DialogPool.get_dialog_objects(self): 
            return ret
        for widget in DialogPool.get_dialog_objects(self):
            ret[widget.name] = widget.get_value()
        return ret    


class PanelContainer(wx.Panel):
    
    def __init__(self, *args, **kwargs): 
        if not kwargs.get('sizer_class'):
            raise Exception()    
        sizer_class = kwargs.pop('sizer_class')
        panel_kw, sizer_kw = pop_registers(panel_keys, kwargs)
        wx.Panel.__init__(self, args[0], **panel_kw)
        try:
            sizer = sizer_class(**sizer_kw)
            self.SetSizer(sizer)    
        except:
            raise        
    
class BoxSizerContainer(PanelContainer):
    
    def __init__(self, *args, **kwargs): 
        if not kwargs:
            kwargs = {
                'sizer_class': wx.BoxSizer,
                'orient': wx.VERTICAL
            }
        else:
            kwargs['sizer_class'] = wx.BoxSizer
            if not kwargs.get('orient'):
                kwargs['orient'] = wx.VERTICAL
            elif kwargs.get('orient') not in [wx.HORIZONTAL, wx.VERTICAL]:
                raise Exception() 
        super(BoxSizerContainer, self).__init__(*args, **kwargs)


class GridSizerContainer(PanelContainer):
    
    def __init__(self, *args, **kwargs): 
        if not kwargs:
            kwargs = {'sizer_class': wx.GridSizer}
        else:
            kwargs['sizer_class'] = wx.GridSizer
        super(GridSizerContainer, self).__init__(*args, **kwargs)   


class GridBagSizerContainer(PanelContainer):
    def __init__(self, *args, **kwargs): 
        if not kwargs:
            kwargs = {'sizer_class': wx.GridBagSizer}
        else:
            kwargs['sizer_class'] = wx.GridBagSizer
        super(GridBagSizerContainer, self).__init__(*args, **kwargs)          
      
      
class FlexGridSizerContainer(PanelContainer):
    
    def __init__(self, *args, **kwargs): 
        if not kwargs:
            kwargs = {'sizer_class': wx.FlexGridSizer}
        else:
            kwargs['sizer_class'] = wx.FlexGridSizer
        super(FlexGridSizerContainer, self).__init__(*args, **kwargs)    


class WarpSizerContainer(PanelContainer):
    
    def __init__(self, *args, **kwargs): 
        if not kwargs:
            kwargs = {
                'sizer_class': wx.WarpSizer,
                'orient': wx.VERTICAL
            }
        else:
            kwargs['sizer_class'] = wx.BoxSizer
            if not kwargs.get('orient'):
                kwargs['orient'] = wx.VERTICAL
            elif kwargs.get('orient') not in [wx.HORIZONTAL, wx.VERTICAL]:
                raise Exception() 
        super(WarpSizerContainer, self).__init__(*args, **kwargs)


class StaticBoxContainer(wx.StaticBox):
    
    def __init__(self, *args, **kwargs): 
        sbkw, kwargs = pop_registers(static_box_keys, kwargs)
        wx.StaticBox.__init__(self, args[0], **sbkw)
        if kwargs.get('orient') is None:
            orient = wx.VERTICAL
        else:    
            orient = kwargs.pop('orient')  
        self._sizer = wx.StaticBoxSizer(self, orient)       
 
    def GetSizer(self):        
        return self._sizer