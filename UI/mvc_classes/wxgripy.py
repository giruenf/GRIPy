# -*- coding: utf-8 -*-
import wx

from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 

from wx.lib.pubsub import pub
from collections import OrderedDict

from App import log


###############################################################################
###############################################################################


class TopLevelController(UIControllerBase):
    tid = 'toplevel_controller'
         
    def __init__(self):
        super(TopLevelController, self).__init__()


class TopLevelModel(UIModelBase):
    tid = 'toplevel_model'
    
    _ATTRIBUTES = {
        'title': {'default_value': wx.EmptyString, 
                  'type': str
        },
        # TODO: Use icon from App parameters          
        'icon': {'default_value': './icons/logo-transp.ico',
                 'type': str
        },
        'style': {'default_value': wx.DEFAULT_FRAME_STYLE, 
                  'type': int        
        },
        'maximized': {'default_value': False,  
                      'type': bool
        },
        'size': {'default_value': wx.Size(800, 600), 
                 'type': wx.Size
        },
        'pos': {'default_value': wx.Point(50, 50), 
                'type': wx.Point
        }
    }    
    
    def __init__(self, controller_uid, **base_state):     
        super(TopLevelModel, self).__init__(controller_uid, **base_state)


class TopLevel(UIViewBase):
    tid = 'toplevel'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        # MainWindow subscribing MainWindowController PubSub messages
        controller.subscribe(self._set_maximized, 'change.maximized')
        controller.subscribe(self._set_size, 'change.size')
        controller.subscribe(self._set_position, 'change.pos')
        #
        # little hack - on_size
        self._flag = False
        
    def on_maximize(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model.set_value_from_event('maximized', self.IsMaximized())

    def on_move(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model.set_value_from_event('pos', self.GetPosition())

    def on_size(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        self._flag = True
        controller.model.size = event.GetSize()
        self._flag = False
        controller.model.set_value_from_event('maximized', self.IsMaximized())
        event.Skip()
  
    def _set_maximized(self, new_value, old_value):  
        self.Unbind(wx.EVT_MAXIMIZE, handler=self.on_maximize)  
        self.Maximize(new_value)
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)  
    
    def _set_size(self, new_value, old_value):
        if not self._flag:
            self.Unbind(wx.EVT_SIZE, handler=self.on_size)
            self.SetSize(new_value)
            self.Bind(wx.EVT_SIZE, self.on_size)    
    
    def _set_position(self, new_value, old_value):  
        self.Unbind(wx.EVT_MOVE, handler=self.on_move) 
        self.SetPosition(new_value)
        self.Bind(wx.EVT_MOVE, self.on_move)  


###############################################################################
###############################################################################


class FrameController(TopLevelController):
    tid = 'frame_controller'
         
    def __init__(self):
        super(FrameController, self).__init__()


class FrameModel(TopLevelModel):
    tid = 'frame_model'
        
    def __init__(self, controller_uid, **base_state):      
        super(FrameModel, self).__init__(controller_uid, **base_state)


class Frame(TopLevel, wx.Frame):
    tid = 'frame'

    def __init__(self, controller_uid):
        TopLevel.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        parent_uid = UIM._getparentuid(self._controller_uid)
        parent_obj = UIM.get(parent_uid)
        if not parent_obj:
            parent_view = None
        else:
            parent_view = parent_obj.view
        #
        wx.Frame.__init__(self, parent_view, wx.ID_ANY, controller.model.title,
            pos=controller.model.pos, size=controller.model.size, 
            style=controller.model.style              
        ) 
        if controller.model.icon:   
            self.icon = wx.Icon(controller.model.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.model.maximized:
            self.Maximize()   
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)    


###############################################################################
###############################################################################

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

wx_checkbox_keys = ['id', 'label', 'value', 'pos', 'size', 'style', 'validator', 'name']

wx_radiobutton_keys = ['id', 'label', 'pos', 'size', 'style', 'validator', 'name']


registered_widgets = {
    wx.StaticText: wx_statictext_keys,
    wx.SpinCtrl: wx_spinctrl_keys,
    wx.TextCtrl: wx_textctrl_keys,
    wx.Choice: wx_choice_keys,
    wx.ListBox: wx_listbox_keys,
    wx.FilePickerCtrl: wx_filepickerctrl_keys,
    wx.CheckBox: wx_checkbox_keys,
    wx.RadioButton: wx_radiobutton_keys
}


widget_special_keys = ['initial', 'widget_name', 'options', 'controller_uid']

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
    #print 'pop_widget_registers:', keys, kwargs
    ctrl_dict = {}
    special_dict = {}
    for key in keys: 
        if key in kwargs.keys():
            ctrl_dict[key] = kwargs.pop(key)
    for key in widget_special_keys:        
        if key in kwargs.keys():
            special_dict[key] = kwargs.pop(key)   
    return ctrl_dict, special_dict, kwargs



class EncapsulatedControl(object):
    
    def __init__(self, *args, **kwargs):
        self._trigger_func = None
        self._trigger_kwargs_keys = None
        parent = args[0]
        if not self._control_class in registered_widgets.keys():   
            raise Exception('Unregistered class')  
        special_kw = args[1]    
        self.name = special_kw.get('widget_name')
        initial = special_kw.get('initial')
        options = special_kw.get('options', {})
        self._controller_uid = special_kw.get('controller_uid')
        
        self.control = self._control_class(parent, **kwargs)  
        try:
            self.set_options(options)
        except:
            pass
        if initial is not None:
            self.set_value(initial)
        self.old_value = None


    def get_topic(self):
        UIM = UIManager()
        dialog = UIM.get(self._controller_uid)
        return self.name + '_widget_changed@' + dialog.view.get_topic()

   
    def set_trigger(self, func, *args):
        if not callable(func):
            raise Exception('A callable must be supplied.')
        self._trigger_func = func
        self._trigger_kwargs_keys = list(args)
        pub.subscribe(self.check_change, self.get_topic())  


    def unset_trigger(self):
        if not callable(self._trigger_func):
            return None
        pub.unsubscribe(self.check_change, self.get_topic())
        func = self._trigger_func
        self._trigger_func = None
        keys = self._trigger_kwargs_keys
        self._trigger_kwargs_keys = None
        return func, keys
            
         
    def check_change(self, name, old_value, new_value):
        if not callable(self._trigger_func):
            return
        kwargs = {}
        if self._trigger_kwargs_keys:
            UIM = UIManager()
            dialog = UIM.get(self._controller_uid)
            for enc_ctrl_name in self._trigger_kwargs_keys:
                enc_control = dialog.view.get_object(enc_ctrl_name)
                try:
                    kwargs[enc_control.name] = enc_control.get_value()
                except:
                    raise
        self._trigger_func(name, old_value, new_value, **kwargs)


    def on_change(self, event):
        new_value = self.get_value()
        pub.sendMessage(self.get_topic(), name=self.name,
                        old_value=self.old_value, new_value=new_value
        )     
        self.old_value = new_value
        
    def set_options(self, options_dict=None):
        raise NotImplementedError()     
    
    def set_value(self, value):
        raise NotImplementedError()         
  
    def get_value(self):
        raise NotImplementedError()
        

class EncapsulatedChoice(EncapsulatedControl):
    _control_class = wx.Choice    
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedChoice, self).__init__(*args, **kwargs)            
        self.control.Bind(wx.EVT_CHOICE, self.on_change)

    def set_options(self, options_dict=None):
        self.control.Clear()
        self._map = options_dict
        if self._map is not None:
            if not isinstance(self._map, OrderedDict):
                self._map = OrderedDict(self._map)
            self.control.AppendItems(self._map.keys())                       

    def set_value(self, value, event=False):
        if value is None:
            return
        if not isinstance(value, int):
            if not value in self._map.keys():
                raise Exception('')
            value = self._map.keys().index(value)   
        self.control.SetSelection(value)  
        if event:             
            self.on_change(None)    

    def get_value(self):
        if not self._map:
            return None
        if self.control.GetSelection() == -1:
            return None
        return self._map[self.control.GetString(self.control.GetSelection())]    
    
    def show(self):
        return self.control.Show()
    
    def hide(self):
        return self.control.Hide()
        
    def destroy(self):
        return self.control.Destroy()
            

class EncapsulatedRadioButton(EncapsulatedControl):
    _control_class = wx.RadioButton

    def __init__(self, *args, **kwargs):
        super(EncapsulatedRadioButton, self).__init__(*args, **kwargs)    
        self.control.Bind(wx.EVT_RADIOBUTTON, self.on_change)

    def set_value(self, value):
        self.control.SetValue(value)
   
    def get_value(self):
        return self.control.GetValue()


class EncapsulatedCheckBox(EncapsulatedControl):
    _control_class = wx.CheckBox

    def __init__(self, *args, **kwargs):
        super(EncapsulatedCheckBox, self).__init__(*args, **kwargs)    
        self.control.Bind(wx.EVT_CHECKBOX, self.on_change)

    def set_value(self, value):
        self.control.SetValue(value)
   
    def get_value(self):
        return self.control.GetValue()


class EncapsulatedTextCtrl(EncapsulatedControl):
    _control_class = wx.TextCtrl
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedTextCtrl, self).__init__(*args, **kwargs)    
        self.control.Bind(wx.EVT_TEXT, self.on_change)

    def set_value(self, value):
        if value is None:
            self.control.SetValue(wx.EmptyString)
        else:
            self.control.SetValue(str(value))
          
    def get_value(self):
        return self.control.GetValue().strip()
        
    def disable(self):
        return self.control.Disable()
        
    def enable(self):
        return self.control.Enable()
        
    def hide(self):
        return self.control.Hide()
    
    def show(self):
        return self.control.Show()
        
    def destroy(self):
        return self.control.Destroy()

