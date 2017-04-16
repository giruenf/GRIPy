# -*- coding: utf-8 -*-
import wx
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase  
from UI.uimanager import UIViewBase 
from App import log
#
###
import wx.dataview as dv
#from wx.combo import OwnerDrawnComboBox
import wx.lib.colourdb
from collections import OrderedDict
from OM.Manager import ObjectManager
import Parms
import copy
#from logplotformat import LogPlotFormat, TrackFormat, CurveFormat
import cPickle
###
from App.utils import parse_string_to_uid    
from plotter_track import TrackController    
from plotter_object import TrackObjectController     
    
import wx.propgrid as wxpg

   
    
class LogPlotEditorController(UIControllerBase):
    tid = 'log_plot_editor_controller'
     
    def __init__(self):
        super(LogPlotEditorController, self).__init__()
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created Controller object from class: {}.'.format(class_full_name))



class LogPlotEditor(UIViewBase, wx.Frame):
    tid = 'log_plot_editor'

    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        wx.Frame.__init__(self, None, -1, title='LogPlotEditor',
                                          size=(860, 600),
                                          style=wx.DEFAULT_FRAME_STYLE & 
                                          (~wx.RESIZE_BORDER) &(~wx.MAXIMIZE_BOX)
        )   
        UIM = UIManager()
        parent_controller_uid = UIM._getparentuid(self._controller_uid)

        main_sizer = wx.BoxSizer(wx.VERTICAL)  
        self.base_panel = wx.Panel(self)
        note = wx.Notebook(self.base_panel)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(note, 1, wx.ALL|wx.EXPAND, border=5)        
        self.base_panel.SetSizer(bsizer)
                
        tracks_base_panel = wx.Panel(note, style=wx.SIMPLE_BORDER)
        sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        self.tracks_model = TracksModel(parent_controller_uid)
        tp = TracksPanel(tracks_base_panel, self.tracks_model)
        sizer_grid_panel.Add(tp, 1, wx.EXPAND|wx.ALL, border=10)
        tracks_base_panel.SetSizer(sizer_grid_panel)
        note.AddPage(tracks_base_panel, "Tracks", True)
        
        curves_base_panel = wx.Panel(note, style=wx.SIMPLE_BORDER)
        sizer_curves_panel = wx.BoxSizer(wx.VERTICAL)
        self.curves_model = CurvesModel(parent_controller_uid)
        cp = CurvesPanel(curves_base_panel, self.curves_model)
        sizer_curves_panel.Add(cp, 1, wx.EXPAND|wx.ALL, border=10)
        curves_base_panel.SetSizer(sizer_curves_panel)
        note.AddPage(curves_base_panel, "Objects", True)
     
     
        main_sizer.Add(self.base_panel, 1, wx.EXPAND)
        
        bottom_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_close = wx.Button(bottom_panel, -1, "Close")
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM, border=10)
        btn_close.Bind(wx.EVT_BUTTON, self._OnButtonClose)
        bottom_panel.SetSizer(sizer)        
        main_sizer.Add(bottom_panel, 0,  wx.EXPAND)
        self.SetSizer(main_sizer)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)    
        log.debug('Successfully created View object from class: {}.'.format(class_full_name))
        
        
    def _OnButtonClose(self, evt):
        self.Close()



###############################################################################


class VarNodeDropData(wx.CustomDataObject):
    NAME = "VarNode"
    PICKLE_PROTOCOL = 2
	   
    def __init__(self):
        wx.CustomDataObject.__init__(self, VarNodeDropData.GetFormat())
        
    def SetItem(self, item):
        oid = item.GetID()
        data = cPickle.dumps(oid, VarNodeDropData.PICKLE_PROTOCOL)       
        self.SetData(data)
        
    def GetItem(self):
        oid = cPickle.loads(self.GetData())
        return dv.DataViewItem(oid)
        
    @staticmethod  
    def GetFormat():
        return wx.DataFormat(VarNodeDropData.NAME)
        

###############################################################################


