# -*- coding: utf-8 -*-

import wx

from classes.om import ObjectManager
from ui.mvc_classes.workpage import WorkPageController
from ui.mvc_classes.workpage import WorkPage
from classes.ui import UIManager
from ui.plotstatusbar import PlotStatusBar
from ui.wellplot_internal import WellPlotInternal
from app.app_utils import WellPlotState   
from app.app_utils import GripyBitmap  
from app import log  




WP_FLOAT_PANEL = wx.NewId() 
WP_NORMAL_TOOL = wx.NewId()        
WP_SELECTION_TOOL = wx.NewId()     
WP_ADD_TRACK = wx.NewId()     
WP_REMOVE_TRACK = wx.NewId()     
    
  



class WellPlotController(WorkPageController):    
    """
    The :class:`WellPlotController` ...
    """    
    
    tid = 'wellplot_controller'

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
        
    def __init__(self, **state):
        super().__init__(**state)  

    def PostInit(self):
        self.subscribe(self._on_change_cursor_state, 'change.cursor_state')
        self.subscribe(self._on_change_shown_ylim, 'change.shown_ylim')
        #self.subscribe(self._reload_ylims, 'change.y_max_shown')
        # Then subscribe to UIManager in order to adjust Notebook page name 
        # after another WellPlot was removed.
        UIM = UIManager()
        UIM.subscribe(self._on_post_remove_well_plot, 'post_remove')
             
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

    def _on_change_cursor_state(self, new_value, old_value):
        """
        Unselect all tracks when WellPlotState.NORMAL_TOOL is trigged.
        
        Parameters
        ----------
        new_value : WellPlotState.
            Tool type setted by user.       
        old_value: Not used.
            Just to follow GRIPy's pubsub pattern. It is necessary and cannot
            be removed.
        """
        if new_value != WellPlotState.NORMAL_TOOL:
            return
        UIM = UIManager()
        selected_tracks = UIM.exec_query('track_controller',  self.uid,
                                   'selected=True',
                                    orderby='pos'
        )
        if selected_tracks:
            for track in selected_tracks:
                track.selected = False
                    
    # TODO: y or z???
    def _on_change_shown_ylim(self, new_value, old_value):
        ymin, ymax = new_value
        if ymin < 0 or ymax < 0:
            raise Exception() 
        UIM = UIManager()
        for track in UIM.list('track_controller', self.uid):
            if not track.overview:
                track.set_ylim(ymin, ymax)
            else:
                track.reposition_depth_canvas()
                
        self.view._reload_z_axis_textctrls()   

     
        
    def _on_post_remove_well_plot(self, objuid):
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