class EncapsulatedFilePickerCtrl(EncapsulatedControl):
    _control_class = wx.FilePickerCtrl
    
    def __init__(self, *args, **kwargs):
        try:
            super(EncapsulatedFilePickerCtrl, self).__init__(*args, **kwargs)    
        except Exception as e:
            print e
        
        
    def set_value(self, value):
        self.control.SetPath(value)

    def get_value(self):
        return self.control.GetPath()



class EncapsulatedSpinCtrl(EncapsulatedControl):
    _control_class = wx.SpinCtrl
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedSpinCtrl, self).__init__(*args, **kwargs)      
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
        
    def hide(self):
        return self.control.Hide()
    
    def show(self):
        return self.control.Show()

    def destroy(self):
        return self.control.Destroy()
        
class EncapsulatedListBox(EncapsulatedControl):
    _control_class = wx.ListBox 
    
    def __init__(self, *args, **kwargs):
        super(EncapsulatedListBox, self).__init__(*args, **kwargs)             
        self.control.Bind(wx.EVT_LISTBOX, self.on_change)

    def set_value(self, value, event=True):
        self.control.Clear()
        if not value:
            self._map = None
        else:
            self._map = value
            self.control.AppendItems(self._map.keys())        
        # To force on_change    
        if event:              
            self.on_change(None)           

    def get_value(self):
        if not self._map:
            return None
        if not self.control.GetSelections():
            return None
        return [self._map.get(self.control.GetString(sel)) for sel in self.control.GetSelections()]   

