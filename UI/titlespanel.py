# -*- coding: utf-8 -*-
import wx
from wx.lib.scrolledpanel import ScrolledPanel
from trackssplitter import MultiSplitterWindow
import UI
import logplot_base as lpb


class TitlesPanel(ScrolledPanel):
    
    def __init__(self, parent, track_title_color=None):
        ScrolledPanel.__init__(self, parent, -1, style=wx.BORDER_STATIC)    
        self.tracks = MultiSplitterWindow(self)                   
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.item = vbox.Add(self.tracks, 1, wx.LEFT)
        self.SetSizer(vbox)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.SetupScrolling()
        self.tracks.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._SashPosChanged)    
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.set_track_title_color(track_title_color)


    def _get_height(self):
        _, height = self.GetSize()
        return height
        
    def lenght(self):
        return self.tracks.lenght()        

    def get_position(self, track_title_panel):
        return self.tracks.IndexOf(track_title_panel)        
        
    def set_track_title_color(self, color=None):
        if color:
            self._track_title_color = color
        else:
            self._track_title_color = UI.logplotformat.LogPlotFormat.get_default_track_header_color()
        for i in range(self.tracks.lenght()):
            self.tracks.GetWindow(i).set_track_title_color(self._track_title_color)
    
    
    def get_track_title_color(self):
        return self._track_title_color
               
    def get_tracks_titles(self):
        list_ = []
        for i in range(self.tracks.lenght()):
            list_.append(self.tracks.GetWindow(i).get_title_text())
        return list_    

    def append_track_title(self, track_name):
        idx = self.tracks.lenght()
        return self.insert_track_title(idx, track_name)


    def insert_track_title(self, idx, track_name=None, width=None):
        if idx >= 0 and idx <= self.tracks.lenght():
            if width:
                try:
                    width = float(width)
                    if width <= 0:
                        raise ValueError('Width must be greater than zero.')
                except Exception:
                    raise
            else:
                width = UI.logplotformat.LogPlotFormat.DEFAULT_TRACK_WIDTH
               
            if not track_name:
                track_name = str(idx+1)    
            #size = wx.Size(width, self._get_height())    
  
            plot_label = UI.logplot_base.PlotLabel(self.tracks)
            plot_label.update_title(text=track_name, bgcolor=self._track_title_color)
            #TitleFigureCanvas(self.tracks, size, track_name, 
            #                                        self._track_title_color) 

            self.tracks.InsertWindow(idx, plot_label, int(width * lpb.DPI * lpb.FACTOR))
            return plot_label


    def remove_track_title(self, idx):
        window = self.tracks.GetWindow(idx)
        self.tracks.DetachWindow(window)
        window.Destroy()


    '''
    Para receber callbacks do TracksPanel
    '''
    def AdjustAllSashes(self, vetor):
        self.tracks.Unbind(wx.EVT_SPLITTER_SASH_POS_CHANGED)
        #print 'self.Titles.AdjustAllSashes({})'.format(vetor)
        self.tracks.AdjustAllSashes(vetor)
        self.tracks.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._SashPosChanged)
    

    """
    Método para fazer self.tracks ocupar toda área disponível quando 
    boolean = True, ou fazer self.tracks ter seu tamanho original
    """
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
        #self._AdjustSizerItem()
        evt.Skip() 