#    def on_change_ylim(self, new_value, old_value):
#        self._reload_ylim()


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
        selected_tracks = UIM.exec_query('track_controller', self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        # There isn't any track selected
        if not selected_tracks:
            new_track = UIM.create('track_controller', self.uid, pos=len(self))
            return [new_track.uid]  
        # Instead, insert new tracks before every selected track
        new_tracks_uids = []    
        for track in selected_tracks:											 
            new_track = UIM.create('track_controller', self.uid, 
                                   pos=track.pos
            )
            new_tracks_uids.append(new_track.uid)            
        return new_tracks_uids

    def remove_selected_tracks(self):
        """
        Remove selected :class:`~GRIPy-3.ui.mvc_classes.TrackController` on 
        :class:`WellPlot`.
        """
        UIM = UIManager()
        selected_tracks = UIM.exec_query('track_controller',  self.uid,
                                       'selected=True',
                                       orderby='pos',
                                       reverse=True
        )
        for track in selected_tracks:
            UIM.remove(track.uid)  


    def get_overview_track(self):
        """
        Returns the overview TrackController, if it exists. 
        
        Returns
        -------
        track : :class:`~GRIPy-3.ui.mvc_classes.TrackController`
            The track placed as Overview, or None if it does not exist.        
        """
        UIM = UIManager() 
        query_list = UIM.exec_query('track_controller', 
                                   self._controller_uid, 'overview=True'
        )
        track = None
        if query_list:
            track = query_list[0]
        return track


    def _adjust_positions_after_track_deletion(self, pos):
        """
        Adjust tracks position after a deletion.
        
        When one track (or more) is (are) deleted, the others with positions 
        greater must have their positions adjusted. It is done in a silent way
        (not generating :class:`~GRIPy-3.ui.mvc_classes.TrackModel` events).
                         
        Parameters
        ----------
        pos: int
            Position of Track deleted. 
            
        """
        UIM = UIManager()
        tracks = UIM.exec_query('track_controller', self.uid, 'pos>'+str(pos))
        for track in tracks:
            track.set_value_from_event('pos', track.pos-1)   
            track.reload_track_title()        
                    
            
    def _change_width_for_selected_tracks(self, dragged_track_uid):
        """
        Change width for a group of selected tracks.
        
        When some :class:`~GRIPy-3.ui.mvc_classes.TrackController` objects are
        selected and one of then have its width changed by a sash drag, the
        others will have the same new width.
        
        Parameters
        ----------
        dragged_track_uid: :class:`~GRIPy-3.ui.mvc_classes.TrackController` 
                            uid.
            The track identificator for whose have its sash dragged.        
        
        """
        UIM = UIManager()
        dragged_track = UIM.get(dragged_track_uid)
        selected =  UIM.exec_query('track_controller', self.uid, 'selected=True')
        for track in selected:
            if track.uid != dragged_track_uid:
                track.width = dragged_track.width 


    def _increment_tracks_positions(self, pos, exclude_track_uid=None):
        """
        From position on, increment Tracks positions by 1.
        
        When a new :class:`~GRIPy-3.ui.mvc_classes.TrackController` object is
        created, others Tracks with position equal or greater must have their 
        positions incremented by 1.
        
        It is done in a silent way (not generating 
        :class:`~GRIPy-3.ui.mvc_classes.TrackModel` events), because the
        overview Track keep its original position. 
        
        Parameters
        ----------
        pos: int
            First position to be incremented.
        exclude_track_uid: :class:`~GRIPy-3.ui.mvc_classes.TrackController` 
                            uid, optional.    
            If given, exclude the Track to have position incremented.
        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if pos >= len(controller):
            return
        tracks_affected = UIM.exec_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(pos)
        )    
        # There is only one Track and it should be the "exclude_track"
        if len(tracks_affected) == 1:
            return
        #
        else:
            if exclude_track_uid:
                exclude_track = UIM.get(exclude_track_uid)
                tracks_affected.remove(exclude_track)
            for track in tracks_affected:
                # Silent way - not generating model events.
                track.set_value_from_event('pos', track.pos+1)

    def _reload_tracks_titles(self, pos, exclude_track_uid=None):
        """
        From position on, reload Tracks titles.
        
        When a new :class:`~GRIPy-3.ui.mvc_classes.TrackController` object is
        created, others Tracks with position equal or greater must have their 
        titles updates.
        
        Parameters
        ----------
        pos: int
            First position to have title updated.
        exclude_track_uid: :class:`~GRIPy-3.ui.mvc_classes.TrackController` 
                            uid, optional.    
            If given, exclude the Track to have title updated.
        """        
        UIM = UIManager()
        tracks_affected = UIM.exec_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(pos)
        ) 
        if exclude_track_uid:
            exclude_track = UIM.get(exclude_track_uid)
            tracks_affected.remove(exclude_track)        
        for track in tracks_affected:
            track.reload_track_title() 


          


    # TODO: REVER ESSA FUNCAO
#    '''
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
                tracks_next_pos = UIM.exec_query('track_controller',  self.uid, 
                                      'pos='+str(pos-1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                if len(tracks_next_pos) == 0:
                    return    
                track_next_pos = tracks_next_pos[0]
                if not track_pos.overview and not track_next_pos.overview:  
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)
                track_next_pos.pos += 1
                pos -= 1
        
        else:
            while pos < new_pos: 
                tracks_next_pos = UIM.exec_query('track_controller',  self.uid, 
                                      'pos='+str(pos+1))
                if track_pos in tracks_next_pos:
                    tracks_next_pos.remove(track_pos)
                    
                if len(tracks_next_pos) == 0:
                    return
                track_next_pos = tracks_next_pos[0]
                if not track_pos.overview and not track_next_pos.overview:      
                    if new_pos != self.view.get_track_position(track_pos.uid, False):
                        self.view.change_absolute_track_position_on_splitter(track_pos.uid, new_pos)
                track_next_pos.pos -= 1
                pos += 1         
    
#    '''
    
    # TODO: REVER ESSA FUNCAO
    """
    def show_track(self, track_uid, show):
        # Adjust track.model...
        UIM = UIManager()
        track = UIM.get(track_uid)
        track.visible = show
        self.view.show_track(track_uid, show)
    """
    
    


    # TODO: REVER ESSA FUNCAO
    """
    def _pre_delete_overview_track(self):
        self.view._remove_from_overview_panel()
    """

                  


    """
    def get_shown_ylim(self):
        ymin, ymax = self.shown_ylim
        if ymin < 0 or ymax < 0:
            raise Exception()                                                                      
        return shown_ylim
    """
    



   
                
     
        
        
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
        self._hbox = wx.BoxSizer(wx.HORIZONTAL)
        #
        # The tracks panel is a horizontal wx.SplitterWindow object containing
        # 2 wx.MultiSplitterWindow (redesigned). In each of these, Track labels
        # canvas and Track data canvas are respectively placed. 
        self._tracks_panel = WellPlotInternal(self._main_panel) 
        self._hbox.Add(self._tracks_panel, 1, wx.EXPAND) 
        #
        # Overview
        self._overview = None
        self._overview_border = 1
        self._overview_width = 120#60
        self._overview_base_panel = wx.Panel(self._main_panel)
        self._overview_base_panel.SetBackgroundColour('black')
        self._overview_base_panel.SetInitialSize((0, 0))
        self._overview_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self._overview_base_panel.SetSizer(self._overview_sizer)
        self._hbox.Add(self._overview_base_panel, 0, wx.EXPAND)
        #
        self._main_panel.SetSizer(self._hbox)
        self._hbox.Layout()
        self.Layout()
        # 
        # When a sash (width bar) changes Panel width in a MultiSplitterWindow
        # the other one must answer with same change. For example, if a user
        # drags the sash at a Track data canvas, its Track label canvas must 
        # have the same new width setted.
        self._tracks_panel.top_splitter.Bind(
                                            wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                            self._on_change_sash_pos
        )    
        self._tracks_panel.bottom_splitter.Bind(
                                            wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                            self._on_change_sash_pos
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
        well = OM.get(('well', controller.well_oid))      
        controller.attach(well.uid)

        for z_axis_dt in well.get_z_axis_datatypes().keys():
            self._tool_bar.choice_IT.Append(z_axis_dt)
        
        idx_index_type = self._tool_bar.choice_IT.GetItems().index(controller.index_type)
        self._tool_bar.choice_IT.SetSelection(idx_index_type)

        self.set_index_type(controller.index_type)  
        self._tool_bar.choice_IT.Bind(wx.EVT_CHOICE , self._on_index_type) 
        
        controller.subscribe(self._reload_z_axis_textctrls, 
                                                     'change.wellplot_ylim')
 
        self._reload_z_axis_textctrls()


        # Create Overview Track
        UIM.create('track_controller', 
                                 self._controller_uid,
                                 overview=True, plotgrid=False                            
        )



    def PreDelete(self):
        """
        try:
            self._overview_sizer.Detach(self._overview_track.view.track)
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
             

    def _on_change_sash_pos(self, event):
        idx = event.GetSashIdx()
        new_width = event.GetSashPosition()
        track_ctrl = self.get_track_on_position(idx)
        track_ctrl.width = new_width
  

    def _on_change_float_panel(self, event):
        # TODO: Integrar binds de toggle buttons...
        if event.GetId() == WP_FLOAT_PANEL:
            UIM = UIManager()   
            controller = UIM.get(self._controller_uid)
            controller.float_mode = event.IsChecked()    
            
      
        
    # Posicao absoluta considera os tracks invisiveis
    # Posicao relativa considera somente os tracks visiveis
    # Posicao -1 retorna overview track ou None se nao existir overview
    def get_track_on_position(self, pos, relative_position=True): 
        if pos == -1:
            return self.get_overview_track()
        b_splitter = self._tracks_panel.bottom_splitter
        if relative_position:
            pos = b_splitter.get_windows_indexes_shown()[pos]
        bottom_window = b_splitter.GetWindow(pos)
        UIM = UIManager()
        for tcc in UIM.list('track_canvas_controller'):
            if tcc.view == bottom_window:
                track_ctrl_uid = UIM._getparentuid(tcc.uid)
                return UIM.get(track_ctrl_uid)   
        raise Exception('Informed position [{}] is invalid.'.format(pos))    

                       
    def _place_as_overview(self, track_canvas_window):
        """Places a TrackCanvas window at overview place.
        It is a inner function and should (must) be used only by WellPlot.    
        """
        print ('\n\n_place_as_overview')
        
        if not self._overview_sizer.IsEmpty():
            raise Exception('Overview sizer is not empty.')
        self._overview_base_panel.SetInitialSize((self._overview_width, 10))
        self._overview_sizer.Add(track_canvas_window, 1, 
                                wx.EXPAND|wx.ALL, self._overview_border
        )     
        self._hbox.Layout()
        print ('_place_as_overview FINISHED')



    def _remove_from_overview(self):
        """Remove track is at overview place."""
        if self._overview_sizer.IsEmpty():
            raise Exception('Overview sizer is empty.')
            
        self._overview_sizer.Clear()    
            
        """
        otc = controller.get_overview_track()    
            
        try:
            self._overview_sizer.Detach(self._overview_track.view.track)
        except:
            pass
        """    
        self._overview_base_panel.SetInitialSize((0, 0))
        self._hbox.Layout()       



  


    def _get_wx_parent(self, flag):
        """
        """
        if flag == 'overview':
            return self._overview_base_panel
        elif flag == 'track':
            return self._tracks_panel.bottom_splitter
        elif flag == 'label':
            return self._tracks_panel.top_splitter         
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
            well = OM.get(('well', controller.well_oid))
            lpcs = UIM.list('wellplot_controller')
            for lpc in lpcs:
                if lpc == controller:
                    break
                if lpc.well_oid == controller.well_oid:
                    idx += 1
            idx += 1
            controller.title = self._FRIENDLY_NAME + ': ' + well.name + \
                                        ' ['+ str(idx) + ']'    
        except Exception as e:
            print ('ERROR _set_own_name:', e)
    
    

    def _prepare_index_data(self):
#        print ('\nWellPlot._prepare_index_data')
        OM = ObjectManager()
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        try:
            well = OM.get(('well', controller.well_oid))
        except:
            raise
            
        ylim = well.get_z_axis_datatype_range(controller.index_type)
        controller.wellplot_ylim = ylim
        controller.shown_ylim = ylim


    """
    def on_change_wellplot_ylim(self, new_value, old_value):
        #raise Exception('Cannot do it!')
        self._reload_z_axis_textctrls()
    """    
        
    def _reload_z_axis_textctrls(self, *args):    
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        ymin, ymax = controller.shown_ylim
        z_start_str = "{0:.2f}".format(ymin)
        self._tool_bar.z_start.SetValue(z_start_str)
        z_end_str = "{0:.2f}".format(ymax)
        self._tool_bar.z_end.SetValue(z_end_str)
        

    def on_change_z_start(self, event):
        print ('on_change_z_start:', event.GetString())

    def on_change_z_end(self, event):
        print ('on_change_z_end:', event.GetString())
        
    
      
            
        



    
    # Posicao absoluta considera os tracks invisiveis
    # Posicao relativa considera somente os tracks visiveis
    # retorna -1 se o track for overview
    # gera exception se o track nao for filho deste wellplot
    def get_track_position(self, track_uid, relative_position=True):  
        UIM = UIManager()
        if UIM._getparentuid(track_uid) != self._controller_uid:
            raise Exception()
        track = UIM.get(track_uid)    
        if track.overview:
            return -1 
        
        tcc = track._get_canvas_controller()
        
        #if relative_position:
        #    return self._tracks_panel.bottom_splitter.GetVisibleIndexOf(bottom)
        #return self._tracks_panel.bottom_splitter.IndexOf(bottom)
        if relative_position:
            ret = self._tracks_panel.bottom_splitter.GetVisibleIndexOf(tcc.view)
        else:
            ret = self._tracks_panel.bottom_splitter.IndexOf(tcc.view)           
        #print 'get_track_position({}, {}): {}'.format(track_uid, relative_position, ret)    
        return ret    

#    """
        
    # Posicao absoluta, considerando overview
    def get_adjusted_absolute_track_position(self, track_uid):  
        pos = self.get_track_position(track_uid, False)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)   
        track = UIM.get(track_uid)           
        ot = controller.get_overview_track()
        if ot and ot.pos < track.pos:
            pos -= 1
        return pos   
