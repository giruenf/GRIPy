# -*- coding: utf-8 -*-

import wx
import wx.aui as aui
import logging

try:
    from app.gripy_controller import GripyController
except ImportError:
    logging.exception('Import error.')    
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
    
from UI.uimanager import UIManager
    
    
class MainWindowController(UIControllerBase):
    tid = 'main_window_controller'
    _singleton = True
     
    def __init__(self):
        super(MainWindowController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created Controller object from class: {}.'.format(class_full_name))

 #   def __del__(self):
 #       print 'Main Window Controller delete'     

 #   def _value_changed(self, value):
 #       print '_value_changed title', value
 #       self.view.SetTitle(value)
        
        
class MainWindowModel(UIModelBase):
    tid = 'main_window_model'
    
    _ATTRIBUTES = {
        'title': {'default_value': 'Gripy', 'type': str, 'base_attr': True},
        #'title': {'default_value': 'Gripy', 'type': str, 'on_change': MainWindowController._value_changed},
        'icon': {'default_value': '', 'type': str, 'base_attr': True},
        'style': {'default_value': wx.DEFAULT_FRAME_STYLE, 'type': int, 'base_attr': True},
        'maximized': {'default_value': False,  'type': bool},
        'size': {'default_value': wx.Size(800, 600), 'type': wx.Size},
        'pos': {'default_value': wx.Point(50, 50), 'type': wx.Point}
    }    
    
    def __init__(self, controller_uid, **base_state):      
        super(MainWindowModel, self).__init__(controller_uid, **base_state)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created Model object from class: {}.'.format(class_full_name))


  #  def __del__(self):
  #      print 'Main Window Model delete'               
               
               
class MainWindow(UIViewBase, wx.Frame):
    tid = 'main_window'

    
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        #parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        #parent_controller =  _UIM.get(parent_controller_uid)
        
        wx.Frame.__init__(self, None, -1, controller.model.title,
            pos=controller.model.pos, size=controller.model.size, 
            style=controller.model.style              
        )
        
        self._mgr = aui.AuiManager(self)
        self._mgr .GetArtProvider().SetColor(aui.AUI_DOCKART_BACKGROUND_COLOUR, 
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
        self._mgr.GetArtProvider().SetColor(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)) 
                      
        self.note = aui.AuiNotebook(self)
        self._mgr.AddPane(self.note, aui.AuiPaneInfo().Name("notebook").
                          CenterPane())                           
        self._mgr.Update()     

        #self.SetDoubleBuffered(True)

        if controller.model.icon:   
            self.icon = wx.Icon(controller.model.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)
        
        if controller.model.maximized:
            self.Maximize()
            
        self.Bind(wx.EVT_MOVE, self.on_move)
        #self.Bind(wx.EVT_SIZE, self.on_size)     
        self.Bind(wx.EVT_CLOSE, self.on_close) 
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close, self.note)
            
     #   self.Bind(wx.EVT_CONTEXT_MENU, self._on_context)            
            
            
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        logging.debug('Successfully created View object from class: {}.'.format(class_full_name))

  
    #def _on_context(self, event):
    #   print '\n', event.GetClientObject()
  
  
    def on_move(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.model.pos = event.GetPosition()


    def on_size(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.model.size = event.GetSize()
        controller.model.maximized = self.IsMaximized()
        event.Skip()


    def on_close(self, event):
        self._do_close()
        event.Skip()


    def on_page_close(self, event):
        print '\npage_close...'
        panel = self.note.GetPage(event.GetSelection())
        _UIM = UIManager()
        _UIM.remove(panel._controller_uid)
        print 'End _UIM.remove'
        print '\n\n'

      #  event.Skip()
        
        
 #   def __del__(self):
  #      print 'Main Window delete'
        
        
    def _do_close(self):
        gc = GripyController(self)
        gripy_app = wx.GetApp()

        if not gripy_app.load_app_state:
            state_filename = gripy_app._gripy_app_state.get('app_state_file')
            try:
                gc.save_UI_state(state_filename)
            except Exception:
                msg = 'ERROR: UI State was not saved.'
                print msg
                logging.exception(msg)
        gc._UIM.close()

        
        
     