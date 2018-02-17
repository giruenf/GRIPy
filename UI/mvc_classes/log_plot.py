# -*- coding: utf-8 -*-
import wx
from OM.Manager import ObjectManager
from workpage import WorkPageController
from workpage import WorkPageModel
from workpage import WorkPage
from UI.uimanager import UIManager
from UI.logplot_internal import LogPlotInternal
from App.app_utils import LogPlotState  
from App import log   
from mpl_base import TrackFigureCanvas, PlotLabel
from App.app_utils import DropTarget

from DT.DataTypes import VALID_Z_AXIS_DATATYPES


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
        #
        UIM = UIManager()
        UIM.subscribe(self._post_remove, 'post_remove')


    def _post_remove(self, objuid):
        if objuid[0] != self.tid:
            return
        if self.uid != objuid:
            self.view.set_own_name()


    @property
    def size(self):
        UIM = UIManager()
        return len(UIM.list('track_controller', self.uid))
    
    
    @staticmethod
    def get_acceptable_tids():
        return ['log', 'index_curve', 'partition', 'seismic', 'scalogram', 
                'velocity', 'angle', 'gather', 'model1d']


    def is_valid_object(self, obj_uid):
        return True
        """
        OM = ObjectManager(self)
        if obj_uid[0] == 'index_set':
            return False
        parent_uid = OM._getparentuid(obj_uid)
        if obj_uid[0] == 'data_index':
            granpa_uid = OM._getparentuid(parent_uid)
            return granpa_uid[0] == 'well' and granpa_uid[1] == self.model.well_oid
        parent_uid = OM._getparentuid(obj_uid)
        try:
            return parent_uid[0] == 'well' and parent_uid[1] == self.model.well_oid
        except:
            return False
        """    
    
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
        if not selected_tracks:
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=self.size
            )
            return [new_track.uid]         
        ret_list = []    
        
        for track in selected_tracks:											 
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
        UIM = UIManager()
        track_pos = UIM.get(track_uid)
        pos = old_pos
        if new_pos == self.view.get_adjusted_absolute_track_position(track_pos.uid):
            return
        if new_pos < old_pos:
            while pos > new_pos:     
                tracks_next_pos = UIM.do_query('track_controller',  self.uid, 
                                      'pos='+str(pos-1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                if len(tracks_next_pos) == 0:
                    return    
                track_next_pos = tracks_next_pos[0]
                if not track_pos.model.overview and not track_next_pos.model.overview:  
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)
                track_next_pos.model.pos += 1
                pos -= 1
        
        else:
            while pos < new_pos: 
                tracks_next_pos = UIM.do_query('track_controller',  self.uid, 
                                      'pos='+str(pos+1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                    
                if len(tracks_next_pos) == 0:
                    return
                track_next_pos = tracks_next_pos[0]
                if not track_pos.model.overview and not track_next_pos.model.overview:      
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)
                track_next_pos.model.pos -= 1
                pos += 1     
                 
        
    def _propagate_deletion(self, pos, uid):
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


    
    #def show_cursor(self, xdata, ydata):
    def show_cursor(self, event_on_track_ctrl_uid, xdata, ydata):    
        self.view.show_cursor(event_on_track_ctrl_uid, xdata, ydata)
  
    
    def get_ylim(self):
       if self.model.y_min_shown is None or \
                                           self.model.y_max_shown is None:
           raise Exception()                                    
           #return (self.model.logplot_y_min, self.model.logplot_y_max)                                        
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
        #print '\n\non_change_ylim:', new_value, old_value
        self._reload_ylim()
                

    def _reload_ylim(self):
        UIM = UIManager()
        y_min, y_max = self.get_ylim()
        #print self.get_ylim()
        for track in UIM.list('track_controller', self.uid):
            track.set_ylim(y_min, y_max)
            if track.model.overview:
                track.reposition_depth_canvas()
        self.view._reload_z_axis_textctrls()        
         
        #self.update_adaptative()
#        self.view.refresh_overview()




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
        'well_oid': {
                'default_value': None,
                'type': int    
        },
        'logplot_y_min': {'default_value': None, 
                          'type': float
        },
        'logplot_y_max': {'default_value': None, 
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
        },
        'index_type': {'default_value': None, 
                'type': str
        }   
    }
    _ATTRIBUTES.update(WorkPageModel._ATTRIBUTES)    
    
    def __init__(self, controller_uid, **base_state):   
        super(LogPlotModel, self).__init__(controller_uid, **base_state)   
   
                
     
        
        
class LogPlot(WorkPage):
    
    tid = 'logplot'
    _FRIENDLY_NAME = 'Well Plot'
    
    
    def __init__(self, controller_uid):
        super(LogPlot, self).__init__(controller_uid) 
        self.set_own_name()
        self.create_tool_bar()
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)                    
        self.tracks_panel = LogPlotInternal(self.center_panel) 
        self.hbox.Add(self.tracks_panel, 1, wx.EXPAND) 
        self.center_panel.SetSizer(self.hbox)      
        self.overview = None
        self.overview_border = 1
        self.overview_width = 60
        self.overview_base_panel = wx.Panel(self.center_panel)
        self.overview_base_panel.SetBackgroundColour('black')
        self.overview_base_panel.SetInitialSize((0, 0))
        self.overview_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.overview_base_panel.SetSizer(self.overview_sizer)
        self.hbox.Add(self.overview_base_panel, 0, wx.EXPAND)
        self.hbox.Layout()
        self.Layout()
        self.tracks_panel.top_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                          self._on_sash_pos_change
        )    
        self.tracks_panel.bottom_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                             self._on_sash_pos_change
        )         

        
    def PostInit(self):
     #   print '\nLogPlot.PostInit'
                
        OM = ObjectManager(self)
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        
        controller.subscribe(self.set_fit, 'change.fit')
        controller.subscribe(self.set_multicursor, 'change.multicursor')
        controller.subscribe(self.set_index_type, 'change.index_type')
        
        ###
        self._prepare_index_data()
        self.overview_track = UIM.create('track_controller', 
                                         self._controller_uid,
                                         overview=True, plotgrid=False                            
        )
        ###
        

        well = OM.get(('well', controller.model.well_oid))
        for z_axis_dt in well.get_z_axis_datatypes().values():
            self.tool_bar.choice_IT.Append(z_axis_dt)
        

        
        idx_index_type = self.tool_bar.choice_IT.GetItems().index(controller.model.index_type)
        self.tool_bar.choice_IT.SetSelection(idx_index_type)

        self.ot_toc = None
        self.set_index_type(controller.model.index_type, None)
        self.tool_bar.choice_IT.Bind(wx.EVT_CHOICE , self._on_index_type) 
        
        #ot_toc = self.overview_track.append_object(self._zaxis_uid)
        #ot_toc_repr_ctrl = ot_toc.get_representation()
        # TODO: Update Adaptative
        #ot_toc_repr_ctrl.model.step = 200
        #
        
        #

        #
        
        
        #
        controller.subscribe(self.on_change_logplot_ylim, 'change.logplot_y_min')
        controller.subscribe(self.on_change_logplot_ylim, 'change.logplot_y_max')   
        
        #print 'b4 self._reload_z_axis_textctrls'
        
        self._reload_z_axis_textctrls()
        
        
      #  print 'LogPlot.PostInit ENDED'


    def set_own_name(self):
        OM = ObjectManager(self)
        UIM = UIManager()   
        controller = UIM.get(self._controller_uid)
        idx = 0
        well = OM.get(('well', controller.model.well_oid))
        lpcs = UIM.list('logplot_controller')
        for lpc in lpcs:
            if lpc == controller:
                break
            if lpc.model.well_oid == controller.model.well_oid:
                idx += 1
        idx += 1
        #print '\nset_own_name:', self._controller_uid, controller.model.pos, idx
        controller.model.title = self._FRIENDLY_NAME + ': ' + well.name + \
                                    ' ['+ str(idx) + ']'    
                                    #' ['+ str(self._controller_uid[1]+1) + ']'            
    
    
    def _prepare_index_data(self):
   #     print '\nLogPlot._prepare_index_data'
        OM = ObjectManager(self)
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        try:
            well = OM.get(('well', controller.model.well_oid))
        except:
            raise
            
        min_ = 100000
        max_ = -1
        
        data_indexes_uid = well.get_friendly_indexes_dict().values()
        zaxis = []
        
        for data_index_uid in data_indexes_uid:
            data_index = OM.get(data_index_uid)
            if controller.model.index_type == data_index.datatype:
                if data_index.start < min_:
                    min_ = data_index.start
                if data_index.end > max_:
                    max_ = data_index.end   
                zaxis.append(data_index)    
                
        #print '\nLogPlot._prepare_index_data:', min_, max_        
                
        controller.model.logplot_y_min = min_
        controller.model.logplot_y_max = max_
        controller.model.y_min_shown = min_
        controller.model.y_max_shown = max_
        
        if len(zaxis) > 1 or len(zaxis) == 0:
            print 'ATENCAO COM Z-AXIS!'
            

        self._zaxis_uid = zaxis[0].uid
    #    print 'LogPlot._prepare_index_data FIM'

                

    def on_change_logplot_ylim(self, new_value, old_value):
        #raise Exception('Cannot do it!')
        self._reload_z_axis_textctrls()
        
        
    def _reload_z_axis_textctrls(self):    
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        #self.overview_track.set_ylim(controller.model.y_min_shown, controller.model.logplot_y_max)
        z_start_str = "{0:.2f}".format(controller.model.y_min_shown)
        self.tool_bar.z_start.SetValue(z_start_str)
        z_end_str = "{0:.2f}".format(controller.model.y_max_shown)
        self.tool_bar.z_end.SetValue(z_end_str)
        #print '\n_reload_z_axis_textctrls:', z_start_str, z_end_str
        

    def on_change_z_start(self, event):
        print 'on_change_z_start:', event.GetString()

    def on_change_z_end(self, event):
        print 'on_change_z_end:', event.GetString()
        

    """
    # Method for Drag and Drop....
    def append_object(self, obj_uid):
        UIM = UIManager()
        #print 111
        toc = UIM.create('track_object_controller', self.uid)  
        tid, oid = obj_uid
        #print 222
        toc.model.obj_tid = tid
        #print 333
        toc.model.obj_oid = oid
        return toc
    """
    

    '''
    def _set_index_data(self):
        self.overview_track.set_ylim(min_, max_)
        self.overview_track.append_object(zaxis[0].uid)
    '''    
        

    """    
    def _get_overview_track(self):
        UIM = UIManager()
        overview_tracks = UIM.do_query('track_controller', 
                                       self._controller_uid,
                                       'overview=True'
        )        
        if not overview_tracks:
            return None
        return overview_tracks[0]
    """
    
    """
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
    """    


    '''
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
    '''
    
    
    def _remove_from_overview_panel(self):
        self.overview_sizer.Detach(self.overview_track.view.track)
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
            self.dt1 = DropTarget(controller.is_valid_object,
                                  track.append_object
            )
        self.dt2 = DropTarget(controller.is_valid_object,
                              track.append_object
        )

           
        if not track.model.overview:    
            track.view.label.SetDropTarget(self.dt1)        
        track.view.track.SetDropTarget(self.dt2)
            
        if track.model.pos == -1:
            # aqui controller.size jah inclui track
            track.model.pos = controller.size - 1
        
        track.view.track.update_multicursor(controller.model.multicursor)

        pos = track.model.pos

        tracks_affected = UIM.do_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(pos)
        )    
        
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


    def _OnResetZAxis(self, event): 
        #UIM = UIManager()
        self._prepare_index_data()


    def _OnSetZAxis(self, event): 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        try:
            zstart = float(self.tool_bar.z_start.GetValue())
            zend = float(self.tool_bar.z_end.GetValue())
            if not round(zstart, 2) >= round(controller.model.logplot_y_min, 2):
                
                raise Exception('AAA: ', str(zstart) + '   '+ str(controller.model.logplot_y_min))
                
            if not round(zend, 2) <= round(controller.model.logplot_y_max, 2):
                raise Exception('BBB: ', str(zend) + '   '+ str(controller.model.logplot_y_max))              
        except Exception as e:
            print 'ERROR:', e
            self._reload_z_axis_textctrls()
            return
        #controller.model.set_value_from_event('logplot_y_min', zstart)
        #controller.model.logplot_y_max = zend

        #
        controller.model.set_value_from_event('y_min_shown', zstart)
        controller.model.set_value_from_event('y_max_shown', zend)
        controller._reload_ylim()
            


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

    def _on_index_type(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.model.index_type = event.GetString()
        

    def set_multicursor(self, new_value, old_value):        
        UIM = UIManager() 
        tracks = UIM.list('track_controller', self._controller_uid)
        if not tracks:
            return               
        for track in tracks:
            track.view.track.update_multicursor(new_value)



    def set_index_type(self, new_value, old_value):     
      #  print '\n\n\nset_index_type:', new_value, old_value

        UIM = UIManager() 
        self._prepare_index_data()
        
        # TODO: Find a more Pythonic way to write aboxe
        for track_ctrl in UIM.list('track_controller', self._controller_uid):
            
            if track_ctrl.model.overview:
        #        print 'overview'
                if self.ot_toc:
                    UIM.remove(self.ot_toc.uid)    
        #        print self._zaxis_uid    
                self.ot_toc = self.overview_track.append_object(self._zaxis_uid) 
                #ot_toc = self.overview_track.append_object(self._zaxis_uid)
                #ot_toc_repr_ctrl = self.ot_toc.get_representation()
                # TODO: Update Adaptative
                #ot_toc_repr_ctrl.model.step = 200
                
            else:
                for toc_ctrl in UIM.list('track_object_controller', track_ctrl.uid):
                    filter_ = toc_ctrl.get_filter()
                    filter_.reload_z_dimension_indexes()
                    toc_ctrl._do_draw() 
                

      
    def show_cursor(self, event_on_track_ctrl_uid, xdata, ydata):
        UIM = UIManager() 
        tracks = UIM.list('track_controller', self._controller_uid)
        if not tracks:
            return        
        for track in tracks:
            if track.uid == event_on_track_ctrl_uid:
                track.view.track.show_cursor(xdata, ydata, True)
            else:
                track.view.track.show_cursor(xdata, ydata, False)
        
        
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
        button_edit_format = wx.Button(self.tool_bar, label='Edit Plot')
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
        #
        self.tool_bar.label_IT = wx.StaticText(self.tool_bar, label='Z Axis:  ')
        self.tool_bar.AddControl(self.tool_bar.label_IT, '')
        
        self.tool_bar.choice_IT = wx.Choice(self.tool_bar, choices=[])
        #
        #controller = UIM.get(self._controller_uid)
        #idx_index_type = ['MD', 'TVD', 'TVDSS', 'TWT', 'TIME'].index(controller.model.index_type)
        #self.tool_bar.choice_IT.SetSelection(idx_index_type)
        #self.tool_bar.choice_IT.Bind(wx.EVT_CHOICE , self._on_index_type) 
        self.tool_bar.AddControl(self.tool_bar.choice_IT, '')    
        #
       # self.tool_bar.AddSeparator()  
        static_z_start = wx.StaticText(self.tool_bar, label='Start:')
        self.tool_bar.AddControl(static_z_start, '')
        self.tool_bar.z_start = wx.TextCtrl(self.tool_bar, size=(60, 23))
        #self.tool_bar.z_start.Enable(False)
        #self.tool_bar.z_start.Bind(wx.EVT_TEXT, self.on_change_z_start)
        self.tool_bar.AddControl(self.tool_bar.z_start, '')
        static_z_end = wx.StaticText(self.tool_bar, label='End:')
        self.tool_bar.AddControl(static_z_end, '')    
        self.tool_bar.z_end = wx.TextCtrl(self.tool_bar, size=(60, 23))
        #self.tool_bar.z_end.Enable(False)
        #self.tool_bar.z_end.Bind(wx.EVT_TEXT, self.on_change_z_end)
        self.tool_bar.AddControl(self.tool_bar.z_end, '')        
        #
        button_set_zaxis = wx.Button(self.tool_bar, label='Set', size=(40, 23))
        button_set_zaxis.Bind(wx.EVT_BUTTON , self._OnSetZAxis)
        self.tool_bar.AddControl(button_set_zaxis, '')
        #
        #self.tool_bar.AddSeparator()
        button_reset_zaxis = wx.Button(self.tool_bar, label='Reset', size=(40, 23))
        button_reset_zaxis.Bind(wx.EVT_BUTTON , self._OnResetZAxis)
        self.tool_bar.AddControl(button_reset_zaxis, '')
        self.tool_bar.AddSeparator()
        #
        self.tool_bar.Realize()  
        #
