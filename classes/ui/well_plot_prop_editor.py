from collections import OrderedDict

import wx
from wx.adv import OwnerDrawnComboBox
import wx.dataview as dv
import wx.propgrid as pg
import wx.lib.colourdb

from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject
from classes.ui import UIViewObject
from classes.ui import TextChoiceRenderer
#
from classes.ui import TrackController
from classes.ui import TrackObjectController
#
from classes.ui import FrameController
from classes.ui import Frame
#
import app.pubsub as pub
from app import log


class WellPlotEditorController(FrameController):
    tid = 'well_plot_editor_controller'

    def __init__(self, **state):
        super().__init__(**state)
        state['title'] = 'Well Plot Editor'
        state['size'] = (950, 600)
        super().__init__(**state)

    def PostInit(self):
        UIM = UIManager()
        #
        UIM.create('lpe_wellplot_panel_controller', self.uid)
        UIM.create('lpe_track_panel_controller', self.uid)
        UIM.create('lpe_objects_panel_controller', self.uid)
        #
        UIM.subscribe(self.object_created, 'create')
        UIM.subscribe(self.object_removed, 'pre_remove')
        #
        wellplot_ctrl_uid = UIM._getparentuid(self.uid)
        for track in UIM.list('track_controller', wellplot_ctrl_uid):
            track.subscribe(self._on_change_prop, 'change')
            for toc in UIM.list('track_object_controller', track.uid):
                toc.subscribe(self._on_change_prop, 'change')

        wellplot_ctrl = UIM.get(wellplot_ctrl_uid)
        self.title += ': ' + wellplot_ctrl.title.split(':')[1].strip()

    def PreDelete(self):
        UIM = UIManager()
        #        UIM.unsubscribe(self.object_created, 'create')
        #        UIM.unsubscribe(self.object_removed, 'pre_remove')
        #
        wellplot_ctrl_uid = UIM._getparentuid(self.uid)
        for track in UIM.list('track_controller', wellplot_ctrl_uid):
            track.unsubscribe(self._on_change_prop, 'change')
            for toc in UIM.list('track_object_controller', track.uid):
                toc.unsubscribe(self._on_change_prop, 'change')
                #
        # TODO: verificar isso....
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
        wellplot_ctrl_uid = UIM._getparentuid(self.uid)
        if objuid[0] == 'track_controller' and parentuid == wellplot_ctrl_uid:
            track = UIM.get(objuid)
            # print 'LogPlotEditorController._object_created:', objuid, track.pos
            lpe_tp = UIM.list('lpe_track_panel_controller', self.uid)[0]
            lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
            lpe_tp.create_item(track)
            lpe_op.create_item(track)
            track.subscribe(self._on_change_prop, 'change')

        elif objuid[0] == 'track_object_controller':
            wellplot_candidate = UIM._getparentuid(parentuid)
            if wellplot_candidate == wellplot_ctrl_uid:
                lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
                track = UIM.get(parentuid)
                toc = UIM.get(objuid)
                lpe_op.create_item(toc, track)
                toc.subscribe(self._on_change_prop, 'change')

    def object_removed(self, objuid):
        print('object_removed', objuid)
        UIM = UIManager()
        if objuid[0] == 'track_controller':
            track_parent_uid = UIM._getparentuid(objuid)
            wellplot_ctrl_uid = UIM._getparentuid(self.uid)
            if track_parent_uid == wellplot_ctrl_uid:
                track = UIM.get(objuid)
                lpe_tp = UIM.list('lpe_track_panel_controller', self.uid)[0]
                lpe_op = UIM.list('lpe_objects_panel_controller', self.uid)[0]
                track.unsubscribe(self._on_change_prop, 'change')
                lpe_tp.remove_item(track)
                lpe_op.remove_item(track)
        elif objuid[0] == 'track_object_controller':
            print('object_removed:', objuid)
            track_uid = UIM._getparentuid(objuid)
            track_parent_uid = UIM._getparentuid(track_uid)
            wellplot_ctrl_uid = UIM._getparentuid(self.uid)
            if track_parent_uid == wellplot_ctrl_uid:
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
            # print '\n_on_change_prop:', self.oid, '-', topicObj.getName(), obj_uid
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
            # print '_on_change_prop:', self.oid, '-', topicObj.getName()
            # lpe_op.view.reload_propgrid(toc)

        # elif objuid[0] == 'track_object_controller':