class TracksPanel(wx.Panel):
        
    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1)
        self.model = model
        self.dvc = dv.DataViewCtrl(self, style=wx.BORDER_THEME | dv.DV_VERT_RULES | dv.DV_MULTIPLE| dv.DV_ROW_LINES) 
        self.dvc.AssociateModel(self.model)

        # Track
        dv_col = self.dvc.AppendTextColumn("Track", 0, width=45, align=wx.ALIGN_CENTER)
        dv_col.SetMinWidth(45)
        # Track Name
        dv_col = self.dvc.AppendTextColumn("Track Title", 1, width=80, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(80)
        # Width
        dv_col = self.dvc.AppendTextColumn("Width", 2, width=50, mode=dv.DATAVIEW_CELL_EDITABLE)      
        dv_col.SetMinWidth(60)
        # Visible (Track)
        dv_col = self.dvc.AppendToggleColumn("Visible",  3, width=50,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        # Plot Grid
        self.dvc.AppendToggleColumn("Plot Grid", 4, width=60,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        # Depth Lines
        dvcr = dv.DataViewChoiceRenderer(['All', 'Left', 'Right', 'Center', 'Left & Right', 'None'],
                                         mode=dv.DATAVIEW_CELL_EDITABLE
        )
        dvcol = dv.DataViewColumn("Depth Lines", dvcr, 5, width=85)
        self.dvc.AppendColumn(dvcol)
        # Scale Lines
        dv_col = self.dvc.AppendTextColumn("Scale Lines",   6, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70)   
        # Scale (Track)
        dvcr = dv.DataViewChoiceRenderer(['Linear', 'Logarithmic'], mode=dv.DATAVIEW_CELL_EDITABLE)
        dvcol = dv.DataViewColumn("Scale", dvcr, 7, width=80)
        dv_col.SetMinWidth(75)    
        self.dvc.AppendColumn(dvcol)
        # Decimation
        dv_col = self.dvc.AppendTextColumn("Log Decimation", 8, width=100, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(85)        
        # Left Scale
        dv_col = self.dvc.AppendTextColumn("Log Left Scale", 9, width=85, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(80)   
        # Minor Lines  
        self.dvc.AppendToggleColumn("Log Minor Lines", 10, width=100, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(90) 

        for dv_col in self.dvc.Columns:
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER)         
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)
        button_add_track = wx.Button(self, label="Add track")
        self.Bind(wx.EVT_BUTTON, self.OnInsertTrack, button_add_track)
        button_delete_track = wx.Button(self, label="Delete track(s)")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSelectedTracks, button_delete_track)
        button_select_all = wx.Button(self, label="Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, button_select_all)
        button_select_none = wx.Button(self, label="Select None")
        self.Bind(wx.EVT_BUTTON, self.OnSelectNone, button_select_none)
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_select_all, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_select_none, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)
        
        self.dvc.EnableDragSource(VarNodeDropData.GetFormat())
        self.dvc.EnableDropTarget(VarNodeDropData.GetFormat())
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_BEGIN_DRAG, self.OnItemBeginDrag)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_DROP_POSSIBLE, self.OnItemDropPossible)
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnSelectionChanged)

        
   # def get_dataview_ctrl(self):
   #     return self.dvc
      
    def OnItemBeginDrag(self, evt):
        item = evt.GetItem()
        if not item.IsOk():
            evt.Veto()
            return
        self.node = VarNodeDropData()
        self.node.SetItem(item)
        evt.SetDataObject(self.node)
        evt.SetDragFlags(wx.Drag_DefaultMove)
        
        
    def OnItemDropPossible(self, event):
        new_pos_item = event.GetItem()
        old_pos_item = self.node.GetItem()
        if new_pos_item == old_pos_item:
            return False   
        self.dvc.UnselectAll() # Change Selection    
        if new_pos_item.IsOk() and \
                            event.GetDataFormat() == VarNodeDropData.GetFormat():
            self.dvc.Select(new_pos_item)    
            new_pos_track = self.model.ItemToObject(new_pos_item)
            old_pos_track = self.model.ItemToObject(old_pos_item)
            new_pos_track.model.pos = old_pos_track.model.pos
            self.model.ChangedItem(new_pos_item) 
            self.model.ChangedItem(old_pos_item)
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
        self._DoSelectionChanged()

    def _DoSelectionChanged(self):        
        items = self.dvc.GetSelections()
        UIM = UIManager()
        tracks = UIM.list('track_controller', self.model.logplot_ctrl_uid)
        tracks_selected = [self.model.ItemToObject(item) for item in items]
        for track in tracks:
            track.model.selected = track in tracks_selected
            
    def OnInsertTrack(self, event):
        self.model.InsertTracks()
          
    def OnDeleteSelectedTracks(self, event):
        self.model.DeleteTracks()


