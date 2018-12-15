# -*- coding: utf-8 -*-

import wx

from classes.om import ObjectManager
from ui.mvc_classes.workpage import WorkPageController
from ui.mvc_classes.workpage import WorkPageModel
from ui.mvc_classes.workpage import WorkPage
from classes.ui import UIManager
from ui.plotstatusbar import PlotStatusBar
from ui.wellplot_internal import WellPlotInternal
from app.app_utils import WellPlotState   
from app.app_utils import GripyBitmap  
from app import log  


LP_FLOAT_PANEL = wx.NewId() 
LP_NORMAL_TOOL = wx.NewId()        
LP_SELECTION_TOOL = wx.NewId()     
LP_ADD_TRACK = wx.NewId()     
LP_REMOVE_TRACK = wx.NewId()     
    
  



class WellPlotController(WorkPageController):    
    """
    The :class:`WellPlotController` ...
    """    
    
    tid = 'wellplot_controller'
        
    def __init__(self):
        super(WellPlotController, self).__init__()  

    def PostInit(self):
        self.subscribe(self.on_change_cursor_state, 'change.cursor_state')
        self.subscribe(self._reload_ylims, 'change.shown_ylim')
        #self.subscribe(self._reload_ylims, 'change.y_max_shown')
        # Then subscribe to UIManager in order to adjust Notebook page name 
        # after another WellPlot was removed.
        UIM = UIManager()
        UIM.subscribe(self._post_remove_well_plot, 'post_remove')
             
    def __len__(self):
        """
        Returns the number of :class:`~GRIPy-3.ui.mvc_classes.TrackController`
        owned by this object.

        Returns
        -------
        lenght : int        
        
        """
        UIM = UIManager()
        return len(UIM.list('track_controller', self.uid))        
        
    def _post_remove_well_plot(self, objuid):
        """
        Function called by UIManager after any WellPlotController removal.
        
        Used as bridge to call a :class:`WellPlot` function responsible to 
        adjust its wx.Notebook page name.
        
        """             
        if objuid[0] != self.tid:
            return
        if self.uid != objuid:
            # Call view object function using bypass (see 
            # UIControllerObject.__getattribute__)
            self._set_own_name()

    def _get_overview_track(self):
        """
        Returns the overview TrackController, if it exists. 
        
        Returns
        -------
        track : :class:`~GRIPy-3.ui.mvc_classes.TrackController`
            The track placed as Overview, or None if it does not exist.        
        """
        UIM = UIManager() 
        query_list = UIM.do_query('track_controller', 
                                   self._controller_uid, 'overview=True'
        )
        track = None
        if query_list:
            track = query_list[0]
        return track


    def insert_track(self):
        """
        Insert new tracks.
        
        If there is any selected track, create a new 
        :class:`~GRIPy-3.ui.mvc_classes.TrackController` at last position.
        Instead, for every selected track creates a new
        :class:`~GRIPy-3.ui.mvc_classes.TrackController` object one position
        before.
        
        Returns
        -------
        new_tracks_uids : list       
            A list containing :class:`~GRIPy-3.ui.mvc_classes.TrackController` 
            objects uids.
        """
        UIM = UIManager()
        selected_tracks = UIM.do_query('track_controller', self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        if not selected_tracks:
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=len(self)
            )
            return [new_track.uid]         
        new_tracks_uids = []    
        
        for track in selected_tracks:											 
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=track.model.pos
            )
            new_tracks_uids.append(new_track.uid)            
        return new_tracks_uids

    def remove_selected_tracks(self):
        """
        Remove selected :class:`~GRIPy-3.ui.mvc_classes.TrackController` on 
        :class:`WellPlot`.
        """
        UIM = UIManager()
        selected_tracks = UIM.do_query('track_controller',  self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        for track in selected_tracks:
            UIM.remove(track.uid)  

    def _adjust_positions_after_track_deletion(self, pos):
        """
        Adjust tracks position after a deletion.
        
        When one track (or more) is (are) deleted, the others with positions 
        greater must have their positions adjusted. This change must not 
        generate model events
        """
        UIM = UIManager()
        tracks = UIM.do_query('track_controller', self.uid, 'pos>'+str(pos))
        for track in tracks:
            track.model.set_value_from_event('pos', track.model.pos-1)   
            track.reload_track_title()        
                            
    def _change_width_for_selected_tracks(self, dragged_track_uid):
        """
        Change width for a group of selected tracks.
        
        When some :class:`~GRIPy-3.ui.mvc_classes.TrackController` objects are
        selected and one of then have its width changed by a sash drag, the
        others will have the same new width.
        
        Parameters
        ----------
        dragged_track_uid : :class:`~GRIPy-3.ui.mvc_classes.TrackController` uid.
            The track identificator for whose have its sash dragged.        
        
        """
        UIM = UIManager()
        dragged_track = UIM.get(dragged_track_uid)
        selected =  UIM.do_query('track_controller', self.uid, 'selected=True')
        for track in selected:
            if track.uid != dragged_track_uid:
                # TODO: retirar a linha abaixo no futuro
                track.model.selected = False  
                track.model.width = dragged_track.model.width 
                # TODO: retirar a linha abaixo no futuro
                track.model.selected = True

    def on_change_cursor_state(self, *args):
        """
        Unselect all tracks when WellPlotState.NORMAL_TOOL is trigged.
        
        Parameters
        ----------
        tool : WellPlotState.
            Tool type setted by user.             
        """
        tool = args[0]
        if tool != WellPlotState.NORMAL_TOOL:
            return
        UIM = UIManager()
        selected_tracks = UIM.do_query('track_controller',  self.uid,
                                   'selected=True',
                                    orderby='pos'
        )
        if selected_tracks:
            for track in selected_tracks:
                track.model.selected = False
                    

#    def on_change_ylim(self, new_value, old_value):
#        self._reload_ylim()
                

    # TODO: y or z???
    def _reload_ylims(self, *args):
        ymin, ymax = self.model.shown_ylim
        if ymin < 0 or ymax < 0:
            raise Exception() 
        UIM = UIManager()
        for track in UIM.list('track_controller', self.uid):
            track.set_ylim(ymin, ymax)
            if track.model.overview:
                track.reposition_depth_canvas()
        self.view._reload_z_axis_textctrls()   

                    


    # TODO: REVER ESSA FUNCAO
    '''
    def change_track_position(self, track_uid, old_pos, new_pos):
        """
        Change track position.
        
        :class:`~GRIPy-3.ui.mvc_classes.TrackController`
        
        Parameters
        ----------
        track_uid : :class:`~GRIPy-3.ui.mvc_classes.TrackController` uid.
            The track identificator.

        labelpad : scalar, optional, default: None
            Spacing in points between the label and the x-axis.        
        
        """
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
    
    '''
    
    # TODO: REVER ESSA FUNCAO
    """
    def show_track(self, track_uid, show):
        # Adjust track.model...
        UIM = UIManager()
        track = UIM.get(track_uid)
        track.model.visible = show
        self.view.show_track(track_uid, show)
    """
    
    


    # TODO: REVER ESSA FUNCAO
    """
    def _pre_delete_overview_track(self):
        self.view._remove_from_overview_panel()
    """

                  


    """
    def get_shown_ylim(self):
        ymin, ymax = self.model.shown_ylim
        if ymin < 0 or ymax < 0:
            raise Exception()                                                                      
        return shown_ylim
    """
    



     
         





class WellPlotModel(WorkPageModel):
    tid = 'wellplot_model'

    _ATTRIBUTES = {            
        'well_oid': {
                'default_value': None,
                'type': int    
        },
                
        'wellplot_ylim': {
                'default_value': (-9999.25, -9999.25), 
                'type': (tuple, float, 2)  
        },                  
        'shown_ylim': {
                'default_value': (-9999.25, -9999.25), 
                'type': (tuple, float, 2)  
        },                 
        'y_major_grid_lines': {'default_value': 500.0, 
                               'type': float
        },
        'y_minor_grid_lines': {'default_value': 100.0, 
                               'type': float
        },       
        'cursor_state': {'default_value': WellPlotState.NORMAL_TOOL, 
                         'type': WellPlotState
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
    
    def __init__(self, controller_uid, **base_state):   
        super().__init__(controller_uid, **base_state)   
   
                
     
        
        
class WellPlot(WorkPage):
    
    tid = 'wellplot'
    _FRIENDLY_NAME = 'Well Plot'
        
    def __init__(self, controller_uid):   
        super().__init__(controller_uid) 
        # Top
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._tool_bar =  wx.aui.AuiToolBar(self)
        self.sizer.Add(self._tool_bar, 0, flag=wx.TOP|wx.EXPAND)
        # Center    
        self._main_panel = wx.Panel(self)
        self.sizer.Add(self._main_panel, 1, flag=wx.EXPAND)
        # Bottom
        self._status_bar =  PlotStatusBar(self)
        self.sizer.Add(self._status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)
        self.SetSizer(self.sizer)
        #
        # Then, let's construct our ToolBar
        self._build_tool_bar()
        #
        # Main panel is subdivided into a Tracks panel on left side and 
        # a Overview panel in right side. The last one is used as a 'ruler' to
        # guide data navigation (zoom in and  zoom out).
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        #
        # The tracks panel is a horizontal wx.SplitterWindow object containing
        # 2 wx.MultiSplitterWindow (redesigned). In each of these, Track labels
        # canvas and Track data canvas are respectively placed. 
        self.tracks_panel = WellPlotInternal(self._main_panel) 
        self.hbox.Add(self.tracks_panel, 1, wx.EXPAND) 
        #
#        """
        # Overview
        self.overview = None
        self.overview_border = 1
        self.overview_width = 60
        self.overview_base_panel = wx.Panel(self._main_panel)
        self.overview_base_panel.SetBackgroundColour('black')
        self.overview_base_panel.SetInitialSize((0, 0))
        self.overview_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.overview_base_panel.SetSizer(self.overview_sizer)
        self.hbox.Add(self.overview_base_panel, 0, wx.EXPAND)
        #
#        """
        self._main_panel.SetSizer(self.hbox)
        self.hbox.Layout()
        self.Layout()
        # 
        # When a sash (width bar) changes Panel width in a MultiSplitterWindow
        # the other one must answer with same change. For example, if a user
        # drags the sash at a Track data canvas, its Track label canvas must 
        # have the same new width setted.
        self.tracks_panel.top_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                          self._on_sash_pos_change
        )    
        self.tracks_panel.bottom_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                             self._on_sash_pos_change
        )      



    def PostInit(self):
        OM = ObjectManager()
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        controller.subscribe(self.set_fit, 'change.fit')
        controller.subscribe(self.set_multicursor, 'change.multicursor')
        controller.subscribe(self.set_index_type, 'change.index_type')
        #
        # TODO: check function below
        self._prepare_index_data()
        #
        well = OM.get(('well', controller.model.well_oid))      
        controller.attach(well.uid)

        for z_axis_dt in well.get_z_axis_datatypes().keys():
            self._tool_bar.choice_IT.Append(z_axis_dt)
        
        idx_index_type = self._tool_bar.choice_IT.GetItems().index(controller.model.index_type)
        self._tool_bar.choice_IT.SetSelection(idx_index_type)

        self.set_index_type(controller.model.index_type)  
        self._tool_bar.choice_IT.Bind(wx.EVT_CHOICE , self._on_index_type) 
        
        controller.subscribe(self._reload_z_axis_textctrls, 
                                                     'change.wellplot_ylim')
 
        self._reload_z_axis_textctrls()

        """
        self.overview_track = UIM.create('track_controller', 
                                 self._controller_uid,
                                 overview=True, plotgrid=False                            
        )
        """


    def PreDelete(self):
        """
        try:
            self.overview_sizer.Detach(self.overview_track.view.track)
        except:
            pass
        """
        
        try:
            self.sizer.Remove(0)
            del self._tool_bar
            super().PreDelete()  
        except Exception as e:
            msg = 'PreDelete ' + self.__class__.__name__ + \
                                            ' ended with error: ' + str(e)
            print (msg)                                
            raise       
            
            
            
    def _place_as_overview(self, track_canvas_window):
        """Places a TrackCanvas window at overview place.
        It is a inner function and should (must) be used only by WellPlot.    
        """
        print ('\n\n_place_as_overview')
        
        if not self.overview_sizer.IsEmpty():
            raise Exception('Overview sizer is not empty.')
        self.overview_base_panel.SetInitialSize((60, 10))
        self.overview_sizer.Add(track_canvas_window, 1, 
                                wx.EXPAND|wx.ALL, self.overview_border
        )     
        self.hbox.Layout()
        print ('_place_as_overview FINISHED')



    def _remove_from_overview(self):
        """Remove track is at overview place."""
        if self.overview_sizer.IsEmpty():
            raise Exception('Overview sizer is empty.')
            
        self.overview_sizer.Clear()    
            
        """
        otc = controller._get_overview_track()    
            
        try:
            self.overview_sizer.Detach(self.overview_track.view.track)
        except:
            pass
        """    
        self.overview_base_panel.SetInitialSize((0, 0))
        self.hbox.Layout()       



  


    def _get_wx_parent(self, flag):
        """
        """
        if flag == 'overview':
            return self.overview_base_panel
        elif flag == 'track':
            return self.tracks_panel.bottom_splitter
        elif flag == 'label':
            return self.tracks_panel.top_splitter         
        raise Exception('Wrong type window informed. ' + 
                        'Valid values are overview, label or track.'
        )


    def _set_own_name(self):
        """
        """
        try:
            OM = ObjectManager()
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            idx = 0
            well = OM.get(('well', controller.model.well_oid))
            lpcs = UIM.list('wellplot_controller')
            for lpc in lpcs:
                if lpc == controller:
                    break
                if lpc.model.well_oid == controller.model.well_oid:
                    idx += 1
            idx += 1
            controller.model.title = self._FRIENDLY_NAME + ': ' + well.name + \
                                        ' ['+ str(idx) + ']'    
        except Exception as e:
            print ('ERROR _set_own_name:', e)
    
    

    def _prepare_index_data(self):
#        print ('\nWellPlot._prepare_index_data')
        OM = ObjectManager()
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        try:
            well = OM.get(('well', controller.model.well_oid))
        except:
            raise
            
        ylim = well.get_z_axis_datatype_range(controller.model.index_type)
        controller.model.wellplot_ylim = ylim
        controller.model.shown_ylim = ylim


    """
    def on_change_wellplot_ylim(self, new_value, old_value):
        #raise Exception('Cannot do it!')
        self._reload_z_axis_textctrls()
    """    
        
    def _reload_z_axis_textctrls(self, *args):    
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        ymin, ymax = controller.model.shown_ylim
        z_start_str = "{0:.2f}".format(ymin)
        self._tool_bar.z_start.SetValue(z_start_str)
        z_end_str = "{0:.2f}".format(ymax)
        self._tool_bar.z_end.SetValue(z_end_str)
        

    def on_change_z_start(self, event):
        print ('on_change_z_start:', event.GetString())

    def on_change_z_end(self, event):
        print ('on_change_z_end:', event.GetString())
        
    
      
            
        
    # TODO: Verificar mover para WellPlotController
    def _adjust_up_pos(self, track_uid, from_pos):
       # print '\n_adjust_up_pos:', track_uid, from_pos
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if from_pos >= len(controller): # .size:
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

    """"
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

    """
    
    # Posicao absoluta considera os tracks invisiveis
    # Posicao relativa considera somente os tracks visiveis
    # retorna -1 se o track for overview
    # gera exception se o track nao for filho deste wellplot
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

    """
    # Posicao absoluta, considerando overview
    def get_adjusted_absolute_track_position(self, track_uid):  
        pos = self.get_track_position(track_uid, False)
        UIM = UIManager()
        track = UIM.get(track_uid)           
        ot = self._get_overview_track()
        if ot and ot.model.pos < track.model.pos:
            pos -= 1
        return pos   
    """

    def change_absolute_track_position_on_splitter(self, track_uid, new_pos):
        UIM = UIManager()
        track = UIM.get(track_uid)   
        top, bottom = track._get_windows()
        self.tracks_panel.top_splitter.ChangeWindowPosition(top, new_pos)
        self.tracks_panel.bottom_splitter.ChangeWindowPosition(bottom, new_pos)


    def refresh_overview(self):
        self.overview_track._reload_canvas_positions_from_depths()


    """
    def _detach_windows(self, label, track):
        try:
            self.tracks_panel.top_splitter.DetachWindow(label)
            self.tracks_panel.bottom_splitter.DetachWindow(track)  
        except Exception as e:
            msg = 'Error in WellPlot._detach_windows: ' + e.args
            log.exception(msg)
            print (msg)
    """


    def _detach_top_window(self, top_win):
        try:
            self.tracks_panel.top_splitter.DetachWindow(top_win)
        except:
            raise

    def _detach_bottom_window(self, bot_win):
        try:
            self.tracks_panel.bottom_splitter.DetachWindow(bot_win)  
        except:
            raise


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
            controller.model.cursor_state = WellPlotState.NORMAL_TOOL
        elif event.GetId() == LP_SELECTION_TOOL:    
            controller.model.cursor_state = WellPlotState.SELECTION_TOOL
        else:
            raise Exception()    

    def _OnEditFormat(self, event): 
        UIM = UIManager()
        lp_editor_ctrl = UIM.create('well_plot_editor_controller', 
                                    self._controller_uid
        )
        lp_editor_ctrl.view.Show()							  


    def _OnResetZAxis(self, event): 
        #UIM = UIManager()
        self._prepare_index_data()


    def _OnSetZAxis(self, event): 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        ymin, ymax = controller.model.wellplot_ylim
        try:
            zstart = float(self._tool_bar.z_start.GetValue())
            zend = float(self._tool_bar.z_end.GetValue())
            if not round(zstart, 2) >= round(ymin, 2):
                
                raise Exception('AAA: ', str(zstart) + '   '+ str(ymin))
                
            if not round(zend, 2) <= round(ymax, 2):
                raise Exception('BBB: ', str(zend) + '   '+ str(ymax))              
        except Exception as e:
            print ('ERROR:', e)
            self._reload_z_axis_textctrls()
            return
        #
        controller.model.set_value_from_event('shown_ylim', (zstart, zend))
        controller._reload_ylims()
            


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



    def set_index_type(self, new_value, old_value=None):     
        
        print ('\n\n\nset_index_type:', new_value, old_value)

        UIM = UIManager() 
        
        try:
            
            #self._prepare_index_data()
            print ('\nWellPlot._prepare_index_data')
            OM = ObjectManager()
            #UIM = UIManager()        
            controller = UIM.get(self._controller_uid)
            try:
                well = OM.get(('well', controller.model.well_oid))
            except:
                raise
                
            ylim = well.get_z_axis_datatype_range(new_value)
            controller.model.wellplot_ylim = ylim
            controller.model.shown_ylim = ylim

            
    
            #self.zaxis_uid = zaxis[0].uid
            print ('WellPlot._prepare_index_data FIM\n')            
            
            # TODO: Find a more Pythonic way to write aboxe
            for track_ctrl in UIM.list('track_controller', self._controller_uid):
                
                if not track_ctrl.model.overview:
                    """    
#                    print ('overview')
                    try:
                        if self.ot_toc:
                            UIM.remove(self.ot_toc.uid) 
                    except Exception as e:
                        print ('UIM.remove(self.ot_toc.uid):', e)
#                    print (self.zaxis_uid)    
        


#                    self.ot_toc = self.overview_track.append_object(self.zaxis_uid) 
                    
                    
                    
                    #ot_toc = self.overview_track.append_object(self.zaxis_uid)
                    #ot_toc_repr_ctrl = self.ot_toc.get_representation()
                    # TODO: Update Adaptative
                    #ot_toc_repr_ctrl.model.step = 200
                    
                    else:
                    """    
                    for toc_ctrl in UIM.list('track_object_controller', track_ctrl.uid):
                        filter_ = toc_ctrl.get_filter()
                        filter_.reload_z_dimension_indexes()
                        toc_ctrl._do_draw() 
                        
#            print ('FIM set_index_type:', new_value, old_value, '\n\n')                
        except Exception as e: 
            print ('ERROR set_index_type:', e)
            raise
      
        
        
    """    
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
        
    """


    def _on_change_float_panel(self, event):
        # TODO: Integrar binds de toggle buttons...
        if event.GetId() == LP_FLOAT_PANEL:
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            controller.model.float_mode = event.IsChecked()    


    def show_status_message(self, msg):
        self._status_bar.SetStatusText(msg, 0)


        
    def _build_tool_bar(self):
        self.fp_item = self._tool_bar.AddTool(LP_FLOAT_PANEL, 
                      wx.EmptyString,
                      GripyBitmap('restore_window-25.png'), 
                      wx.NullBitmap,
                      wx.ITEM_CHECK,
                      'Float Panel', 
                      'Float Panel',
                      None
        )
        self._tool_bar.ToggleTool(LP_FLOAT_PANEL, False)
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_float_panel, None,
                  LP_FLOAT_PANEL
        )                
        self._tool_bar.AddSeparator()
        
        
        self._tool_bar.AddTool(LP_NORMAL_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self._tool_bar.ToggleTool(LP_NORMAL_TOOL, True) 
        #
        self._tool_bar.AddTool(LP_SELECTION_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_tool, None,
                  LP_NORMAL_TOOL, LP_SELECTION_TOOL
        )
        #
        self._tool_bar.AddSeparator()
        #
        tb_item = self._tool_bar.AddTool(-1, u"Insert Track", 
                                  GripyBitmap('table_add_24.png'),
                                  'Insert a new track'
        )
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_toolbar_insert_track, tb_item)
        #
        tb_item = self._tool_bar.AddTool(-1, u"Remove Track", 
                                  GripyBitmap('table_delete_24.png'),
                                 'Remove selected tracks'
        )
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_toolbar_remove_track, tb_item)
        #
        self._tool_bar.AddSeparator()  
        #
        button_edit_format = wx.Button(self._tool_bar, label='Edit Plot')
        button_edit_format.Bind(wx.EVT_BUTTON , self._OnEditFormat)
        self._tool_bar.AddControl(button_edit_format, '')
        self._tool_bar.AddSeparator()    
        #    
        self._tool_bar.cbFit = wx.CheckBox(self._tool_bar, -1, 'Fit')        
        self._tool_bar.cbFit.Bind(wx.EVT_CHECKBOX , self._on_fit) 
        self._tool_bar.AddControl(self._tool_bar.cbFit, '')    
        #
        self._tool_bar.AddSeparator() 
        self._tool_bar.label_MC = wx.StaticText(self._tool_bar, label='Multi cursor:  ')
        #self._tool_bar.label_MC.SetLabel('Multi cursor:')
        self._tool_bar.AddControl(self._tool_bar.label_MC, '')
        self._tool_bar.choice_MC = wx.Choice(self._tool_bar, choices=['None', 'Horizon', 'Vertical', 'Both'])  
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        idx_mc = ['None', 'Horizon', 'Vertical', 'Both'].index(controller.model.multicursor)
        self._tool_bar.choice_MC.SetSelection(idx_mc)
        self._tool_bar.choice_MC.Bind(wx.EVT_CHOICE , self._on_multicursor) 
        self._tool_bar.AddControl(self._tool_bar.choice_MC, '')    
        #
        self._tool_bar.AddSeparator() 
        #
        self._tool_bar.label_IT = wx.StaticText(self._tool_bar, label='Z Axis:  ')
        self._tool_bar.AddControl(self._tool_bar.label_IT, '')
        
        self._tool_bar.choice_IT = wx.Choice(self._tool_bar, choices=[])
        #
        #controller = UIM.get(self._controller_uid)
        #idx_index_type = ['MD', 'TVD', 'TVDSS', 'TWT', 'TIME'].index(controller.model.index_type)
        #self._tool_bar.choice_IT.SetSelection(idx_index_type)
        #self._tool_bar.choice_IT.Bind(wx.EVT_CHOICE , self._on_index_type) 
        self._tool_bar.AddControl(self._tool_bar.choice_IT, '')    
        #
       # self._tool_bar.AddSeparator()  
        static_z_start = wx.StaticText(self._tool_bar, label='Start:')
        self._tool_bar.AddControl(static_z_start, '')
        self._tool_bar.z_start = wx.TextCtrl(self._tool_bar, size=(60, 23))
        #self._tool_bar.z_start.Enable(False)
        #self._tool_bar.z_start.Bind(wx.EVT_TEXT, self.on_change_z_start)
        self._tool_bar.AddControl(self._tool_bar.z_start, '')
        static_z_end = wx.StaticText(self._tool_bar, label='End:')
        self._tool_bar.AddControl(static_z_end, '')    
        self._tool_bar.z_end = wx.TextCtrl(self._tool_bar, size=(60, 23))
        #self._tool_bar.z_end.Enable(False)
        #self._tool_bar.z_end.Bind(wx.EVT_TEXT, self.on_change_z_end)
        self._tool_bar.AddControl(self._tool_bar.z_end, '')        
        #
        button_set_zaxis = wx.Button(self._tool_bar, label='Set', size=(40, 23))
        button_set_zaxis.Bind(wx.EVT_BUTTON , self._OnSetZAxis)
        self._tool_bar.AddControl(button_set_zaxis, '')
        #
        #self._tool_bar.AddSeparator()
        button_reset_zaxis = wx.Button(self._tool_bar, label='Reset', size=(40, 23))
        button_reset_zaxis.Bind(wx.EVT_BUTTON , self._OnResetZAxis)
        self._tool_bar.AddControl(button_reset_zaxis, '')
        self._tool_bar.AddSeparator()
        #
        self._tool_bar.Realize()  
        #