class WellPlotEditor(Frame):
    tid = 'well_plot_editor'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)

        # self.status_bar = self.CreateStatusBar()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.base_panel = wx.Panel(self)
        self.note = wx.Notebook(self.base_panel)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.note, 1, wx.ALL | wx.EXPAND, border=5)
        self.base_panel.SetSizer(bsizer)

        main_sizer.Add(self.base_panel, 1, wx.EXPAND)
        bottom_panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_close = wx.Button(bottom_panel, -1, "Close")
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        bottom_panel.SetSizer(sizer)
        main_sizer.Add(bottom_panel, 0, wx.EXPAND)
        self.SetSizer(main_sizer)
        class_full_name = str(self.__class__.__module__) + '.' + str(self.__class__.__name__)
        log.debug('Successfully created View object from class: {}.'.format(class_full_name))
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        event.Skip()
        UIM = UIManager()
        wx.CallAfter(UIM.remove, self._controller_uid)
        self.Unbind(wx.EVT_CLOSE)

    def _get_wx_parent(self, *args, **kwargs):
        return self.note


class LPEWellPlotPanelController(UIControllerObject):
    tid = 'lpe_wellplot_panel_controller'

    def __init__(self):
        super(LPEWellPlotPanelController, self).__init__()


class LPEWellPlotPanel(UIViewObject, wx.Panel):
    tid = 'lpe_wellplot_panel'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wx.Panel.__init__(self,
                          wpe_ctrl._get_wx_parent(),
                          -1,
                          style=wx.SIMPLE_BORDER
                          )

    def PostInit(self):
        self.base_panel = wx.Panel(self)
        base_sizer = wx.BoxSizer(wx.VERTICAL)
        #
        UIM = UIManager()
        pgc = UIM.create('property_grid_controller', self._controller_uid)
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wp_ctrl_uid = UIM._getparentuid(wpe_ctrl_uid)
        pgc.obj_uid = wp_ctrl_uid
        base_sizer.Add(pgc.view, 1, wx.EXPAND)
        self.base_panel.SetSizer(base_sizer)
        #
        sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_grid_panel.Add(self.base_panel, 1, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(sizer_grid_panel)
        #
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wpe_ctrl._get_wx_parent().AddPage(self, "WellPlot", True)

    def _get_wx_parent(self, *args, **kwargs):
        return self.base_panel


class LPETrackPanelController(UIControllerObject):
    tid = 'lpe_track_panel_controller'

    def __init__(self):
        super(LPETrackPanelController, self).__init__()
        # LPETrackPanelModel is not a UIModelObject object
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
        7: 'xscale',
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
        # print '\nGetChildren'
        UIM = UIManager()
        # controller = UIM.get(self._controller_uid)
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        tracks = UIM.list('track_controller', wellplot_ctrl_uid)
        for track in tracks:
            children.append(self.ObjectToItem(track))
        return len(tracks)

    def GetValue(self, item, col):
        track = self.ItemToObject(item)

        UIM = UIManager()
        tcc = UIM.list('track_canvas_controller', track.uid)[0]

        if col == 0:
            return track.pos + 1
        elif col == 5:
            value = tcc[self.TRACKS_MODEL_MAPPING.get(col)]
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
            value = tcc[self.TRACKS_MODEL_MAPPING.get(col)]
            if value == 'linear':
                return 'Linear'
            elif value == 'log':
                return 'Logarithmic'
            raise Exception('Error.', value)

        if col in [0, 1, 2, 3, 11]:
            return track[self.TRACKS_MODEL_MAPPING.get(col)]
        else:
            return tcc[self.TRACKS_MODEL_MAPPING.get(col)]

    def SetValue(self, value, item, col):
        track = self.ItemToObject(item)
        UIM = UIManager()
        tcc = UIM.list('track_canvas_controller', track.uid)[0]
        # print 'SetValue', track.uid, col, value
        if col == 5:
            if value == 'All':
                tcc.depth_lines = 0
            elif value == 'Left':
                tcc.depth_lines = 1
            elif value == 'Right':
                tcc.depth_lines = 2
            elif value == 'Center':
                tcc.depth_lines = 3
            elif value == 'Left & Right':
                tcc.depth_lines = 4
            elif value == 'None':
                tcc.depth_lines = 5
            else:
                raise Exception('Error.')
        elif col == 7:
            if value == 'Linear':
                tcc.x_scale = 'linear'
            elif value == 'Logarithmic':
                tcc.x_scale = 'log'
            else:
                raise Exception('Error.', value)
        elif col == 11:
            UIM = UIManager()
            wellplot_uid = UIM._getparentuid(track.uid)
            wellplot_ctrl = UIM.get(wellplot_uid)
            if value:
                wellplot_ctrl.set_overview_track(track.uid)
            else:
                wellplot_ctrl.unset_overview_track()

        elif col in [0, 1, 2, 3, 11]:
            track[self.TRACKS_MODEL_MAPPING.get(col)] = value
        else:
            tcc[self.TRACKS_MODEL_MAPPING.get(col)] = value

        return True

    # def ChangedItem(self, item):
    # print 'ChangedItem'
    # obj = self.ItemToObject(item)
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

        if track1.pos == track2.pos:
            raise Exception('Two tracks cannot have same position: {} - {}.'.format(track1.uid, track2.uid))

        if ascending:
            if track1.pos > track2.pos:
                return 1
            else:
                return -1
        else:
            if track1.pos > track2.pos:
                return -1
            else:
                return 1

    def IsEnabled(self, item, col):
        return True

    '''
    def InsertTracks(self):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        well_plot_ctrl = UIM.get(wellplot_ctrl_uid)
        new_tracks_uid = well_plot_ctrl.insert_track()
        for uid in new_tracks_uid:
            new_track = UIM.get(uid)
            item = self.ObjectToItem(new_track)
            self.ItemAdded(dv.NullDataViewItem, item)
        return True
    '''


class LPETrackPanel(UIViewObject, wx.Panel):
    tid = 'lpe_track_panel'

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wx.Panel.__init__(self,
                          wpe_ctrl._get_wx_parent(),
                          -1,
                          style=wx.SIMPLE_BORDER
                          )

    def PostInit(self):
        self.base_panel = wx.Panel(self)
        self.dvc = self.create_data_view_ctrl()
        #
        base_sizer = wx.BoxSizer(wx.VERTICAL)
        base_sizer.Add(self.dvc, 1, wx.EXPAND)
        button_add_track = wx.Button(self.base_panel, label="Add track")
        self.Bind(wx.EVT_BUTTON, self.OnInsertTrack, button_add_track)
        button_delete_track = wx.Button(self.base_panel, label="Delete track(s)")
        self.Bind(wx.EVT_BUTTON, self.OnDeleteSelectedTracks, button_delete_track)
        button_select_all = wx.Button(self.base_panel, label="Select All")
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, button_select_all)
        button_select_none = wx.Button(self.base_panel, label="Select None")
        self.Bind(wx.EVT_BUTTON, self.OnSelectNone, button_select_none)
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT | wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT | wx.RIGHT, 5)
        btnbox.Add(button_select_all, 0, wx.LEFT | wx.RIGHT, 5)
        btnbox.Add(button_select_none, 0, wx.LEFT | wx.RIGHT, 5)
        base_sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)
        self.base_panel.SetSizer(base_sizer)
        #
        self.dvc.EnableDragSource(VarNodeDropData.GetFormat())
        self.dvc.EnableDropTarget(VarNodeDropData.GetFormat())
        #
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_BEGIN_DRAG, self.OnItemBeginDrag)
        self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_DROP_POSSIBLE, self.OnItemDropPossible)
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnSelectionChanged)
        ###
        sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        sizer_grid_panel.Add(self.base_panel, 1, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(sizer_grid_panel)
        #
        UIM = UIManager()
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wpe_ctrl._get_wx_parent().AddPage(self, "Tracks", True)

    def create_data_view_ctrl(self):
        dvc = dv.DataViewCtrl(self.base_panel, style=wx.BORDER_THEME | \
                                                     dv.DV_VERT_RULES | dv.DV_MULTIPLE | dv.DV_ROW_LINES
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
        dv_col = dvc.AppendToggleColumn("Visible", 3, width=50, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        dv_col.SetMinWidth(50)
        # Plot Grid
        dvc.AppendToggleColumn("Plot Grid", 4, width=60, mode=dv.DATAVIEW_CELL_ACTIVATABLE)
        # Depth Lines
        dvcr = dv.DataViewChoiceRenderer(['All', 'Left', 'Right', 'Center', 'Left & Right', 'None'],
                                         mode=dv.DATAVIEW_CELL_EDITABLE
                                         )
        dvcol = dv.DataViewColumn("Depth Lines", dvcr, 5, width=85)
        dvc.AppendColumn(dvcol)
        # Scale Lines
        dv_col = dvc.AppendTextColumn("Scale Lines", 6, width=70, mode=dv.DATAVIEW_CELL_EDITABLE)
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

        # TODO: wtf this armengue?
        model = controller._get_real_model()
        #
        obj = model.ItemToObject(item)
        self.node = VarNodeDropData()

        print('\n\n\nOnItemBeginDrag obj:', obj, type(obj), model)

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
        self.dvc.UnselectAll()  # Change Selection

        if new_pos_item.IsOk() and \
                event.GetDataFormat() == VarNodeDropData.GetFormat():
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            model = controller._get_real_model()
            self.dvc.Select(new_pos_item)
            new_pos_track = model.ItemToObject(new_pos_item)

            print('old_pos_track:', old_pos_track, old_pos_track.pos)
            print('new_pos_track:', new_pos_track, new_pos_track.pos)

            #            new_pos_track.pos = old_pos_track.pos
            try:
                old_pos_track.pos = new_pos_track.pos
            except Exception as e:
                print('DEU RUIM! ', e)
                raise
            print('FOI\n\n')

            # model.ItemChanged(new_pos_item)
            # model.ItemChanged(old_pos_item)
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
        # self._DoSelectionChanged()

    def _DoSelectionChanged(self):
        items = self.dvc.GetSelections()
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        tracks = UIM.list('track_controller', wellplot_ctrl_uid)
        tracks_selected = [model.ItemToObject(item) for item in items]
        for track in tracks:
            track.selected = track in tracks_selected

    def OnInsertTrack(self, event):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        well_plot_ctrl = UIM.get(wellplot_ctrl_uid)
        well_plot_ctrl.insert_track()

    def OnDeleteSelectedTracks(self, event):
        UIM = UIManager()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        well_plot_ctrl = UIM.get(wellplot_ctrl_uid)
        well_plot_ctrl.remove_selected_tracks()


###############################################################################

"""
From tree.py
============

def DoDragDrop():
    data_obj = wx.CustomDataObject('obj_uid')
    data_obj.SetData(str.encode(str(node_main_info)))
    drag_source = wx.DropSource(self)
    drag_source.SetData(data_obj)  
    drag_source.DoDragDrop()


From app_utils.py
=================

class DropTarget(wx.DropTarget):
    
    def __init__(self, _test_func, callback=None):
        wx.DropTarget.__init__(self)
        self.data = wx.CustomDataObject('obj_uid')
        self.SetDataObject(self.data)
        self._test_func = _test_func
        self._callback = callback
        
    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, defResult):
        obj_uid = self._get_object_uid()
        if self._callback:
            wx.CallAfter(self._callback, obj_uid)
        return defResult   
    
    def OnDragOver(self, x, y, defResult):    
        obj_uid = self._get_object_uid()
        if obj_uid:
            if self._test_func(obj_uid):
                return defResult   
        return wx.DragNone

    def _get_object_uid(self):
        if self.GetData(): 
            obj_uid_bytes = self.data.GetData().tobytes()   
            obj_uid_str = obj_uid_bytes.decode()
            if obj_uid_str:
                obj_uid = parse_string_to_uid(obj_uid_str)
                return obj_uid
        return None    
        
"""


class VarNodeDropData(wx.CustomDataObject):
    NAME = "VarNode"
    PICKLE_PROTOCOL = 2

    def __init__(self):
        super().__init__(VarNodeDropData.GetFormat())

    def SetObject(self, obj):
        self.SetData(str.encode(str(obj.uid)))

    def GetObject(self):
        obj_uid_bytes = self.GetData().tobytes()
        obj_uid_str = obj_uid_bytes.decode()
        #        print('\n\n\nGetObject:', obj_uid_str, type(obj_uid_str))

        UIM = UIManager()
        return UIM.get(obj_uid_str)

    @staticmethod
    def GetFormat():
        return wx.DataFormat(VarNodeDropData.NAME)


###############################################################################
###############################################################################


class LPEObjectsPanelController(UIControllerObject):
    tid = 'lpe_objects_panel_controller'

    def __init__(self):
        super(LPEObjectsPanelController, self).__init__()
        # LPEObjectsPanelModel is not a UIModelObject object
        self._real_model = LPEObjectsPanelModel(self.uid)

    def PostInit(self):
        self.view.dvc.AssociateModel(self._real_model)
        self.expand_dvc_all_items()

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
            wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
            tracks = UIM.list('track_controller', wellplot_ctrl_uid)
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
        # print '\nIsContainer'
        if not item:
            #    print 'not item - True'
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackController):
            #    print obj.uid, '- TrackController - True'
            return True
        # print obj.uid, '- not TrackController - False'
        return False

    def GetParent(self, item):
        # print '\nGetParent:'
        if not item:
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)
        # print obj.uid
        if isinstance(obj, TrackController):
            return dv.NullDataViewItem
        elif isinstance(obj, TrackObjectController):
            UIM = UIManager()
            track_uid = UIM._getparentuid(obj.uid)
            track_ctrl = UIM.get(track_uid)
            item = self.ObjectToItem(track_ctrl)
            return item

    def GetValue(self, item, col):
        try:
            obj = self.ItemToObject(item)

            if isinstance(obj, TrackController):
                if col == 0:
                    if obj.label:
                        return obj.label
                    return 'Track ' + str(obj.pos + 1)
                return wx.EmptyString

            elif isinstance(obj, TrackObjectController):
                if col == 0:
                    return wx.EmptyString
                elif col == 1:
                    try:
                        if obj.data_obj_uid:
                            ret = ObjectManager.get_tid_friendly_name(obj.data_obj_uid[0])
                            if ret:
                                return ret
                            return wx.EmptyString
                        else:
                            return 'Select...'
                    except AttributeError:
                        print('\nERRO! O objeto nao possui model: ' + str(obj.uid) + '\n')
                        return ''

                elif col == 2:
                    return obj.get_data_name()

            else:
                raise RuntimeError("unknown node type")

        except Exception  as  e:
            print('\nGetValue: ERROR:', e)
            raise

    def SetValue(self, value, item, col):
        obj = self.ItemToObject(item)
        if isinstance(obj, TrackController):
            raise Exception()

            # TODO: rever isso, pois esta horrivel
        if isinstance(obj, TrackObjectController):
            UIM = UIManager()
            ctrl = UIM.get(self._controller_uid)
            if col == 1 or col == 2:
                print('SetValue:', col, value)
                pgcs = UIM.list('property_grid_controller',
                                self._controller_uid)
                if pgcs:
                    pgc = pgcs[0]
                    ctrl.view.splitter.Unsplit(pgc.view)
                    UIM.remove(pgc.uid)
            if col == 1:
                obj.obj_tid = value
            if col == 2:
                if isinstance(value, tuple):
                    print('aqui')
                    obj.obj_oid = value[1]
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
        # print 'Compare:', obj1.uid, obj2.uid
        if obj1.tid == 'track_controller' and obj2.tid == 'track_controller' \
                or obj1.tid == 'track_object_controller' and \
                obj2.tid == 'track_object_controller':
            if obj1.pos == obj2.pos:
                raise Exception('Two tracks cannot have same position.')
            if ascending:
                if obj1.pos > obj2.pos:
                    return 1
                else:
                    return -1
            else:
                if obj1.pos > obj2.pos:
                    return -1
                else:
                    return 1
                    # print 'Compare:', obj1, obj2
        # TODO: Falta

    def ChangeValue(self, value, item, col):
        """ChangeValue(self, wxVariant variant, DataViewItem item, unsigned int col) -> bool"""
        print('CurvesModel.ChangeValue: ', col, value)
        return super().ChangeValue(value, item, col)
        if item is None:
            print('item is None')
            return False
        return False

    ###############################################################################


class LPEObjectsPanel(UIViewObject, wx.Panel):
    tid = 'lpe_objects_panel'
    DEPTH_LINES_CHOICE = ['Full', 'Left', 'Right', 'Center', 'Left & Right', 'None']

    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wx.Panel.__init__(self,
                          wpe_ctrl._get_wx_parent(),
                          -1,
                          style=wx.SIMPLE_BORDER
                          )
        self.splitter = None
        self.dvc = None
        self.Sizer = None

    def PostInit(self):
        self.splitter = wx.SplitterWindow(self, -1)
        self.dvc = self.create_data_view_ctrl()

        self.splitter.Initialize(self.dvc)
        self.splitter.SetSashPosition(400)

        self.splitter.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self._OnSplitterDclick)

        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, border=10)

        button_add_track = wx.Button(self, label="Add Object")
        self.Bind(wx.EVT_BUTTON, self.on_add_track_object, button_add_track)
        button_delete_track = wx.Button(self, label="Delete Object")
        self.Bind(wx.EVT_BUTTON, self.on_delete_track_object,
                  button_delete_track
                  )
        btnbox = wx.BoxSizer(wx.HORIZONTAL)
        btnbox.Add(button_add_track, 0, wx.LEFT | wx.RIGHT, 5)
        btnbox.Add(button_delete_track, 0, wx.LEFT | wx.RIGHT, 5)

        self.Sizer.Add(btnbox, 0, wx.TOP | wx.BOTTOM, 5)

        """
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        lpe_ctrl_uid = UIM._getparentuid(self._controller_uid) 
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        all_tracks = UIM.list('track_controller', wellplot_ctrl_uid)
        
        for track in all_tracks:     
            print 'expanding:', track.uid
            item = model.ObjectToItem(track)
            print item
            self.dvc.Expand(item)
            print self.dvc.IsExpanded(item)
            #model.Resort()
            #print self.dvc.IsExpanded(item)
        """
        # self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_START_EDITING, self.OnItemStartEditing)
        # self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_STARTED, self.OnItemEditingStart)
        # self.dvc.Bind(dv.EVT_DATAVIEW_ITEM_EDITING_DONE, self.OnItemEditingDone)
        self.dvc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.OnSelectionChanged)

        ###
        # sizer_grid_panel = wx.BoxSizer(wx.VERTICAL)
        # sizer_grid_panel.Add(self.splitter, 1, wx.EXPAND|wx.ALL, border=10)
        self.SetSizer(self.Sizer)
        #
        UIM = UIManager()
        wpe_ctrl_uid = UIM._getparentuid(self._controller_uid)
        wpe_ctrl = UIM.get(wpe_ctrl_uid)
        wpe_ctrl._get_wx_parent().AddPage(self, "Objects", True)

        # self.dvc.Bind(wx.EVT_IDLE, self._dvc_idle)

    # def _dvc_idle(self, event):
    #    print 'DVC IDLE'

    def create_data_view_ctrl(self):
        dvc = dv.DataViewCtrl(self.splitter, style=dv.DV_ROW_LINES |
                                                   dv.DV_VERT_RULES | dv.DV_MULTIPLE
                              )
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()

        # Track
        dv_col = dvc.AppendTextColumn("Track", 0, width=85)
        dv_col.SetMinWidth(55)

        # Object Type 
        dvcr_object_tid = ObjectTidRenderer()
        dv_col = dv.DataViewColumn("Object Type", dvcr_object_tid, 1, width=85)
        dv_col.SetMinWidth(85)
        dvc.AppendColumn(dv_col)

        # Object Name 
        dvcr_curve_name = ObjectNameRenderer()
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
        wellplot_ctrl_uid = UIM._getparentuid(lpe_ctrl_uid)
        all_tracks = UIM.list('track_controller', wellplot_ctrl_uid)

        for track in all_tracks:
            # print 'expanding:', track.uid
            item = model.ObjectToItem(track)
            # print item
            self.dvc.Expand(item)
        # print self.dvc.IsExpanded(item)
        # model.Resort()
        # print self.dvc.IsExpanded(item)

    def OnSelectionChanged(self, event):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        model = controller._get_real_model()
        items = self.dvc.GetSelections()
        selected_objs = [model.ItemToObject(item) for item in items]
        selected_toc_objs = [obj for obj in selected_objs if isinstance(obj,
                                                                        TrackObjectController)
                             ]
        #
        pg_shown = False
        #
        print('\n\ntoc_objs:', selected_toc_objs)
        #
        pgcs = UIM.list('property_grid_controller', self._controller_uid)
        #
        if pgcs:
            pgc = pgcs[0]
            if self.splitter.IsSplit():
                self.splitter.Unsplit(pgc.view)
            UIM.remove(pgc.uid)

        if selected_toc_objs:
            selected_toc_obj = selected_toc_objs[-1]
            if selected_toc_obj.is_valid():
                #
                print('CRIANDO property_grid_controller PARA:',
                      self._controller_uid)
                # print
                pgc = UIM.create('property_grid_controller',
                                 self._controller_uid
                                 )

                if not self.splitter.IsSplit():
                    self.splitter.SplitVertically(self.dvc, pgc.view)

                # Setting object uid to Property Grid
                pgc.obj_uid = selected_toc_obj.get_representation().uid
                #                

    #                self.Refresh()
    #                self.Layout()
    #

    def on_add_track_object(self, event):
        tracks, track_objs = self._get_objects_selected()
        UIM = UIManager()
        for track in tracks:
            UIM.create('track_object_controller', track.uid)
        for track_obj in track_objs:
            UIM = UIManager()
            track_uid = UIM._getparentuid(track_obj.uid)
            track = UIM.get(track_uid)
            UIM.create('track_object_controller', track.uid)

    def on_delete_track_object(self, event):
        _, track_objs = self._get_objects_selected()
        UIM = UIManager()
        for track_obj in track_objs:
            UIM.remove(track_obj.uid)

    def _OnSplitterDclick(self, event):
        print('_OnSplitterDclick:', event)

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

    def _get_wx_parent(self, *args, **kwargs):
        return self.splitter


