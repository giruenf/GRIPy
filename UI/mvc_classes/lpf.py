# -*- coding: utf-8 -*-
import sys
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase  
from UI.uimanager import UIModelBase
from UI.uimanager import UIViewBase 
from App import log
#
###
import wx.dataview as dv
import wx.propgrid as pg
from wx.propgrid import PropertyGrid
#from wx.combo import OwnerDrawnComboBox
import wx.lib.colourdb
from collections import OrderedDict
from OM.Manager import ObjectManager
###
from track import TrackController    
from track_object import TrackObjectController     
from App.app_utils import parse_string_to_uid

from wx.adv import OwnerDrawnComboBox  

import App.pubsub as pub

from log_plot import LogPlotController



class LogPlotEditorController(UIControllerBase):
    tid = 'log_plot_editor_controller'
     
    def __init__(self):
        super(LogPlotEditorController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))


    def PostInit(self):
        UIM = UIManager()
        UIM.create('lpe_track_panel_controller', self.uid)
        UIM.create('lpe_objects_panel_controller', self.uid)
        #
        UIM.subscribe(self.object_created, 'create')
        UIM.subscribe(self.object_removed, 'pre_remove')
        #
        logplot_ctrl_uid = UIM._getparentuid(self.uid)
        for track in UIM.list('track_controller', logplot_ctrl_uid):
            track.subscribe(self._on_change_prop, 'change')
            for toc in UIM.list('track_object_controller', track.uid):
                toc.subscribe(self._on_change_prop, 'change')
            
        
    def PreDelete(self):
        UIM = UIManager()
        UIM.unsubscribe(self.object_created, 'create')
        UIM.unsubscribe(self.object_removed, 'pre_remove') 
        #
        logplot_ctrl_uid = UIM._getparentuid(self.uid)
        for track in UIM.list('track_controller', logplot_ctrl_uid):
            track.unsubscribe(self._on_change_prop, 'change')
            for toc in UIM.list('track_object_controller', track.uid):
                toc.unsubscribe(self._on_change_prop, 'change')        
        #
        #TODO: verificar isso....
        try:
            self.view.Close()
        except RuntimeError:    
            # Error on executing PreDelete on App exit
            pass


    def object_created(self, objuid, parentuid):
        if objuid[0] != 'track_controller' and \
                                    objuid[0] != 'track_object_controller':
            return
        UIM = UIManager()
        logplot_ctrl_uid = UIM._getparentuid(self.uid) 
        if objuid[0] == 'track_controller' and parentuid == logplot_ctrl_uid:       
            track = UIM.get(objuid)
            #print 'LogPlotEditorController._object_created:', objuid, track.model.pos
            lpe_tp = UIM.list('lpe_track_panel_controller', self.uid)[0]
            lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
            lpe_tp.create_item(track)
            lpe_op.create_item(track)
            track.subscribe(self._on_change_prop, 'change')
        
        elif objuid[0] == 'track_object_controller':
            logplot_candidate = UIM._getparentuid(parentuid)
            if logplot_candidate == logplot_ctrl_uid:
                lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
                track = UIM.get(parentuid)
                toc = UIM.get(objuid)
                lpe_op.create_item(toc, track)
                toc.subscribe(self._on_change_prop, 'change')

        
    def object_removed(self, objuid):   
        print 'object_removed', objuid
        UIM = UIManager()
        if objuid[0] == 'track_controller':
            track_parent_uid = UIM._getparentuid(objuid)
            logplot_ctrl_uid = UIM._getparentuid(self.uid)
            if track_parent_uid == logplot_ctrl_uid:
                track = UIM.get(objuid)
                lpe_tp = UIM.list('lpe_track_panel_controller', self.uid)[0]
                lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
                track.unsubscribe(self._on_change_prop, 'change')
                lpe_tp.remove_item(track)
                lpe_op.remove_item(track)       
        elif objuid[0] == 'track_object_controller':
            print 'object_removed:', objuid
            track_uid = UIM._getparentuid(objuid)
            track_parent_uid = UIM._getparentuid(track_uid)
            logplot_ctrl_uid = UIM._getparentuid(self.uid)
            if track_parent_uid == logplot_ctrl_uid:     
                toc = UIM.get(objuid)
                toc.unsubscribe(self._on_change_prop, 'change')
                lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
                lpe_op.remove_item(toc)
                pgcs = UIM.list('property_grid_controller', lpe_op.uid)
                if pgcs:
                    pgc = pgcs[0]
                    if pgc.get_object_uid():
                        UIM = UIManager()
                        toc = UIM.get(pgc.get_object_uid())
                        if toc.uid == objuid:
                            pgc.clear()                
                track = UIM.get(track_uid)            
                track_op_item = lpe_op._get_real_model().ObjectToItem(track)      
                lpe_op.expand_dvc_item(track_op_item)
     
                
    def _on_change_prop(self, topicObj=pub.AUTO_TOPIC, 
                                              new_value=None, old_value=None):
        UIM = UIManager()
        obj_uid = pub.pubuid_to_uid(topicObj.getName().split('.')[0])
        
        
        if obj_uid[0] == 'track_controller':
            #print '\n_on_change_prop:', self.oid, '-', topicObj.getName(), obj_uid
            track = UIM.get(obj_uid)
            lpe_tp = UIM.list('lpe_track_panel_controller', self.uid)[0]
            track_tp_item = lpe_tp._get_real_model().ObjectToItem(track)
            lpe_tp._get_real_model().ItemChanged(track_tp_item)
            lpe_tp.update_dvc()
            
            lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
            track_op_item = lpe_op._get_real_model().ObjectToItem(track)
            lpe_op._get_real_model().ItemChanged(track_op_item)
            lpe_op.update_dvc()

            
        elif obj_uid[0] == 'track_object_controller':
            toc = UIM.get(obj_uid)
            lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
            toc_item = lpe_op._get_real_model().ObjectToItem(toc)
            lpe_op._get_real_model().ItemChanged(toc_item)
            #print '_on_change_prop:', self.oid, '-', topicObj.getName()
            #lpe_op.view.reload_propgrid(toc)
        
        #elif objuid[0] == 'track_object_controller':    

            
          