###############################################################################


class TracksModel(dv.PyDataViewModel):
    TRACKS_MODEL_MAPPING = {
        0: 'pos',
        1: 'label',
        2: 'width', 
        3: 'show_track',
        4: 'plotgrid',
        5: 'depth_lines',
        6: 'scale_lines',
        7: 'x_scale', 
        8: 'decades',
        9: 'leftscale',
        10: 'minorgrid'
    }    

    def __init__(self, logplot_ctrl_uid):
        dv.PyDataViewModel.__init__(self)
        self.logplot_ctrl_uid = logplot_ctrl_uid
        #self.objmapper.UseWeakRefs(True)

    def IsContainer(self, item):
        if not item:
            return True
        return False  

    def GetParent(self, item):
        return dv.NullDataViewItem
        
    def GetChildren(self, parent, children):     
        UIM = UIManager()
        tracks = UIM.list('track_controller', self.logplot_ctrl_uid)
        for track in tracks:
            children.append(self.ObjectToItem(track)) 
        return len(tracks)

    def GetValue(self, item, col):
        track = self.ItemToObject(item)
        if col == 0:
            return track.model.pos+1
        elif col == 3:
            return True
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
        else:       
            track.model[self.TRACKS_MODEL_MAPPING.get(col)] = value
        return True

    def ChangedItem(self, item):
        print '\nChangedItem'
        self.ItemChanged(item)

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
            raise Exception('Two tracks cannot have same position.')
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
   
    def InsertTracks(self):
        UIM = UIManager()
        log_plot_ctrl = UIM.get(self.logplot_ctrl_uid)
        new_tracks_uid = log_plot_ctrl.insert_track()
        for uid in new_tracks_uid:
            new_track = UIM.get(uid)
            item = self.ObjectToItem(new_track)
            self.ItemAdded(dv.NullDataViewItem, item)
        return True
               
    def DeleteTracks(self):
        UIM = UIManager()
        log_plot_ctrl = UIM.get(self.logplot_ctrl_uid)
        selected_tracks = log_plot_ctrl.get_tracks_selected()
        items_selected = [self.ObjectToItem(track) for track in selected_tracks]
        all_tracks = UIM.list('track_controller', self.logplot_ctrl_uid)
        not_selected_tracks = [track for track in all_tracks if track not in selected_tracks]
        items_not_selected = [self.ObjectToItem(track) for track in not_selected_tracks]
        log_plot_ctrl.remove_selected_tracks()
        for item in items_selected:
            self.ItemDeleted(dv.NullDataViewItem, item)  
        for item in items_not_selected:
            self.ItemChanged(item)  
        
        
        
