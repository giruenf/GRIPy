# -*- coding: utf-8 -*-
import wx
import wx.aui as aui
from plotter import PlotterController 
from plotter import PlotterModel
from plotter import Plotter
from UI.uimanager import UIManager
from UI.logplot_base import OverviewFigureCanvas
from UI.logplot_internal import LogPlotInternal
from UI.plotstatusbar import PlotStatusBar
from App.utils import LogPlotState  
from App.utils import is_wxPhoenix      
from App import log   
      
      
      
LP_NORMAL_TOOL = wx.NewId()        
LP_SELECTION_TOOL = wx.NewId()     
LP_ADD_TRACK = wx.NewId()     
LP_REMOVE_TRACK = wx.NewId()     
    
  

  
class LogPlotController(PlotterController):
    
    tid = 'logplot_controller'
        
    def __init__(self):
        super(LogPlotController, self).__init__()     

    def __len__(self):
        try:
            return len(self.view.main_panel)
        except AttributeError:   
            return 0
        except Exception:
            log.exception('ERROR')
            raise
    
        
    def insert_track(self):
        UIM = UIManager()
        selected_tracks = self.get_tracks_selected()
        if not selected_tracks:
            new_track = UIM.create('track_controller', self.uid)
            return [new_track.uid] 
        ret_list = []    
        for track in selected_tracks[::-1]:
																 
            new_track = UIM.create('track_controller', self.uid)
            new_track.model.pos = track.model.pos
            ret_list.append(new_track.uid)
        return ret_list


    def remove_selected_tracks(self):
        UIM = UIManager()
        for track in self.get_tracks_selected():
            UIM.remove(track.uid)    
        self.refresh_child_positions() 

    def show_status_message(self, msg):
        self.view.status_bar.SetStatusText(msg, 0)
 
 
    def get_tracks_selected(self):
        UIM = UIManager()
        return [track for track in UIM.list('track_controller', self.uid) \
                if track.model.selected]        
       

    def get_track_on_position(self, pos):
       # print 'get_track_on_position:', pos
        try:
            window = self.view.main_panel.top_splitter.GetWindow(pos)
        except Exception:
            window = None
        if window:
            UIM = UIManager()
            for track in UIM.list('track_controller', self.uid):
                if track.view.label == window:
                    return track
        else:
            return None
 

    def get_ylim(self):
       return (self.model.y_min, self.model.y_max)
 
   
    def refresh_child_positions(self, **kwargs):
        start_pos = 0
        if kwargs:
            if kwargs.get('start_pos'):
                start_pos = kwargs.get('start_pos')
        for i in range(start_pos, len(self)):
            #try:
            track_ctrl = self.get_track_on_position(i)
            if track_ctrl:
                track_ctrl.model.pos = i
            else:
                msg = 'ERROR: No track at given position {}'.format(i)
                log.error(msg)
                raise Exception(msg)
            #except Exception:
            #    msg = 'ERROR on setting position {} to TrackController {}'.format(i, track_ctrl.uid)
            #    log.exception(msg)
            #    raise  


    #def add_to_selection(self, track_controller):
    #    print '\n\n\nadd_to_selection', track_controller.uid         

    '''
    def destroy_track(self, track_controller):
        try:
            title_parent = self.view.main_panel.top_splitter
            track_parent = self.view.main_panel.bottom_splitter
            # TODO: As linhas abaixo faziam com que a aplicação 'voasse' quando um Track
            # fosse excluido. Verificar se o comentário será mantido. 
            #track_controller.view.label.SetDropTarget(None)
            #track_controller.view.track.SetDropTarget(None) 
            title_parent.DetachWindow(track_controller.view.label)
            track_parent.DetachWindow(track_controller.view.track)        
            track_controller.view.label.Hide()
            track_controller.view.track.Hide()
            UIM = UIManager()
            UIM.remove(track_controller.uid)
     
        except Exception:
            msg = 'ERROR destroying track {}.'.format(self.uid)
            log.exception(msg)
    '''        
  

    def on_change_ylim(self, **kwargs):
        UIM = UIManager()
        for track in UIM.list('track_controller', self.uid):
            #print track.uid
            track.set_ylim(self.model.y_min, self.model.y_max)
        self.update_adaptative()
        

    def on_change_cursor_state(self, **kwargs):
        if kwargs.get('new_value') == LogPlotState.NORMAL_TOOL:
            for track in self.get_tracks_selected():
                track.model.selected = False
        
        

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
        #print '\nscale chosen', SCALES[idx]    




