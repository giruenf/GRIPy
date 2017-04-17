# -*- coding: utf-8 -*-
import wx
import wx.aui as aui
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from UI.uimanager import UI_MODEL_ATTR_CLASS
from App import log
from App.utils import is_wxPhoenix

    
class MainWindowController(UIControllerBase):
    tid = 'main_window_controller'
    _singleton = True
     
    def __init__(self):
        super(MainWindowController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))

    """
    When the MainWindow calls the function below, GripyApp will close UIManager 
    but not finish the wx.App.
    This job must be done by Wx. (don't try to change it!)
    """
    def _pre_exit_application(self):
        wx.App.Get().PreExit()

    def on_change_model_attr(self, **kwargs):
        if kwargs.get('key') == 'maximized':
            self.view._set_maximized(kwargs.get('new_value'))
        elif kwargs.get('key') == 'size':
            self.view._set_size(kwargs.get('new_value'))
        elif kwargs.get('key') == 'pos':    
            self.view._set_position(kwargs.get('new_value'))
        else:
            raise Exception('Unnknown key: {}'.format(kwargs.get('key')))


class MainWindowModel(UIModelBase):
    tid = 'main_window_model'
    
    _ATTRIBUTES = {
        'title': {'default_value': 'Gripy', 
                  'type': str, 
                  'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'icon': {'default_value': '', 
                 'type': str, 
                 'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'style': {'default_value': wx.DEFAULT_FRAME_STYLE, 
                  'type': int, 
                  'attr_class': UI_MODEL_ATTR_CLASS.APPLICATION
        },
        'maximized': {'default_value': False,  
                      'type': bool, 
                      'on_change': MainWindowController.on_change_model_attr,
                      'attr_class': UI_MODEL_ATTR_CLASS.USER
        },
        'size': {'default_value': wx.Size(800, 600), 
                 'type': wx.Size, 
                 'on_change': MainWindowController.on_change_model_attr,
                 'attr_class': UI_MODEL_ATTR_CLASS.USER
        },
        'pos': {'default_value': wx.Point(50, 50), 
                'type': wx.Point, 
                'on_change': MainWindowController.on_change_model_attr,
                'attr_class': UI_MODEL_ATTR_CLASS.USER
        }
    }    
    
    def __init__(self, controller_uid, **base_state):      
        super(MainWindowModel, self).__init__(controller_uid, **base_state)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Model object from class: {}.'.format(class_full_name))



class MainWindow(UIViewBase, wx.Frame):
    tid = 'main_window'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        wx.Frame.__init__(self, None, -1, controller.model.title,
            pos=controller.model.pos, size=controller.model.size, 
            style=controller.model.style              
        ) 
        self.Maximize
        self._mgr = aui.AuiManager(self)      
        if is_wxPhoenix():
            # Phoenix wx.aui.AuiDockArt changed SetColor to SetColour 
            self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_BACKGROUND_COLOUR, 
                   wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
            self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
                   wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)) 
        else:    
            # wxPython classic code
            self._mgr.GetArtProvider().SetColor(aui.AUI_DOCKART_BACKGROUND_COLOUR, 
                   wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
            self._mgr.GetArtProvider().SetColor(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
                   wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)) 
        self.note = aui.AuiNotebook(self)
        self._mgr.AddPane(self.note, aui.AuiPaneInfo().Name("notebook").
                          CenterPane())                           
        self._mgr.Update()     
        if controller.model.icon:   
            self.icon = wx.Icon(controller.model.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.model.maximized:
            self.Maximize()   
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)    
        self.Bind(wx.EVT_CLOSE, self.on_close) 
         
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close, self.note)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created View object from class: {}.'.format(class_full_name))
        
    def on_maximize(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.model.set_value_from_event('maximized', self.IsMaximized())

    def on_move(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.model.set_value_from_event('pos', self.GetPosition())

    def on_size(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.model.set_value_from_event('size', event.GetSize())
        event.Skip()

    def on_close(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller._pre_exit_application()
        event.Skip()

    def on_page_close(self, event):
        panel = self.note.GetPage(event.GetSelection())
        _UIM = UIManager()
        _UIM.remove(panel._controller_uid)

    def _set_maximized(self, maximized):
        self.Unbind(wx.EVT_MAXIMIZE, handler=self.on_maximize)  
        self.Maximize(maximized)
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)  
    
    def _set_size(self, size):
        self.Unbind(wx.EVT_SIZE, handler=self.on_size)
        self.SetSize(size)
        self.Bind(wx.EVT_SIZE, self.on_size)    
    
    def _set_position(self, pos):
        self.Unbind(wx.EVT_MOVE, handler=self.on_move) 
        self.SetPosition(pos)
        self.Bind(wx.EVT_MOVE, self.on_move)  