###############################################################################


            
class CurvesPanel(wx.Panel):
    
    DEPTH_LINES_CHOICE = ['Full', 'Left', 'Right', 'Center', 'Left & Right', 'None']    
    
    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1)
        
        self.model = model
        self.dvc = dv.DataViewCtrl(self, style=dv.DV_ROW_LINES|dv.DV_VERT_RULES|dv.DV_MULTIPLE)
        self.dvc.AssociateModel(self.model)
       
        # Track
        dv_col = self.dvc.AppendTextColumn("Track",  0, width=85)      
        dv_col.SetMinWidth(55)    

        # Object Type 
        dvcr_curve_type = dv.DataViewChoiceRenderer(['Log', 'Seismic'],  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col = dv.DataViewColumn("Object Type", dvcr_curve_type, 1, width=85)#, flags=dv.DATAVIEW_COL_REORDERABLE) , mode=dv.DATAVIEW_CELL_EDITABLE)          
        dv_col.SetMinWidth(85)
        self.dvc.AppendColumn(dv_col)
        
        # Object Name 
        #dvcr_curve_name = dv.DataViewChoiceRenderer([],  mode=dv.DATAVIEW_CELL_EDITABLE)
        dvcr_curve_name = LogRenderer(self.model)
        dv_col = dv.DataViewColumn("Object Name", dvcr_curve_name, 2, width=130)#, flags=dv.DATAVIEW_COL_REORDERABLE)           
        dv_col.SetMinWidth(85)
        self.dvc.AppendColumn(dv_col)
        
        # Left Scale        
        dv_col = self.dvc.AppendTextColumn("Left Scale",   3, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70) 
        
        # Right Scale
        dv_col = self.dvc.AppendTextColumn("Right Scale",   4, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70)
        
        # Visible (Curve)        
        dv_col = self.dvc.AppendToggleColumn("Visible",   5, width=50,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        
        # Back up
        dv_col = self.dvc.AppendTextColumn("Back up",   6, width=60,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(60)
        
        # Scale (Curve)
        #print CurveFormat.SCALE_MAPPING.values()
        dvcr = dv.DataViewChoiceRenderer(['Linear', 'Logarithmic'], mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col = dv.DataViewColumn("Scale", dvcr,7, width=75)
        dv_col.SetMinWidth(75)    
        self.dvc.AppendColumn(dv_col)
           
        
        # Line Color
        dv_col = self.dvc.AppendTextColumn("Color", 8, width=75,  mode=dv.DATAVIEW_CELL_EDITABLE)
        #dvcr = dv.DataViewChoiceRenderer([], mode=dv.DATAVIEW_CELL_EDITABLE)
        #dv_col = dv.DataViewColumn("Color", dvcr, 7, width=75)
        dv_col.SetMinWidth(75)    
        #self.dvc.AppendColumn(dv_col)

        
        
        # Width         
        dv_col = self.dvc.AppendTextColumn("Width",   9, width=45,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(45)
        # Style   
        
        dv_col = self.dvc.AppendTextColumn("Style",   10, width=90,  mode=dv.DATAVIEW_CELL_EDITABLE)      
        dv_col.SetMinWidth(90) 
            

        for idx, dv_col in enumerate(self.dvc.Columns):
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER) 

        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)
        
        button_add_track = wx.Button(self, label="Add curve")
    #    self.Bind(wx.EVT_BUTTON, self._OnAddCurve, button_add_track)
        button_delete_track = wx.Button(self, label="Delete curve(s)")
    #    self.Bind(wx.EVT_BUTTON, self._OnDeleteCurves, button_delete_track)
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)

        
      
        UIM = UIManager()
        all_tracks = UIM.list('track_controller', self.model.logplot_ctrl_uid)
        for track in all_tracks:     
            item = self.model.ObjectToItem(track)
            self.dvc.Expand(item)
          #  self.model.Resort()
                
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_START_EDITING, self.OnItemStartEditing)        
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_STARTED, self.OnItemEditingStart)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.OnItemEditingDone)
        #dv.


    def OnItemStartEditing(self, event):
        print '\nOnItemStartEditing'
        

    def OnItemEditingStart(self, event):
        print '\nOnItemEditingStart:'
        '''
        editing_col = event.GetDataViewColumn().GetModelColumn()
        if editing_col == 2:
            OM = ObjectManager(self)
            renderer = event.GetDataViewColumn().GetRenderer()
            obj_type_value = event.GetModel().GetValue(event.GetItem(), 1)
            if obj_type_value == 'Log':
                tid = 'log'
            elif obj_type_value == 'Seismic':    
                tid = 'seismic'
            self.obj_values = OrderedDict()    
            for obj in OM.list(tid):
                self.obj_values[obj.name] = obj.oid
            renderer.GetEditorCtrl().AppendItems(self.obj_values.keys())
       '''   
         
         
    def OnItemEditingDone(self, event):
        #import PySwigObject
        #psobj = PySwigObject
       # dv._swig_getattr()
       # import wx.dataview as dv
        #_dv.DataViewRenderer_GetVariantType
        #wxDVCVariant_in_helper
        #_dataview. wxDVCVariant_in_helper(event.GetValue())
                
        print '\nOnItemEditingDone:'
        '''
        py_swig_obj = event.GetValue()
        print dv._swig_repr(py_swig_obj)
        print py_swig_obj,'\n'
        '''
        '''
        print  wxpg._propgrid.__dict__
        
        PGProperty('label', 'name')
        val = prop.ValueToString(py_swig_obj, wxpg.PG_FULL_VALUE)
       
        print 'VAL:', val
        '''

        
        '''
        if not self.obj_values:
            event.SetValue(wx.EmptyString)
        else:
            selected_choice_value = event.GetValue()
            print str(selected_choice_value)
            #real_value = self.obj_values.get(selected_choice_value)
            #event.SetValue(real_value)
        '''
        '''          
        wxDataViewEvent event( wxEVT_DATAVIEW_ITEM_EDITING_DONE, dv_ctrl->GetId() );
        event.SetDataViewColumn( GetOwner() );
        event.SetModel( dv_ctrl->GetModel() );
        event.SetItem( m_item );
        event.SetValue( value );
        event.SetColumn( col );
        event.SetEditCanceled( !isValid );
        event.SetEventObject( dv_ctrl );
        dv_ctrl->GetEventHandler()->ProcessEvent( event );
        '''
        
        
        
