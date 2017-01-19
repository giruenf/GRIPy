# -*- coding: utf-8 -*-


import wx
import logging
import wx.aui as aui


#import Parms   
from plotter import PlotterController 
from plotter import PlotterModel
from plotter import Plotter

#from app.utils import Chronometer


from UI.uimanager import UIManager
#import UI.logplotformat as logplotformat
from UI.logplot_base import OverviewFigureCanvas
from UI.logplot_internal import LogPlotInternal

from UI.plotstatusbar import PlotStatusBar

#from track_base import OverviewFigureCanvas# rackFigureCanvas       
        
        
        
class LogPlotController(PlotterController):
    tid = 'logplot_controller'
        
    def __init__(self):
        super(LogPlotController, self).__init__()     
        
       
    def insert_track(self, **track_state):
        _UIM = UIManager()
        tracks = self.get_tracks_selected()
        if not tracks:
            _UIM.create('track_controller', self.uid, **track_state)
        else:
            if track_state.get('pos'):
                del track_state['pos']
            for track in tracks[::-1]:
                _UIM.create('track_controller', self.uid, pos=track.model.pos,
                            **track_state
                )
        self.refresh_child_positions()         
        self.on_change_ylim()
        
 
    def get_tracks_selected(self):
        _UIM = UIManager()
        return [track for track in _UIM.list('track_controller', self.uid) \
                if track.model.selected]        
       

    def get_track_on_position(self, pos):
        try:
            window = self.view.main_panel.top_splitter.GetWindow(pos)
        except Exception:
            window = None
        if window:
            _UIM = UIManager()
            return _UIM.get(window._view._controller_uid)
        else:
            return None
 
 
    def refresh_child_positions(self, **kwargs):
        start_pos = 0
        if kwargs:
            if kwargs.get('start_pos'):
                start_pos = kwargs.get('start_pos')
        for i in range(start_pos, len(self.view)):
            #try:
            track_ctrl = self.get_track_on_position(i)
            if track_ctrl:
                track_ctrl.model.pos = i
            else:
                msg = 'ERROR: No track at given position {}'.format(i)
                logging.error(msg)
                raise Exception(msg)
            #except Exception:
            #    msg = 'ERROR on setting position {} to TrackController {}'.format(i, track_ctrl.uid)
            #    logging.exception(msg)
            #    raise
       
         
    def remove_selected_tracks(self):
        for track in self.get_tracks_selected():
            self.destroy_track(track)
        self.refresh_child_positions()    


    def add_to_selection(self, track_controller):
        print 'add_selection', track_controller.uid         


    def destroy_track(self, track_controller):
        try:
            title_parent = self.view.main_panel.top_splitter
            track_parent = self.view.main_panel.bottom_splitter
            track_controller.view.label.SetDropTarget(None)
            track_controller.view.track.SetDropTarget(None) 
            title_parent.DetachWindow(track_controller.view.label)
            track_parent.DetachWindow(track_controller.view.track)        
            track_controller.view.label.Hide()
            track_controller.view.track.Hide()
            _UIM = UIManager()
            _UIM.remove(track_controller.uid)
     
        except Exception:
            msg = 'ERROR destroying track {}.'.format(self.uid)
            logging.exception(msg)

  

    def on_change_ylim(self, **kwargs):
        _UIM = UIManager()
        print '\non_change_ylim'
        for track in _UIM.list('track_controller', self.uid):
            print track.uid
            track._set_ylim(self.model.y_min, self.model.y_max)
        self.update_adaptative()
        

    def update_adaptative(self):
        _UIM = UIManager() 
        tracks = _UIM.list('track_controller', self.uid)
        if not tracks:
            return
        print '\nupdate_adaptative'
        NUM_PX = 80
        SCALES = [1000.0, 500.0, 250.0, 100.0, 50.0, 25.0, 10.0, 
                  5.0, 2.5, 1.0, 0.5, 0.1
        ]
        height = self.view.main_panel.bottom_splitter.GetSize()[1]
        val = ((self.model.y_max - self.model.y_min) / float(height)) * NUM_PX
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
        print '\nscale chosen', SCALES[idx]    