###############################################################################
###############################################################################


class DialogController(TopLevelController):
    tid = 'dialog_controller'
         
    def __init__(self):
        super(DialogController, self).__init__()

    def PreDelete(self):
        pub.unsubAll(topicFilter=self._topic_filter)
        self.view._objects = {}
        try:
            self.view.Destroy()
        except:
            pass
    
    def _topic_filter(self, topic_name):
        return topic_name == '_widget_changed@' + self.view.get_topic()   
        #'_widget_changed@' + dialog.get_topic()
        
    def get_results(self):
        return self.view.get_results()
        

class DialogModel(TopLevelModel):
    tid = 'dialog_model'
    
    _ATTRIBUTES = {
        'flags': {
                'default_value': wx.OK|wx.CANCEL, 
                'type': int
        }
    }    
    _ATTRIBUTES.update(TopLevelModel._ATTRIBUTES) 
    _ATTRIBUTES['style'] = {
        'default_value': wx.DEFAULT_DIALOG_STYLE, 
        'type': int        
    }
    
    def __init__(self, controller_uid, **base_state):      
        super(DialogModel, self).__init__(controller_uid, **base_state) 
    
          
class Dialog(TopLevel, wx.Dialog):   
    tid = 'dialog'
    
    def __init__(self, controller_uid):
        TopLevel.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        wx.Dialog.__init__(self, None, wx.ID_ANY, controller.model.title,
            pos=controller.model.pos, size=controller.model.size, 
            style=controller.model.style              
        ) 
        self._objects = {}
        if controller.model.icon:   
            self.icon = wx.Icon(controller.model.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.model.maximized:
            self.Maximize()   
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)  
        dialog_box = wx.BoxSizer(wx.VERTICAL) 
        self.SetSizer(dialog_box) 
        self.mainpanel = self.AddCreateContainer('BoxSizer', self, proportion=1, 
                            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10
        )
        button_sizer = self.CreateButtonSizer(controller.model.flags)
        dialog_box.Add(button_sizer, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)    
        dialog_box.Layout()  

    def get_topic(self):
        return 'dialog_' + str(self._controller_uid[1])


    def _get_button(self, button_id):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if button_id & controller.model.flags:
            return self.FindWindow(button_id)
        return None

    def enable_button(self, button_id, enable=True):
        btn = self._get_button(button_id)
        btn.Enable(enable)

    def register(self, enc_control):
        if enc_control.name:
            self._objects[enc_control.name] = enc_control


    def AddContainer(self, container, *args, **kwargs):
        #print 'AddContainer:', args, kwargs
        for key in kwargs.keys():
            if key not in item_sizer_keys:
                raise Exception('Invalid container key. [key=\"{}\"]'.format(key))
        if not args:
            parent = self.mainpanel
            #print 'self.mainpanel:', self.mainpanel
        else:
            parent = args[0]
        container.Show()            
        if container.__class__ == StaticBoxContainer:
            parent.GetSizer().Add(container.GetSizer(), **kwargs)
        else:    
            parent.GetSizer().Add(container, **kwargs)
        parent.GetSizer().Layout()


    def DetachContainer(self, container):
        ctn_sizer = container.GetSizer()
        parent = container.GetParent()
        if container.__class__ == StaticBoxContainer:
            result = parent.GetSizer().Detach(ctn_sizer)
        else:
            result =  parent.GetSizer().Detach(container)
        #print '\nDetachContainer:', container, parent, result    
        container.Show(False)    
        #self.Refresh()
        return result
        #print 777
        

    def CreateContainer(self, container_type_name, *args, **kwargs):
        try:
            if container_type_name == 'BoxSizer':
                container_class = BoxSizerContainer
            elif container_type_name == 'GridSizer':
                container_class = GridSizerContainer
            elif container_type_name == 'FlexGridSizer':
                container_class = FlexGridSizerContainer            
            elif container_type_name == 'GridBagSizer':
                container_class = GridBagSizerContainer             
            elif container_type_name == 'StaticBox':
                container_class = StaticBoxContainer   
            elif container_type_name == 'WarpSizer':
                container_class = WarpSizerContainer  
            else:
                raise Exception('Unregistered container.')          
            #print 'CreateContainer:', container_class, args, kwargs
            if not args:
                #print 'self.mainpanel:', self.mainpanel
                parent = self.mainpanel
            else:
                parent = args[0]
            container = container_class(parent, **kwargs)
            #print 'CreateContainer fim'
            return container
        except:
            raise
            

    def AddCreateContainer(self, container_type_name, *args, **kwargs):
        #print '\n\nAddCreateContainer:', container_type_name, args, kwargs
        try:
            item_sizer_kw, kwargs = pop_registers(item_sizer_keys, kwargs)
            container = self.CreateContainer(container_type_name, *args, **kwargs)
            self.AddContainer(container, *args, **item_sizer_kw)    
            return container
        except:
            raise
            
    
    '''
    def AddBoxSizerContainer(self, *args, **kwargs):
        #print 'AddBoxSizerContainer'
        return self._AddCreateContainer(BoxSizerContainer, *args, **kwargs)
        
    def AddGridSizerContainer(self, *args, **kwargs):
        return self._AddCreateContainer(GridSizerContainer, *args, **kwargs)     

    def AddFlexGridSizerContainer(self, *args, **kwargs):
        return self._AddCreateContainer(FlexGridSizerContainer, *args, **kwargs)
        
    def AddGridBagSizerContainer(self, *args, **kwargs):
        return self._AddCreateContainer(GridBagSizerContainer, *args, **kwargs)    

    def AddStaticBoxContainer(self, *args, **kwargs):
        return self._AddCreateContainer(StaticBoxContainer, *args, **kwargs)
                 
    def AddWarpSizerContainer(self, *args, **kwargs):
        return self._AddCreateContainer(WarpSizerContainer, *args, **kwargs)                 
    '''
                 
    def CreateControl(self, enc_class, container, **kwargs):
        # Create and Add a new control.
        try:
            keys = get_control_keys(enc_class._control_class)
            controlkw, specialkw, kwargs = pop_widget_registers(keys, kwargs)
            specialkw['controller_uid'] = self._controller_uid
            enc_control = enc_class(container, specialkw, **controlkw)
            self.register(enc_control)
            container.GetSizer().Add(enc_control.control, **kwargs)
            container.GetSizer().Layout()
        except:
            raise
            
    def AddChoice(self, *args, **kwargs):
        self.CreateControl(EncapsulatedChoice, args[0], **kwargs)

    def AddRadioButton(self, *args, **kwargs):
        self.CreateControl(EncapsulatedRadioButton, args[0], **kwargs)

    def AddCheckBox(self, *args, **kwargs):
        self.CreateControl(EncapsulatedCheckBox, args[0], **kwargs)

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

    def get_results(self):
        ret = {}
        for name, widget in self._objects.items():
            ret[name] = widget.get_value()
        return ret    
    
    def get_object(self, name):
        return self._objects.get(name)




class PanelContainer(wx.Panel):
    
    def __init__(self, *args, **kwargs): 
        #print '\nPanelContainer:', args, kwargs
        if not kwargs.get('sizer_class'):
            raise Exception()    
        sizer_class = kwargs.pop('sizer_class')
        panel_kw, sizer_kw = pop_registers(panel_keys, kwargs)
        #print 'wx.Panel.__init__:', args[0], panel_kw
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
      
  
            
###############################################################################
###############################################################################