class LogPlotEditor(UIViewBase, wx.Frame):
    tid = 'log_plot_editor'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        wx.Frame.__init__(self, None, -1, title='LogPlotEditor',
                                          size=(950, 600),
                                          style=wx.DEFAULT_FRAME_STYLE & 
                                          (~wx.RESIZE_BORDER) &(~wx.MAXIMIZE_BOX)
        )   


        main_sizer = wx.BoxSizer(wx.VERTICAL)  
        self.base_panel = wx.Panel(self)
        self.note = wx.Notebook(self.base_panel)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.note, 1, wx.ALL|wx.EXPAND, border=5)        
        self.base_panel.SetSizer(bsizer)
                
        #UIM = UIManager()
        #UIM.create('lpe_track_panel_controller', self.uid)
        #parent_controller_uid = UIM._getparentuid(self._controller_uid)        
        
        '''
        tracks_base_panel = wx.Panel(note, style=wx.SIMPLE_BORDER)
        sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        self.tracks_model = TracksModel(parent_controller_uid)
        tp = TracksPanel(tracks_base_panel, self.tracks_model)
        sizer_grid_panel.Add(tp, 1, wx.EXPAND|wx.ALL, border=10)
        tracks_base_panel.SetSizer(sizer_grid_panel)
        note.AddPage(tracks_base_panel, "Tracks", True)
        '''
        
        '''
        curves_base_panel = wx.Panel(note, style=wx.SIMPLE_BORDER)
        sizer_curves_panel = wx.BoxSizer(wx.VERTICAL)
        self.curves_model = CurvesModel(parent_controller_uid)
        cp = TrackObjectsPanel(curves_base_panel, self.curves_model)
        sizer_curves_panel.Add(cp, 1, wx.EXPAND|wx.ALL, border=10)
        curves_base_panel.SetSizer(sizer_curves_panel)
        note.AddPage(curves_base_panel, "Objects", True)
        '''
        
        main_sizer.Add(self.base_panel, 1, wx.EXPAND)
        bottom_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_close = wx.Button(bottom_panel, -1, "Close")
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, border=10)
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        bottom_panel.SetSizer(sizer)        
        main_sizer.Add(bottom_panel, 0,  wx.EXPAND)
        self.SetSizer(main_sizer)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created View object from class: {}.'.format(class_full_name))
        self.Bind(wx.EVT_CLOSE, self.on_close) 
         
    def on_close(self, event):
        event.Skip()
        UIM = UIManager()
        wx.CallAfter(UIM.remove, self._controller_uid)
        self.Unbind(wx.EVT_CLOSE)







class LPETrackPanelController(UIControllerBase):
    tid = 'lpe_track_panel_controller'
    
    def __init__(self):
        super(LPETrackPanelController, self).__init__()
        # LPETrackPanelModel is not a UIModelBase object
        self._real_model = LPETrackPanelModel(self.uid)

    def PostInit(self):
        self.view.dvc.AssociateModel(self._real_model)

    def _get_real_model(self):
        # LPETrackPanel needs the model
        return self._real_model
    
    def create_item(self, obj):    
        if obj.tid != 'track_controller':
            raise Exception('Cannot insert {}.'.format(obj.uid))   
        item = self._get_real_model().ObjectToItem(obj)
        self._get_real_model().ItemAdded(dv.NullDataViewItem, item)

    def remove_item(self, obj):  
        if obj.tid != 'track_controller':
            raise Exception('Cannot remove {}.'.format(obj.uid))    
        item = self._get_real_model().ObjectToItem(obj)    
        self._get_real_model().ItemDeleted(dv.NullDataViewItem, item)    
        
    def update_dvc(self):
        self.view.dvc.Refresh()     

    
# TODO: include some observation below....   
# Despite it's name       
class LPETrackPanelModel(dv.PyDataViewModel):        
    
    TRACKS_MODEL_MAPPING = {
        0: 'pos',
        1: 'label',
        2: 'width', 
        3: 'visible',
        4: 'plotgrid',
        5: 'depth_lines',
        6: 'scale_lines',
        7: 'x_scale', 
        8: 'decades',
        9: 'leftscale',
        10: 'minorgrid',
        11: 'overview'
    }    

    def __init__(self, controller_uid):   
        dv.PyDataViewModel.__init__(self)
        self._controller_uid = controller_uid  # To send commands to controller...
            
    def IsContainer(self, item):
        if not item:
            return True
        return False  

    def GetParent(self, item):
        return dv.NullDataViewItem
        
    def GetChildren(self, parent, children):   
        #print '\nGetChildren'
        UIM = UIManager()
        #controller = UIM.get(self._controller_uid)
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        tracks = UIM.list('track_controller', logplot_ctrl_uid)
        for track in tracks:
            children.append(self.ObjectToItem(track)) 
        return len(tracks)
            
            
    def GetValue(self, item, col):
        track = self.ItemToObject(item)
        if col == 0:
            return track.model.pos+1
        elif col == 5:
            value = track.model[self.TRACKS_MODEL_MAPPING.get(col)]
            if value == 0:
                return 'All'
            elif value == 1:
                return 'Left'
            elif value == 2:
                return 'Right'
            elif value == 3:
                return 'Center'    
            elif value == 4:
                return 'Left & Right'
            elif value == 5:
                return 'None'
            raise Exception('Error.')
        elif col == 7:
            value = track.model[self.TRACKS_MODEL_MAPPING.get(col)]
            if value == 0:
                return 'Linear'
            elif value == 1:
                return 'Logarithmic'
            raise Exception('Error.')    
        return track.model[self.TRACKS_MODEL_MAPPING.get(col)]

    def SetValue(self, value, item, col):
        track = self.ItemToObject(item)
        #print 'SetValue', track.uid, col, value
        if col == 5:
            if value == 'All':
                track.model.depth_lines = 0
            elif value == 'Left':
                track.model.depth_lines = 1
            elif value == 'Right':
                track.model.depth_lines = 2
            elif value == 'Center':
                track.model.depth_lines = 3
            elif value == 'Left & Right':
                track.model.depth_lines = 4
            elif value == 'None':
                track.model.depth_lines = 5
            else:    
                raise Exception('Error.')  
        elif col == 7:
            if value == 'Linear':
                track.model.x_scale = 0
            elif value == 'Logarithmic':
                track.model.x_scale = 1
            else:
                raise Exception('Error.')    
        elif col == 11:
            UIM = UIManager()
            logplot_uid = UIM._getparentuid(track.uid)
            logplot_ctrl = UIM.get(logplot_uid)
            if value:
                logplot_ctrl.set_overview_track(track.uid)
            else:
                logplot_ctrl.unset_overview_track()  
        else:       
            track.model[self.TRACKS_MODEL_MAPPING.get(col)] = value
        return True

    #def ChangedItem(self, item):
        #print 'ChangedItem'
        #obj = self.ItemToObject(item)
    #    self.ItemChanged(item)

    def GetAttr(self, item, col, attr):
        if col == 0:
            attr.SetColour('blue')
            return True
        return False
        
    def HasDefaultCompare(self):    
        return True
           
    def Compare(self, item1, item2, col, ascending):
        track1 = self.ItemToObject(item1)
        track2 = self.ItemToObject(item2)
        if track1.model.pos == track2.model.pos:
            raise Exception('Two tracks cannot have same position: {} - {}.'.format(track1.uid, track2.uid))
        if ascending: 
            if track1.model.pos > track2.model.pos:
                return 1
            else:
                return -1
        else:
            if track1.model.pos > track2.model.pos:
                return -1
            else:
                return 1
         
    def IsEnabled(self, item, col):
        return True 
   
    '''
    def InsertTracks(self):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        log_plot_ctrl = UIM.get(logplot_ctrl_uid)
        new_tracks_uid = log_plot_ctrl.insert_track()
        for uid in new_tracks_uid:
            new_track = UIM.get(uid)
            item = self.ObjectToItem(new_track)
            self.ItemAdded(dv.NullDataViewItem, item)
        return True
    '''           

        
        