###############################################################################        
###############################################################################


class ObjectTidRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):
        OM = ObjectManager()
        acceptable_tids = LogPlotController.get_acceptable_tids()
        tids = list(set([obj._get_tid_friendly_name() for obj in OM.list() \
                         if obj.tid in acceptable_tids
                         ]
                        )
                    )
        # print 'tids:', tids
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
        # print 'GetValueFromEditorCtrl:', selected_index
        if selected_index == -1:
            return wx.EmptyString
        self._value = editor.GetString(selected_index)
        self._value = ObjectManager.get_tid(self._value)
        return self._value


class ObjectNameRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):
        OM = ObjectManager()
        obj = self.ItemToObject(self.item)
        self._options = OrderedDict()
        # print 'ObjectNameRenderer:', obj.obj_uid[0]
        if obj.data_obj_uid[0] in LogPlotController.get_acceptable_tids():
            for om_obj in OM.list(obj.data_obj_uid[0]):
                # print '   Adding:', om_obj.uid, om_obj.name
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
            return wx.EmptyString
        self._value = self._options.keys()[editor.GetSelection()]
        return self._value


###############################################################################        
###############################################################################


class PropertyMixin(object):

    def _get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        return controller[self._model_key]

    def _set_value(self, value):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller[self._model_key] = value


