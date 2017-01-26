# -*- coding: utf-8 -*-

import wx
from trackspanel import TracksPanel
from titlespanel import TitlesPanel
from chronometer import Chronometer


class TracksTitlesSplitter(wx.SplitterWindow):
    
    def __init__(self, parent):
        self._logplot = parent
        super(TracksTitlesSplitter, self).__init__(self._logplot)

        self._titles = TitlesPanel(self)#._logplot)
        self._tracks = TracksPanel(self)#._logplot)
        
        self._titles.SashPositionChangedCallBack(self._tracks.AdjustAllSashes)
        self._tracks.SashPositionChangedCallBack(self._titles.AdjustAllSashes)
        self.SplitHorizontally(self._titles, self._tracks)
        # Falta forçar a posição do Splitter (3 tracks)
        #self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._OnPosChanged)
        self.SetSashPosition(self._titles.tracks.GetSize().GetHeight()+2)
        #self.Bind(wx.EVT_SIZE, self._OnSize)

    
    def insert_track(self, idx, status_bar_callback=None, 
                     zoom_callback=None, **kwargs):

        #print '\nTracksTitlesSplitter.insert_track kwargs: ', kwargs          
        #c = Chronometer()
        #def __init__(self, parent, title_text=None, title_bgcolor='white', 
        #         min_height_pixels=100, data=None, layout_properties=None):                       
        titlePanel = self._titles.insert_track_title(idx, 
                            kwargs.get('track_name'), kwargs.get('width'))
        #insert_track_title(self, idx, track_name=None, width=None):
        #c.end('TracksTitlesSplitter.titlePanel')        
        #c = Chronometer()
        
        trackPanel = self._tracks.insert_track(idx, status_bar_callback,
                                    zoom_callback, **kwargs)
        #c.end('TracksTitlesSplitter.trackPanel')        
        return (titlePanel, trackPanel)
     

    def remove_tracks(self, index_list):
        sorted(index_list, key=int, reverse=True)
        for idx in index_list:
            if idx >= 0 and idx < self._titles.lenght():
                print '\nTracksTitlesSplitter.remove_tracks: ', idx
                self._titles.remove_track_title(idx)
                self._tracks.remove_track(idx)
        self._titles.tracks._SizeComponent()
        self._tracks.tracks._SizeComponent()
            
    def _SetFit(self, boolean):
        self._titles._SetFit(boolean)
        self._tracks._SetFit(boolean)            
        
        