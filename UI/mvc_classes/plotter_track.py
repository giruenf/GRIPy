# -*- coding: utf-8 -*-
import wx
from App.utils import DropTarget
from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIModelBase 
from UI.uimanager import UIViewBase 
from track_base import TrackFigureCanvas
from title_base import PlotLabel
from App.utils import LogPlotState  
from App.utils import parse_string_to_uid
from App import log




class TrackController(UIControllerBase):
    tid = 'track_controller'
    
    def __init__(self):
        super(TrackController, self).__init__()
        
    def PostInit(self):    
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        y_min, y_max = parent_ctrl.get_ylim()
        self.set_ylim(y_min, y_max)


    def get_position(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        title_parent = parent_ctrl.view.main_panel.top_splitter
        track_parent = parent_ctrl.view.main_panel.bottom_splitter
        idx_top = title_parent.IndexOf(self.view.label)        
        idx_bottom = track_parent.IndexOf(self.view.track)
        assert idx_top == idx_bottom, "ERROR: Diferent positions for top and bottom TrackView panels."
        return idx_top
        
        
    def append_object(self, obj_uid):
        UIM = UIManager()
        toc = UIM.create('track_object_controller', self.uid)  
        toc.set_uid(obj_uid)
        toc.plot()
        #toc.set_data(obj.data, index_data)
        
        """
        _ATTRIBUTES = {
            'obj_uid': {'default_value': wx.EmptyString, 
                        'type': str, 
                        'on_change': TrackObjectController.on_change_objuid
            },
            'left_scale': {'default_value': FLOAT_NULL_VALUE, 'type': float},
            'right_scale': {'default_value': FLOAT_NULL_VALUE, 'type': float},
            'unit': {'default_value': wx.EmptyString, 'type': str},
            'backup': {'default_value': wx.EmptyString, 'type': str},
            'thickness': {'default_value': 1, 'type': int},
            'color': {'default_value': 'black', 'type': str},
            'x_scale': {'default_value': 0, 'type': int},
            'plottype': {'default_value': wx.EmptyString, 'type': str},
            'visible': {'default_value': True, 'type': bool},
            'cmap': {'default_value': 'rainbow', 'type': str},
        }     
        """
        
    def set_ylim(self, ymin, ymax):
        self.view._set_ylim(ymin, ymax) 
        
        
    def get_cursor_state(self):
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        return parent_ctrl.model.cursor_state 

    """    
    def on_change_label(self, **kwargs):
        text = ''        
        if kwargs.get('key') == 'label':
            if kwargs.get('new_value'):
                text = kwargs.get('new_value')         
        if not text:
            text = str(self.model.pos+1)  
        self.view.label.update_title(text=text)  
    """
    
    def on_change_width(self, **kwargs):  
        UIM = UIManager()
        parent_uid = UIM._getparentuid(self.uid)
        parent_ctrl = UIM.get(parent_uid)
        parent_ctrl.view._do_change_width(self.get_position(), self.model.width)
        if not self.model.selected:
            return
        selected = parent_ctrl.get_tracks_selected()
        selected.remove(self)    
        for track in selected:
            track.model.selected = False  
            track.model.width = self.model.width   
            track.model.selected = True


    def on_change_properties(self, **kwargs):  
        if kwargs.get('key') == 'label':
            text = '' 
            if kwargs.get('new_value'):
                text = kwargs.get('new_value') 
            if not text:
                text = str(self.model.pos+1)  
            self.view.update_title(text) 

        elif kwargs.get('key') == 'pos':
            if kwargs.get('old_value') != -1:
                
                if self.view._change_position(kwargs.get('new_value')):    
                    UIM = UIManager()
                    if kwargs.get('new_value') < kwargs.get('old_value'):
                        for i in range(kwargs.get('old_value')-1, kwargs.get('new_value')-1, -1):
                            for track in UIM.do_query(self.tid, pos=i):
                                if track is not self:
                                    track.model.pos += 1 
                    else:
                        for i in range(kwargs.get('old_value'), kwargs.get('new_value')+1):
                            for track in UIM.do_query(self.tid, pos=i):
                                if track is not self:
                                    track.model.pos -= 1 
                #i = kwargs.get('old_value')
                #for i in range(kwargs.get('old_value')-1, kwargs.get('new_value'), -1):
                    
                
            if not self.model.label:
                self.view.update_title(kwargs.get('new_value')+1)                
            
        elif kwargs.get('key') == 'show_depth':
            if kwargs.get('new_value'):
                self.view.track.show_index_curve(self.model.y_major_grid_lines)               
            else:
                self.view.track.hide_index_curve()   
        else:
            if kwargs.get('key') == 'y_major_grid_lines' and self.model.show_depth:
                self.view.track.show_index_curve(self.model.y_major_grid_lines)
            self.view.track.update(kwargs.get('key'), kwargs.get('new_value'))

    def on_change_selection(self, **kwargs):  
        self.view._invert_selection()
        
        
        
        

class TrackModel(UIModelBase):
    tid = 'track_model'
    
    _ATTRIBUTES = {
        'pos': {'default_value': -1, 'type': int, 'on_change': TrackController.on_change_properties},
        'label': {'default_value': wx.EmptyString, 'type': unicode, 'on_change': TrackController.on_change_properties},
        'plotgrid': {'default_value': False, 'type': bool, 'on_change': TrackController.on_change_properties},
        'x_scale': {'default_value': 0, 'type': int, 'on_change': TrackController.on_change_properties},
        'y_major_grid_lines': {'default_value': 500.0, 'type': float, 'on_change': TrackController.on_change_properties},
        'y_minor_grid_lines': {'default_value': 100.0, 'type': float, 'on_change': TrackController.on_change_properties},
        'depth_lines': {'default_value': 5, 'type': int, 'on_change': TrackController.on_change_properties},
        'width': {'default_value': 160, 'type': int, 'on_change': TrackController.on_change_width},
        'minorgrid': {'default_value': False, 'type': bool, 'on_change': TrackController.on_change_properties},
        'leftscale': {'default_value': 0.2, 'type': float, 'on_change': TrackController.on_change_properties},
        'decades':  {'default_value': 4, 'type': int, 'on_change': TrackController.on_change_properties},   
        'scale_lines': {'default_value': 5, 'type': int, 'on_change': TrackController.on_change_properties},
        'selected': {'default_value': False, 'type': bool, 'on_change': TrackController.on_change_selection},    
        'show_depth': {'default_value': False, 'type': bool, 'on_change': TrackController.on_change_properties}
    }        
    
  
    def __init__(self, controller_uid, **base_state): 
        super(TrackModel, self).__init__(controller_uid, **base_state) 
   


    
ShowDepthId = wx.NewId()
HideDepthId = wx.NewId()
ShowGridId = wx.NewId()
HideGridId = wx.NewId()
ScaleLinGridId = wx.NewId()
ScaleLogGridId = wx.NewId()
DepthLinesAllId = wx.NewId()
DepthLinesLeftId = wx.NewId()
DepthLinesRightId = wx.NewId()
DepthLinesCenterId = wx.NewId()
DepthLinesLeftRightId = wx.NewId()
DepthLinesNoneId = wx.NewId()
Decades1Id = wx.NewId()
Decades10Id = wx.NewId()
Decades100Id = wx.NewId()
Decades1000Id = wx.NewId()
Decades10000Id = wx.NewId()
Decades100000Id = wx.NewId()
Decades1000000Id = wx.NewId()

ScaleLines3Id = wx.NewId()
ScaleLines4Id = wx.NewId()
ScaleLines5Id = wx.NewId()
ScaleLines6Id = wx.NewId()
ScaleLines7Id = wx.NewId()




class TrackView(UIViewBase):
    tid = 'track_view'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        
        title_parent = parent_controller.view.main_panel.top_splitter
        track_parent = parent_controller.view.main_panel.bottom_splitter
        
        self.label = PlotLabel(title_parent, self) 
        self.track = TrackFigureCanvas(track_parent, self,
                size=wx.Size(controller.model.width, track_parent.GetSize()[1]),
                **controller.model.get_state()
        ) 
        
        self.dt1 = DropTarget(controller.append_object)
        #self.dt1.set_callback(controller.append_object)
        self.label.SetDropTarget(self.dt1)
        self.dt2 = DropTarget(controller.append_object)
        #self.dt2.set_callback(controller.append_object)
        self.track.SetDropTarget(self.dt2)
        #self.track.SetDropTarget(self.dt)

        self.track.mpl_connect('motion_notify_event', self.on_track_move)
        

    def on_track_move(self, event):
        if event.inaxes is None:
            return
        info = 'Index: ' + "{:0.2f}".format(event.ydata)    
        OM = ObjectManager(self)
        UIM = UIManager()
        pixelsdata = event.inaxes.transData.transform_point((event.xdata, event.ydata))
        for to in UIM.list('track_object_controller', self._controller_uid):
            uid_string, value = to.get_curve_value(pixelsdata)
            tid, oid = parse_string_to_uid(uid_string)
            obj = OM.get((tid, oid))
            info += ', ' + obj.name + ': {:0.2f}'.format(value)    
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        parent_controller.show_status_message(info)



    def PostInit(self):  
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        
        if controller.model.pos == -1:
            #controller.model.set_value_from_event('pos', len(parent_controller.view))
            controller.model.pos = len(parent_controller)
    


        parent_controller.view._insert(controller.model.pos, self.label, 
                                      self.track,
                                      controller.model.width
        )         
        
        
    def PreDelete(self):
        #print 'PreDelete TrackView start'
        try:
            UIM = UIManager()
            parent_controller_uid = UIM._getparentuid(self._controller_uid)
            parent_controller =  UIM.get(parent_controller_uid)
            parent_controller.view._detach_windows(self.label, self.track)  
            #self.label.Hide()
            #self.track.Hide()
            #self.label.SetDropTarget(None)
            #self.track.SetDropTarget(None)
            #self.dt.set_callback(None)
            #del self.dt
            self.label.Destroy()
            self.track.Destroy()
           # del self.label
           # del self.track
        except Exception, e:
            print'PreDelete TrackView ended with error:', e.args
            raise
        #print 'PreDelete TrackView ended normally'


    def update_title(self, new_title):
        self.label.update_title(text=str(new_title))        
                              
        
    def _invert_selection(self):
        self.track._do_select()
        self.label._do_select()


    def _set_ylim(self, ymin, ymax):
        self.track.set_ylim((ymax, ymin))


    def _change_position(self, new_pos):
        UIM = UIManager()
        #controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)
        title_parent = parent_controller.view.main_panel.top_splitter
        track_parent = parent_controller.view.main_panel.bottom_splitter
        return (title_parent.ChangeWindowPosition(self.label, new_pos) and 
                        track_parent.ChangeWindowPosition(self.track, new_pos))
        
            

    #def _has_changed_position_to(self, new_pos):


    def process_event(self, event):
        ### From: http://stackoverflow.com/questions/14617722/matplotlib-and-wxpython-popupmenu-cooperation     
        print
        #if event.guiEvent.GetEventObject().HasCapture():            
        #    event.guiEvent.GetEventObject().ReleaseMouse()        
        ###
        #print '\nTrackView.process_event:', event
        
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        
        if isinstance(event, wx.MouseEvent):        
            gui_evt = event
        else:
            gui_evt = event.guiEvent
        
        #print '\n', gui_evt.GetEventObject()   
        #if isinstance(gui_evt.GetEventObject(), TrackFigureCanvas):
        #    print '\nTrackFigureCanvas'
        #else:
        #    print '\nPlotLabel'
        ###
        # Context Menu
        ###

        if gui_evt.GetButton() == 1:
            #print 'botao 1'
            if controller.get_cursor_state() == LogPlotState.SELECTION_TOOL:
                controller.model.selected = not controller.model.selected
            
        
        elif gui_evt.GetButton() == 2:
            pass
            #print 'botao 2'   
            #controller.model.selected = not controller.model.selected
            #self.track._do_select()
            
        elif gui_evt.GetButton() == 3: 
            #print 'botao 3'  
            if isinstance(gui_evt.GetEventObject(), TrackFigureCanvas):
                menu = wx.Menu()
                #
                depth_submenu = wx.Menu()
                depth_submenu.AppendRadioItem(ShowDepthId, 'Show')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ShowDepthId)
                depth_submenu.AppendRadioItem(HideDepthId, 'Hide')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=HideDepthId)
                if controller.model.show_depth:
                    depth_submenu.Check(ShowDepthId, True)
                else:
                    depth_submenu.Check(HideDepthId, True)
                menu.AppendSubMenu(depth_submenu, 'Depth')
                #
                grid_submenu = wx.Menu()
                grid_submenu.AppendRadioItem(ShowGridId, 'Show')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ShowGridId)
                grid_submenu.AppendRadioItem(HideGridId, 'Hide')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=HideGridId)
                if controller.model.plotgrid:
                    grid_submenu.Check(ShowGridId, True)
                else:
                    grid_submenu.Check(HideGridId, True)
                menu.AppendSubMenu(grid_submenu, 'Grid')
                
                #
                scale_submenu = wx.Menu()
                scale_submenu.AppendRadioItem(ScaleLinGridId, 'Linear')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLinGridId)
                scale_submenu.AppendRadioItem(ScaleLogGridId, 'Logarithmic')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLogGridId)
                if not controller.model.x_scale:
                    scale_submenu.Check(ScaleLinGridId, True)
                else:
                    scale_submenu.Check(ScaleLogGridId, True)
                menu.AppendSubMenu(scale_submenu, 'Scale')
                #           
                 
                depth_lines_submenu = wx.Menu()
                
                depth_lines_submenu.AppendRadioItem(DepthLinesAllId, 'All')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesAllId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesLeftId, 'Left')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesLeftId)
    
                depth_lines_submenu.AppendRadioItem(DepthLinesRightId, 'Right')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesRightId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesCenterId, 'Center')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesCenterId)
                
                depth_lines_submenu.AppendRadioItem(DepthLinesLeftRightId, 'Left and Right')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesLeftRightId)  
     
                depth_lines_submenu.AppendRadioItem(DepthLinesNoneId, 'None')
                event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=DepthLinesNoneId)  
               
                if controller.model.depth_lines == 0:
                    depth_lines_submenu.Check(DepthLinesAllId, True)
                    
                elif controller.model.depth_lines == 1:
                    depth_lines_submenu.Check(DepthLinesLeftId, True)
                    
                elif controller.model.depth_lines == 2:
                    depth_lines_submenu.Check(DepthLinesRightId, True)
                    
                elif controller.model.depth_lines == 3:
                    depth_lines_submenu.Check(DepthLinesCenterId, True)  
    
                elif controller.model.depth_lines == 4:
                    depth_lines_submenu.Check(DepthLinesLeftRightId, True)  
                    
                elif controller.model.depth_lines == 5:
                    depth_lines_submenu.Check(DepthLinesNoneId, True)                  
                    
                menu.AppendSubMenu(depth_lines_submenu, 'Depth Lines')
                #                   
             
                menu.AppendSeparator() 
                if controller.model.x_scale == 0:
                    scale_lines_submenu = wx.Menu()
                
                    scale_lines_submenu.AppendRadioItem(ScaleLines3Id, '3')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLines3Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines4Id, '4')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLines4Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines5Id, '5')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLines5Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines6Id, '6')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLines6Id)
                    scale_lines_submenu.AppendRadioItem(ScaleLines7Id, '7')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=ScaleLines7Id)
    
                    if controller.model.scale_lines == 3:
                        scale_lines_submenu.Check(ScaleLines3Id, True)  
                    elif controller.model.scale_lines == 4:
                        scale_lines_submenu.Check(ScaleLines4Id, True)  
                    elif controller.model.scale_lines == 5:
                        scale_lines_submenu.Check(ScaleLines5Id, True)                   
                    elif controller.model.scale_lines == 6:
                        scale_lines_submenu.Check(ScaleLines6Id, True)
                    elif controller.model.scale_lines == 7:
                        scale_lines_submenu.Check(ScaleLines7Id, True)    
                    menu.AppendSubMenu(scale_lines_submenu, 'Scale Lines')
                    
                else:    
                    decades_submenu = wx.Menu()
                
                    decades_submenu.AppendRadioItem(Decades1Id, '1')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades1Id)
                    decades_submenu.AppendRadioItem(Decades10Id, '10')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades10Id)
                    decades_submenu.AppendRadioItem(Decades100Id, '100')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades100Id)
                    decades_submenu.AppendRadioItem(Decades1000Id, '1.000')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades1000Id)        
                    decades_submenu.AppendRadioItem(Decades10000Id, '10.000')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades10000Id)
                    decades_submenu.AppendRadioItem(Decades100000Id, '100.000')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades100000Id)
                    decades_submenu.AppendRadioItem(Decades100000Id, '1.000.000')
                    event.canvas.Bind(wx.EVT_MENU, self.menu_selection, id=Decades1000000Id)
                    if controller.model.decades == 1:
                        decades_submenu.Check(Decades1Id, True)  
                    elif controller.model.decades == 2:
                        decades_submenu.Check(Decades10Id, True)  
                    elif controller.model.decades == 3:
                        decades_submenu.Check(Decades100Id, True)  
                    elif controller.model.decades == 4:
                        decades_submenu.Check(Decades1000Id, True)  
                    elif controller.model.decades == 5:
                        decades_submenu.Check(Decades10000Id, True)                   
                    elif controller.model.decades == 6:
                        decades_submenu.Check(Decades100000Id, True)
                    elif controller.model.decades == 7:
                        decades_submenu.Check(Decades1000000Id, True)    
                    menu.AppendSubMenu(decades_submenu, 'Log Max')
                #   
                    
                event.canvas.PopupMenu(menu, event.guiEvent.GetPosition())  
                menu.Destroy() # destroy to avoid mem leak
            

        
    def menu_selection(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if event.GetId() == ShowDepthId:
            controller.model.show_depth = True    
        elif event.GetId() == HideDepthId:
            controller.model.show_depth = False
        elif event.GetId() == ShowGridId:
            controller.model.plotgrid = True    
        elif event.GetId() == HideGridId:
            controller.model.plotgrid = False
        elif event.GetId() == ScaleLinGridId:
            controller.model.x_scale = 0    
        elif event.GetId() == ScaleLogGridId:
            controller.model.x_scale = 1        
        elif event.GetId() == DepthLinesAllId:
            controller.model.depth_lines = 0
        elif event.GetId() == DepthLinesLeftId:
            controller.model.depth_lines = 1  
        elif event.GetId() == DepthLinesRightId:
            controller.model.depth_lines = 2
        elif event.GetId() == DepthLinesCenterId:
            controller.model.depth_lines = 3   
        elif event.GetId() == DepthLinesLeftRightId:
            controller.model.depth_lines = 4           
        elif event.GetId() == DepthLinesNoneId:
            controller.model.depth_lines = 5       
        elif event.GetId() == Decades1Id:
            controller.model.decades = 1
        elif event.GetId() == Decades10Id:
            controller.model.decades = 2
        elif event.GetId() == Decades100Id:
            controller.model.decades = 3
        elif event.GetId() == Decades1000Id:
            controller.model.decades = 4
        elif event.GetId() == Decades10000Id:
            controller.model.decades = 5
        elif event.GetId() == Decades100000Id:
            controller.model.decades = 6
        elif event.GetId() == Decades1000000Id:
            controller.model.decades = 7
        elif event.GetId() == ScaleLines3Id:
            controller.model.scale_lines = 3
        elif event.GetId() == ScaleLines4Id:
            controller.model.scale_lines = 4
        elif event.GetId() == ScaleLines5Id:
            controller.model.scale_lines = 5
        elif event.GetId() == ScaleLines6Id:
            controller.model.scale_lines = 6
        elif event.GetId() == ScaleLines7Id:
            controller.model.scale_lines = 7
