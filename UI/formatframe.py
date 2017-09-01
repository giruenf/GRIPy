# -*- coding: utf-8 -*-
import wx
from wx.combo import OwnerDrawnComboBox
import wx.lib.colourdb
from collections import OrderedDict
from OM.Manager import ObjectManager
import Parms
import wx.dataview as dv
import copy
#from logplotformat import LogPlotFormat, TrackFormat, CurveFormat
import cPickle



class LogPlotFormatFrame(wx.Frame):
    ID_ALL_TRACKS = -1
            
    def __init__(self, logplot, track_id=ID_ALL_TRACKS, logplotformat=None, ok_callback=None):
                 
        self.logplot = logplot
        self.track_id = track_id
        
        self.welluid = self.logplot.get_well_uid()
        self._OM = ObjectManager(self)
        #well = self._OM.get(self.welluid)
        
        if logplotformat is None:
            logplotformat = LogPlotFormat()
        self.original_logplotformat = logplotformat
        self.edited_logplotformat = copy.deepcopy(self.original_logplotformat)
        

        wx.Frame.__init__(self, self.logplot, -1,
                                          title="Log Plot Format - TESTE",
                                          size=(850, 600),
                                          style=wx.DEFAULT_FRAME_STYLE & 
                                          (~wx.RESIZE_BORDER) &(~wx.MAXIMIZE_BOX))

        self.callback = ok_callback             
        sizer = wx.BoxSizer(wx.VERTICAL)                                  
        self.base = wx.Panel(self)
        note = wx.Notebook(self.base)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(note, 1, wx.ALL|wx.EXPAND, border=5)        
        self.base.SetSizer(bsizer)
        
        self.tracks_model = None
        self.curves_model = CurvesModel(self.edited_logplotformat, self.track_id)
        
        if self.track_id == self.ID_ALL_TRACKS:
            self.tracks_model = TracksModel(self.edited_logplotformat)
            tn = TracksNotifier(self.edited_logplotformat, self.curves_model)
            self.tracks_model.AddNotifier(tn)
            tn.SetOwner(self.tracks_model)
            self.grid_panel = BasePanel(note, 'grid', self.welluid, self.track_id, self.tracks_model)                  
            note.AddPage(self.grid_panel, "Grid", True)
        else:
            self.grid_panel = None
        if self.tracks_model is not None:    
            cn = CurvesNotifier(self.edited_logplotformat, self.tracks_model)
            self.curves_model.AddNotifier(cn)
            cn.SetOwner(self.curves_model) 
        self.curves_panel = BasePanel(note, 'curves', self.welluid, self.track_id, self.curves_model)
        note.AddPage(self.curves_panel, "Curves", False)
        
        
        note.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._OnNotePageChanging)
        sizer.Add(self.base, 1, wx.EXPAND)
        sizer.Add(self.getPanelBottomButtons(), 0, wx.EXPAND|wx.BOTTOM|wx.TOP)
        self.SetSizer(sizer)

        
    def getPanelBottomButtons(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        b1 = wx.Button(panel, -1, "OK")
        sizer.Add(b1, 0, wx.ALIGN_RIGHT, border=5)
        
        b2 = wx.Button(panel, -1, "Apply")
        sizer.Add(b2, 0, wx.ALIGN_RIGHT, border=5)
        
        b3 = wx.Button(panel, -1, "Cancel")
        sizer.Add(b3, 0, wx.LEFT|wx.RIGHT, border=5)
        
        b1.Bind(wx.EVT_BUTTON, self._OnButtonOK)      
        b2.Bind(wx.EVT_BUTTON, self._OnButtonApply)
        b3.Bind(wx.EVT_BUTTON, self._OnButtonCancel)
        
        panel.SetSizer(sizer)
        return panel
        
        
    def _OnButtonOK(self, evt):
        if self.original_logplotformat != self.edited_logplotformat:
            if self.callback:
                self.callback(self.edited_logplotformat) 
            else:
                raise Exception('A callback function was not given to this LogPlotFormatFrame.')
        self.Close()    
     

    def _OnButtonApply(self, evt):
        if self.original_logplotformat != self.edited_logplotformat:
            if self.callback:
                # To avoid troubles in Apply action:
                # - Same logplotformat on LogPlot._process_plot_format 
                self.original_logplotformat = copy.deepcopy(self.edited_logplotformat)
                self.callback(self.original_logplotformat)
            else:
                raise Exception('A callback function was not given to this LogPlotFormatFrame.')
     
     
     
    def _OnButtonCancel(self, evt):
        self.Close()


    def _OnNotePageChanging(self, evt):
        if self.tracks_model is not None:
            if evt.GetSelection() == 0:
                self.tracks_model.Resort()
                
            elif  evt.GetSelection() == 1:   
                dvc = self.curves_panel.get_dataview_ctrl()
                for track in self.curves_model.logplotformat.get_tracks():     
                    item = self.curves_model.ObjectToItem(track)
                    dvc.Expand(item)
                self.curves_model.Resort()
        


##########################################################################



class BasePanel(wx.Panel):
    VALID_TIDS = ['grid', 'curves', 'shading']
    
    def __init__(self, parent, tid, welluid, track_id, model=None):
        if tid not in self.VALID_TIDS:
            raise Exception('BasePanel type [{}] not valid. Valid types: {}.'.format(tid, self.VALID_TIDS))
        #self.parent = parent    
        self.tid = tid    
        self.welluid = welluid
        self.track_id = track_id        
        self.model = model
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('white')
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inside_panel = self._get_tid_panel()
        self.sizer.Add(self.inside_panel, 1, wx.ALL|wx.EXPAND, border=5)     
        self.SetSizer(self.sizer)
        

    def get_dataview_ctrl(self):
        return self.true_panel.get_dataview_ctrl()       
        
        
    def _get_tid_panel(self):
        if self.tid == 'grid' and self.track_id == LogPlotFormatFrame.ID_ALL_TRACKS:
            panel = self._get_inside_panel_grid()
        elif self.tid == 'curves':    
            panel = self._get_inside_panel_curves()                
        elif self.tid == 'shading':
            panel = wx.Panel(self)
        return panel


    def _get_inside_panel_grid(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        tp = TracksPanel(panel, self.model)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tp, 1, wx.EXPAND|wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.true_panel = tp
        return panel 
        
        
    def _get_inside_panel_curves(self):
        panel = wx.Panel(self, style=wx.SIMPLE_BORDER)
        cp = CurvesPanel(panel, self.welluid, self.model)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(cp, 1, wx.EXPAND|wx.ALL, border=10)
        panel.SetSizer(sizer)
        self.true_panel = cp
        return panel    
        
        



######################################################################


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
        return wx.CustomDataFormat(VarNodeDropData.NAME)
  
  
#######################################################################
  

class TracksPanel(wx.Panel):
        
    def __init__(self, parent, model):
        wx.Panel.__init__(self, parent, -1)
        self.model = model
        self.dvc = dv.DataViewCtrl(self, style=wx.BORDER_THEME
        | dv.DV_VERT_RULES | dv.DV_MULTIPLE| dv.DV_ROW_LINES) 
        
        self.dvc.AssociateModel(self.model)
        
        # Track
        dv_col = self.dvc.AppendTextColumn("Track", 0, width=45, align=wx.ALIGN_CENTER)
        dv_col.SetMinWidth(45)
        # Track Name
        dv_col = self.dvc.AppendTextColumn("Track Title",  1, width=80, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(80)
        # Width
        dv_col = self.dvc.AppendTextColumn("Width",   2, width=50, mode=dv.DATAVIEW_CELL_EDITABLE)      
        dv_col.SetMinWidth(50)
        # Visible (Track)
        dv_col = self.dvc.AppendToggleColumn("Visible",   3, width=50,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        # Plot Grid
        self.dvc.AppendToggleColumn("Plot Grid",   4, width=60,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        # Depth Lines
        dvcr = dv.DataViewChoiceRenderer(TrackFormat.DEPTH_LINES_MAPPING.values(), 
                                        mode=dv.DATAVIEW_CELL_EDITABLE)
        dvcol = dv.DataViewColumn("Depth Lines", dvcr, 5, width=75)
        self.dvc.AppendColumn(dvcol)
        # Scale Lines
        dv_col = self.dvc.AppendTextColumn("Scale Lines",   6, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70)   
        # Scale (Track)
        dvcr = dv.DataViewChoiceRenderer(TrackFormat.SCALE_MAPPING.values(), 
                                        mode=dv.DATAVIEW_CELL_EDITABLE)
        dvcol = dv.DataViewColumn("Scale", dvcr, 7, width=75)
        dv_col.SetMinWidth(75)    
        self.dvc.AppendColumn(dvcol)
        # Decimation
        dv_col = self.dvc.AppendTextColumn("Decimation", 8, width=75, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(75)        
        # Left Scale
        dv_col = self.dvc.AppendTextColumn("Left Scale", 9, width=65, mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(65)   
        # Minor Lines  
        self.dvc.AppendToggleColumn("Minor Lines",   10, width=75, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(75) 
        # Overview        
        self.dvc.AppendToggleColumn("Overview", 11, width=65, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(65) 

        for dv_col in self.dvc.Columns:
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER)         
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)
        button_add_track = wx.Button(self, label="Add track")
        self.Bind(wx.EVT_BUTTON, self._OnAddTrack, button_add_track)
        button_delete_track = wx.Button(self, label="Delete track(s)")
        self.Bind(wx.EVT_BUTTON, self._OnDeleteTracks, button_delete_track)
        button_select_all = wx.Button(self, label="Select All")
        self.Bind(wx.EVT_BUTTON, self._OnSelectAll, button_select_all)
        button_select_none = wx.Button(self, label="Select None")
        self.Bind(wx.EVT_BUTTON, self._OnSelectNone, button_select_none)
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
    

    def get_dataview_ctrl(self):
        return self.dvc
    
        
    def OnItemBeginDrag(self, evt):
        item = evt.GetItem()
        if not item.IsOk():
            evt.Veto()
            return
        self.node = VarNodeDropData()
        self.node.SetItem(item)
        evt.SetDataObject(self.node)
        evt.SetDragFlags(wx.Drag_DefaultMove)
        
        
    def OnItemDropPossible(self, evt):
        new_item = evt.GetItem()
        old_item = self.node.GetItem()
        if new_item == old_item:
            return 
        self.dvc.UnselectAll() # Change Selection    
        if new_item.IsOk() and \
                            evt.GetDataFormat() == VarNodeDropData.GetFormat():
            self.dvc.Select(new_item)    
            new_track = self.model.ItemToObject(new_item)
            new_pos = self.model.logplotformat.get_track_index(new_track)
            old_track = self.model.ItemToObject(old_item)
            self.model.logplotformat.set_track_new_position(old_track, new_pos)
            self.model.ChangedItem(new_item) 
            return True    
        return False        
    
 
            
    def _OnDeleteTracks(self, evt):
        rows = self._get_selection_positions()
        for row in rows:
            track = self.model.logplotformat.get_track(row)
            self.DeleteTrack(track)


        
    def _OnAddTrack(self, evt):
        rows = self._get_selection_positions()
        if not rows:
            self.InsertTrack(self._get_dummy_track())
        else:
            for row in rows:
                self.InsertTrack(self._get_dummy_track(), row)        
                
                
    def _OnSelectAll(self, evt):
        self.dvc.SelectAll()
        
    def _OnSelectNone(self, evt):
        self.dvc.UnselectAll()        
        
    def _get_selection_positions(self):
        items = self.dvc.GetSelections()
        tracks_selected = [self.model.ItemToObject(item) for item in items]
        rows = []
        for track in tracks_selected:
            rows.append(self.model.logplotformat.get_track_index(track))
        rows.sort(reverse=True)  
        return rows    


    def DeleteTrack(self, track):
        self.model.DeleteTrack(track)
        
        
    def InsertTrack(self, track, pos=None):
        #print 'TracksPanel.InsertTrack pos: ', pos
        if not isinstance(track, TrackFormat):
            raise ValueError('Parameter track must be a TrackFormat.')
        self.model.InsertTrack(track, pos)
          

    def _get_dummy_track(self):
        dummy_map = OrderedDict()
        dummy_map['width'] = 2.0
        dummy_map['plotgrid'] = True
        dummy_map['x_scale'] = 0
        dummy_map['decades'] = 2                 
        dummy_map['leftscale'] = 0.2
        dummy_map['minorgrid'] = False
        dummy_map['overview'] = False
        dummy_map['scale_lines'] = 5           
        dummy_map['depth_lines'] = 0
        dummy_map['show_track'] = True
        tf = TrackFormat(dummy_map)
        return tf


###############################################################################

###  NOVO ###


class TracksModel(dv.PyDataViewModel):
    TRACKS_MODEL_MAPPING = {
        1: 'track_name',
        2: 'width',
        3: 'show_track',
        4: 'plotgrid',
        5: 'depth_lines',
        6: 'scale_lines',
        7: 'x_scale', 
        8: 'decades',
        9: 'leftscale',
        10: 'minorgrid', 
        11: 'overview',
        12: 'unidentified'
    }    
    
    
    def __init__(self, logplotformat):
        dv.PyDataViewModel.__init__(self)
        self.logplotformat = logplotformat
        self.objmapper.UseWeakRefs(True)


    def GetColumnCount(self):   
        return len(self.TRACKS_MODEL_MAPPING)-1


    def GetColumnType(self, col):
        if col == 0:
            return 'int'
        key = self.TRACKS_MODEL_MAPPING.get(col)    
        type_ = LogPlotFormat.get_track_key_type(key)    
        return str(type_)

        
    def GetChildren(self, parent, children):     
        # Root
        if self.logplotformat is None:
            return 0
        for track in self.logplotformat.get_tracks():
            children.append(self.ObjectToItem(track)) 
        return len(children)

    
        
    def IsContainer(self, item):
        if not item:
            return True
        return False  
       
    def GetParent(self, item):
        return dv.NullDataViewItem
            
    def GetValue(self, item, col):
        track = self.ItemToObject(item)
        if isinstance(track, TrackFormat):
            if col == 0:    
                return self.logplotformat.get_track_index(track)+1
            col_key = self.TRACKS_MODEL_MAPPING.get(col)
            value = track.get_value(col_key)
            if col_key == 'depth_lines':
                return TrackFormat.DEPTH_LINES_MAPPING.get(value)
            elif col_key == 'x_scale': 
                return TrackFormat.SCALE_MAPPING.get(value)
            else:
                return value

    def SetValue(self, value, item, col):
        track = self.ItemToObject(item)    
        if isinstance(track, TrackFormat):
            col_key = self.TRACKS_MODEL_MAPPING.get(col)
            if col_key == 'depth_lines':
                value_int = TrackFormat.DEPTH_LINES_MAPPING.values().index(value)
                track.set_value(col_key, value_int)
                return True
            elif col_key == 'x_scale':  
                value = TrackFormat.SCALE_MAPPING.values().index(value)
                track.set_value(col_key, value)
                return True
            else:
                track.set_value(col_key, value)
                return True
        
    def DeleteTrack(self, track):
        if track in self.logplotformat.get_tracks():
            self.logplotformat.remove_track(track)
            item = self.ObjectToItem(track)
            self.ItemDeleted(dv.NullDataViewItem, item)
 
    def InsertTrack(self, track, pos=None):
        if self.logplotformat is None:
            self.logplotformat = LogPlotFormat()
            self.logplotformat.append_track(track)
            item = self.ObjectToItem(track)
            self.ItemAdded(dv.NullDataViewItem, item)
            return True
        elif track not in self.logplotformat.get_tracks():
            if pos is None:
                last_pos_old = len(self.logplotformat)-1
                if last_pos_old >= 0:
                    last_track_old = self.logplotformat.get_track(last_pos_old)
                    if last_track_old.get_value('overview') == True:
                        last_track_old.set_value('overview', False)
                        last_item_old = self.ObjectToItem(last_track_old)
                        self.ItemChanged(last_item_old)
                self.logplotformat.append_track(track)
            else:
                self.logplotformat.insert_track(pos, track)
            item = self.ObjectToItem(track)
            self.ItemAdded(dv.NullDataViewItem, item)
            return True
        return False    

    def ChangedItem(self, item):
        self.ItemChanged(item)

    def GetAttr(self, item, col, attr):
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackFormat) and col == 0:
            attr.SetColour('blue')
            return True
        return False
        

    def HasDefaultCompare(self):    
        return True
        
        
    def Compare(self, item1, item2, col, ascending):
        track1 = self.ItemToObject(item1)
        track2 = self.ItemToObject(item2)
        # I think it won't occur, but...
        if self.logplotformat.get_track_index(track1) == self.logplotformat.get_track_index(track2):
            return 0
        if ascending: 
            if self.logplotformat.get_track_index(track1) > self.logplotformat.get_track_index(track2):
                return 1
            else:
                return -1
        else:
            if self.logplotformat.get_track_index(track1) > self.logplotformat.get_track_index(track2):
                return -1
            else:
                return 1
        


    def IsEnabled(self, item, col):
        #print '\nNEW IsEnabled'
        track = self.ItemToObject(item)
        if not isinstance(track, TrackFormat):
            return True
            
        if col in [5, 6, 7, 8, 9, 10]:
            if track.get_value('plotgrid') == False:
                return False
            else:
                if col in [8, 9, 10]:
                    if track.get_value('x_scale') == 0:
                        return False
                return True
                
        if col == 11:
            if self.logplotformat.get_track_index(track) == len(self.logplotformat)-1:
                return True
            return False        
        return True            
        

             
####################################################################


            
class CurvesPanel(wx.Panel):
    
    DEPTH_LINES_CHOICE = ['Full', 'Left', 'Right', 'Center', 'Left & Right', 'None']    
    
    def __init__(self, parent, welluid, model):
        wx.Panel.__init__(self, parent, -1)
        self.model = model
        self.dvc = dv.DataViewCtrl(self, style=wx.BORDER_THEME
            | dv.DV_ROW_LINES | dv.DV_VERT_RULES | dv.DV_MULTIPLE)
        self.welluid = welluid
        self.dvc.AssociateModel(self.model)
        self._OM = ObjectManager(self) 
        
        self.curves = OrderedDict()
        depth = self._OM.list('depth', self.welluid)
        depth =  depth[0]
        self.curves[depth.name] = depth.uid
        for log in self._OM.list('log', self.welluid):
            self.curves[log.name] = log.uid
        for part in self._OM.list('partition', self.welluid):
            self.curves[part.name] = part.uid
            
        # Track
        dv_col = self.dvc.AppendTextColumn("Track",  0, width=85)      
        dv_col.SetMinWidth(55)    
        
        # Curve 
        dvcr_curve_name= dv.DataViewChoiceRenderer(self.curves.keys(),  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col = dvcol_curve_name = dv.DataViewColumn("Curve", dvcr_curve_name, 1, width=85, flags=dv.DATAVIEW_COL_REORDERABLE)           
        dv_col.SetMinWidth(85)
        dv_col = self.dvc.AppendColumn(dvcol_curve_name)
        
        # Left Scale        
        dv_col = self.dvc.AppendTextColumn("Left Scale",   2, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70) 
        
        # Right Scale
        dv_col = self.dvc.AppendTextColumn("Right Scale",   3, width=70,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(70)
        
        # Visible (Curve)        
        dv_col = self.dvc.AppendToggleColumn("Visible",   4, width=50,  mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        
        # Back up
        dv_col = self.dvc.AppendTextColumn("Back up",   5, width=60,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(60)
        
        # Scale (Curve)
        #print CurveFormat.SCALE_MAPPING.values()
        dvcr = dv.DataViewChoiceRenderer(CurveFormat.SCALE_MAPPING.values(),  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col = dv.DataViewColumn("Scale", dvcr, 6, width=75)
        dv_col.SetMinWidth(75)    
        self.dvc.AppendColumn(dv_col)
        
               
        #self.dvc.GetMainWindowOfCompositeControl        
 
 
###############################################################################        
        
        # Line Color
        #'''
        dvcr = dv.DataViewChoiceRenderer(ColorSelectorComboBox.get_colors(),
                                         mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col = dv.DataViewColumn("Line Color", dvcr, 7, width=75)
        dv_col.SetMinWidth(75)    
        self.dvc.AppendColumn(dv_col)
        #'''
        
        '''
        # Em busca do armengue do ColorComboBox
        color_renderer = ColorRenderer(self.model)
        dv_col = dv.DataViewColumn("Line Color", renderer=color_renderer,
                                   model_column=7, width=70)
        self.dvc.AppendColumn(dv_col)
        '''
        
###############################################################################    
        
        
        # Width         
        dv_col = self.dvc.AppendTextColumn("Width",   8, width=45,  mode=dv.DATAVIEW_CELL_EDITABLE)
        dv_col.SetMinWidth(45)
        # Style   
        
        dv_col = self.dvc.AppendTextColumn("Style",   9, width=90,  mode=dv.DATAVIEW_CELL_EDITABLE)      
        dv_col.SetMinWidth(90) 
            

        for idx, dv_col in enumerate(self.dvc.Columns):
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER) 

        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)
        button_add_track = wx.Button(self, label="Add curve")
        self.Bind(wx.EVT_BUTTON, self._OnAddCurve, button_add_track)
        button_delete_track = wx.Button(self, label="Delete curve(s)")
        self.Bind(wx.EVT_BUTTON, self._OnDeleteCurves, button_delete_track)
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT|wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT|wx.RIGHT, 5)
        self.Sizer.Add(btnbox, 0, wx.TOP|wx.BOTTOM, 5)


        if self.model.logplotformat is not None:
            for track in self.model.logplotformat.get_tracks():     
                item = self.model.ObjectToItem(track)
                self.dvc.Expand(item)
                self.model.Resort()
     
        

        self.dvc.EnableDragSource(VarNodeDropData.GetFormat())
        self.dvc.EnableDropTarget(VarNodeDropData.GetFormat())
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_BEGIN_DRAG, self.OnItemBeginDrag)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_DROP_POSSIBLE, self.OnItemDropPossible)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_DROP, self.OnItemDrop) 
        

    
    def OnItemBeginDrag(self, evt):

        item = evt.GetItem()
        try:    
            obj = self.model.ItemToObject(item)
            if isinstance(obj, CurveFormat):
                self.node = VarNodeDropData()
                self.node.SetItem(item)
                evt.SetDataObject(self.node)
                evt.SetDragFlags(wx.Drag_DefaultMove)
            else:
                evt.Veto()
        except Exception:
            evt.Veto()
        
        
    def OnItemDropPossible(self, evt):
        new_item = evt.GetItem()
        old_item = self.node.GetItem()
        if new_item == old_item:
            return 
        self.dvc.UnselectAll() # Change Selection    

        if new_item.IsOk() and \
                            evt.GetDataFormat() == VarNodeDropData.GetFormat():
                         
            self.dvc.Select(new_item)    
            new_obj = self.model.ItemToObject(new_item)
            new_track = None
            if isinstance(new_obj, TrackFormat):
                new_track = new_obj
            elif isinstance(new_obj, CurveFormat):
                new_track = self.model.logplotformat.get_curve_parent(new_obj)
            curve = self.model.ItemToObject(old_item)   
            
            old_parent_track = self.model.logplotformat.get_curve_parent(curve)    
            if old_parent_track == new_track:
                evt.Veto()
                return False              
            evt.Allow()    
            return True    
        evt.Veto()
        return False            
       
       
    def OnItemDrop(self, evt):  
        old_item = self.node.GetItem()
        # From OnItemBeginDrag, we're sure it's a CurveFormat
        curve = self.model.ItemToObject(old_item)
        
        new_item = evt.GetItem()
        new_obj = self.model.ItemToObject(new_item)
        new_track = None
        if isinstance(new_obj, TrackFormat):
            new_track = new_obj
        elif isinstance(new_obj, CurveFormat):
            new_track = self.model.logplotformat.get_curve_parent(new_obj)
        
        self.DeleteCurve(curve)           
        self.AddCurve(new_track, curve)
        

        return True


    def get_dataview_ctrl(self):
        return self.dvc            
            
    def _OnAddCurve(self, evt):
        #print 'OnAddCurve' 
        tracks, curves = self._get_objects_selected() 
        if curves:
            parent = self.model.logplotformat.get_curve_parent(curves[0]) 
            self.AddCurve(parent, self._get_dummy_curve())
        elif tracks:
            parent = tracks[0]
            self.AddCurve(parent, self._get_dummy_curve())
        else:
            if self.model.track_id != LogPlotFormatFrame.ID_ALL_TRACKS:
                track = self.model.logplotformat.get_track(self.model.track_id)
                self.AddCurve(track, self._get_dummy_curve())
            
    def _OnDeleteCurves(self, evt):
        #print 'OnDeleteRow'
        _, curves = self._get_objects_selected()
        for curve in curves:
            self.DeleteCurve(curve)
            
    def AddCurve(self, track_parent, curve):
        self.model.AddCurve(track_parent, curve)                

    def DeleteCurve(self, curve):
        #print 'DeleteCurve'
        self.model.DeleteCurve(curve)
        
    def _get_objects_selected(self):
        items = self.dvc.GetSelections()
        objects_selected = [self.model.ItemToObject(item) for item in items]
        tracks = []
        curves = []
        for obj in objects_selected:
            if isinstance(obj, TrackFormat):
                tracks.append(obj)
            if isinstance(obj, CurveFormat):
                curves.append(obj)    
        return tracks, curves                

    def _get_dummy_curve(self):
        dummy_map = OrderedDict()
        dummy_map['curve_name'] = None
        dummy_map['left_scale'] = None
        dummy_map['right_scale'] = None
        dummy_map['visible'] = None                
        dummy_map['backup'] = None
        dummy_map['x_scale'] = None
        dummy_map['color'] = None
        dummy_map['thickness'] = None         
        dummy_map['point_plotting'] = None
        cf = CurveFormat(dummy_map)
        return cf            
            
            
            
#######################################################################



class CurvesModel(dv.PyDataViewModel):
    CURVES_MODEL_MAPPING = {
        1: 'curve_name',
        2: 'left_scale',
        3: 'right_scale',
        4: 'visible',
        5: 'backup',
        6: 'x_scale',
        7: 'color',     
        8: 'thickness',
        9: 'point_plotting',
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


    def __init__(self, logplotformat, track_id):
        dv.PyDataViewModel.__init__(self)
        self.logplotformat = logplotformat
        self.objmapper.UseWeakRefs(True)
        self.track_id = track_id
        self._OM = ObjectManager(self) 
        #print 'CurvesModel: '
        #print self
                
    def __str__(self):
        return 'CurvesModel'            
        
    def GetColumnCount(self):
        #print 'GetColumnCount'        
        return len(self.CURVES_MODEL_MAPPING)-1

    def GetColumnType(self, col):
        #print 'GetColumnType'
        mapper = {0 : 'string'}
        for i in range(1, len(self.CURVES_MODEL_MAPPING)):
            key = self.CURVES_MODEL_MAPPING.get(i)
            mapper[i] = LogPlotFormat.get_curve_key_type(key)
        return mapper[col]
        
        
    def GetChildren(self, parent, children):  
        # Root
        if not parent:
            if self.logplotformat is None:
                return 0
            if self.track_id == LogPlotFormatFrame.ID_ALL_TRACKS:
                for track in self.logplotformat.get_tracks():
                    children.append(self.ObjectToItem(track))
                return len(children)
            else:
                track = self.logplotformat.get_track(self.track_id)
                children.append(self.ObjectToItem(track))
                return 1
        # Child    
        obj = self.ItemToObject(parent)
        if isinstance(obj, TrackFormat):
            for curve in obj.get_curves():
                children.append(self.ObjectToItem(curve))
            return len(obj.get_curves())
        return 0
    
    def IsContainer(self, item):
        if not item:
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackFormat):
            return True
        return False    
   


    # Just to notify others   
    def DeleteCurve(self, curve): 
        if not isinstance(curve, CurveFormat):
            raise ValueError('curve must be a CurveFormat instance.')
        if curve in self.logplotformat.get_curves(): 
            item = self.ObjectToItem(curve)
            parent = self.GetParent(item)            
            self.logplotformat.remove_curve(curve)
            self.ItemDeleted(parent, item)
        

    
    
    def AddCurve(self, track, curve):
        #print 'CurvesModel.AddCurve'  
        if not isinstance(track, TrackFormat):
            raise ValueError('track must be a TrackFormat instance.')
        if not isinstance(curve, CurveFormat):
            raise ValueError('curve must be a CurveFormat instance.')    
        if track not in self.logplotformat.get_tracks():
            raise ValueError('track does not belong to this LogPlotFormat')
        track.add_curve(curve)
        item_track = self.ObjectToItem(track)
        item_curve = self.ObjectToItem(curve)
        self.ItemAdded(item_track, item_curve)

        
    def GetParent(self, item):
        #print 'CurvesModel.GetParent'
        if not item:
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)        
        if isinstance(obj, TrackFormat):
            return dv.NullDataViewItem
        elif isinstance(obj, CurveFormat):
            track = self.logplotformat.get_curve_parent(obj)
            return self.ObjectToItem(track)
                    
                    
    def GetValue(self, item, col):
        #print 'CurvesModel.GetValue'
        obj = self.ItemToObject(item)    
        if isinstance(obj, TrackFormat):
            if col == 0:
                return 'Track ' + str(self.logplotformat.get_track_index(obj) + 1)
            return ''
        
        elif isinstance(obj, CurveFormat):
            if col == 0:
                return '' 
            col_key = self.CURVES_MODEL_MAPPING.get(col)
            value = obj.get_value(col_key)  
            if col == 1:
                #print 'CurvesModel.GetValue: 1: ', value
                return value
            if col == 6: # Scale
                #print 'value: ', value
                #print 'CurvesModel.GetValue: 6: ', CurveFormat.SCALE_MAPPING.get(value)
                return CurveFormat.SCALE_MAPPING.get(value)
            if col == 7: # Color line 
                #print 'value: ', value
                #print 'CurvesModel.GetValue: 7: ', value
                return value
            else:               
               return value       
        else:
            raise RuntimeError("unknown node type")
            
    def ChangedItem(self, item):
        #print 'CurvesModel.ChangedItem'
        self.ItemChanged(item)
        
        
    def ChangeValue(self, value, item, col):
        """ChangeValue(self, wxVariant variant, DataViewItem item, unsigned int col) -> bool"""
        #print 'CurvesModel.ChangeValue: ', col, value
        if item is None:
            #print 'item is None'
            return False
        return False    
  
    
    
    def SetValue(self, value, item, col):
        obj = self.ItemToObject(item)    
        if isinstance(obj, CurveFormat):
            key = self.CURVES_MODEL_MAPPING.get(col)
            if col == 1:
                #print 'CurvesModel.SetValue: ', value
                '''
                for part in self._OM.list('partition', self.welluid):
                    if value == part.name:
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(2), 0)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(3), 1)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(4), True)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(5), None)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(6), 0)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(7), None)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(8), 1)
                        obj.set_value(self.CURVES_MODEL_MAPPING.get(9), 'Partition')
                        return
                '''        
                parms = Parms.ParametersManager.get().get_curve_parms(value)
                if parms:
                    for i in range(2, len(self.CURVES_MODEL_MAPPING)+1):
                        key_model = self.CURVES_MODEL_MAPPING.get(i)
                        if i == 4:
                             obj.set_value(key_model, True)
                        else:     
                            key_parm = self.CURVES_DICT_MAPPING.get(i)
                            value_parm = str(parms.get(key_parm))
                            if i == 6:
                                if value_parm == 'Lin':
                                    value_parm = 0
                                elif value_parm == 'Log':
                                    value_parm = 1
                            if i == 7 and value_parm == 'DkGray':
                                value_parm = 'DarkGray'
                            #print 'obj.set_value({}, {})'.format(key_model, value_parm)    
                            obj.set_value(key_model, value_parm)
                #else:
                #    # In case of not recognized curve name
                #    print '\nNOT RECOGNIZE'
                    '''
                    for i in range(2, len(self.CURVES_MODEL_MAPPING)):
                        key_model = self.CURVES_MODEL_MAPPING.get(i)

                    2: 'LeftScale', 
                    3: 'RightScale',
                    5: 'Backup',
                    6: 'LogLin',
                    7: 'Color',
                    8: 'LineWidth',
                    9: 'LineStyle'                        
                        
                    self.SetCellValue(row, 1, 'None')
                    self.SetCellValue(row, 2, 'None')
                    self.SetCellValue(row, 3, 'No') 
                    self.SetCellValue(row, 4, 'None')
                    self.SetCellValue(row, 5, '') 
                    self.SetCellValue(row, 6, '')
                    self.SetCellValue(row, 7, '') 
                    self.SetCellValue(row, 8, '')
                    '''
            if col == 6:
                value = CurveFormat.SCALE_MAPPING.values().index(value)
           # if col == 7:
           #     print 'CurvesModel.SetValue: ', value
            obj.set_value(key, value)
        elif isinstance(obj, TrackFormat):    
            #print 'Entrou SetValue TrackFormat'
            obj.set_value(key, value)
        return True
        

    def GetAttr(self, item, col, attr):
        #print 'CurvesModel.GetAttr'
        if col == 0:
            node = self.ItemToObject(item)
            if isinstance(node, TrackFormat):
                attr.SetColour('blue')
                return True
        return False

    def HasDefaultCompare(self):    
        #print 'CurvesModel.HasDefaultCompare'
        return True
        
        
    def Compare(self, item1, item2, col, ascending):
        # ascending does not matter here
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

        
        
        
###############################################################################


class TracksNotifier(dv.PyDataViewModelNotifier):                 
                    
    def __init__(self, logplotformat, model_to_callback):
        dv.PyDataViewModelNotifier.__init__(self)
        self.logplotformat = logplotformat
        if not isinstance(model_to_callback, CurvesModel):
            raise ValueError('Cannot notify this object. ')
        self.model_to_callback = model_to_callback
        self._owner = None
        
    def ItemAdded(self, parent, item):
        #print 'TracksNotifier.ItemAdded'
        tracks_model = self.GetOwner()  
        track = tracks_model.ItemToObject(item)
        item = self.model_to_callback.ObjectToItem(track)
        if item.IsOk():
            #print self.model_to_callback
            self.model_to_callback.ItemAdded(dv.NullDataViewItem, item)
        #else:
        #    print '\n\nNOT OK\n\n'
        #print 'TracksNotifier.ItemAdded: TRUE'    
        return True
        
    def ItemDeleted(*args, **kwargs):
       # print 'TracksNotifier.ItemDeleted'
        tracks_model = args[0].GetOwner()            
        track = tracks_model.ItemToObject(args[2])
        item = args[0].model_to_callback.ObjectToItem(track)
        args[0].model_to_callback.ItemDeleted(dv.NullDataViewItem, item)
        return True
        
    def SetOwner(self, owner):
        self._owner = owner

    def GetOwner(self):
        return self._owner
  
       
###############################################################################



class CurvesNotifier(dv.PyDataViewModelNotifier):
                    
    def __init__(self, logplotformat, model_to_callback):
        dv.PyDataViewModelNotifier.__init__(self)
        self.logplotformat = logplotformat
        if not isinstance(model_to_callback, TracksModel):
            raise ValueError('Cannot notify this object. ')
        self.model_to_callback = model_to_callback
        self._owner = None
        
    def ItemAdded(self, parent, item):
        #print 'CurvesNotifier.ItemAdded'
        curves_model = self.GetOwner() 
        #print curves_model
        obj = curves_model.ItemToObject(item)
        #print '1'
        if isinstance(obj, TrackFormat):
            #print '2'
            if self.model_to_callback.logplotformat is not None:
                #print '3'
                if obj not in self.model_to_callback.logplotformat.get_tracks():
                    #print 'ENTROU'
                    self.model_to_callback.InsertTrack(obj)
                else:
                    #print 'retornou FALSO'
                    return False
        # if it is a curve there no need to notify   
        #print '4'            
        return True
        
    def ItemDeleted(self, parent, item):
        #print 'CurvesNotifier.ItemDeleted'
        curves_model = self.GetOwner()            
        obj = curves_model.ItemToObject(item)
        if isinstance(obj, TrackFormat):   
            self.model_to_callback.DeleteTrack(obj)
        return True  
        

    def ItemChanged(self, item):
        """
        ItemChanged(self, DataViewItem item) -> bool

        Override this to be informed that an item's value has changed.
        """
        #print 'CurvesNotifier.ItemChanged'
        tracks_model = self.GetOwner()
        obj = tracks_model.ItemToObject(item)
        #print obj.get_id()
        
        #super(ModelNotifier, args[0]).ItemChanged(*args, **kwargs)
        #if isinstance(args[0].model_to_callback, CurvesModel):
            #tracks_model = args[0].GetOwner()  
            #track = tracks_model.ItemToObject(args[2])
            #item = args[0].model_to_callback.ObjectToItem(track)
            #args[0].model_to_callback.ItemChanged(args[1])
                
        
        #for col in range(tracks_model.GetColumnCount()):
        #    tracks_model.ValueChanged(args[1], col)
        return True
        #return dv.PyDataViewModelNotifier.ItemChanged(*args, **kwargs)

    '''
    def ValueChanged(self, item, col):
        print 'CurvesNotifier.ValueChanged'
        return True
    '''
    
    def SetOwner(self, owner):
        self._owner = owner

    def GetOwner(self):
        return self._owner
        
        

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
        kwargs['choices'] = self.colors.keys()
        OwnerDrawnComboBox.__init__(self, *args, **kwargs)

    def OnDrawItem(self, dc, rect, item, flags):
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
            color = wx.NamedColour(color_name)
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(r.x, r.y, tam, tam)
        dc.DrawText(self.GetString(item), r.x + tam + 2, r.y)            
        
        
    def OnMeasureItem(self, item):
        return 15

    @staticmethod
    def get_colors():
        return ColorSelectorComboBox.colors.keys()






'''
class ComboCellEditor(wx.grid.PyGridCellEditor):
    
    def __init__(self):
        dv.PyDataViewCustomRenderer.__init__(self)

    def Create(self, parent, id, evtHandler):
        self._tc = ColorSelectorComboBox(parent, style=wx.CB_READONLY)
        self.SetControl(self._tc)
        if evtHandler:
            self._tc.PushEventHandler(evtHandler)

    def SetSize(self, rect):
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)

    def BeginEdit(self, row, col, grid):
        self.startValue = grid.GetTable().GetValue(row, col)
        self._tc.SetFocus()        
        if self.startValue:
            self._tc.SetStringSelection(self.startValue)

    def EndEdit(self, row, col, grid, oldVal):
        val = self._tc.GetValue()
        if val != oldVal:  
            return val
        else:
            return None
        
    def ApplyEdit(self, row, col, grid):
        val = self._tc.GetValue()
        grid.GetTable().SetValue(row, col, val)
        self._tc.SetSelection(wx.NOT_FOUND)
        
    def Reset(self):
        self._tc.SetSelection(wx.NOT_FOUND)   
        
        
'''

####################################################################

'''

class ColorRenderer(dv.PyDataViewCustomRenderer):
    
    def __init__(self):#, model):
        print 'ColorRenderer.__init__'
        #colors = ColorSelectorComboBox.get_colors()
        #print colors
        #dv.DataViewChoiceRenderer.__init__(self, colors, mode=dv.DATAVIEW_CELL_EDITABLE)
        #super(ColorRenderer, self).__init__(colors, mode=dv.DATAVIEW_CELL_EDITABLE)
        #self.model = model
        dv.PyDataViewCustomRenderer.__init__(self, mode=dv.DATAVIEW_CELL_EDITABLE)
        #self.value = 'Black'

'''

'''
class LogRenderer(dv.PyDataViewCustomRenderer):
    def __init__(self, welluid):
        print 'ColorRenderer.__init__'
        dv.PyDataViewCustomRenderer.__init__(self, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.welluid = welluid
        self._OM = ObjectManager(self)
        self._value = None    
        self.curves = {}
        for log in self._OM.list('log', self.welluid):
            self.curves[log.name] = log.uid           
        
    def SetValue(self, value):
        print 'SetValue'
        self._value = value
        return True
      
    def GetValue(self):
        print 'GetValue'
        return  self._value 
        
    def GetSize(self):
        print 'GetSize'
        return wx.Size(70, 20)
        
    def Render(self, rect, dc, state):
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True

    def HasEditorCtrl(self):  
        return True      

    def CreateEditorCtrl(self, parent, rect, value):    
        print 'CreateEditorCtrl'
        for log in self._OM.list('log', self.welluid):
            self.curves[log.name] = log.uid           
        #logs = self._OM.list('log', self.welluid)
        #print logs
        self._editor = wx.Choice(parent, choices=self.curves.keys())
        self._editor.SetRect(rect)
        print 'value: ', value
        if value is None:
            self._editor.SetSelection(0)
        return self._editor

    def GetValueFromEditorCtrl(self, editor):
        print 'GetValueFromEditorCtrl'
        self._value = editor.GetValue()
        return self._value
        
'''


'''
class ColorRenderer(dv.PyDataViewCustomRenderer):
    
    def __init__(self, model):
        print 'ColorRenderer.__init__'
        dv.PyDataViewCustomRenderer.__init__(self, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.model = model
        self._value = None
    
    def Validate(self, value):
        """Validate(self, wxVariant value) -> bool"""
        print '\nColorRenderer.Validate: '
        value = self._value
        return True 
    
    def SetValue(self, value):
        print '\nColorRenderer.SetValue: ', value   
        self._value = value
        return True
      
    def GetValue(self):
        print '\nColorRenderer.GetValue: ', self._value 
        return True
        
    def GetSize(self):
        #print 'ColorRenderer.GetSize'
        return wx.Size(70, 20)
        
    def Render(self, rect, dc, state):
        """
        Render(self, Rect cell, DC dc, int state) -> bool

        Override this to render the cell. Before this is called, `SetValue`
        was called so that this instance knows what to render.  This must be
        overridden in derived classes.
        """
        print 'ColorRenderer.Render: state: {}  rect: {}'.format(state, rect)
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True

    def HasEditorCtrl(self):
        """HasEditorCtrl(self) -> bool"""
        print '\nColorRenderer.HasEditorCtrl'   
        return False
    
    def CreateEditorCtrl(self, parent, rect, value):
        """CreateEditorCtrl(self, Window parent, Rect labelRect, wxVariant value) -> Window"""
        print '\nColorRenderer.CreateEditorCtrl: starting value: {}'.format(value)
        print self.model
        #self.model.teste()
        
        #self._editor = ColorSelectorComboBox(parent, pos=rect.GetTopLeft(), 
        #                                 size=wx.Size(rect.GetWidth(), -1))
                                         
        #self._editor.Move((rect.GetRight() - self._editor.GetSize().GetWidth(), wx.DefaultCoord))
        #self._editor.SetStringSelection(value)                                 
        #self._editor.SetFocus()
        
        self._editor = ColorSelectorComboBox(parent, style=wx.CB_READONLY, size=wx.DefaultSize)
        self._editor.SetRect(rect)
        self._editor.SetValue(value)
        
        return self._editor


    def GetValueFromEditorCtrl(self, editor):
        """GetValueFromEditorCtrl(self, Window editor) -> wxVariant"""
        self._value = editor.GetValue()
        #self._tc.SetSelection(wx.NOT_FOUND)
        print 'ColorRenderer.GetValueFromEditorCtrl: ', self._value
        return self._value
        

    def StartEditing(self, item, rect):
        """StartEditing(self, DataViewItem item, Rect labelRect) -> bool"""
        print '\nColorRenderer.StartEditing '
        #obj = self.model.ItemToObject(item)
        
        #print obj
        self._item = item
        bol = super(ColorRenderer, self).StartEditing(item, rect)
        print 'bol: ', bol
        return bol
        #col = self.GetOwner().GetModelColumn()
        #value = self.model.GetValue(item, col)
        #dvc = self.GetOwner().GetOwner()
        #dvc.GetMainWindowOfCompositeControl() 
        #self._editor = self.CreateEditorCtrl(dvc , rect, value)
        #if not self._editor:
        #    return False
        #self._editor.SetFocus()
        #return True
    
    
    def FinishEditing(self):
        """FinishEditing(self) -> bool"""
        print '\nColorRenderer.FinishEditing '
        bol = super(ColorRenderer, self).FinishEditing()
        print 'bol: ', bol
        return bol
      
      

        self.GetValueFromEditorCtrl(self._editor) 
        print 'ColorRenderer.FinishEditing: ', self._value
        col = self.GetOwner().GetModelColumn()
        
        if not self._editor:
            return True
        wx.CallAfter(self.CancelEditing)    
        #value = self.GetValueFromEditorCtrl(self._editor)
        
        #dvc = self.GetOwner().GetOwner()
        #dvc.GetMainWindow().SetFocus()
        #isValid = self.Validate(value)
        #self.CancelEditing()        
        #handler = self._editor.PopEventHandler()
        #self._editor.Hide()
        #handler.Add
        dv.DataViewR
        self.DestroyEditor()

        #wx.CallAfter(del handler)
        #wx.CallAfter(self._editor.Destro
        #self._editor.Release()
        
        #if isValid:
        self.model.ChangeValue(self._value, self._item, col);
        #self.CancelEditing() 
        return True
        #return False
        
        
    def DestroyEditor(self):
        handler = self._editor.PopEventHandler()
        self._editor.Hide()
        #wxPendingDelete.Append(handler);
        #wxPendingDelete.Append(m_editorCtrl);
        # Ensure that DestroyEditControl() is not called again for this control.
        self._editor.Release()
        
        



    def PrepareForItem(self, model, item, col):
        """PrepareForItem(self, DataViewModel model, DataViewItem item, unsigned int column)"""
        print '\n\nColorRenderer.PrepareForItem'
        print 'model: ', model
        print 'item: ', item
        print 'column: ', col
        print
        
    
    def StartEditing(self, item, labelRect):
        """StartEditing(self, DataViewItem item, Rect labelRect) -> bool"""
        print 'ColorRenderer.StartEditing'
        print 'item: ', item
        print 'rect: ', labelRect
        if self._value:
            self._tc.SetStringSelection(self._value)
        return True
      
      

    def CancelEditing(self):
        """CancelEditing(self)"""
        print 'ColorRenderer.CancelEditing'
        #return _dataview.DataViewRenderer_CancelEditing(*args, **kwargs)

    
    
    def SetValue(self, value):
        """SetValue(self, wxVariant value) -> bool"""
        print 'ColorRenderer.SetValue: ', value   
        self._value = value
        return True
      
      
    def GetValue(self):
        """GetValue(self) -> wxVariant"""
        print '\nColorRenderer.GetValue: ', self._value 
        return self._value
        

    def GetSize(self):
        #print 'ColorRenderer.GetSize'
        return wx.Size(70, 20)
        
        
    def Render(self, rect, dc, state):
        """
        Render(self, Rect cell, DC dc, int state) -> bool

        Override this to render the cell. Before this is called, `SetValue`
        was called so that this instance knows what to render.  This must be
        overridden in derived classes.
        """
        print 'ColorRenderer.Render'
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True


    def GetEditorCtrl(self):
        """GetEditorCtrl(self) -> Window"""
        print '\nColorRenderer.GetEditorCtrl'
        return self._tc 
           

    # NO NEED TO OVERRIDE
    def RenderText(*args, **kwargs):
        """
        RenderText(self, String text, int xoffset, Rect cell, DC dc, int state)

        This method should be called from within your `Render` override
        whenever you need to render simple text. This will help ensure that the
        correct colour, font and vertical alignment will be chosen so the text
        will look the same as text drawn by native renderers.
        """
        print 'ColorRenderer.RenderText'
        #return _dataview.PyDataViewCustomRenderer_RenderText(*args, **kwargs)
            
        


    def GetVariantType(*args, **kwargs):
        """GetVariantType(self) -> String"""
        print 'ColorRenderer.GetVariantType'
        #return _dataview.DataViewRenderer_GetVariantType(*args, **kwargs)

    def PrepareForItem(*args, **kwargs):
        """PrepareForItem(self, DataViewModel model, DataViewItem item, unsigned int column)"""
        print 'ColorRenderer.PrepareForItem'
        #return _dataview.DataViewRenderer_PrepareForItem(*args, **kwargs)

    def SetMode(*args, **kwargs):
        """SetMode(self, int mode)"""
        print 'ColorRenderer.SetMode'
        #return _dataview.DataViewRenderer_SetMode(*args, **kwargs)

    def GetMode(*args, **kwargs):
        """GetMode(self) -> int"""
        print 'ColorRenderer.GetMode'
        #return _dataview.DataViewRenderer_GetMode(*args, **kwargs)
      
#####
  
  
        
    def HasEditorCtrl(*args, **kwargs):
        """HasEditorCtrl(self) -> bool"""
        print '\nColorRenderer.HasEditorCtrl'
        return True


    def CreateEditorCtrl(*args, **kwargs):
        """CreateEditorCtrl(self, Window parent, Rect labelRect, wxVariant value) -> Window"""
        print '\nColorRenderer.CreateEditorCtrl'
        print 'rect: ', args[2]
        print 'value: ', args[3]
        print
        args[0]._tc = ColorSelectorComboBox(args[1], style=wx.CB_READONLY)
        args[0]._tc.SetRect(args[2])
        return args[0]._tc 
        #return _dataview.DataViewRenderer_CreateEditorCtrl(*args, **kwargs)


    
    def SetValue(*args, **kwargs):
        """SetValue(self, wxVariant value) -> bool"""
        print 'ColorRenderer.SetValue: ', args[1]        
        #return _dataview.DataViewRenderer_SetValue(*args, **kwargs)

    def GetValue(*args, **kwargs):
        """GetValue(self) -> wxVariant"""
        print 'ColorRenderer.GetValue'        
        #return _dataview.DataViewRenderer_GetValue(*args, **kwargs)


    def GetValueFromEditorCtrl(*args, **kwargs):
        """GetValueFromEditorCtrl(self, Window editor) -> wxVariant"""
        print 'ColorRenderer.GetValueFromEditorCtrl'
        #return _dataview.DataViewRenderer_GetValueFromEditorCtrl(*args, **kwargs)              
            
            
    def RenderText(*args, **kwargs):
        """
        RenderText(self, String text, int xoffset, Rect cell, DC dc, int state)

        This method should be called from within your `Render` override
        whenever you need to render simple text. This will help ensure that the
        correct colour, font and vertical alignment will be chosen so the text
        will look the same as text drawn by native renderers.
        """
        print 'ColorRenderer.RenderText'
        #return _dataview.PyDataViewCustomRenderer_RenderText(*args, **kwargs)
        

    
    def SetSize(self, rect):
        print 'ColorRenderer.SetSize'
        self._tc.SetDimensions(rect.x, rect.y, rect.width+2, rect.height+2,
                               wx.SIZE_ALLOW_MINUS_ONE)
                               
                             

    def GetSize(*args, **kwargs):
        """
        GetSize(self) -> Size

        Returns the size required to show content.  This must be overridden in
        derived classes.
        """
        print 'ColorRenderer.GetSize'
        return (20, 20)        
        #return _dataview.PyDataViewCustomRenderer_GetSize(*args, **kwargs)
    
    
    def Render(*args, **kwargs):
        """
        Render(self, Rect cell, DC dc, int state) -> bool

        Override this to render the cell. Before this is called, `SetValue`
        was called so that this instance knows what to render.  This must be
        overridden in derived classes.
        """
        print 'ColorRenderer.Render'
        print 'cell', args[1]
        print 'state: ', args[3]
        print
        return True
        #return _dataview.PyDataViewCustomRenderer_Render(*args, **kwargs)
        
 

     
    def Activate(*args, **kwargs):
        """
        Activate(self, Rect cell, DataViewModel model, DataViewItem item, 
            unsigned int col) -> bool

        Override this to react to double clicks or <ENTER>.
        """
        print 'ColorRenderer.Activate'
        #return _dataview.PyDataViewCustomRenderer_Activate(*args, **kwargs)


    def ActivateCell(*args, **kwargs):
        """
        Activate(self, Rect cell, DataViewModel model, DataViewItem item, 
            unsigned int col) -> bool

        Override this to react to double clicks or <ENTER>.
        """
        print 'ColorRenderer.ActivateCell'
        

    def LeftClick(*args, **kwargs):
        """
        LeftClick(self, Point cursor, Rect cell, DataViewModel model, DataViewItem item, 
            unsigned int col) -> bool

        Overrride this to react to a left click.
        """
        print '\n\n\nColorRenderer.LeftClick'
        #return _dataview.PyDataViewCustomRenderer_LeftClick(*args, **kwargs)
        
 
    def StartDrag(*args, **kwargs):
        """
        StartDrag(self, Point cursor, Rect cell, DataViewModel model, DataViewItem item, 
            unsigned int col) -> bool

        Overrride this to react to the start of a drag operation.
        """
        return _dataview.PyDataViewCustomRenderer_StartDrag(*args, **kwargs)

    def GetDC(*args, **kwargs):
        """GetDC(self) -> DC"""
        return _dataview.PyDataViewCustomRenderer_GetDC(*args, **kwargs)


    def GetTextExtent(*args, **kwargs):
        """GetTextExtent(self, String str) -> Size"""
        print '\nColorRenderer.GetTextExtent'
        #return _dataview.PyDataViewCustomRenderer_GetTextExtent(*args, **kwargs)


    def GetView(*args, **kwargs):
        """GetView(self) -> DataViewCtrl"""
        print '\nColorRenderer.GetView'
        #return _dataview.PyDataViewCustomRenderer_GetView(*args, **kwargs)

        
#########################################################################
    
    
    def PrepareForItem(*args, **kwargs):
        """PrepareForItem(self, DataViewModel model, DataViewItem item, unsigned int column)"""
        print 'ColorRenderer.PrepareForItem'
        print 'model: ', args[1]
        print 'item: ', args[2]
        print 'column: ', args[3]
        print
        #return _dataview.DataViewRenderer_PrepareForItem(*args, **kwargs)      
      
      
    def Validate(*args, **kwargs):
        """Validate(self, wxVariant value) -> bool"""
        print 'ColorRenderer.Validate'
        print 'value: ', args[1]
        #return _dataview.DataViewRenderer_Validate(*args, **kwargs)


    
    def StartEditing(*args, **kwargs):
        """StartEditing(self, DataViewItem item, Rect labelRect) -> bool"""
        print 'ColorRenderer.StartEditing'
        print 'item: ', 
        print 'rect: ', args[2]
        #def BeginEdit(self, row, col, grid):
        #dvc = args[0].GetView()#GetOwner().GetOwner().GetModel()
        #model = args[0].model
        col = args[0].GetOwner().GetModelColumn()
        print 'col: ', col
        print 'item id: ', args[1].GetID()
        #if isinstance(model, CurvesModel):
        #    print 'model: ', model
        #else:
        #    print 'NAO EH CURVESMODEL!'
        args[0].startValue = args[0].model.ItemToObject(args[1]) #grid.GetTable().GetValue(row, col)
        #args[0]._tc.SetFocus()        
        if args[0].startValue:
            args[0]._tc.SetStringSelection(args[0].startValue)
        return True
        #return _dataview.DataViewRenderer_StartEditing(*args, **kwargs)
    
    
    
    def CancelEditing(*args, **kwargs):
        """CancelEditing(self)"""
        print 'ColorRenderer.CancelEditing' 
        #return _dataview.DataViewRenderer_CancelEditing(*args, **kwargs)

    def FinishEditing(*args, **kwargs):
        """FinishEditing(self) -> bool"""
        print 'ColorRenderer.FinishEditing'
        return True
        #return _dataview.DataViewRenderer_FinishEditing(*args, **kwargs)

    def GetEditorCtrl(*args, **kwargs):
        """GetEditorCtrl(self) -> Window"""
        print 'ColorRenderer.GetEditorCtrl'
        return args[0]._tc 
        #return _dataview.DataViewRenderer_GetEditorCtrl(*args, **kwargs)   
        
      

    def SetOwner(*args, **kwargs):
        """SetOwner(self, DataViewColumn owner)"""
        return _dataview.DataViewRenderer_SetOwner(*args, **kwargs)

    def GetOwner(*args, **kwargs):
        """GetOwner(self) -> DataViewColumn"""
        return _dataview.DataViewRenderer_GetOwner(*args, **kwargs)

    def SetValue(*args, **kwargs):
        """SetValue(self, wxVariant value) -> bool"""
        return _dataview.DataViewRenderer_SetValue(*args, **kwargs)

    def GetValue(*args, **kwargs):
        """GetValue(self) -> wxVariant"""
        return _dataview.DataViewRenderer_GetValue(*args, **kwargs)

    def SetAttr(*args, **kwargs):
        """SetAttr(self, DataViewItemAttr attr)"""
        return _dataview.DataViewRenderer_SetAttr(*args, **kwargs)

    def SetEnabled(*args, **kwargs):
        """SetEnabled(self, bool enabled)"""
        return _dataview.DataViewRenderer_SetEnabled(*args, **kwargs)

    def GetVariantType(*args, **kwargs):
        """GetVariantType(self) -> String"""
        return _dataview.DataViewRenderer_GetVariantType(*args, **kwargs)


    def PrepareForItem(*args, **kwargs):
        """PrepareForItem(self, DataViewModel model, DataViewItem item, unsigned int column)"""
        return _dataview.DataViewRenderer_PrepareForItem(*args, **kwargs)


    def HasEditorCtrl(*args, **kwargs):
        """HasEditorCtrl(self) -> bool"""
        return _dataview.DataViewRenderer_HasEditorCtrl(*args, **kwargs)

    def CreateEditorCtrl(*args, **kwargs):
        """CreateEditorCtrl(self, Window parent, Rect labelRect, wxVariant value) -> Window"""
        return _dataview.DataViewRenderer_CreateEditorCtrl(*args, **kwargs)

    def GetValueFromEditorCtrl(*args, **kwargs):
        """GetValueFromEditorCtrl(self, Window editor) -> wxVariant"""
        return _dataview.DataViewRenderer_GetValueFromEditorCtrl(*args, **kwargs)
        
        

'''            