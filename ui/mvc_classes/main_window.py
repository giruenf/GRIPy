# -*- coding: utf-8 -*-
import wx
import wx.aui as aui
from ui.uimanager import UIManager

from ui.mvc_classes.wxgripy import FrameController
from ui.mvc_classes.wxgripy import FrameModel
from ui.mvc_classes.wxgripy import Frame

from app import log


class MainWindowController(FrameController):
    tid = 'main_window_controller'
    _singleton = True
     
    def __init__(self):
        super().__init__()
        
    """
    When the MainWindow calls the function below, GripyApp will close UIManager 
    but not finish the wx.App.
    This job must be done by Wx. (don't try to change it!)
    """
    #def _pre_exit_application(self):
    #    wx.App.Get().PreExit()

    def insert_notebook_page(self, *args, **kwargs):
        return self.view.insert_notebook_page(*args, **kwargs)
        

class MainWindowModel(FrameModel):
    tid = 'main_window_model'
    
    def __init__(self, controller_uid, **base_state):    
        super().__init__(controller_uid, **base_state)


class MainWindow(Frame):
    tid = 'main_window'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
        #
        self._mgr = aui.AuiManager(self)      
        self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_BACKGROUND_COLOUR, 
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
        self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)) 
        self.note = aui.AuiNotebook(self)
        self._mgr.AddPane(self.note, aui.AuiPaneInfo().Name("notebook").
                          CenterPane())                           
        self._mgr.Update()    
        #
        self.Bind(wx.EVT_CLOSE, self.on_close)          
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close, self.note)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        
        
    def on_close(self, event):
        '''
        print ('\nMainWindow.on_close')
        import app
        for ci in app.app_utils.get_callers_stack():
            print ('\n'+str(ci))

        print ('\n\n')
        '''
        
        event.Skip()
        wx.GetApp().PreExit()
        
        '''
        try:
            wx.GetApp().PreExit()
        except:
            import traceback
            traceback.print_stack()
        '''
        
        '''
        #
        # TODO: remover isso 
        if wx.GetApp():
            event.Skip()
            wx.GetApp().PreExit()
        else:
            print ('Not app')
        '''


    def on_page_close(self, event):
        panel = self.note.GetPage(event.GetSelection())
        UIM = UIManager()
        UIM.remove(panel._controller_uid)


    def on_page_changed(self, event):
        UIM = UIManager()
        for idx in range(self.note.GetPageCount()):
            page = self.note.GetPage(idx)
            controller = UIM.get(page._controller_uid)
            controller.model.set_value_from_event('pos', idx)
        event.Skip()
     
        
    def insert_notebook_page(self, *args, **kwargs):
        try:
            page = None
            if kwargs:
                page = kwargs.get('page')
            if not page:
                page = args[1]
            UIM = UIManager()
            page_ctrl_parent_uid = UIM._getparentuid(page._controller_uid)
            if self._controller_uid == page_ctrl_parent_uid:
                return self.note.InsertPage(*args, **kwargs)
        except:
            pass
        return False
        
    def get_notebook_page_index(self, page):
        return self.note.GetPageIndex(page)
 
    def set_notebook_page_text(self, page_index, text):
        return self.note.SetPageText(page_index, text)
            
       