class LogPlotModel(PlotterModel):
    tid = 'logplot_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 'type': int},
        'y_min': {'default_value': 2200, 'type': float, 'on_change': LogPlotController.on_change_ylim},
        'y_max': {'default_value': 3000, 'type': float, 'on_change': LogPlotController.on_change_ylim},
    }    
    
    def __init__(self, controller_uid, **base_state):   
        super(LogPlotModel, self).__init__(controller_uid, **base_state)   
                   
    
    
    
    
class LogPlot(Plotter):
    tid = 'logplot'


    def __init__(self, controller_uid, **kwargs):
        self.main_panel_class = LogPlotInternal
        super(LogPlot, self).__init__(controller_uid) 
        self.main_panel = self.main_panel_class(self) 
        self._create_toolbar()
        self.statusBar = PlotStatusBar(self)
                                  
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)        
        self.hbox.Add(self.main_panel, 1, wx.EXPAND)  #self.ttsplitter, 1, flag=wx.EXPAND)    

        ### Overview track
        self.overview_border = 1
        self.overview_panel = wx.Panel(self)
        self.overview_panel.SetMinSize((0, 0))
        #self.overview_panel.SetBestFittingSizeMinSize((0, 0))
        self.overview_panel.SetBackgroundColour('black')
        self.overview_panel.SetInitialSize((50, 50))
        op_sizer = wx.BoxSizer(wx.HORIZONTAL)  
        self.overview_track = OverviewFigureCanvas(self.overview_panel, 
                            wx.Size(50, self.GetSize()[1]),
                            0,
                            6000,

        )
        self.overview_track.set_callback(self.set_new_depth)
        op_sizer.Add(self.overview_track, 1, wx.EXPAND|wx.ALL, self.overview_border)
        self.overview_panel.SetSizer(op_sizer)
        self.overview_track.show_index_curve()
        self.hbox.Add(self.overview_panel, 0, wx.EXPAND|wx.ALIGN_RIGHT)
        ###        
        
        
        #self.SetInitialSize((50, 50))
        
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.vbox.Add(self.tb, 0, flag=wx.TOP|wx.EXPAND)
        self.vbox.Add(self.hbox, 1, flag=wx.EXPAND)
        
        self.vbox.Add(self.statusBar, 0, flag=wx.BOTTOM|wx.EXPAND)
        
        self.SetSizer(self.vbox)          
        self.Layout()
        
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)        
        
        if controller.model.pos == -1:
            controller.model.pos = parent_controller.view.note.GetPageCount()
        parent_controller.view.note.InsertPage(controller.model.pos, self, self.get_title(), True) 
        
        #InsertPage(self, size_t n, Window page, String text, bool select=False, 
        #    int imageId=-1) -> bool


        self.main_panel.top_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                          self._on_sash_pos_change
        )    
        self.main_panel.bottom_splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, 
                                             self._on_sash_pos_change
        ) 

        self.main_panel.bottom_splitter.Bind(wx.EVT_SIZE, 
                                             self._on_bottom_splitter_size
        ) 

    
    def set_new_depth(self, depth):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid) 
        controller.model.y_min, controller.model.y_max = depth
        

    def __len__(self):
        try:
            return len(self.main_panel)
        except AttributeError:   
            #logging.exception('ERROR')
            return 0
        except Exception:
            logging.exception('ERROR')
            raise


    def _on_sash_pos_change(self, event):
        idx = event.GetSashIdx()
        new_width = event.GetSashPosition()
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        track_ctrl = controller.get_track_on_position(idx)
        track_ctrl.model.width = new_width


    def _on_bottom_splitter_size(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid) 
        controller.update_adaptative()
        

    def _do_change_width(self, idx, width, event_object=None):
        self.main_panel.bottom_splitter._DoSetSashPosition(idx, width)
        self.main_panel.bottom_splitter._SizeComponent()
        self.main_panel.top_splitter._DoSetSashPosition(idx, width)
        self.main_panel.top_splitter._SizeComponent()    


    def _insert(self, pos, label_window, track_window, width):
        self.main_panel.insert(pos, label_window, track_window, width)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if pos < (len(self)-1):
            controller.refresh_child_positions(start_pos=pos+1)
                                              
                                      
    def get_title(self):
        return 'Log Plot [oid:' + str(self._controller_uid[1]) + ']'     


    def _on_toolbar_insert_track(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.insert_track()   


    def _on_toolbar_remove_track(self, event):
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        controller.remove_selected_tracks()   
        

    def _create_toolbar(self): 
        self.tb = aui.AuiToolBar(self)
        self.tb.SetToolBitmapSize(wx.Size(48, 48))   
    #    self.button_edit_format = wx.Button(self.tb, label='Edit Format')
    #    self.button_edit_format.Bind(wx.EVT_BUTTON , self._OnEditFormat)
    #    self.tb.AddControl(self.button_edit_format, '')
        
        """
        AddTool(self, int toolId, String label, Bitmap bitmap, String shortHelpString=wxEmptyString, 
            int kind=ITEM_NORMAL) -> AuiToolBarItem
        AddTool(self, int toolId, String label, Bitmap bitmap, Bitmap disabledBitmap, 
            int kind, String shortHelpString, 
            String longHelpString, Object clientData) -> AuiToolBarItem
        AddTool(self, int toolId, Bitmap bitmap, Bitmap disabledBitmap, bool toggle=False, 
            Object clientData=None, String shortHelpString=wxEmptyString, 
            String longHelpString=wxEmptyString) -> AuiToolBarItem
        """
        """AddControl(self, Control control, String label=wxEmptyString) -> AuiToolBarItem"""
        
  
        nt = self.tb.AddTool(-1, 'Normal Tool',
                        wx.Bitmap('./icons/cursor_24.png'),
                        'Normal Tool'
        )
        self.tb.ToggleTool(nt.GetId(), True)
        
        st = self.tb.AddTool(-1, 'Selection Tool',
                        wx.Bitmap('./icons/cursor_filled_24.png'),
                        'Selection Tool'
        )        
        self.tb.ToggleTool(st.GetId(), False)
        
        zi = self.tb.AddTool(-1, 'Zoom in',
                        wx.Bitmap('./icons/magnifier_zoom_in_24.png'),
                        'Zoom in'
        )        
        self.tb.ToggleTool(zi.GetId(), False)        
        
        zo = self.tb.AddTool(-1, 'Zoom out',
                        wx.Bitmap('./icons/magnifier_zoom_out_24.png'),
                        'Zoom out'
        )        
        self.tb.ToggleTool(zo.GetId(), False)    
        
        self.tb.AddSeparator()
        
        tb_item = self.tb.AddTool(-1, u"Insert Track", 
                                  wx.Bitmap('./icons/table_add_24.png'),
                                  'Insert a new track'
        )
        self.Bind(wx.EVT_TOOL, self._on_toolbar_insert_track, tb_item)
  
        tb_item = self.tb.AddTool(-1, u"Remove Track", 
                                  wx.Bitmap('./icons/table_delete_24.png'),
                                 'Remove selected tracks'
        )
        self.Bind(wx.EVT_TOOL, self._on_toolbar_remove_track, tb_item)
  
        self.tb.AddSeparator()  
  
        #def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        """
        Bind an event to an event handler.

        :param event: One of the EVT_* objects that specifies the
                      type of event to bind,

        :param handler: A callable object to be invoked when the
                      event is delivered to self.  Pass None to
                      disconnect an event handler.

        :param source: Sometimes the event originates from a
                      different window than self, but you still
                      want to catch it in self.  (For example, a
                      button event delivered to a frame.)  By
                      passing the source of the event, the event
                      handling system is able to differentiate
                      between the same event type from different
                      controls.

        :param id: Used to spcify the event source by ID instead
                   of instance.

        :param id2: Used when it is desirable to bind a handler
                      to a range of IDs, such as with EVT_MENU_RANGE.
        """
      
        #plot_ranges = UI.UIManager.get().get_well_plot_ranges(self.well_oid)
        #self.choice_plot_ranges = wx.Choice(self.tb, choices=plot_ranges.keys())
        #self.choice_plot_ranges.Bind(wx.EVT_CHOICE , self._OnChoicePlotRange)
        #self.tb.AddControl(self.choice_plot_ranges, '')       
        
        #self.button_edit_range = wx.Button(self.tb, label='Edit Range')
        #self.button_edit_range.Bind(wx.EVT_BUTTON , self._OnEditRange)
        #self.tb.AddControl(self.button_edit_range, '')
        
        #self.cbFit = wx.CheckBox(self.tb, -1, 'Fit')        
        #self.cbFit.Bind(wx.EVT_CHECKBOX , self._OnFit) 
        #self.tb.AddControl(self.cbFit, '')
        self.tb.Realize()    
           
    
     
     
     
     
     