class CurvesModel(dv.PyDataViewModel):

    def __init__(self, logplot_ctrl_uid):
        dv.PyDataViewModel.__init__(self)
        self.logplot_ctrl_uid = logplot_ctrl_uid
        #self.objmapper.UseWeakRefs(True)
        

    def GetChildren(self, parent, children):  
        print 'GetChildren'
        UIM = UIManager()
        # Root
        if not parent:
            tracks = UIM.list('track_controller', self.logplot_ctrl_uid)
            if not tracks:
                return 0
            for track in tracks:
                children.append(self.ObjectToItem(track))
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
        if not item:
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackController):
            return True
        return False    
      
    
    
    def GetParent(self, item):
        if not item:
            #print 'GetParent: None'
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)    
        #print 'GetParent:', obj.uid
        if isinstance(obj, TrackController):
            return dv.NullDataViewItem
        elif isinstance(obj, TrackObjectController):
            UIM = UIManager()
            track_uid = UIM._getparentuid(obj.uid)
            track_ctrl = UIM.get(track_uid)
            item = self.ObjectToItem(track_ctrl)
            #print item
            return item
        #print 'GetParent: RUIM'    
            
            
    """                
    _ATTRIBUTES = {
        'obj_uid': {'default_value': wx.EmptyString, 
                    'type': str, 
                    'on_change': TrackObjectController.on_change_objuid
        },
        'left_scale': {'default_value': FLOAT_NULL_VALUE, 
                       'type': float,
                       'on_change': TrackObjectController.on_change_xlim
        },
        'right_scale': {'default_value': FLOAT_NULL_VALUE, 
                        'type': float,
                        'on_change': TrackObjectController.on_change_xlim
        },
        'unit': {'default_value': wx.EmptyString, 'type': str},
        'backup': {'default_value': wx.EmptyString, 'type': str},
        'thickness': {'default_value': 0, 
                      'type': int,
                      'on_change': TrackObjectController.on_change_thickness
        },
        'color': {'default_value': wx.EmptyString,
                  'type': str,
                  'on_change': TrackObjectController.on_change_color       
        },
        'x_scale': {'default_value': 0, 
                    'type': int,
                    'on_change': TrackObjectController.on_change_xscale
        },
        'plottype': {'default_value': wx.EmptyString, 
                     'type': str, 
                     'on_change': TrackObjectController.on_change_plottype
        },
        'visible': {'default_value': True, 'type': bool},
        'cmap': {'default_value': 'rainbow', 
                 'type': str,
                 'on_change': TrackObjectController.on_change_colormap
        },
        'zmin':  {'default_value': FLOAT_NULL_VALUE, 
                  'type': float,
                  'on_change': TrackObjectController.on_change_zlim
        }, 
        'zmax':  {'default_value': FLOAT_NULL_VALUE, 
                  'type': float,
                  'on_change': TrackObjectController.on_change_zlim
        },
        'alpha':  {'default_value': FLOAT_NULL_VALUE, 
                  'type': float,
                  'on_change': TrackObjectController.on_change_alpha
        },
        'zorder':  {'default_value': -1, 
                   'type': LogPlotDisplayOrder,
                   'on_change': TrackObjectController.on_change_zorder
        } 
        
    CURVES_DICT_MAPPING = {
        1: 'Name', 
        2: 'LeftScale', 
        3: 'RightScale',
        5: 'Backup',
        6: 'LogLin',
        7: 'Color',
        8: 'LineWidth',
        9: 'LineStyle'
    } 
    """    


    def SetValue(self, value, item, col):
        print 'SetValue:', col, value
        try:
            obj = self.ItemToObject(item)    
        except KeyError:
            print '\nPERDEU O ITEM: AQUI JAZ O PROBLEMA'
            return False
        if isinstance(obj, TrackController):
            raise Exception()
            
        if isinstance(obj, TrackObjectController):
            if col == 1:
                if value == 'Log':
                    obj.model.obj_tid = 'log'
                elif value == 'Seismic':
                    obj.model.obj_tid = 'seismic'
            if col == 2:
                print 'value:', value
                obj.model.obj_oid = value[1]
            if col == 3:
                obj.model.left_scale = value
            elif col == 4:
                obj.model.right_scale = value
            elif col == 5:
                obj.model.visible = value 
            elif col == 6:
                pass
            elif col == 7:
                if value == 'Linear':
                    obj.model.x_scale = 0  
                elif value == 'Logarithmic':
                    obj.model.x_scale = 1
                else:
                    raise Exception()
            elif col == 8:
                obj.model.color = value
            elif col == 9:  
                obj.model.thickness = value      
            elif col == 10:
                pass                    
        return True

                   
    def GetValue(self, item, col):
        #print 'GetValue:', col
        obj = self.ItemToObject(item)    
        if isinstance(obj, TrackController):
            if col == 0:
                return 'Track ' + str(obj.model.pos + 1)
            return wx.EmptyString
            
        elif isinstance(obj, TrackObjectController):
            if col == 0:
                return wx.EmptyString 
            elif col == 1:
                if obj.model.obj_tid == 'log':
                    return 'Log'
                elif obj.model.obj_tid  == 'seismic':
                    return 'Seismic'
                else:
                        return 'Outros'
            elif col == 2:    
                OM = ObjectManager(self)
                try:
                    om_obj = OM.get((obj.model.obj_tid, obj.model.obj_oid))
                    ret_val = om_obj.name
                except:
                    ret_val = wx.EmptyString
                if not om_obj:
                    ret_val = wx.EmptyString
                print '\nGetValue:', (obj.model.obj_tid, obj.model.obj_oid), ret_val    
                return ret_val 
            elif col == 3:
                return obj.model.left_scale
            elif col == 4:
                return obj.model.right_scale 
            elif col == 5:
                return True
            elif col == 6:
                return 'None'     
            elif col == 7:
                if obj.model.x_scale == 0:
                    return 'Linear'
                elif obj.model.x_scale == 1:
                    return 'Logarithmic'
                else:
                    raise Exception()                    
            elif col == 8:
                return obj.model.color  
            elif col == 9:
                return obj.model.thickness  
            elif col == 10:
                return 'None'      
            else:               
               return wx.EmptyString      
        else:
            raise RuntimeError("unknown node type")
            
            
            
    def GetAttr(self, item, col, attr):
        if col == 0:
            obj = self.ItemToObject(item)
            if isinstance(obj, TrackController):
                attr.SetColour('blue')
                return True
        return False
        
        
    def HasDefaultCompare(self):    
        return False
        
        
    def Compare(self, item1, item2, col, ascending):
        # ascending does not matter here
        pass
        '''
        obj1 = self.ItemToObject(item1)
        obj2 = self.ItemToObject(item2)
        if isinstance(obj1, TrackFormat) and isinstance(obj2, TrackFormat):
            # I think it won't occur, but...
            if self.logplotformat.get_track_index(obj1) == self.logplotformat.get_track_index(obj2):
                return 0
            if ascending: 
                if self.logplotformat.get_track_index(obj1) > self.logplotformat.get_track_index(obj2):
                    return 1
                else:
                    return -1
            else:
                if self.logplotformat.get_track_index(obj1) > self.logplotformat.get_track_index(obj2):
                    return -1
                else:
                    return 1
        elif isinstance(obj1, CurveFormat) and isinstance(obj2, CurveFormat): 
            i1 = int(obj1.get_id().lstrip('CurveFormat '))
            i2 = int(obj2.get_id().lstrip('CurveFormat '))
            # I think it won't occur, but...
            if i1 == i2:
                return 0
            if i1 > i2:
                return 1
            else:
                return -1           

        '''      

    def ValueChanged(self, item, col):
        """
        ValueChanged(self, DataViewItem item, unsigned int col) -> bool

        Call this to inform the registered notifiers that a value in the model
        has been changed.  This will eventually result in a EVT_DATAVIEW_ITEM_VALUE_CHANGED
        event.
        """
        print 'CurvesModel.ValueChanged'
        return super(CurvesModel, self).ValueChanged(item, col)
        
        
    def ChangeValue(self, value, item, col):
        """ChangeValue(self, wxVariant variant, DataViewItem item, unsigned int col) -> bool"""
        print 'CurvesModel.ChangeValue: ', col, value
        return super(CurvesModel, self).ChangeValue(value, item, col)
        if item is None:
            print 'item is None'
            return False
        return False           
      

