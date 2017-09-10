# -*- coding: utf-8 -*-
import wx
from wx.lib.scrolledpanel import ScrolledPanel     
from trackssplitter import MultiSplitterWindow

class LogPlotInternal(wx.SplitterWindow):  
    SASH_POSITION = 100    
    
    def __init__(self, parent):
        super(LogPlotInternal, self).__init__(parent, style=wx.SP_THIN_SASH) 
        self._top_panel = BaseScrolled(self)
        self._bottom_panel = BaseScrolled(self)
        self.SplitHorizontally(self._top_panel, self._bottom_panel)
        self.SetSashPosition(self._top_panel._splitter.GetSize().GetHeight()) # + 2)
        self.SetMinimumPaneSize(self.SASH_POSITION) 
        self.Bind(wx.EVT_SIZE, self._on_size)
         
    def _on_size(self, event):
        event.Skip()        
        
    def _on_sash_changing(self, event):
        if isinstance(event, wx.SplitterEvent):
            event.SetSashPosition(-1)  
        else:
            event.Skip()
      
    def __len__(self):
        if len(self.top_splitter) != len(self.bottom_splitter):
            raise Exception('ERROR: Top panel and bottom panel must have same size.')
        return len(self.top_splitter)

    def insert(self, pos, top_window, bottom_window, width):
        self.top_splitter.InsertWindow(pos, top_window, width)
        self.bottom_splitter.InsertWindow(pos, bottom_window, width)
            
    def append(self, top_window, bottom_window):
        pos = len(self.top_splitter)
        self.insert(pos, top_window, bottom_window)
            
    @property
    def top_splitter(self):
        return self._top_panel._splitter
             
    @property
    def bottom_splitter(self):
        return self._bottom_panel._splitter
  
class BaseScrolled(ScrolledPanel):
    
    def __init__(self, parent, **kwargs):
        ScrolledPanel.__init__(self, parent, -1, style=wx.BORDER_STATIC)    
        self._splitter = MultiSplitterWindow(self)      
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.item = hbox.Add(self._splitter , 0, wx.EXPAND)
        hbox.Layout()
        self.SetSizer(hbox)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetupScrolling()

    def fit(self, fit=True):
        self._splitter._SetFit(fit)
        self.Layout()
      



  