class EnumProperty(pg.EnumProperty, PropertyMixin):

    def __init__(self, controller_uid, model_key,
                 label=wx.propgrid.PG_LABEL,
                 name=wx.propgrid.PG_LABEL,
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
        # return self._labels[idx]

    def GetIndexForValue(self, value):
        val = self._get_value()
        return self._labels.index(val)


class IntProperty(pg.IntProperty):

    def __init__(self, controller_uid, model_key,
                 label=wx.propgrid.PG_LABEL,
                 name=wx.propgrid.PG_LABEL):
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(IntProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller[self._model_key]
        return str(value)

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller[self._model_key] = text
        return True


class FloatProperty(pg.FloatProperty):

    def __init__(self, controller_uid, model_key,
                 label=wx.propgrid.PG_LABEL,
                 name=wx.propgrid.PG_LABEL):
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(FloatProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller[self._model_key]
        return str(value)

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller[self._model_key] = text
        return True


class StringProperty(pg.StringProperty):

    def __init__(self, controller_uid, model_key,
                 label=wx.propgrid.PG_LABEL,
                 name=wx.propgrid.PG_LABEL):
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(StringProperty, self).__init__(label, name)

    def ValueToString(self, *args):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        value = controller[self._model_key]
        return value

    def StringToValue(self, variant, text, flag):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        controller[self._model_key] = text
        return True


class ColorSelectorComboBox(OwnerDrawnComboBox):
    colors = OrderedDict()
    colors['Black'] = None
    colors['Maroon'] = None
    colors['Green'] = wx.Colour(0, 100, 0)  # Dark Green
    colors['Olive'] = wx.Colour(128, 128, 0)
    colors['Navy'] = None
    colors['Purple'] = None
    colors['Teal'] = wx.Colour(0, 128, 128)
    colors['Gray'] = None
    colors['Silver'] = wx.Colour(192, 192, 192)
    colors['Red'] = None
    colors['Lime'] = wx.Colour(0, 255, 0)  # Green
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
        print('ColorSelectorComboBox.__init__')
        kwargs['choices'] = self.colors.keys()
        OwnerDrawnComboBox.__init__(self, *args, **kwargs)
        print('ColorSelectorComboBox.__init__ ENDED')
        # super(ColorSelectorComboBox, self).SetSelection().#SetSelection()

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
        # print 'OnMeasureItem'
        return 15

    @staticmethod
    def get_colors():
        return ColorSelectorComboBox.colors.keys()


class ColorPropertyEditor(pg.PGEditor):

    def __init__(self):
        print('ColorPropertyEditor.__init__')
        pg.PGEditor.__init__(self)
        print('ColorPropertyEditor.__init__ ENDED')

    def CreateControls(self, propgrid, property, pos, size):
        print('\nCreateControls')
        csc = ColorSelectorComboBox(propgrid.GetPanel(), pos=pos, size=size)
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        csc.SetSelection(idx)
        window_list = pg.PGWindowList(csc)
        return window_list

    def GetName(self):
        return 'ColorPropertyEditor'

    def UpdateControl(self, property, ctrl):
        idx = ColorSelectorComboBox.get_colors().index(property.get_value())
        print('UpdateControl:', idx)
        ctrl.SetSelection(idx)

    def DrawValue(self, dc, rect, property, text):
        print('DrawValue:', text)
        # dc.SetPen( wxPen(propertyGrid->GetCellTextColour(), 1, wxSOLID) )
        # pen = dc.GetPen()
        # print pen.GetColour(), pen.GetStyle(), wx.PENSTYLE_SOLID
        # dc.SetPen(wx.Pen(wx.Colour(0, 0, 255, 255), 1, wx.SOLID))
        cell_renderer = property.GetCellRenderer(1)
        cell_renderer.DrawText(dc, rect, 0, text)  # property.get_value())#rect.x+15, rect.y)
        # dc.DrawText(property.get_value(), rect.x+15, rect.y)

    #    if not property.IsValueUnspecified():
    #        dc.DrawText(property.get_value(), rect.x+5, rect.y)

    def OnEvent(self, propgrid, property, ctrl, event):
        if isinstance(event, wx.CommandEvent):
            if event.GetEventType() == wx.EVT_COMBOBOX:
                print('COMBAO DA MASSA\n\n\n')
            if event.GetString():
                print('VALUE:', event.GetString(), '\n')
                return True
        return False

    def GetValueFromControl(self, variant, property, ctrl):
        """ Return tuple (wasSuccess, newValue), where wasSuccess is True if
            different value was acquired succesfully.
        """
        print('\nGetValueFromControl:', ctrl.GetValue())
        if property.UsesAutoUnspecified() and not ctrl.GetValue():
            return True
        ret_val = property.StringToValue(ctrl.GetValue(), pg.PG_EDITABLE_VALUE)
        return ret_val

    def SetValueToUnspecified(self, property, ctrl):
        print('\nSetValueToUnspecified')
        ctrl.SetSelection(0)  # Remove(0, len(ctrl.GetValue()))

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
        print('InsertItem:', label, index)

    def CanContainCustomImage(self):
        print('CanContainCustomImage')
        return True

    def OnFocus(self, property, ctrl):
        # print 'OnFocus:' #, property, ctrl
        # ctrl.SetSelection(-1)#,-1)
        ctrl.SetFocus()


class ColorProperty(pg.PGProperty):
    # All arguments of this ctor should have a default value -
    # use wx.propgrid.PG_LABEL for label and name
    def __init__(self, controller_uid, model_key,
                 label=wx.propgrid.PG_LABEL,
                 name=wx.propgrid.PG_LABEL):
        print('ColorProperty.__init__')
        self._controller_uid = controller_uid
        self._model_key = model_key
        super(pg.PGProperty, self).__init__(label, name)
        self.SetValue(self.get_value())
        print('ColorProperty.__init__ ENDED')

    # def OnSetValue(self):
    #    print 'ColorProperty.OnSetValue'

    def DoGetEditorClass(self):
        # print 'ColorProperty.DoGetEditorClass'
        return pg.PropertyGridInterface.GetEditorByName('ColorPropertyEditor')
        # _CPEditor #ColorPropertyEditor #wx.PGEditor_TextCtrl

    def ValueToString(self, value, flags):
        print('\nColorProperty.ValueToString')
        value = self.get_value()
        return value

    def StringToValue(self, text, flags):
        print('ColorProperty.StringToValue:', text)
        value = self.set_value(text)
        self.SetValue(value)
        return value

    def get_value(self):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        print('ColorProperty.get_value:', controller[self._model_key])
        return controller[self._model_key]

    def set_value(self, new_value):
        print('ColorProperty.set_value', new_value)
        try:
            UIM = UIManager()
            controller = UIM.get(self._controller_uid)
            controller[self._model_key] = new_value
            return True
        except:
            return False

    def GetDisplayedString(self):
        print('GetDisplayedString')
        return self.get_value()

    def GetChoiceSelection(self):
        idx = ColorSelectorComboBox.get_colors().index(self.get_value())
        print('GetChoiceSelection:', idx)
        return idx

    def IsTextEditable(self):
        ret = super(pg.PGProperty, self).IsTextEditable()
        print('IsTextEditable')
        return ret

    def IsValueUnspecified(self):
        print('\n\nColorProperty.IsValueUnspecified\n\n')
        return False

    def SetLabel(self, label):
        print('SetLabel:', label)
        super(pg.PGProperty, self).SetLabel(label)

# _CPEditor = pg.PropertyGrid.RegisterEditorClass(ColorPropertyEditor())
# _CPEditor = pg.PropertyGrid.RegisterEditorClass(ColorPropertyEditor())#, wx.EmptyString, False)