class LPETrackPanel(UIViewBase, wx.Panel):
    tid = 'lpe_track_panel'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        wx.Panel.__init__(self, self._get_lpeview_notebook(), -1, style=wx.SIMPLE_BORDER)       


    def PostInit(self):
        self.base_panel = wx.Panel(self)
        self.dvc = self.create_data_view_ctrl()
        
        self.base_panel.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.base_panel.Sizer.Add(self.dvc, 1, wx.EXPAND)
        button_add_track = wx.Button(self.base_panel, label="Add track")
        self.Bind(wx.EVT_BUTTON, self.OnInsertTrack, button_add_track)
        button_delete_track = wx.Button(self.base_panel, label="Delete track(s)")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSelectedTracks, button_delete_track)
        button_select_all = wx.Button(self.base_panel, label="Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, button_select_all)
        button_select_none = wx.Button(self.base_panel, label="Select None")
        self.Bind(wx.EVT_BUTTON, self.OnSelectNone, button_select_none)
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_select_all, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_select_none, 0, wx.LEFT|wx.RIGHT, 5)
        self.base_panel.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)
        
        self.dvc.EnableDragSource(VarNodeDropData.GetFormat())
        self.dvc.EnableDropTarget(VarNodeDropData.GetFormat())
        
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_BEGIN_DRAG, self.OnItemBeginDrag)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_DROP_POSSIBLE, self.OnItemDropPossible)
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnSelectionChanged)          
        ###
        sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_grid_panel.Add(self.base_panel, 1, wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(sizer_grid_panel)
        self._get_lpeview_notebook().AddPage(self, "Tracks", True)
  

    def _get_lpeview_notebook(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid) 
        lpe_ctrl = UIM.get(parent_controller_uid)
        return lpe_ctrl.view.note
        

    def create_data_view_ctrl(self):
        dvc = dv.DataViewCtrl(self.base_panel, style=wx.BORDER_THEME | \
                            dv.DV_VERT_RULES | dv.DV_MULTIPLE| dv.DV_ROW_LINES
        ) 

        # Track
        dv_col = dvc.AppendTextColumn("Track", 0, width=45, align=wx.ALIGN_CENTER)
        dv_col.SetMinWidth(45)
        # Track Name
        dv_col = dvc.AppendTextColumn("Track Title", 1, width=80, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(80)
        # Width
        dv_col = dvc.AppendTextColumn("Width", 2, width=50, mode=dv.DATAVIEW_CELL_EDITABLE)      
        dv_col.SetMinWidth(60)
        # Visible (Track)
        dv_col = dvc.AppendToggleColumn("Visible",  3, width=50,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        # Plot Grid
        dvc.AppendToggleColumn("Plot Grid", 4, width=60,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        # Depth Lines
        dvcr = dv.DataViewChoiceRenderer(['All', 'Left', 'Right', 'Center', 'Left & Right', 'None'],
                                         mode=dv.DATAVIEW_CELL_EDITABLE
        )
        dvcol = dv.DataViewColumn("Depth Lines", dvcr, 5, width=85)
        dvc.AppendColumn(dvcol)
        # Scale Lines
        dv_col = dvc.AppendTextColumn("Scale Lines",   6, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70)   
        # Scale (Track)
        dvcr = dv.DataViewChoiceRenderer(['Linear', 'Logarithmic'], mode=dv.DATAVIEW_CELL_EDITABLE)
        dvcol = dv.DataViewColumn("Scale", dvcr, 7, width=80)
        dv_col.SetMinWidth(75)    
        dvc.AppendColumn(dvcol)
        # Decimation
        dv_col = dvc.AppendTextColumn("Log Decimation", 8, width=100, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(85)        
        # Left Scale
        dv_col = dvc.AppendTextColumn("Log Left Scale", 9, width=85, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(80)   
        # Minor Lines  
        dv_col = dvc.AppendToggleColumn("Log Minor Lines", 10, width=100, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(90) 
        # Overview Track
        dv_col = dvc.AppendToggleColumn("Overview", 11, width=90, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(90) 
        
        for dv_col in dvc.Columns:
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER)         
        
        return dvc    
      
         
    def OnItemBeginDrag(self, event):
        item = event.GetItem()
        if not item.IsOk():
            event.Veto()
            return
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        obj = model.ItemToObject(item)
        self.node = VarNodeDropData()
        self.node.SetObject(obj) 
        event.SetDataObject(self.node)
        event.SetDragFlags(wx.Drag_DefaultMove)

        
    def OnItemDropPossible(self, event):
        new_pos_item = event.GetItem()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        old_pos_track = self.node.GetObject()
        old_pos_item = model.ObjectToItem(old_pos_track)

        if new_pos_item == old_pos_item:
            return False   
        self.dvc.UnselectAll() # Change Selection    
        
        if new_pos_item.IsOk() and \
                            event.GetDataFormat() == VarNodeDropData.GetFormat():                
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            model = controller._get_real_model()                    
            self.dvc.Select(new_pos_item)    
            new_pos_track = model.ItemToObject(new_pos_item)
            new_pos_track.model.pos = old_pos_track.model.pos

            #model.ItemChanged(new_pos_item) 
            #model.ItemChanged(old_pos_item)
            return True    
        return False        
                 

    def OnSelectAll(self, evt):
        self.dvc.SelectAll()
        self._DoSelectionChanged()
        self.dvc.SetFocus()
   
    def OnSelectNone(self, evt):
        self.dvc.UnselectAll()        
        self._DoSelectionChanged()
           
    def OnSelectionChanged(self, event):
        pass
        #self._DoSelectionChanged()

    def _DoSelectionChanged(self):        
        items = self.dvc.GetSelections()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        tracks = UIM.list('track_controller', logplot_ctrl_uid)
        tracks_selected = [model.ItemToObject(item) for item in items]
        for track in tracks:
            track.model.selected = track in tracks_selected
            
            
    def OnInsertTrack(self, event):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        log_plot_ctrl = UIM.get(logplot_ctrl_uid)
        log_plot_ctrl.insert_track()  
        
        
    def OnDeleteSelectedTracks(self, event):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        log_plot_ctrl = UIM.get(logplot_ctrl_uid)
        log_plot_ctrl.remove_selected_tracks()
        





###############################################################################


class VarNodeDropData(wx.CustomDataObject):
    NAME = "VarNode"
    PICKLE_PROTOCOL = 2
	   
    def __init__(self):
        wx.CustomDataObject.__init__(self, VarNodeDropData.GetFormat())
    
    def SetObject(self, obj):
        self.SetData(str(obj.uid))
        
    def GetObject(self):
        obj_uid_str = self.GetData().tobytes()
        UIM = UIManager()
        return UIM.get(obj_uid_str)
    
    @staticmethod  
    def GetFormat():
        return wx.DataFormat(VarNodeDropData.NAME)
        

###############################################################################
###############################################################################


class LPEObjectsPanelController(UIControllerBase):
    tid = 'lpe_objects_panel_controller'
    
    def __init__(self):
        super(LPEObjectsPanelController, self).__init__()
        # LPEObjectsPanelModel is not a UIModelBase object
        self._real_model = LPEObjectsPanelModel(self.uid)
        
    def PostInit(self):
        self.view.dvc.AssociateModel(self._real_model)
        self.expand_dvc_all_items()
 
    def PreDelete(self):
        pass
      
    def create_item(self, obj, parent_obj=None):
        if obj.tid != 'track_controller' and \
                                        obj.tid != 'track_object_controller':
            raise Exception('Cannot insert {}.'.format(obj.tid))                                    
    
        item = self._get_real_model().ObjectToItem(obj)
        if obj.tid == 'track_controller':
            self._get_real_model().ItemAdded(dv.NullDataViewItem, item)
            self.expand_dvc_item(item)
        else:
            if parent_obj is None:
                raise Exception('Cannot insert a object whose parent is None.')
            parent_item = self._get_real_model().ObjectToItem(parent_obj)
            self._get_real_model().ItemAdded(parent_item, item)
            self.expand_dvc_item(parent_item)
            
    def remove_item(self, obj):  
        if obj.tid != 'track_controller' and \
                                        obj.tid != 'track_object_controller':            
            raise Exception('Cannot remove {}.'.format(obj.tid))   
        item = self._get_real_model().ObjectToItem(obj)
        if obj.tid == 'track_controller':
            self._get_real_model().ItemDeleted(dv.NullDataViewItem, item)
        else:
            parent_item = self._get_real_model().GetParent(item)
            self._get_real_model().ItemDeleted(parent_item, item)

    def expand_dvc_item(self, item):
        return self.view.dvc.Expand(item)

    def expand_dvc_all_items(self):
        self.view.expand_dvc_all_items()
        
    def _get_real_model(self):
        # LPETrackPanel needs the model
        return self._real_model

    def update_dvc(self):
        self.view.dvc.Refresh()
        
        
###############################################################################


class LPEObjectsPanelModel(dv.PyDataViewModel):

    def __init__(self, controller_uid):
        dv.PyDataViewModel.__init__(self)
        self._controller_uid = controller_uid  # To send commands to controller...
        
        
    def GetChildren(self, parent, children):  
        UIM = UIManager()
        # Root
        if not parent:
            lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
            logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
            tracks = UIM.list('track_controller', logplot_ctrl_uid)
            if not tracks:
                return 0
            for track in tracks:
                item = self.ObjectToItem(track)
                children.append(item)
            return len(children)
            
        # Child    
        obj = self.ItemToObject(parent)
        if isinstance(obj, TrackController):
            track_objects = UIM.list('track_object_controller', obj.uid) 
            for track_object in track_objects:
                children.append(self.ObjectToItem(track_object))
            return len(track_objects)
        return 0
    

    def IsContainer(self, item):
        #print '\nIsContainer'
        if not item:
        #    print 'not item - True'
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackController):
        #    print obj.uid, '- TrackController - True'
            return True
        #print obj.uid, '- not TrackController - False'
        return False         
    
    def GetParent(self, item):
        #print '\nGetParent:'
        if not item:
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)    
        #print obj.uid
        if isinstance(obj, TrackController):
            return dv.NullDataViewItem
        elif isinstance(obj, TrackObjectController):
            UIM = UIManager()
            track_uid = UIM._getparentuid(obj.uid)
            track_ctrl = UIM.get(track_uid)
            item = self.ObjectToItem(track_ctrl)
            return item
             
    def GetValue(self, item, col):
        obj = self.ItemToObject(item)    
        if isinstance(obj, TrackController):
            if col == 0:
                if obj.model.label:
                    return obj.model.label
                return 'Track ' + str(obj.model.pos + 1)
            return wx.EmptyString     
        elif isinstance(obj, TrackObjectController):
            if col == 0:
                return wx.EmptyString 
            elif col == 1:
                try:
                    if obj.model.obj_tid:
                        ret = ObjectManager.get_tid_friendly_name(obj.model.obj_tid)
                        if ret:
                            return ret
                        return wx.EmptyString
                    else:
                        return 'Select...'
                except AttributeError:
                    print '\nERRO! O objeto nao possui model: ' + str(obj.uid) + '\n'
                    return ''
            elif col == 2:    
                om_obj = obj.get_object()
                if om_obj:
                    return om_obj.name
                return 'Select...' 
        else:
            raise RuntimeError("unknown node type")
            

    def SetValue(self, value, item, col):
        obj = self.ItemToObject(item)    
        if isinstance(obj, TrackController):
            raise Exception()  
        #TODO: rever isso, pois esta horrivel    
        if isinstance(obj, TrackObjectController):
            UIM = UIManager()
            ctrl = UIM.get(self._controller_uid)
            if col == 1 or col == 2:
                print 'SetValue:', col, value
                pgcs = UIM.list('property_grid_controller', self._controller_uid)
                if pgcs:
                    pgc = pgcs[0]
                    ctrl.view.splitter.Unsplit(pgc.view)  
                    UIM.remove(pgc.uid)
            if col == 1:
                obj.model.obj_tid = value
            if col == 2:
                if isinstance(value, tuple):
                    print 'aqui' 
                    obj.model.obj_oid = value[1]
                    ctrl.view.dvc.Select(item)
        #            
        return True
            
            
    def GetAttr(self, item, col, attr):
        if col == 0:
            obj = self.ItemToObject(item)
            if isinstance(obj, TrackController):
                attr.SetColour('blue')
                return True
        return False
        

    def HasDefaultCompare(self):    
        return True
           
    def Compare(self, item1, item2, col, ascending):
        obj1 = self.ItemToObject(item1)
        obj2 = self.ItemToObject(item2)
        #print 'Compare:', obj1.uid, obj2.uid  
        if obj1.tid == 'track_controller' and obj2.tid == 'track_controller'\
                                or obj1.tid == 'track_object_controller' and \
                                obj2.tid == 'track_object_controller':
            if obj1.model.pos == obj2.model.pos:
                raise Exception('Two tracks cannot have same position.')
            if ascending: 
                if obj1.model.pos > obj2.model.pos:
                    return 1
                else:
                    return -1
            else:
                if obj1.model.pos > obj2.model.pos:
                    return -1
                else:
                    return 1                                
        #print 'Compare:', obj1, obj2        
        # TODO: Falta
        
            
    def ChangeValue(self, value, item, col):
        """ChangeValue(self, wxVariant variant, DataViewItem item, unsigned int col) -> bool"""
        print 'CurvesModel.ChangeValue: ', col, value
        return super(LPEObjectsPanelModel, self).ChangeValue(value, item, col)
        if item is None:
            print 'item is None'
            return False
        return False           


###############################################################################



class LPEObjectsPanel(UIViewBase, wx.Panel):
    tid = 'lpe_objects_panel'
    DEPTH_LINES_CHOICE = ['Full', 'Left', 'Right', 'Center', 'Left & Right', 'None']   
    
    
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        wx.Panel.__init__(self, self._get_lpeview_notebook(), -1, style=wx.SIMPLE_BORDER)       


    def PostInit(self):
        self.splitter = wx.SplitterWindow(self, -1)
        self.dvc = self.create_data_view_ctrl()

        self.splitter.Initialize(self.dvc)
        self.splitter.SetSashPosition(400)

        self.splitter.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self._OnSplitterDclick)
    
        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.splitter, 1, wx.EXPAND|wx.ALL, border=10)
       
        button_add_track = wx.Button(self, label="Add Object")
        self.Bind(wx.EVT_BUTTON, self.on_add_track_object, button_add_track)
        button_delete_track = wx.Button(self, label="Delete Object")
        self.Bind(wx.EVT_BUTTON, self.on_delete_track_object, 
                                              button_delete_track
        )
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT|wx.RIGHT, 5)
        
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)

        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        all_tracks = UIM.list('track_controller', logplot_ctrl_uid)
        
        for track in all_tracks:     
            print 'expanding:', track.uid
            item = model.ObjectToItem(track)
            print item
            self.dvc.Expand(item)
            print self.dvc.IsExpanded(item)
            #model.Resort()
            #print self.dvc.IsExpanded(item)
        """
        #self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_START_EDITING, self.OnItemStartEditing)        
        #self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_STARTED, self.OnItemEditingStart)
        #self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.OnItemEditingDone)
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnSelectionChanged)

        ###
        #sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        #sizer_grid_panel.Add(self.splitter, 1, wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(self.Sizer)
        self._get_lpeview_notebook().AddPage(self, "Objects", True)


        #self.dvc.Bind(wx.EVT_IDLE, self._dvc_idle)
        
    #def _dvc_idle(self, event):
    #    print 'DVC IDLE'

    def _get_lpeview_notebook(self):
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid) 
        lpe_ctrl = UIM.get(parent_controller_uid)
        return lpe_ctrl.view.note


    def create_data_view_ctrl(self):
        dvc = dv.DataViewCtrl(self.splitter, style=dv.DV_ROW_LINES|
                                    dv.DV_VERT_RULES|dv.DV_MULTIPLE
        )
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        # Track
        dv_col = dvc.AppendTextColumn("Track",  0, width=85)      
        dv_col.SetMinWidth(55)    
        # Object Type 
        dvcr_object_tid = ObjectTidRenderer()
        dv_col = dv.DataViewColumn("Object Type", dvcr_object_tid, 1, width=85)          
        dv_col.SetMinWidth(85)
        dvc.AppendColumn(dv_col)
        # Object Name 
        dvcr_curve_name = ObjectNameRenderer(model)
        dv_col = dv.DataViewColumn("Object Name", dvcr_curve_name, 2, width=130)      
        dv_col.SetMinWidth(85)
        dvc.AppendColumn(dv_col)
        # Adjusting
        for idx, dv_col in enumerate(dvc.Columns):
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER) 
        return dvc


    def expand_dvc_all_items(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        logplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        all_tracks = UIM.list('track_controller', logplot_ctrl_uid)
        
        for track in all_tracks:     
            #print 'expanding:', track.uid
            item = model.ObjectToItem(track)
            #print item
            self.dvc.Expand(item)
           #print self.dvc.IsExpanded(item)
            #model.Resort()
            #print self.dvc.IsExpanded(item)


    def OnSelectionChanged(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        items = self.dvc.GetSelections()
        objs = [model.ItemToObject(item) for item in items]
        toc_objs = [obj for obj in objs if isinstance(obj, TrackObjectController)]
        pg_shown = False
        if toc_objs:
            toc_obj = toc_objs[-1]
            if toc_obj.is_valid():
                pgcs = UIM.list('property_grid_controller', self._controller_uid)
                if not pgcs:
                    #print '\nself._controller_uid:', self._controller_uid
                    #print
                    pgc = UIM.create('property_grid_controller', 
                                           self._controller_uid
                    )
                else:
                    pgc = pgcs[0]   
                pgc.set_object_uid(toc_obj.uid)    
                if not self.splitter.IsSplit():
                    self.splitter.SplitVertically(self.dvc, pgc.view)
                pg_shown = True
        if not pg_shown and self.splitter.IsSplit():
            pgc = UIM.list('property_grid_controller', self._controller_uid)[0]
            self.splitter.Unsplit(pgc.view)       
            

    def on_add_track_object(self, event):
        tracks, track_objs = self._get_objects_selected() 
        UIM = UIManager()
        for track in tracks:
            UIM.create('track_object_controller', track.uid)
        for track_obj in track_objs:
            UIM = UIManager()
            track_uid = UIM._getparentuid(track_obj.uid)
            track =  UIM.get(track_uid)
            UIM.create('track_object_controller', track.uid)


    def on_delete_track_object(self, event):
        _, track_objs = self._get_objects_selected()
        UIM = UIManager()
        for track_obj in track_objs:
            UIM.remove(track_obj.uid)
           
            
    def _OnSplitterDclick(self, event):
        print '_OnSplitterDclick:', event


    def _get_objects_selected(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        items = self.dvc.GetSelections()
        objects_selected = [model.ItemToObject(item) for item in items]
        tracks = []
        track_objs = []
        for obj in objects_selected:
            if isinstance(obj, TrackController):
                tracks.append(obj)
            if isinstance(obj, TrackObjectController):
                track_objs.append(obj)    
        return tracks, track_objs           
        
             

        

###############################################################################        
###############################################################################


    
class TextChoiceRenderer(dv.DataViewCustomRenderer):
 
    def __init__(self, model=None):
        dv.DataViewCustomRenderer.__init__(self, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.model = model
        self._value = None    
  
    def GetValue(self):
        return self._value 
        
    def SetValue(self, value):
        self._value = value
        return True
        
    def GetSize(self):
        return wx.Size(100, 20)
        
    def Render(self, rect, dc, state):
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True

    def StartEditing(self, item, rect):
        self.item = item 
        super(TextChoiceRenderer, self).StartEditing(item, rect)
        return True
         
    def CreateEditorCtrl(self, parent, rect, value):  
        raise NotImplemented('CreateEditorCtrl need to be implemented by child Class.')
        
    def GetValueFromEditorCtrl(self, editor):       
        raise NotImplemented('GetValueFromEditorCtrl need to be implemented by child Class.')



class ObjectTidRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):    
        OM = ObjectManager(self)
        acceptable_tids = LogPlotController.get_acceptable_tids()
        tids = list(set([obj._TID_FRIENDLY_NAME for obj in OM.list() \
                         if obj.tid in acceptable_tids
                        ]
                       )
        )
        #print 'tids:', tids
        _editor = wx.Choice(parent, 
                            wx.ID_ANY,
                            rect.GetTopLeft(),
                            wx.Size(rect.GetWidth(), -1),
                            choices=tids
        )
        _editor.SetRect(rect)
        return _editor

    def GetValueFromEditorCtrl(self, editor):
        selected_index = editor.GetSelection()
        #print 'GetValueFromEditorCtrl:', selected_index
        if selected_index == -1:
            return True, wx.EmptyString
        self._value = editor.GetString(selected_index)
        self._value = ObjectManager.get_tid(self._value)
        return True, self._value



class ObjectNameRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):    
        OM = ObjectManager(self)
        obj = self.model.ItemToObject(self.item)
        self._options = OrderedDict()
        #print 'ObjectNameRenderer:', obj.model.obj_tid
        if obj.model.obj_tid in LogPlotController.get_acceptable_tids():
            for om_obj in OM.list(obj.model.obj_tid):
                #print '   Adding:', om_obj.uid, om_obj.name  
                self._options[om_obj.uid] = om_obj.name    
        _editor = wx.Choice(parent, 
                            wx.ID_ANY,
                            rect.GetTopLeft(),
                            wx.Size(rect.GetWidth(), -1),
                            choices=self._options.values()
        )
        _editor.SetRect(rect)
        return _editor

    def GetValueFromEditorCtrl(self, editor):
        if editor.GetSelection() == -1:
            return True, -1
        self._value = self._options.keys()[editor.GetSelection()]
        return True, self._value
    
    
    
    
###############################################################################        
###############################################################################


class PropertyMixin(object):
    
    def _get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        return controller.model[self._model_key]

    def _set_value(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = value   



class EnumProperty(pg.EnumProperty, PropertyMixin):    
 
    def __init__(self, controller_uid, model_key, 
                 label = wx.propgrid.PG_LABEL,
                 name = wx.propgrid.PG_LABEL,
                 labels=[], values=[]):
        super(EnumProperty, self).__init__(label, name, labels, values)
        self._controller_uid = controller_uid
        self._model_key = model_key
        self._labels = labels
        self._values = values

    def IntToValue(self, variant, int_value, flag): 
        raise NotImplemented('IntToValue need to be implemented by child Class.')
           
    def ValueToString(self, value, flag):
        raise NotImplemented('ValueToString need to be implemented by child Class.')
        
    def GetIndexForValue(self, value):
        raise NotImplemented('GetIndexForValue need to be implemented by child Class.')
    
     
# Set and Get integer indexes to the model and display theirs labels.    
class IndexesEnumProperty(EnumProperty):  
    
    def IntToValue(self, variant, int_value, flag):
        self._set_value(int_value)
        return True
        
    def ValueToString(self, value, flag):
        idx = self._get_value()
        return self._labels[idx]
        
    def GetIndexForValue(self, value):
        return self._get_value()


# Set and Get label values to the model.    
class LabelsEnumProperty(EnumProperty):  
    
    def IntToValue(self, variant, int_value, flag):
        val = self._labels[int_value]
        self._set_value(val)
        return True
        
    def ValueToString(self, value, flag):
        return self._get_value()
        #return self._labels[idx]
        
    def GetIndexForValue(self, value):
        val = self._get_value()
        return self._labels.index(val)
    


class IntProperty(pg.IntProperty):    

    def __init__(self, controller_uid, model_key, 
                 label = wx.propgrid.PG_LABEL,
                 name = wx.propgrid.PG_LABEL):
        
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(IntProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller.model[self._model_key]
        return str(value)

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = text
        return True    
    
    
    
class FloatProperty(pg.FloatProperty):    

    def __init__(self, controller_uid, model_key, 
                 label = wx.propgrid.PG_LABEL,
                 name = wx.propgrid.PG_LABEL):

        self._controller_uid = controller_uid
        self._model_key = model_key
        super(FloatProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller.model[self._model_key]
        return str(value)

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = text
        return True    



class StringProperty(pg.StringProperty):
    
    def __init__(self, controller_uid, model_key, 
                 label = wx.propgrid.PG_LABEL,
                 name = wx.propgrid.PG_LABEL):
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(StringProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller.model[self._model_key]
        return value

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller.model[self._model_key] = text
        return True

    







class ColorSelectorComboBox(OwnerDrawnComboBox):
    colors = OrderedDict()
    colors['Black'] = None
    colors['Maroon'] = None
    colors['Green'] = wx.Colour(0, 100, 0) # Dark Green
    colors['Olive'] = wx.Colour(128, 128, 0)
    colors['Navy'] = None
    colors['Purple'] = None
    colors['Teal'] = wx.Colour(0, 128, 128)
    colors['Gray'] = None
    colors['Silver'] = wx.Colour(192, 192, 192)
    colors['Red'] = None
    colors['Lime'] = wx.Colour(0, 255, 0) # Green
    colors['Yellow'] = None
    colors['Blue'] = None
    colors['Fuchsia'] = wx.Colour(255, 0, 255)
    colors['Aqua'] = wx.Colour(0, 255, 255)
    colors['White'] = None
    colors['SkyBlue'] = wx.Colour(135, 206, 235)
    colors['LightGray'] = wx.Colour(211, 211, 211)
    colors['DarkGray'] = wx.Colour(169, 169, 169)
    colors['SlateGray'] = wx.Colour(112, 128, 144)
    colors['DimGray'] = wx.Colour(105, 105, 105)
    colors['BlueViolet'] = wx.Colour(138, 43, 226)
    colors['DarkViolet'] = wx.Colour(148, 0, 211)
    colors['Magenta'] = None
    colors['DeepPink'] = wx.Colour(148, 0, 211)
    colors['Brown'] = None
    colors['Crimson'] = wx.Colour(220, 20, 60)
    colors['Firebrick'] = None
    colors['DarkRed'] = wx.Colour(139, 0, 0)
    colors['DarkSlateGray'] = wx.Colour(47, 79, 79)
    colors['DarkSlateBlue'] = wx.Colour(72, 61, 139)
    colors['Wheat'] = None
    colors['BurlyWood'] = wx.Colour(222, 184, 135)
    colors['Tan'] = None
    colors['Gold'] = None
    colors['Orange'] = None
    colors['DarkOrange'] = wx.Colour(255, 140, 0)
    colors['Coral'] = None
    colors['DarkKhaki'] = wx.Colour(189, 183, 107)
    colors['GoldenRod'] = None
    colors['DarkGoldenrod'] = wx.Colour(184, 134, 11)
    colors['Chocolate'] = wx.Colour(210, 105, 30)
    colors['Sienna'] = None
    colors['SaddleBrown'] = wx.Colour(139, 69, 19)
    colors['GreenYellow'] = wx.Colour(173, 255, 47)
    colors['Chartreuse'] = wx.Colour(127, 255, 0)
    colors['SpringGreen'] = wx.Colour(0, 255, 127)
    colors['MediumSpringGreen'] = wx.Colour(0, 250, 154)
    colors['MediumAquamarine'] = wx.Colour(102, 205, 170)
    colors['LimeGreen'] = wx.Colour(50, 205, 50)
    colors['LightSeaGreen'] = wx.Colour(32, 178, 170)
    colors['MediumSeaGreen'] = wx.Colour(60, 179, 113)
    colors['DarkSeaGreen'] = wx.Colour(143, 188, 143)
    colors['SeaGreen'] = wx.Colour(46, 139, 87)
    colors['ForestGreen'] = wx.Colour(34, 139, 34)
    colors['DarkOliveGreen'] = wx.Colour(85, 107, 47)
    colors['DarkGreen'] = wx.Colour(1, 50, 32)
    colors['LightCyan'] = wx.Colour(224, 255, 255)
    colors['Thistle'] = None
    colors['PowderBlue'] = wx.Colour(176, 224, 230)
    colors['LightSteelBlue'] = wx.Colour(176, 196, 222)
    colors['LightSkyBlue'] = wx.Colour(135, 206, 250)
    colors['MediumTurquoise'] = wx.Colour(72, 209, 204)
    colors['Turquoise'] = None
    colors['DarkTurquoise'] = wx.Colour(0, 206, 209)
    colors['DeepSkyBlue'] = wx.Colour(0, 191, 255)
    colors['DodgerBlue'] = wx.Colour(30, 144, 255)
    colors['CornflowerBlue'] = wx.Colour(100, 149, 237)
    colors['CadetBlue'] = wx.Colour(95, 158, 160)
    colors['DarkCyan'] = wx.Colour(0, 139, 139)
    colors['SteelBlue'] = wx.Colour(70, 130, 180)
    colors['RoyalBlue'] = wx.Colour(65, 105, 225)
    colors['SlateBlue'] = wx.Colour(106, 90, 205)
    colors['DarkBlue'] = wx.Colour(0, 0, 139)
    colors['MediumBlue'] = wx.Colour(0, 0, 205)
    colors['SandyBrown'] = wx.Colour(244, 164, 96)
    colors['DarkSalmon'] = wx.Colour(233, 150, 122)
    colors['Salmon'] = None
    colors['Tomato'] = wx.Colour(255, 99, 71) 
    colors['Violet'] = wx.Colour(238, 130, 238)
    colors['HotPink'] = wx.Colour(255, 105, 180)
    colors['RosyBrown'] = wx.Colour(188, 143, 143)
    colors['MediumVioletRed'] = wx.Colour(199, 21, 133)
    colors['DarkMagenta'] = wx.Colour(139, 0, 139)
    colors['DarkOrchid'] = wx.Colour(153, 50, 204)
    colors['Indigo'] = wx.Colour(75, 0, 130)
    colors['MidnightBlue'] = wx.Colour(25, 25, 112)
    colors['MediumSlateBlue'] = wx.Colour(123, 104, 238)
    colors['MediumPurple'] = wx.Colour(147, 112, 219)
    colors['MediumOrchid'] = wx.Colour(186, 85, 211)        
  
    
    def __init__(self, *args, **kwargs): 
        print 'ColorSelectorComboBox.__init__'
        kwargs['choices'] = self.colors.keys()
        OwnerDrawnComboBox.__init__(self, *args, **kwargs)
        print 'ColorSelectorComboBox.__init__ ENDED'
        #super(ColorSelectorComboBox, self).SetSelection().#SetSelection()
        
    """    
    def OnDrawItem(self, dc, rect, item, flags):
        print 'OnDrawItem:' , item, flags
        if wx.adv.ODCB_PAINTING_CONTROL == flags:
            print 'wx.adv.ODCB_PAINTING_CONTROL'
        elif wx.adv.ODCB_PAINTING_SELECTED == flags:
            print 'ODCB_PAINTING_SELECTED'
        if item == wx.NOT_FOUND:
            # painting the control, but there is no valid item selected yet
            return 
        font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'Segoe UI')             
        dc.SetFont(font)
        
        if flags == 3:
            margin = 3    
        else:
            margin = 1
        r = wx.Rect(*rect)  # make a copy
        r.Deflate(margin, margin)
        tam = self.OnMeasureItem(item)-2
        dc.SetPen(wx.Pen("grey", style=wx.TRANSPARENT))
        color_name = self.GetString(item)     
        color = self.colors.get(color_name)
        if not color:
            color = wx.Colour(color_name)
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(r.x, r.y, tam, tam)
        dc.DrawText(self.GetString(item), r.x + tam + 2, r.y)            
    """   
        
    def OnMeasureItem(self, item):
        #print 'OnMeasureItem'
        return 15


    @staticmethod
    def get_colors():
        return ColorSelectorComboBox.colors.keys()

    



class ColorPropertyEditor(pg.PGEditor):

    def __init__(self):
        print 'ColorPropertyEditor.__init__'
        pg.PGEditor.__init__(self)
        print 'ColorPropertyEditor.__init__ ENDED'
        
        
    def CreateControls(self, propgrid, property, pos, size):
        print '\nCreateControls'
        csc = ColorSelectorComboBox(propgrid.GetPanel(), pos=pos, size=size)
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        csc.SetSelection(idx)
        window_list = pg.PGWindowList(csc)
        return window_list


    def GetName(self):
        return 'ColorPropertyEditor'
    
    
    def UpdateControl(self, property, ctrl):
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        print 'UpdateControl:', idx
        ctrl.SetSelection(idx)


    def DrawValue(self, dc, rect, property, text):        
        print 'DrawValue:', text
        #dc.SetPen( wxPen(propertyGrid->GetCellTextColour(), 1, wxSOLID) )
        #pen = dc.GetPen()
        #print pen.GetColour(), pen.GetStyle(), wx.PENSTYLE_SOLID
        #dc.SetPen(wx.Pen(wx.Colour(0, 0, 255, 255), 1, wx.SOLID))
        cell_renderer = property.GetCellRenderer(1)
        cell_renderer.DrawText(dc, rect, 0, text) # property.get_value())#rect.x+15, rect.y)
        #dc.DrawText(property.get_value(), rect.x+15, rect.y)
    #    if not property.IsValueUnspecified():
    #        dc.DrawText(property.get_value(), rect.x+5, rect.y)


    def OnEvent(self, propgrid, property, ctrl, event):
        if isinstance(event, wx.CommandEvent):
            if event.GetEventType() == wx.EVT_COMBOBOX:
                print 'COMBAO DA MASSA\n\n\n'
            if event.GetString():
                print 'VALUE:', event.GetString(), '\n'
                return True
        return False


    def GetValueFromControl(self, variant, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        print '\nGetValueFromControl:', ctrl.GetValue()
        if property.UsesAutoUnspecified() and not ctrl.GetValue():
            return True
        ret_val = property.StringToValue(ctrl.GetValue(), pg.PG_EDITABLE_VALUE)
        return ret_val


    def SetValueToUnspecified(self, property, ctrl):
        print '\nSetValueToUnspecified'
        ctrl.SetSelection(0) #Remove(0, len(ctrl.GetValue()))


    """
    def SetControlIntValue(self, property, ctrl, value):
        print 'SetControlIntValue:', value

    def SetControlStringValue(self, property, ctrl, text):
        print 'SetControlStringValue'
        ctrl.SetValue(text)
    """     

    """
    def SetControlAppearance(self, pg, property, ctrl, cell, old_cell, unspecified):
        print 'SetControlAppearance' 
        '''
        cb = ctrl
        tc = ctrl.GetTextCtrl()
        
        changeText = False
        
        if cell.HasText() and not pg.IsEditorFosuced():
            print '   ENTROU A'
            tcText = cell.GetText()
            changeText = True
        elif old_cell.HasText():
            print '   ENTROU B'
            tcText = property.get_value()
            changeText = True
        else:
            print '   NEM A NEM B'
        if changeText:
            if tc:
                print '   ENTROU C'
                pg.SetupTextCtrlValue(tcText)
                tc.SetValue(tcText)
            else:
                print '   ENTROU D'
                cb.SetText(tcText)
        else:
            print '   NEM C NEM D'
        '''    
        '''    
        # Do not make the mistake of calling GetClassDefaultAttributes()
        # here. It is static, while GetDefaultAttributes() is virtual
        # and the correct one to use.
        vattrs = ctrl.GetDefaultAttributes()
    
        #Foreground colour
        fgCol = cell.GetFgCol()
        if fgCol.IsOk():
            ctrl.SetForegroundColour(fgCol)
            print 'fgCol:', fgCol
        
        elif old_cell.GetFgCol().IsOk():
            ctrl.SetForegroundColour(vattrs.colFg)
            print 'vattrs.colFg:', vattrs.colFg
    
        # Background colour
        bgCol = cell.GetBgCol()
        if bgCol.IsOk():
            ctrl.SetBackgroundColour(bgCol)
        elif old_cell.GetBgCol().IsOk():
            ctrl.SetBackgroundColour(vattrs.colBg)
    
        # Font
        font = cell.GetFont()
        if font.IsOk():
            ctrl.SetFont(font)
        elif old_cell.GetFont().IsOk():
            ctrl.SetFont(vattrs.font)
        '''    
        # Also call the old SetValueToUnspecified()
        #if unspecified
        #    SetValueToUnspecified(property, ctrl);

                
        #print 'cell.GetText():', cell.GetText()
        #print 'old_cell.GetText():', old_cell.GetText()
        
        #print tc#, tc.GetText()
        super(ColorPropertyEditor, self).SetControlAppearance(pg, property, ctrl, cell, old_cell, unspecified)
    """    

    def InsertItem(self, ctrl, label, index):
        print 'InsertItem:', label, index
        
        
    def CanContainCustomImage(self):
        print 'CanContainCustomImage'
        return True
    
    def OnFocus(self, property, ctrl):
        #print 'OnFocus:' #, property, ctrl
        #ctrl.SetSelection(-1)#,-1)
        ctrl.SetFocus()



class ColorProperty(pg.PGProperty):
    # All arguments of this ctor should have a default value -
    # use wx.propgrid.PG_LABEL for label and name
    def __init__(self, controller_uid, model_key, 
             label = wx.propgrid.PG_LABEL,
             name = wx.propgrid.PG_LABEL):
        print 'ColorProperty.__init__'
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(pg.PGProperty, self).__init__(label, name)
        self.SetValue(self.get_value())
        print 'ColorProperty.__init__ ENDED'
        
        
    #def OnSetValue(self):
    #    print 'ColorProperty.OnSetValue'
        
    def DoGetEditorClass(self):
        #print 'ColorProperty.DoGetEditorClass'
        return pg.PropertyGridInterface.GetEditorByName('ColorPropertyEditor')
        #_CPEditor #ColorPropertyEditor #wx.PGEditor_TextCtrl

    def ValueToString(self, value, flags):
        print '\nColorProperty.ValueToString'
        value = self.get_value()
        return value

    def StringToValue(self, text, flags):
        print 'ColorProperty.StringToValue:', text
        value = self.set_value(text) 
        self.SetValue(value)
        return value      
    
    def get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        print 'ColorProperty.get_value:', controller.model[self._model_key]
        return controller.model[self._model_key]


    def set_value(self, new_value):
        print 'ColorProperty.set_value', new_value
        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            controller.model[self._model_key] = new_value  
            return True
        except:
            return False


    def GetDisplayedString(self):
        print 'GetDisplayedString'
        return self.get_value()

    def GetChoiceSelection(self):
        idx = ColorSelectorComboBox.get_colors().index(self.get_value())
        print 'GetChoiceSelection:', idx
        return idx

    def IsTextEditable(self):
        ret = super(pg.PGProperty, self).IsTextEditable()
        print 'IsTextEditable'
        return ret

    def IsValueUnspecified(self):
        print '\n\nColorProperty.IsValueUnspecified\n\n'
        return False
  
    def SetLabel(self, label):
        print 'SetLabel:', label
        super(pg.PGProperty, self).SetLabel(label)
    
    
    
#_CPEditor = pg.PropertyGrid.RegisterEditorClass(ColorPropertyEditor())  
#_CPEditor = pg.PropertyGrid.RegisterEditorClass(ColorPropertyEditor())#, wx.EmptyString, False)  
        
        
    