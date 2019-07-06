# -*- coding: utf-8 -*-
import wx
import wx.aui as aui
from classes.ui import UIManager

from classes.ui import FrameController
from classes.ui import Frame
from app.app_utils import GripyBitmap
from app import log


class MainWindowController(FrameController):
    tid = 'main_window_controller'
    _singleton = True
     
    def __init__(self, **state):
        super().__init__(**state)
         

class MainWindow(Frame):
    tid = 'main_window'

    def __init__(self, controller_uid):
        #
        super().__init__(controller_uid)
        #
        self._mgr = aui.AuiManager(self)   
        #
        self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_BACKGROUND_COLOUR, 
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
        self._mgr.GetArtProvider().SetColour(aui.AUI_DOCKART_INACTIVE_CAPTION_COLOUR,
               wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)) 
        #
        self.main_area_panel = wx.Panel(self)
        
        bmp_filename = "gripy_logo.jpg"
        bmp = GripyBitmap(bmp_filename)
        self._static_bmp = wx.StaticBitmap(self.main_area_panel, wx.ID_ANY, 
                                    bmp, wx.Point(0, 0), 
                                    bmp.GetSize()
        )  
        self.main_area_panel.SetBackgroundColour('white')
        
        self._mgr.AddPane(self.main_area_panel, 
                        aui.AuiPaneInfo().Name("main_area_panel").CenterPane())    
        #
        self._notebook = aui.AuiNotebook(self.main_area_panel)
        #
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._notebook, 1, flag=wx.EXPAND)
        sizer.Add(self._static_bmp, 1, flag=wx.EXPAND)
        #
        self._notebook.Show(False)
        #
        sizer.Layout()
        #
        self.main_area_panel.SetSizerAndFit(sizer)
        #
        self.Bind(aui.EVT_AUINOTEBOOK_TAB_RIGHT_DOWN, 
                  self.on_page_right_down)     
        #    
        self._mgr.Update()    
        #
#        self.Bind(wx.EVT_CLOSE, self.on_close)     
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, 
                  self.on_page_close, self._notebook)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, 
                  self.on_page_changed)


    def _get_wx_parent(self, *args, **kwargs):
        return self
    

    def adjust_background_panel(self):
        if ((self.get_notebook_page_count() == 0) and 
                                                (self._notebook.IsShown())): 
            # Last page was removed
            self.show_main_area_panel()

        if ((self.get_notebook_page_count() == 1) and 
                                            (not self._notebook.IsShown())):
            # Fist page was shown
            self.show_main_area_panel(False)



    def show_main_area_panel(self, b=True):
        sizer = self.main_area_panel.GetSizer()
        sizer.Show(self._notebook, show=not b)
        sizer.Show(self._static_bmp, show=b)
        sizer.Layout()

        #
        # Refresh(self, eraseBackground=True, rect=None) - Invalidate window
        #   Causes this window, and all of its children recursively 
        #   (except under GTK1 where this is not implemented), 
        #   to be repainted.
        #
        # Update(self) - Do not invalidate window
        #   Calling this method immediately repaints the invalidated area 
        #   of the window and all of its children recursively 
        #   (this normally only happens when the flow of control returns 
        #   to the event loop). Notice that this function doesn’t invalidate 
        #   any area of the window so nothing happens if
        #   nothing has been invalidated (i.e. marked as requiring a redraw). 
        #   Use Refresh first if you want 
        #   to immediately redraw the window unconditionally.
 


    def on_page_right_down(self, event):
        print ('\non_page_right_down:', event)
        print (event.GetId())
        print (event.GetEventType())
        window = wx.FindWindowById(event.GetId())
        print (window)

        
    def on_close(self, event):
#       TODO: Coloar exibir mensagem de saida aqui...       
#        if event.CanVeto():
#            print ('') 
        wx.GetApp().PreExit()
        wx.CallAfter(self.Destroy)


    def PreDelete(self):
        # As indicated by https://forums.wxwidgets.org/viewtopic.php?t=32138   
        
#        aui_manager = wx.aui.AuiManager.GetManager(self)
#        aui_manager.UnInit()   
        
        self._mgr.UnInit()
        
        
    def on_page_changed(self, event):
        UIM = UIManager()
        for idx in range(self._notebook.GetPageCount()):
            page = self._notebook.GetPage(idx)
            controller = UIM.get(page._controller_uid)
            controller.set_value_from_event('pos', idx)
        event.Skip()


    def on_page_close(self, event):
        panel = self._notebook.GetPage(event.GetSelection())
        # Remove page without destruct
        self.remove_notebook_page(panel)
        # Remove from UIManager with Window destruction
        UIM = UIManager()
        UIM.remove(panel._controller_uid)  
        # Line below must exist in order to prevent SystemError
        wx.CallAfter(self.adjust_background_panel)
        
      
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
#                print ('b4 insert page')
                ret_val = self._notebook.InsertPage(*args, **kwargs)
#                print ('after insert page')
            
            self.adjust_background_panel()
            #if not self._notebook.IsShown():
            #    print ('SETTING show_main_area_panel(False)')
            #    self.show_main_area_panel(False)
                
                       
            return ret_val    
                
        except Exception as e:
            print ('ERROR:', e)
        return False


    def remove_notebook_page(self, page_window):
        # Remove page without destruct
        page_idx = self._notebook.GetPageIndex(page_window)
        ret_val =  self._notebook.RemovePage(page_idx)
        # Line below must exist in order to prevent SystemError
        wx.CallAfter(self.adjust_background_panel)
        return ret_val
    

    def get_notebook_page_index(self, idx):
        return self._notebook.GetPageIndex(idx)


    def get_notebook_page_count(self):
        return self._notebook.GetPageCount()
    

    def set_notebook_page_text(self, page_index, text):
        return self._notebook.SetPageText(page_index, text)
            
     
        
    
    
    