'''
class MyDVC(dv.DataViewCtrl):
    
    def __init__(self):
        super(MyDVC, self).__init__(style=wx.BORDER_THEME | dv.DV_VERT_RULES | dv.DV_MULTIPLE| dv.DV_ROW_LINES) 
      

    def FinishedEditing()          
'''


#class Teste(dv.DataViewChoiceRenderer):      

class LogRenderer(dv.DataViewCustomRenderer):
    
    def __init__(self, model):
        print '\n\nLogRenderer.__init__'
        dv.DataViewCustomRenderer.__init__(self, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.model = model
        self._value = None    
        self.curves = {}
  
    def GetValue(self):
        print 'LogRenderer.GetValue:', self._value
        return self._value 
        
        
    def SetValue(self, value):
        print 'LogRenderer.SetValue', value
        self._value = value
        return True
        
    def GetSize(self):
        print 'LogRenderer.GetSize'
        return wx.Size(100, 20)
        
    def Render(self, rect, dc, state):
        """
        RenderText(self, String text, int xoffset, Rect cell, DC dc, int state)
        """
        print 'LogRenderer.Render'#, str(self._value), dc, state
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True

    #def HasEditorCtrl(self):
    #    print 'LogRenderer.HasEditorCtrl'
    #    return True      
   
    """
        wxWindow* wxDataViewChoiceRenderer::CreateEditorCtrl( wxWindow *parent, wxRect labelRect, const wxVariant &value )
        {
            wxChoice* c = new wxChoice
                              (
                                  parent,
                                  wxID_ANY,
                                  labelRect.GetTopLeft(),
                                  wxSize(labelRect.GetWidth(), -1),
                                  m_choices
                              );
            c->Move(labelRect.GetRight() - c->GetRect().width, wxDefaultCoord);
            c->SetStringSelection( value.GetString() );
            return c;
        }   
    """
   
    def CreateEditorCtrl(self, parent, rect, value):    
        print 'LogRenderer.CreateEditorCtrl:', parent
        OM = ObjectManager(self)
        obj = self.model.ItemToObject(self.item)
        self._options = OrderedDict()
        for om_obj in OM.list(obj.model.obj_tid):
            print '   Adding:', om_obj.uid, om_obj.name  
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
        print 'LogRenderer.GetValueFromEditorCtrl'
        self._value = self._options.keys()[editor.GetSelection()]
        return True, self._value
       

    """
    wxWindow* wxDataViewChoiceRenderer::CreateEditorCtrl( wxWindow *parent, 
                                                         wxRect labelRect, const wxVariant &value )
    {
        wxChoice* c = new wxChoice
                          (
                              parent,
                              wxID_ANY,
                              labelRect.GetTopLeft(),
                              wxSize(labelRect.GetWidth(), -1),
                              m_choices
                          );
        c->Move(labelRect.GetRight() - c->GetRect().width, wxDefaultCoord);
        c->SetStringSelection( value.GetString() );
        return c;
    }
    
    bool wxDataViewChoiceRenderer::GetValueFromEditorCtrl( wxWindow* editor, wxVariant &value )
    {
        wxChoice *c = (wxChoice*) editor;
        wxString s = c->GetStringSelection();
        value = s;
        return true;
    }
    """

    def StartEditing(self, item, rect):
        self.item = item 
        print 'LogRenderer.StartEditing:', item
        super(LogRenderer, self).StartEditing(item, rect)
        return True
         
    """  
    def StartEditing(self, item, rect):
        self.item = item 
        #print 'LogRenderer.StartEditing:', item
        #super(LogRenderer, self).StartEditing(item, rect)
        #return True
              
        value = self.model.GetValue(item, 2)
        print 'LogRenderer.StartEditing:', value
        dvc = self.GetOwner().GetOwner()
        self.editorCtrl = self.CreateEditorCtrl(dvc.GetMainWindow(), rect, value)        
        
        if not self.editorCtrl:
            return False

        handler = DataViewEditorCtrlEvtHandler(self.editorCtrl, self)
        self.editorCtrl.PushEventHandler(handler)
        self.editorCtrl.SetFocus()
        #handler.SetFocusOnIdle()
        
        '''
        // Now we should send Editing Started event
        wxDataViewEvent event( wxEVT_DATAVIEW_ITEM_EDITING_STARTED, dv_ctrl->GetId() );
        event.SetDataViewColumn( GetOwner() );
        event.SetModel( dv_ctrl->GetModel() );
        event.SetItem( item );
        event.SetEventObject( dv_ctrl );
        dv_ctrl->GetEventHandler()->ProcessEvent( event );
        '''
            
        return True
       
       
        
   
    def FinishEditing(self):
        print '\nLogRenderer.FinishedEditing'
        #editor = self.GetEditorCtrl()
        pos = self.editorCtrl.GetCurrentSelection()
        choice_val =  self._options.items()[pos]
        #editor.Destroy()
        if not choice_val:
            return False
        om_uid = choice_val[0]    
        column = self.GetOwner()
        col = column.GetModelColumn()
        
        #print 'LogRenderer.StartEditing:'
        '''
        if not self.item:
            print 'item is None'
        elif self.item == dv.NullDataViewItem:
            print 'dv.NullDataViewItem'
        else:
            print 'LEGAL:', self.item
        '''    
        #value = self.model.ChangeValue(om_uid, self.item, col)
        print self.item
        value = self.model.SetValue(om_uid, self.item, col)
        print 'VOLTOU DO ALÉM'
        return value   

    """
     
"""
bool wxDataViewRendererBase::FinishEditing()        
{
    if (!m_editorCtrl)
        return true;

    wxVariant value;
    GetValueFromEditorCtrl( m_editorCtrl, value );

    wxDataViewCtrl* dv_ctrl = GetOwner()->GetOwner();

    DestroyEditControl();

    dv_ctrl->GetMainWindow()->SetFocus();

    bool isValid = Validate(value);
    unsigned int col = GetOwner()->GetModelColumn();

    // Now we should send Editing Done event
    wxDataViewEvent event( wxEVT_DATAVIEW_ITEM_EDITING_DONE, dv_ctrl->GetId() );
    event.SetDataViewColumn( GetOwner() );
    event.SetModel( dv_ctrl->GetModel() );
    event.SetItem( m_item );
    event.SetValue( value );
    event.SetColumn( col );
    event.SetEditCanceled( !isValid );
    event.SetEventObject( dv_ctrl );
    dv_ctrl->GetEventHandler()->ProcessEvent( event );

    if ( isValid && event.IsAllowed() )
    {
        dv_ctrl->GetModel()->ChangeValue(value, m_item, col);
        return true;
    }

    return false;
}        
        
"""    


    
# Translated from wxDataViewEditorCtrlEvtHandler found in datavcmn.cpp        
# Custom handler pushed on top of the edit control used by wxDataViewCtrl to
# forward some events to the main control itself.
class DataViewEditorCtrlEvtHandler(wx.EvtHandler):
    
    def __init__(self, editor, renderer):
        print 'DVEvtHandler.__init__'
        wx.EvtHandler.__init__(self)
        self.editorCtrl = editor
        self.owner = renderer
        self.finished = False
        self.focusOnIdle = False
        self.editorCtrl.Bind(wx.EVT_CHAR, self.OnChar)
        self.editorCtrl.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.editorCtrl.Bind(wx.EVT_IDLE, self.OnIdle)
        self.editorCtrl.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)

    def AcceptChangesAndFinish(self):
        print 'DVEvtHandler.AcceptChangesAndFinish'
        #pass
    
    def SetFocusOnIdle(self, focus=True):
        print 'DVEvtHandler.SetFocusOnIdle'
        self.focusOnIdle = focus

    def OnIdle(self, event):
        print 'DVEvtHandler.OnIdle'
        if self.focusOnIdle:
            if wx.Window.FindFocus() != self.editorCtrl:
                self.editorCtrl.SetFocus()
        event.Skip()

    def OnTextEnter(self, event):
        print 'DVEvtHandler.OnTextEnter'
        self.finished = True
        self.owner.FinishEditing()            

    def OnChar(self, event):
        print 'DVEvtHandler.OnChar'
        if event.m_keyCode == wx.WXK_RETURN:
            self.finished = True
            self.owner.FinishEditing()
        elif event.m_keyCode == wx.WXK_ESCAPE:
            self.finished = True
            self.owner.CancelEditing()
        else:    
            event.Skip()    

    def OnKillFocus(self, event):
        print 'DVEvtHandler.OnKillFocus'
        if not self.finished:
            self.finished = True
            self.owner.FinishEditing()
        event.Skip()    



        
    
