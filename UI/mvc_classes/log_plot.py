# -*- coding: utf-8 -*-
import wx
#import wx.aui as aui

from UI.uimanager import UIControllerBase 

from workpage import WorkPageController
from workpage import WorkPageModel
from workpage import WorkPage

from UI.uimanager import UIManager
#from UI.logplot_base import OverviewFigureCanvas
from UI.logplot_internal import LogPlotInternal
#from UI.plotstatusbar import PlotStatusBar
from App.utils import LogPlotState  

from App import log   
     
from mpl_base import TrackFigureCanvas, PlotLabel

from App.utils import DropTarget


 
LP_NORMAL_TOOL = wx.NewId()        
LP_SELECTION_TOOL = wx.NewId()     
LP_ADD_TRACK = wx.NewId()     
LP_REMOVE_TRACK = wx.NewId()     
    
  

  
class LogPlotController(WorkPageController):
    
    tid = 'logplot_controller'
        
    def __init__(self):
        super(LogPlotController, self).__init__()  

    def PostInit(self):
        self.subscribe(self.on_change_cursor_state, 
                             'change.cursor_state'
        )
        self.subscribe(self.on_change_ylim, 'change.y_min_shown')
        self.subscribe(self.on_change_ylim, 'change.y_max_shown')

    @property
    def size(self):
        UIM = UIManager()
        return len(UIM.list('track_controller', self.uid))
    
    
    @staticmethod
    def get_acceptable_tids():
        return ['log', 'index_curve', 'partition', 'seismic', 'scalogram', 
                'velocity', 'angle', 'gather']
            
    
    def show_track(self, track_uid, show):
        # Adjust track.model...
        UIM = UIManager()
        track = UIM.get(track_uid)
        track.model.visible = show
        self.view.show_track(track_uid, show)
    
    
    def insert_track(self):
        UIM = UIManager()
        selected_tracks = UIM.do_query('track_controller', self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        #print 'insert_track', self.size
        if not selected_tracks:
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=self.size
            )
            return [new_track.uid]         
        ret_list = []    
        
        for track in selected_tracks:
            #print '\ncreating in pos:', track.model.pos 													 
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=track.model.pos
            )
            ret_list.append(new_track.uid)            
        return ret_list


    def remove_selected_tracks(self):
        UIM = UIManager()
        selected_tracks = UIM.do_query('track_controller',  self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        for track in selected_tracks:
            UIM.remove(track.uid)  


    def _create_windows(self, track_uid):
        self.view._create_windows(track_uid)

    def _pre_delete_overview_track(self):
        self.view._remove_from_overview_panel()

    def get_track_position(self, track_uid, relative_position=True):  
        return self.view.get_track_position(track_uid, True)


    def change_track_position(self, track_uid, old_pos, new_pos):
        #print 'change_track_position:', track_uid, old_pos, new_pos
        UIM = UIManager()
        track_pos = UIM.get(track_uid)
        #print 'track new pos:', track_pos.model.pos
        pos = old_pos
        
        
        #for t in UIM.list('track_controller',  self.uid):
        #    print t.uid, t.model.pos
            
        #raise Exception()    
        
        if new_pos == self.view.get_adjusted_absolute_track_position(track_pos.uid):
            #print 'JAH ESTOU CERTINHO:', track_pos.uid, new_pos
            return
        #else:
            #print 'NAO ESTOU CERTINHO:', track_pos.uid, \
            #    self.view.get_adjusted_absolute_track_position(track_pos.uid), new_pos
            
        if new_pos < old_pos:
            while pos > new_pos:
                #print '\nOPCAO 1:', pos, new_pos       
                tracks_next_pos = UIM.do_query('track_controller',  self.uid, 
                                      'pos='+str(pos-1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                if len(tracks_next_pos) == 0:
                    return    
                track_next_pos = tracks_next_pos[0]
                
                #print 'track_next_pos:', track_next_pos.uid, track_next_pos.model.pos
                if not track_pos.model.overview and not track_next_pos.model.overview:  
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)
                
                #print 'Setting', track_next_pos.uid, 'to position: ',  track_next_pos.model.pos+1
                track_next_pos.model.pos += 1
                pos -= 1
        
        else:
            while pos < new_pos:
                #print '\nOPCAO 2:', pos, new_pos           
                tracks_next_pos = UIM.do_query('track_controller',  self.uid, 
                                      'pos='+str(pos+1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                    
                if len(tracks_next_pos) == 0:
                    return
                track_next_pos = tracks_next_pos[0]
                                
                #print 'track_next_pos:', track_next_pos.uid, track_next_pos.model.pos
                if not track_pos.model.overview and not track_next_pos.model.overview:      
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)

                #print 'Setting', track_next_pos.uid, 'to position: ',  track_next_pos.model.pos-11
                track_next_pos.model.pos -= 1
                pos += 1


    '''
    def _propagate_position_change(self, uid, new_value, old_value):
        UIM = UIManager()             
        if new_value < old_value:
            tracks = UIM.do_query('track_controller',  self.uid,
                                  'pos>='+str(new_value),
                                  'pos<='+str(old_value-1)
            )
            for track in tracks:
                if track.uid != uid:
                    track.model.pos += 1
                    #track.model.set_value_from_event('pos', track.model.pos+1)   
                    #track.reload_track_title()
        else:
            tracks = UIM.do_query('track_controller',  self.uid,
                                  'pos>='+str(old_value+1), 
                                  'pos<='+str(new_value)
            )
            for track in tracks:
                if track.uid != uid:
                    track.model.pos += 1
                    #track.model.set_value_from_event('pos', track.model.pos-1)   
                    #track.reload_track_title()
    '''


    def set_overview_track(self, track_uid):
        self.view.set_overview_track(track_uid)
     
    def unset_overview_track(self):
        self.view.unset_overview_track()
     


    """
    def _propagate_insertion(self, pos, uid):
        print '\n_propagate_insertion:', pos, uid
        UIM = UIManager()
        #inserted_track = UIM.get(uid)
        #if inserted_track.model.overview:
        #    return
        tracks = UIM.do_query('track_controller',  self.uid,
                              'pos>='+str(pos)
        )    
        for track in tracks:
            if track.uid != uid:
                track.model.set_value_from_event('pos', track.model.pos+1)   
                track.reload_track_title()   
    """            
                 
        
    def _propagate_deletion(self, pos, uid):
        #print '\n_propagate_deletion:', pos, uid
        UIM = UIManager()
        tracks = UIM.do_query('track_controller',  self.uid,
                              'pos>'+str(pos)
        )    
        for track in tracks:
            track.model.set_value_from_event('pos', track.model.pos-1)   
            track.reload_track_title()        
            
            
         
               
                
    def _propagate_change_width(self, uid):
        UIM = UIManager()
        obj = UIM.get(uid)
        selected =  UIM.do_query('track_controller',  self.uid,
                                 'selected=True'
        )
        for track in selected:
            if track.uid != uid:
                # TODO: retirar a linha abaixo no futuro
                track.model.selected = False  
                track.model.width = obj.model.width 
                # TODO: retirar a linha abaixo no futuro
                track.model.selected = True


    def show_status_message(self, msg):
        self.view.status_bar.SetStatusText(msg, 0)


    def show_cursor(self, xdata, ydata):
        self.view.show_cursor(xdata, ydata)
  
    
    def get_ylim(self):
       if self.model.y_min_shown is None or \
                                           self.model.y_max_shown is None:
           return (self.model.logplot_y_min, self.model.logplot_y_max)                                        
       return (self.model.y_min_shown, self.model.y_max_shown)
 
    
    def on_change_cursor_state(self, new_value, old_value):
        if new_value == LogPlotState.NORMAL_TOOL:
            UIM = UIManager()
            selected_tracks = UIM.do_query('track_controller',  self.uid,
                                       'selected=True',
                                        orderby='pos'
            )
            if selected_tracks:
                for track in selected_tracks:
                    track.model.selected = False


    def on_change_ylim(self, new_value, old_value):
        UIM = UIManager()
        y_min, y_max = self.get_ylim()
        
      #  print 'self.get_ylim():', self.get_ylim()
        for track in UIM.list('track_controller', self.uid):
            if not track.model.overview:
                track.set_ylim(y_min, y_max)
            else:
                track.reposition_depth_canvas()
        #self.update_adaptative()
#        self.view.refresh_overview()


    """
    def track_object_included(self, y_min, y_max):

        if self.model.y_min_shown == self.model.logplot_y_min \
                                            or y_min < self.model.y_min_shown:
        #    print 'Setting y_min_shown:', y_min
            self.model.y_min_shown = y_min
        if self.model.y_max_shown == self.model.logplot_y_max \
                                            or y_max > self.model.y_min_shown:
         #   print 'Setting y_min_shown:', y_min
            self.model.y_max_shown = y_max
    """    

    """
    def update_adaptative(self):
        UIM = UIManager() 
        tracks = UIM.list('track_controller', self.uid)
        if not tracks:
            return
        #print '\nupdate_adaptative'
        NUM_PX = 80
        SCALES = [1000.0, 500.0, 250.0, 100.0, 50.0, 25.0, 10.0, 
                  5.0, 2.5, 1.0, 0.5, 0.1
        ]
        height = self.view.main_panel.bottom_splitter.GetSize()[1]
        val = ((self.model.y_max_shown - self.model.y_min_shown) / float(height)) * NUM_PX
        idx = len(SCALES)-1
        for i, scale in enumerate(SCALES):
            if val > scale:
                if i==0:
                    idx = 0
                else:    
                    idx = i-1
                break
           
        for track in tracks:
            track.model.y_major_grid_lines = SCALES[idx]
            track.model.y_minor_grid_lines = SCALES[idx]/5  
        #print '\nscale chosen', SCALES[idx]    
    """
    


class LogPlotModel(WorkPageModel):
    tid = 'logplot_model'

    _ATTRIBUTES = {
        'logplot_y_min': {'default_value': 0.0, 
                          'type': float
        },
        'logplot_y_max': {'default_value': 6000.0, 
                          'type': float
        },
        'y_min_shown': {'default_value': None,
                        'type': float
        },
        'y_max_shown': {'default_value': None, 
                        'type': float
        },
        'y_major_grid_lines': {'default_value': 500.0, 
                               'type': float
        },
        'y_minor_grid_lines': {'default_value': 100.0, 
                               'type': float
        },       
        'cursor_state': {'default_value': LogPlotState.NORMAL_TOOL, 
                         'type': LogPlotState
        },
        'fit': {'default_value': False, 
                'type': bool
        },
        'multicursor': {'default_value': 'None', 
                'type': str
        }                 
    }
    _ATTRIBUTES.update(WorkPageModel._ATTRIBUTES)    
    
    def __init__(self, controller_uid, **base_state):   
        super(LogPlotModel, self).__init__(controller_uid, **base_state)   
   
                
     
class LogPlot(WorkPage):
    tid = 'logplot'

    def __init__(self, controller_uid):
        super(LogPlot, self).__init__(controller_uid) 
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        #
        '''
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.tb = LogPlotToolBar(self)     
        self.center_panel = wx.Panel(self)
        self.status_bar = PlotStatusBar(self) 
        self.vbox.Add(self.tb, 0, flag=wx.TOP|wx.EXPAND)
        self.vbox.Add(self.center_panel, 1, flag=wx.EXPAND)        
        self.vbox.Add(self.status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)                         
        self.SetSizer(self.vbox)
        '''
        #
        self.create_tool_bar()
        #
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)                    
        self.tracks_panel = LogPlotInternal(self.center_panel) 
        self.hbox.Add(self.tracks_panel, 1, wx.EXPAND) 
        self.center_panel.SetSizer(self.hbox)
        #        
        self.overview = None
        self.overview_border = 1
        self.overview_width = 60
        #
        self.overview_base_panel = wx.Panel(self.center_panel)
        self.overview_base_panel.SetBackgroundColour('black')
        self.overview_base_panel.SetInitialSize((0, 0))
        self.overview_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.overview_base_panel.SetSizer(self.overview_sizer)
        self.hbox.Add(self.overview_base_panel, 0, wx.EXPAND)
        self.hbox.Layout()
        #  
        self.Layout()
        #
        '''
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)                
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.note.GetPageCount()
        parent_controller.view.note.InsertPage(controller.model.pos, self, self.get_title(), True) 
        '''
        self.tracks_panel.top_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                          self._on_sash_pos_change
        )    
        self.tracks_panel.bottom_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                             self._on_sash_pos_change
        )         
        controller.subscribe(self.set_fit, 'change.fit')
        controller.subscribe(self.set_multicursor, 'change.multicursor')
        
        if controller.model.y_min_shown is None:
            controller.model.y_min_shown = controller.model.logplot_y_min
        if controller.model.y_max_shown is None:
            controller.model.y_max_shown = controller.model.logplot_y_max  
            
            
    def PreDelete(self):
        try:
            self.vbox.Remove(0)
            del self.tb
        except Exception, e:
            print 'PreDelete LogPlot ended with error:', e.args
        
        
    def _get_overview_track(self):
        UIM = UIManager()
        overview_tracks = UIM.do_query('track_controller', 
                                       self._controller_uid,
                                       'overview=True'
        )        
        if not overview_tracks:
            return None
        return overview_tracks[0]
    
    
    def set_overview_track(self, track_uid):
        if track_uid[0] != 'track_controller':
            raise Exception()
        UIM = UIManager()
        if self._controller_uid != UIM._getparentuid(track_uid):
            raise Exception('This LogPLot cannot set an overview Track from another Logplot.')  
        # First, we need to unset any existing overview track 
        ot = self._get_overview_track()
        if ot:
            self.unset_overview_track()
        # Then, set the new overview track
        track = UIM.get(track_uid) 
        state = track.get_state()[1]
        UIM.remove(track.uid)
        state['overview'] = True
        state['selected'] = False
        print '\n', state
        UIControllerBase.load_state(state, 'track_controller',
                                    parentuid=self._controller_uid
        )

    def unset_overview_track(self):
        ot = self._get_overview_track()
        if not ot:
            return
        self._remove_from_overview_panel()
        #self.overview_sizer.Detach(ot.view.track)
        state = ot.get_state()[1]
        UIM = UIManager()
        UIM.remove(ot.uid)
        state['overview'] = False
        UIControllerBase.load_state(state, 'track_controller',
                                           parentuid=self._controller_uid
        )        
        #self.overview_base_panel.SetInitialSize((0, 0))
        #self.hbox.Layout()          

    
    def _remove_from_overview_panel(self):
        ot = self._get_overview_track()
        self.overview_sizer.Detach(ot.view.track)
        self.overview_base_panel.SetInitialSize((0, 0))
        self.hbox.Layout()             
            
    
    def _create_windows(self, track_uid):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        track = UIM.get(track_uid)
        
        #self.label, self.track = parent_controller._create_windows(self._controller_uid)
        if not track.model.overview:
            track.view.label = PlotLabel(self.tracks_panel.top_splitter, 
                                         track.view
            ) 
            track.view.track = TrackFigureCanvas(self.tracks_panel.bottom_splitter, 
                                track.view,                      
                                size=wx.Size(track.model.width, 
                                    self.tracks_panel.bottom_splitter.GetSize()[1]
                                ),
                                y_major_grid_lines=controller.model.y_major_grid_lines,
                                y_minor_grid_lines=controller.model.y_minor_grid_lines,
                                **track.model._getstate()
            )
        else:
            track.view.label = None
            track.view.track = TrackFigureCanvas(self.overview_base_panel, #self.center_panel, 
                                track.view,                      
                                size=wx.Size(track.model.width, 
                                    self.tracks_panel.bottom_splitter.GetSize()[1]
                                ),
                                y_major_grid_lines=controller.model.y_major_grid_lines,
                                y_minor_grid_lines=controller.model.y_minor_grid_lines,
                                **track.model._getstate()
            )
            self.overview_base_panel.SetInitialSize((60, 10))
            self.overview_sizer.Add(track.view.track, 1, 
                                    wx.EXPAND|wx.ALL, self.overview_border
            )     
            self.hbox.Layout()                

        if not track.model.overview:
            self.dt1 = DropTarget(controller.get_acceptable_tids(),
                                  track.append_object
            )
        self.dt2 = DropTarget(controller.get_acceptable_tids(),
                              track.append_object
        )

           
        if not track.model.overview:    
            track.view.label.SetDropTarget(self.dt1)        
        track.view.track.SetDropTarget(self.dt2)
            
        if track.model.pos == -1:
            # aqui controller.size jah inclui track
            track.model.pos = controller.size - 1
        

        track.view.track.update_multicursor(controller.model.multicursor)
        
        
        #print 'inserindo na pos:',  track.model.pos 
        pos = track.model.pos
        #pos = self.get_real_position_in_splitter(track)
        #print 'inserindo na pos:',  track.model.pos   
        
        #controller._propagate_insertion(track.model.pos, 
        #                                      track.uid
        #)
        
        #UIM = UIManager()
        #inserted_track = UIM.get(uid)
        #if inserted_track.model.overview:
        #    return
        tracks_affected = UIM.do_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(pos)
        )    
        
        """
        print
        print track.uid, pos
        for track_affected in tracks_affected:
            
            print track_affected.uid, track_affected.model.pos
            
            if track_affected.uid != track.uid:
                track_affected.model.set_value_from_event('pos', 
                                    track_affected.model.pos+1
                )   
        """
        self._adjust_up_pos(track.uid, pos)          
        if not track.model.overview:     
            self.tracks_panel.insert(pos, track.view.label, 
                                          track.view.track,
                                          track.model.width
            )

            
            for track_affected in tracks_affected:
                if track_affected.uid != track.uid:
                    track_affected.reload_track_title() 
             
            
            track.set_ylim(controller.model.y_min_shown, 
                           controller.model.y_max_shown
            )

        else:
            
            track.set_ylim(controller.model.logplot_y_min, 
                           controller.model.logplot_y_max
            )
        



    def _adjust_up_pos(self, track_uid, from_pos):
       # print '\n_adjust_up_pos:', track_uid, from_pos
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if from_pos >= controller.size:
            return
        track = UIM.get(track_uid)
        tracks_affected = UIM.do_query('track_controller',  
                                            self._controller_uid,
                                            'pos='+str(from_pos)
        )    
        if len(tracks_affected) == 0:
            #for t in UIM.list('track_controller', self._controller_uid):
             #   print t.uid, t.model.pos
            raise Exception('HAVIA ERRO ==0')
        elif len(tracks_affected) == 1:
            return
           # print 'SOH TEM EU - TUDO OK - NADA A FAZER'
        elif len(tracks_affected) == 2:
            tracks_affected.remove(track)
            other_track = tracks_affected[0]
            other_track.model.set_value_from_event('pos', 
                                    from_pos+1
            )
            self._adjust_up_pos(other_track.uid, from_pos+1)
        else:
            raise Exception('HAVIA ERRO >2')


    # Posicao absoluta considera os tracks invisiveis
    # Posicao relativa considera somente os tracks visiveis
    # Posicao -1 retorna overview track ou None se nao existir overview
    def get_track_on_position(self, pos, relative_position=True): 
        if pos == -1:
            return self._get_overview_track()

        if relative_position:
            pos = self.tracks_panel.bottom_splitter.get_windows_indexes_shown()[pos]
        top = self.tracks_panel.top_splitter.GetWindow(pos)
        bottom = self.tracks_panel.bottom_splitter.GetWindow(pos)
        UIM = UIManager()
        tracks = UIM.list('track_controller', self._controller_uid)
        for track in tracks:
            if (top, bottom) == track._get_windows():
                return track


    # Posicao absoluta considera os tracks invisiveis
    # Posicao relativa considera somente os tracks visiveis
    # retorna -1 se o track for overview
    # gera exception se o track nao for filho deste logplot
    def get_track_position(self, track_uid, relative_position=True):  
        UIM = UIManager()
        if UIM._getparentuid(track_uid) != self._controller_uid:
            raise Exception()
        track = UIM.get(track_uid)    
        if track.model.overview:
            return -1 
        _, bottom = track._get_windows()
        #if relative_position:
        #    return self.tracks_panel.bottom_splitter.GetVisibleIndexOf(bottom)
        #return self.tracks_panel.bottom_splitter.IndexOf(bottom)
        if relative_position:
            ret = self.tracks_panel.bottom_splitter.GetVisibleIndexOf(bottom)
        else:
            ret = self.tracks_panel.bottom_splitter.IndexOf(bottom)           
        #print 'get_track_position({}, {}): {}'.format(track_uid, relative_position, ret)    
        return ret    


    # Posicao absoluta, considerando overview
    def get_adjusted_absolute_track_position(self, track_uid):  
        pos = self.get_track_position(track_uid, False)
        UIM = UIManager()
        track = UIM.get(track_uid)           
        ot = self._get_overview_track()
        if ot and ot.model.pos < track.model.pos:
            pos -= 1
        return pos   
    


    def change_absolute_track_position_on_splitter(self, track_uid, new_pos):
        UIM = UIManager()
        track = UIM.get(track_uid)   
        top, bottom = track._get_windows()
        self.tracks_panel.top_splitter.ChangeWindowPosition(top, new_pos)
        self.tracks_panel.bottom_splitter.ChangeWindowPosition(bottom, new_pos)


    def refresh_overview(self):
        self.overview_track._reload_canvas_positions_from_depths()


    def _detach_windows(self, label, track):
        try:
            self.tracks_panel.top_splitter.DetachWindow(label)
            self.tracks_panel.bottom_splitter.DetachWindow(track)  
        except Exception, e:
            msg = 'Error in LogPlot._detach_windows: ' + e.args
            log.exception(msg)
            print msg


    def show_track(self, track_uid, show):
        UIM = UIManager()
        track = UIM.get(track_uid)
        if track.view.label:
            self.tracks_panel.top_splitter.ShowWindow(track.view.label, show)
        if not track.model.overview:   
            self.tracks_panel.bottom_splitter.ShowWindow(track.view.track, show)
        else:
            raise Exception('show_track overview track???')
            
        tracks_affected= UIM.do_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(track.model.pos)
        )    
        for track_affected in tracks_affected:
            if track_affected.uid != track.uid:
                #print 'track_affected.uid:', track_affected.uid
                track_affected.reload_track_title() 
           
        
        
        
    def _set_new_depth(self, min_max):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        # To trigger only one LogPlotController.on_change_ylim
        controller.model.set_value_from_event('y_min_shown', min_max[0])
        controller.model.y_max_shown = min_max[1]


    def _on_sash_pos_change(self, event):
        idx = event.GetSashIdx()
        new_width = event.GetSashPosition()
        track_ctrl = self.get_track_on_position(idx)
        track_ctrl.model.width = new_width


    def _on_bottom_splitter_size(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.update_adaptative()
        
        
    def _do_change_width(self, idx, width, event_object=None):
        
        self.tracks_panel.top_splitter._sashes[idx] = width
        self.tracks_panel.bottom_splitter._sashes[idx] = width
        
        if self.tracks_panel.top_splitter._windows[idx].IsShown():
            self.tracks_panel.top_splitter._SizeComponent()  
        if self.tracks_panel.bottom_splitter._windows[idx].IsShown():
            self.tracks_panel.bottom_splitter._SizeComponent()              
        
        #self.tracks_panel.bottom_splitter._DoSetSashPosition(idx, width)
        #self.tracks_panel.bottom_splitter._SizeComponent()
        #self.tracks_panel.top_splitter._DoSetSashPosition(idx, width)
        #self.tracks_panel.top_splitter._SizeComponent()    

    #def _insert(self, pos, label_window, track_window, width):
    #    self.tracks_panel.insert(pos, label_window, track_window, width)
                                                                                  
    #def get_title(self):
    #    return 'Log Plot [oid:' + str(self._controller_uid[1]) + ']'     

    def _on_toolbar_insert_track(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.insert_track()   

    def _on_toolbar_remove_track(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.remove_selected_tracks()   

    def _on_change_tool(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        if event.GetId() == LP_NORMAL_TOOL:
            controller.model.cursor_state = LogPlotState.NORMAL_TOOL
        elif event.GetId() == LP_SELECTION_TOOL:    
            controller.model.cursor_state = LogPlotState.SELECTION_TOOL
        else:
            raise Exception()    

    def _OnEditFormat(self, event): 
        UIM = UIManager()
        lp_editor_ctrl = UIM.create('log_plot_editor_controller', 
                                    self._controller_uid
        )
        lp_editor_ctrl.view.Show()							  


    def _on_fit(self, event): 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.model.fit = event.IsChecked()
 
    
    def set_fit(self, new_value, old_value):
        self.tracks_panel.top_splitter._SetFit(new_value)
        self.tracks_panel.bottom_splitter._SetFit(new_value)        

            
    def _on_multicursor(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.model.multicursor = event.GetString()
        

    def set_multicursor(self, new_value, old_value):        
        UIM = UIManager() 
        tracks = UIM.list('track_controller', self._controller_uid)
        if not tracks:
            return               
        for track in tracks:
            track.view.track.update_multicursor(new_value)

            
    def show_cursor(self, xdata, ydata):
        UIM = UIManager() 
        tracks = UIM.list('track_controller', self._controller_uid)
        if not tracks:
            return        
        for track in tracks:
            track.view.track.show_cursor(xdata, ydata)     
        
        
    def create_tool_bar(self):
        self.tool_bar.AddTool(LP_NORMAL_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self.tool_bar.ToggleTool(LP_NORMAL_TOOL, True) 
        #
        self.tool_bar.AddTool(LP_SELECTION_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self.tool_bar.Bind(wx.EVT_TOOL, self._on_change_tool, None,
                  LP_NORMAL_TOOL, LP_SELECTION_TOOL
        )
        #
        self.tool_bar.AddSeparator()
        #
        tb_item = self.tool_bar.AddTool(-1, u"Insert Track", 
                                  wx.Bitmap('./icons/table_add_24.png'),
                                  'Insert a new track'
        )
        self.tool_bar.Bind(wx.EVT_TOOL, self._on_toolbar_insert_track, tb_item)
        #
        tb_item = self.tool_bar.AddTool(-1, u"Remove Track", 
                                  wx.Bitmap('./icons/table_delete_24.png'),
                                 'Remove selected tracks'
        )
        self.tool_bar.Bind(wx.EVT_TOOL, self._on_toolbar_remove_track, tb_item)
        #
        self.tool_bar.AddSeparator()  
        #
        button_edit_format = wx.Button(self.tool_bar, label='Edit LogPlot')
        button_edit_format.Bind(wx.EVT_BUTTON , self._OnEditFormat)
        self.tool_bar.AddControl(button_edit_format, '')
        self.tool_bar.AddSeparator()    
        #    
        self.tool_bar.cbFit = wx.CheckBox(self.tool_bar, -1, 'Fit')        
        self.tool_bar.cbFit.Bind(wx.EVT_CHECKBOX , self._on_fit) 
        self.tool_bar.AddControl(self.tool_bar.cbFit, '')    
        #
        self.tool_bar.AddSeparator() 
        self.tool_bar.label_MC = wx.StaticText(self.tool_bar, label='Multi cursor:  ')
        #self.tool_bar.label_MC.SetLabel('Multi cursor:')
        self.tool_bar.AddControl(self.tool_bar.label_MC, '')
        self.tool_bar.choice_MC = wx.Choice(self.tool_bar, choices=['None', 'Horizon', 'Vertical', 'Both'])  
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        idx_mc = ['None', 'Horizon', 'Vertical', 'Both'].index(controller.model.multicursor)
        self.tool_bar.choice_MC.SetSelection(idx_mc)
        self.tool_bar.choice_MC.Bind(wx.EVT_CHOICE , self._on_multicursor) 
        self.tool_bar.AddControl(self.tool_bar.choice_MC, '')    
        #
        self.tool_bar.AddSeparator() 
        self.tool_bar.Realize()  
        
    
