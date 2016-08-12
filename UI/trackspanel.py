# -*- coding: utf-8 -*-
import wx
from trackssplitter import MultiSplitterWindow
from wx.lib.scrolledpanel import ScrolledPanel
import UI
import logplot_base as lpb 



class TracksPanel(ScrolledPanel):

    
    def __init__(self, parent):
        ScrolledPanel.__init__(self, parent, -1, style=wx.BORDER_STATIC)
        self.tracks = MultiSplitterWindow(self)                   
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.item = vbox.Add(self.tracks, 1, wx.LEFT)
        self.SetSizer(vbox)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetupScrolling()
        self.tracks.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._SashPosChanged)
        self._tracks_attr = []
        self.Bind(wx.EVT_SIZE, self._OnSize)

    def _get_height(self):
        _, height = self.GetSize()
        return height
        
    def lenght(self):
        return self.tracks.lenght()        
    
    def get_position(self, track_panel):
        return self.tracks.IndexOf(track_panel)
        
    def append_track(self, callback, **kwargs):
        idx = self.tracks.lenght()
        return self.insert_track(idx, callback, **kwargs)
        
    def insert_track(self, idx, status_bar_callback=None, 
                                             zoom_callback=None, **kwargs):
        if idx >= 0 and idx <= self.tracks.lenght():
            width = 0
            if kwargs.get('width'):
                try:
                    width = float(kwargs.get('width'))
                    del kwargs['width']
                    if width <= 0:
                        raise ValueError('width_inches deve ser maior que zero.')
                except Exception:
                    raise
            else:
                width = UI.logplotformat.LogPlotFormat.DEFAULT_TRACK_WIDTH
            trackPanel = lpb.TrackFigureCanvas(self.tracks, (width, self._get_height()),
                                           properties=kwargs)
            # TODO: colocar os callbacks no LogPlot e corrigir nomes das 
            # funcoes de callback no logplot_base (set_callback e set_zoom_callback)
            if status_bar_callback:
                trackPanel.set_callback(status_bar_callback)
            if zoom_callback:
                trackPanel.set_zoom_callback(zoom_callback)
            self.tracks.InsertWindow(idx, trackPanel, int(width * lpb.DPI * lpb.FACTOR))
            self._tracks_attr.insert(idx, None)
            return trackPanel


    def update_track(self, idx, **kwargs):
        trackPanel = self.tracks.GetWindow(idx)
        trackPanel.update_dummy_axes(**kwargs)

    def remove_track(self, idx):
        self._remove_attributes(idx)
        window = self.tracks.GetWindow(idx)
        self.tracks.DetachWindow(window)
        window.Destroy()
    
    def get_track_width(self, idx):
        return self.tracks._sashes[idx] / self.WIDTH_FACTOR
        
    def set_track_width(self, idx, width):        
        width = width * self.WIDTH_FACTOR
       
    def _remove_attributes(self, idx):
        try :
            self._tracks_attr.pop(idx)
        except Exception:
            raise       
        
    def AdjustAllSashes(self, vetor):
        self.tracks.Unbind(wx.EVT_SPLITTER_SASH_POS_CHANGED)
        self.tracks.AdjustAllSashes(vetor)
        self.tracks.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._SashPosChanged)
    

    def _SetFit(self, boolean):
        self.tracks._SetFit(boolean)
        self.Layout()
                          
    def _SashPosChanged(self, evt):
        if self.tracks._GetFit():
            self._execSashPosChangedCallBack(self.tracks._proporcao)
        else:    
            self._execSashPosChangedCallBack(self.tracks._sashes)
        
    def SashPositionChangedCallBack(self, function):
        self.CB = function            
                 
    def _execSashPosChangedCallBack(self, vetor):
        if self.CB:        
            self.CB(vetor)
                  
    def _AdjustSizerItem(self):
        self.item.SetMinSize(self.tracks.GetSize())
            
    def _OnSize(self, evt):
        self._AdjustSizerItem()
        evt.Skip()    