#    """

    def change_absolute_track_position_on_splitter(self, track_uid, new_pos):
        UIM = UIManager()
        track = UIM.get(track_uid)   
        #
        tlc = track._get_label_controller()
        tcc = track._get_canvas_controller()
        #
        self._tracks_panel.top_splitter.ChangeWindowPosition(tlc.view, new_pos)
        self._tracks_panel.bottom_splitter.ChangeWindowPosition(tcc.view, new_pos)


    def refresh_overview(self):
        self._overview_track._reload_canvas_positions_from_depths()


    """
    def _detach_windows(self, label, track):
        try:
            self._tracks_panel.top_splitter.DetachWindow(label)
            self._tracks_panel.bottom_splitter.DetachWindow(track)  
        except Exception as e:
            msg = 'Error in WellPlot._detach_windows: ' + e.args
            log.exception(msg)
            print (msg)
    """


    def _detach_top_window(self, top_win):
        try:
            self._tracks_panel.top_splitter.DetachWindow(top_win)
        except:
            raise

    def _detach_bottom_window(self, bot_win):
        try:
            self._tracks_panel.bottom_splitter.DetachWindow(bot_win)  
        except:
            raise


    def show_track(self, track_uid, show):
        UIM = UIManager()
        track = UIM.get(track_uid)
        if track.view.label:
            self._tracks_panel.top_splitter.ShowWindow(track.view.label, show)
        if not track.overview:   
            self._tracks_panel.bottom_splitter.ShowWindow(track.view.track, show)
        else:
            raise Exception('show_track overview track???')
            

        tracks_affected= UIM.exec_query('track_controller',  
                                            self._controller_uid,
                                            'pos>='+str(track.pos)
        )    

        for track_affected in tracks_affected:
            if track_affected.uid != track.uid:
                #print 'track_affected.uid:', track_affected.uid
                track_affected.reload_track_title() 
           
        




    def _on_bottom_splitter_size(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.update_adaptative()
        
        
    def _do_change_width(self, idx, width, event_object=None):
        
        self._tracks_panel.top_splitter._sashes[idx] = width
        self._tracks_panel.bottom_splitter._sashes[idx] = width
        
        if self._tracks_panel.top_splitter._windows[idx].IsShown():
            self._tracks_panel.top_splitter._SizeComponent()  
        if self._tracks_panel.bottom_splitter._windows[idx].IsShown():
            self._tracks_panel.bottom_splitter._SizeComponent()              
    

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
        if event.GetId() == WP_NORMAL_TOOL:
            controller.cursor_state = WellPlotState.NORMAL_TOOL
        elif event.GetId() == WP_SELECTION_TOOL:    
            controller.cursor_state = WellPlotState.SELECTION_TOOL
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
        ymin, ymax = controller.wellplot_ylim
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
        controller.set_value_from_event('shown_ylim', (zstart, zend))
        controller._reload_ylims()
            


    def _on_fit(self, event): 
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.fit = event.IsChecked()
 
    
    def set_fit(self, new_value, old_value):
        self._tracks_panel.top_splitter._SetFit(new_value)
        self._tracks_panel.bottom_splitter._SetFit(new_value)        

            
    def _on_multicursor(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.multicursor = event.GetString()

    def _on_index_type(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.index_type = event.GetString()
        


    def _insert_windows_on_track_panel(self, pos, label_window, 
                                           canvas_window, initial_width=200):
        self._tracks_panel.insert(pos, label_window, canvas_window,
                                                              initial_width
        )


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
                well = OM.get(('well', controller.well_oid))
            except:
                raise
                
            ylim = well.get_z_axis_datatype_range(new_value)
            controller.wellplot_ylim = ylim
            controller.shown_ylim = ylim

            
    
            #self.zaxis_uid = zaxis[0].uid
            print ('WellPlot._prepare_index_data FIM\n')            
            
            # TODO: Find a more Pythonic way to write aboxe
            for track_ctrl in UIM.list('track_controller', self._controller_uid):
                
                if not track_ctrl.overview:
                    """    
#                    print ('overview')
                    try:
                        if self.ot_toc:
                            UIM.remove(self.ot_toc.uid) 
                    except Exception as e:
                        print ('UIM.remove(self.ot_toc.uid):', e)
#                    print (self.zaxis_uid)    
        


#                    self.ot_toc = self._overview_track.append_object(self.zaxis_uid) 
                    
                    
                    
                    #ot_toc = self._overview_track.append_object(self.zaxis_uid)
                    #ot_toc_repr_ctrl = self.ot_toc.get_representation()
                    # TODO: Update Adaptative
                    #ot_toc_repr_ctrl.step = 200
                    
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





    def show_status_message(self, msg):
        self._status_bar.SetStatusText(msg, 0)


        
    def _build_tool_bar(self):
        self.fp_item = self._tool_bar.AddTool(WP_FLOAT_PANEL, 
                      wx.EmptyString,
                      GripyBitmap('restore_window-25.png'), 
                      wx.NullBitmap,
                      wx.ITEM_CHECK,
                      'Float Panel', 
                      'Float Panel',
                      None
        )
        self._tool_bar.ToggleTool(WP_FLOAT_PANEL, False)
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_float_panel, None,
                  WP_FLOAT_PANEL
        )                
        self._tool_bar.AddSeparator()
        
        
        self._tool_bar.AddTool(WP_NORMAL_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self._tool_bar.ToggleTool(WP_NORMAL_TOOL, True) 
        #
        self._tool_bar.AddTool(WP_SELECTION_TOOL, 
                      wx.EmptyString,
                      GripyBitmap('cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self._tool_bar.Bind(wx.EVT_TOOL, self._on_change_tool, None,
                  WP_NORMAL_TOOL, WP_SELECTION_TOOL
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
        idx_mc = ['None', 'Horizon', 'Vertical', 'Both'].index(controller.multicursor)
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
        #idx_index_type = ['MD', 'TVD', 'TVDSS', 'TWT', 'TIME'].index(controller.index_type)
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