class LogPlotModel(PlotterModel):
    tid = 'logplot_model'

    _ATTRIBUTES = {
        'pos': {'default_value': -1, 'type': int},
        'y_min': {'default_value': 0.0, 
                  'type': float, 
                  'on_change': LogPlotController.on_change_ylim
        },
        'y_max': {'default_value': 10000.0, 
                  'type': float, 
                  'on_change': LogPlotController.on_change_ylim
        },
        'cursor_state': {'default_value': LogPlotState.NORMAL_TOOL, 
                         'type': LogPlotState, 
                         'on_change': LogPlotController.on_change_cursor_state
        },
    }    
    
    def __init__(self, controller_uid, **base_state):   
        super(LogPlotModel, self).__init__(controller_uid, **base_state)   
                   
    
    
    
    
class LogPlot(Plotter):
    tid = 'logplot'


    def __init__(self, controller_uid, **kwargs):
        self.main_panel_class = LogPlotInternal
        super(LogPlot, self).__init__(controller_uid) 
        UIM = UIManager()        
        controller = UIM.get(self._controller_uid)
        
        self.main_panel = self.main_panel_class(self) 
 #       self._create_toolbar()
        self.tb = LogPlotToolBar(self)
       
        self.status_bar = PlotStatusBar(self)
                                  
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)        
            
        self.hbox.Add(self.main_panel, 1, wx.EXPAND)  #self.ttsplitter, 1, flag=wx.EXPAND)  
        
        #'''
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
                            controller.model.y_min,
                            controller.model.y_max,

        )
        
        self.overview_track.set_callback(self._set_new_depth)
        op_sizer.Add(self.overview_track, 1, wx.EXPAND|wx.ALL, self.overview_border)
        self.overview_panel.SetSizer(op_sizer)
        self.overview_track.show_index_curve()
        self.hbox.Add(self.overview_panel, 0, wx.EXPAND)
        #'''        
        
        ###        
        
        
        #self.SetInitialSize((50, 50))
        
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.vbox.Add(self.tb, 0, flag=wx.TOP|wx.EXPAND)
        self.vbox.Add(self.hbox, 1, flag=wx.EXPAND)
        
        self.vbox.Add(self.status_bar, 0, flag=wx.BOTTOM|wx.EXPAND)
        
        self.SetSizer(self.vbox)          
        self.Layout()
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)        
        
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
        
        '''
        self.main_panel.bottom_splitter.Bind(wx.EVT_SIZE, 
                                             self._on_bottom_splitter_size
        ) 
        '''
        
   
    def PreDelete(self):
        #print 'PreDelete LogPlot start'
        try:
            if is_wxPhoenix():
                # Phoenix code
                self.vbox.Remove(0)
            else:
                # wxPython classic code    
                self.vbox.Remove(self.tb)
            del self.tb
            #print 'PreDelete LogPlot ended normally'
        except Exception, e:
            print 'PreDelete LogPlot ended with error:', e.args
         


    def _detach_windows(self, label, track):
        try:
            self.main_panel.top_splitter.DetachWindow(label)
            self.main_panel.bottom_splitter.DetachWindow(track)  
        except Exception, e:
            msg = 'Error in LogPlot._detach_windows: ' + e.args
            log.exception(msg)
            print msg
            
    
    
    def _set_new_depth(self, depth):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.model.y_min, controller.model.y_max = depth
        
    """    
    def __len__(self):
        try:
            return len(self.main_panel)
        except AttributeError:   
            #log.exception('ERROR')
            return 0
        except Exception:
            log.exception('ERROR')
            raise
    """        

    def _on_sash_pos_change(self, event):
        idx = event.GetSashIdx()
        new_width = event.GetSashPosition()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        track_ctrl = controller.get_track_on_position(idx)
        track_ctrl.model.width = new_width


    def _on_bottom_splitter_size(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid) 
        controller.update_adaptative()
        

    def _do_change_width(self, idx, width, event_object=None):
        self.main_panel.bottom_splitter._DoSetSashPosition(idx, width)
        self.main_panel.bottom_splitter._SizeComponent()
        self.main_panel.top_splitter._DoSetSashPosition(idx, width)
        self.main_panel.top_splitter._SizeComponent()    


    def _insert(self, pos, label_window, track_window, width):
        self.main_panel.insert(pos, label_window, track_window, width)
        #UIM = UIManager()
        #controller = UIM.get(self._controller_uid)
        #if pos < (len(self)-1):
        #    controller.refresh_child_positions(start_pos=pos+1)
                                              
                                      
    def get_title(self):
        return 'Log Plot [oid:' + str(self._controller_uid[1]) + ']'     


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
        
       # print '\n_on_change_tool:'
        if event.GetId() == LP_NORMAL_TOOL:
       #     print 'NORMAL_TOOL'
            controller.model.cursor_state = LogPlotState.NORMAL_TOOL
        elif event.GetId() == LP_SELECTION_TOOL:    
       #     print 'SELECTION_TOOL'
            controller.model.cursor_state = LogPlotState.SELECTION_TOOL
        else:
            raise Exception()    


    def _OnEditFormat(self, event): 
        UIM = UIManager()
        lp_editor_ctrl = UIM.create('log_plot_editor_controller', self._controller_uid)
        lp_editor_ctrl.view.Show()							  
        
            
     #   print aui.AUI_BUTTON_STATE_NORMAL    
     #   print aui.AUI_BUTTON_STATE_HOVER
     #   print aui.AUI_BUTTON_STATE_PRESSED
     #   print aui.AUI_BUTTON_STATE_DISABLED
     #   print aui.AUI_BUTTON_STATE_HIDDEN  
     #   print aui.AUI_BUTTON_STATE_CHECKED  
            
            
            
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
        

        self.tb.AddTool(LP_NORMAL_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self.tb.ToggleTool(LP_NORMAL_TOOL, True) 

        self.tb.AddTool(LP_SELECTION_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self.Bind(wx.EVT_TOOL, self._on_change_tool, None, LP_NORMAL_TOOL, LP_SELECTION_TOOL)

        
        ''' 
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
        '''
        
 
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
          
          

     
class LogPlotToolBar(aui.AuiToolBar):
    
    def __init__(self, parent):
        super(LogPlotToolBar, self).__init__(parent)
        self.SetToolBitmapSize(wx.Size(48, 48))  
        

        self.AddTool(LP_NORMAL_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Normal Tool', 
                      'Normal Tool',
                      None
        )
        self.ToggleTool(LP_NORMAL_TOOL, True) 

        self.AddTool(LP_SELECTION_TOOL, 
                      wx.EmptyString,
                      wx.Bitmap('./icons/cursor_filled_24.png'), 
                      wx.NullBitmap,
                      wx.ITEM_RADIO,
                      'Selection Tool', 
                      'Selection Tool',
                      None
        )  
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_change_tool, None,
                  LP_NORMAL_TOOL, LP_SELECTION_TOOL
        )

        self.AddSeparator()
        
        tb_item = self.AddTool(-1, u"Insert Track", 
                                  wx.Bitmap('./icons/table_add_24.png'),
                                  'Insert a new track'
        )
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_toolbar_insert_track, tb_item)
  
  
        tb_item = self.AddTool(-1, u"Remove Track", 
                                  wx.Bitmap('./icons/table_delete_24.png'),
                                 'Remove selected tracks'
        )
        self.Bind(wx.EVT_TOOL, self.GetParent()._on_toolbar_remove_track, tb_item)
  
        self.AddSeparator()  

        if is_wxPhoenix():
            # Phoenix code
            button_edit_format = wx.Button(self, label='Edit LogPlot')
            button_edit_format.Bind(wx.EVT_BUTTON , self.GetParent()._OnEditFormat)
            self.AddControl(button_edit_format, '')
            self.AddSeparator() 
            
        self.Realize()  
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
