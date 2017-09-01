# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 

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
'''

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


registered_widgets = {
    wx.StaticText: wx_statictext_keys,
    wx.SpinCtrl: wx_spinctrl_keys,
    wx.TextCtrl: wx_textctrl_keys,
    wx.Choice: wx_choice_keys,
    wx.ListBox: wx_listbox_keys
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


###############################################################################
###############################################################################


class DialogController(TopLevelController):
    tid = 'dialog_controller'
         
    def __init__(self):
        super(DialogController, self).__init__() 
        

class DialogModel(TopLevelModel):
    tid = 'dialog_model'
    
    _ATTRIBUTES = {
        'flags': {
                'default_value': wx.OK|wx.CANCEL, 
                'type': int
        }
    }    
    _ATTRIBUTES.update(TopLevelModel._ATTRIBUTES) 
    
    def __init__(self, controller_uid, **base_state):      
        super(DialogModel, self).__init__(controller_uid, **base_state) 
    
    
      
class Dialog(TopLevel, wx.Dialog):   
    tid = 'dialog'
    
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
        #__init__ (self, parent, id=ID_ANY, title=””, pos=DefaultPosition, 
        #          size=DefaultSize, style=DEFAULT_DIALOG_STYLE, name=DialogNameStr)
        wx.Dialog(self, parent_view, wx.ID_ANY, controller.model.title,
            pos=controller.model.pos, size=controller.model.size, 
            style=controller.model.style              
        ) 
        #
        if controller.model.icon:   
            self.icon = wx.Icon(controller.model.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.model.maximized:
            self.Maximize()   
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)  
        #
        dialog_box = wx.BoxSizer(wx.VERTICAL) 
        self.SetSizer(dialog_box) 
        self.mainpanel = self.AddBoxSizerContainer(self, proportion=1, 
                            flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10
        )
        
        button_sizer = self.CreateButtonSizer(controller.model.flags)
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
    
    
'''






###############################################################################
###############################################################################


class ToolBarController(UIControllerBase):
    tid = 'toolbar_controller'
    _singleton_per_parent = True
    
    def __init__(self):
        super(ToolBarController, self).__init__()
      
  
class ToolBarModel(UIModelBase):
    tid = 'toolbar_model'
    _ATTRIBUTES = {
        'id': {
                'default_value': wx.ID_ANY, 
                'type': int#,
               #'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'pos': {
                'default_value': wx.DefaultPosition, 
                'type': wx.Point#,
                #'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'size': {
                 'default_value': wx.DefaultSize, 
                 'type': wx.Size#,
                 #'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'style': {
                'default_value': wx.TB_FLAT|wx.TB_NODIVIDER, 
                'type': long#,
                #  'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        }
    }    
    
    def __init__(self, controller_uid, **base_state):     
        super(ToolBarModel, self).__init__(controller_uid, **base_state)    
               
            
class ToolBar(UIViewBase, wx.ToolBar):
    tid = 'toolbar'
    
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)
        
        #wx.SystemOptions.SetOption("msw.remap", '0')
        wx.ToolBar.__init__(self, parent_controller.view, controller.model.id, 
                            controller.model.pos,
                            controller.model.size, controller.model.style
        )
        self.Realize()  
        mgr = wx.aui.AuiManager.GetManager(parent_controller.view)
        if mgr:
            # TODO: Vale trocar Name(self.tid) por Name(str(self.uid)) abaixo?
            self.paneinfo = wx.aui.AuiPaneInfo().Name(self.tid).ToolbarPane().Top()
            mgr.AddPane(self, self.paneinfo)
            mgr.Update()
        else:
            print 'Toolbar else'
            #parent_controller.view
            
###############################################################################
###############################################################################


