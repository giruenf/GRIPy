from collections import OrderedDict

import wx
import wx.dataview as dv

from classes.om import ObjectManager
from classes.ui import FrameController
from classes.ui import Frame
from classes.ui import TextChoiceRenderer
from fileio.liswell import LISWells
from fileio.utils import IOWell, IOWellRun, IOWellLog
from basic.parms import ParametersManager
#from app import log



class TidRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):
        PM = ParametersManager.get()
        f_tids = [ObjectManager.get_tid_friendly_name(tid) \
                                                      for tid in PM.get_tids()]
        _editor = wx.Choice(parent, 
                            wx.ID_ANY,
                            rect.GetTopLeft(),
                            wx.Size(rect.GetWidth(), -1),
                            choices=f_tids
        )
        _editor.SetRect(rect)
        return _editor

    def GetValueFromEditorCtrl(self, editor):
        selected_index = editor.GetSelection()
        if selected_index == -1:
            return wx.EmptyString
        self._value = editor.GetString(selected_index)
        return self._value


class DatatypeRenderer(TextChoiceRenderer):

    def CreateEditorCtrl(self, parent, rect, value):
        try:
            PM = ParametersManager.get()
            dvc = self.GetView()
            model = dvc.GetModel()
            obj = model.ItemToObject(self.item)
            self._options = OrderedDict()
            
            datatypes = PM.get_datatypes(obj.tid)
            _editor = wx.Choice(parent, 
                                wx.ID_ANY,
                                rect.GetTopLeft(),
                                wx.Size(rect.GetWidth(), -1),
                                choices=datatypes
            )
            _editor.SetRect(rect)
            return _editor
        except Exception as e:
            print('\n\nERROR:', e)
            raise
            
    def GetValueFromEditorCtrl(self, editor):
        try:
            selected_index = editor.GetSelection()
            if selected_index == -1:
                return wx.EmptyString
            self._value = editor.GetString(selected_index)
            return self._value     
        except Exception as e:
            print('\n\nERROR:', e)
            raise        





class WellImportFrameController(FrameController):
    tid = 'well_import_frame_controller'
    
    _ATTRIBUTES = OrderedDict()

    def __init__(self, **state):
        state['title'] = 'GRIPy Well Loader'
        state['size'] = (1000, 800)
        super().__init__(**state)
  

class WellImportFrame(Frame):
    tid = 'well_import_frame'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
        
        self.mainpanel = wx.Panel(self)
        self.status_bar = self.CreateStatusBar()
        self.model = None
        self._create_inside_panel()
               
    def _create_inside_panel(self):
        self.dvc = dv.DataViewCtrl(self.mainpanel, 
                                   style=wx.BORDER_THEME|dv.DV_VERT_RULES\
                                   |dv.DV_MULTIPLE|dv.DV_ROW_LINES
        ) 
        #
        dv_col = self.dvc.AppendTextColumn("Name",  0, width=120)      
        dv_col.SetMinWidth(120)
        #
        dvcr = TidRenderer()
        dv_col = dv.DataViewColumn("Datatype", 
                                   dvcr,
                                   1, 
                                   width=100
                                           
        )      
        dv_col.SetMinWidth(100)
        self.dvc.AppendColumn(dv_col)
        #
        dvcr = DatatypeRenderer()
        dv_col = dv.DataViewColumn("Curvetype", 
                                   dvcr,
                                   2, 
                                   width=100
                                           
        )      
        dv_col.SetMinWidth(100)
        self.dvc.AppendColumn(dv_col)    

        #
        dv_col = self.dvc.AppendTextColumn("Curve Name",  3, width=100)      
        dv_col.SetMinWidth(100)
        #        
        dv_col = self.dvc.AppendTextColumn("Start",  4, width=100)      
        dv_col.SetMinWidth(100)        
        #
        dv_col = self.dvc.AppendTextColumn("End",  5, width=100)      
        dv_col.SetMinWidth(100)
        #
        dv_col = self.dvc.AppendTextColumn("Unit",  
                                           6, 
                                           width=80,
                                           mode=dv.DATAVIEW_CELL_ACTIVATABLE
        )      
        dv_col.SetMinWidth(80)
        #
        dv_col = self.dvc.AppendToggleColumn("Import", 
                                             7, 
                                             width=70, 
                                             mode=dv.DATAVIEW_CELL_ACTIVATABLE
        )      
        dv_col.SetMinWidth(70)
        #
        dv_col = self.dvc.AppendProgressColumn ("Progress",  
                                                8, 
                                                width=100
        )
        dv_col.SetMinWidth(100) 
        #
        for dv_col in self.dvc.Columns:
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER)  
        #    
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dvc, 1, wx.EXPAND|wx.ALL, border=10)
        self._create_bottom_buttons_panel()
        sizer.Add(self.bottom_buttons_panel,  0, wx.EXPAND|wx.BOTTOM|wx.TOP)
        self.mainpanel.SetSizer(sizer)
        self.mainpanel.Layout()

         
        
    def _create_bottom_buttons_panel(self):
        self.bottom_buttons_panel = wx.Panel(self.mainpanel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        b1 = wx.Button(self.bottom_buttons_panel, -1, "Selecionar Todos")
        sizer.Add(b1, 0, wx.ALIGN_RIGHT, border=5)
        b2 = wx.Button(self.bottom_buttons_panel, -1, "Desmarcar Todos")
        sizer.Add(b2, 0, wx.ALIGN_RIGHT, border=5)
        b3 = wx.Button(self.bottom_buttons_panel, -1, "Importar Selecionados")
        sizer.Add(b3, 0, wx.LEFT|wx.RIGHT, border=5)
        b1.Bind(wx.EVT_BUTTON, self.on_toggle_all)      
        b2.Bind(wx.EVT_BUTTON, self.on_toggle_none)
        b3.Bind(wx.EVT_BUTTON, self.on_import_selected)
        self.bottom_buttons_panel.SetSizer(sizer)
      


    def expand_dvc_all_items(self):
        for well in self.model.wells:     
            well_item = self.model.ObjectToItem(well)
            self.dvc.Expand(well_item)
            for run in well.data:          
                run_item = self.model.ObjectToItem(run)
                self.dvc.Expand(run_item)


    def set_status_bar_text(self, text):
        self.status_bar.SetStatusText(text)


    def set_lis_file(self, lis_file):
        wells = LISWells(lis_file)     
        if self.model is not None:
            old_model = self.model
            old_model.Clear()
        else:
            old_model = None
        for well in wells.data:
            well.name = self._get_lis_well_name(well)
        self.model = WellImportModel(wells.data)
        self.dvc.AssociateModel(self.model)
        if old_model:
            del old_model
        self.expand_dvc_all_items()



    def set_dlis_file(self, dlis_file):
        if self.model is not None:
            old_model = self.model
            old_model.Clear()
        else:
            old_model = None   
        if old_model:
            del old_model
        # 
        well = IOWell()    
        well.name = self._get_dlis_well_name(dlis_file)
        run_name = well._get_run_name()
        run = IOWellRun(run_name)
        well.append(run)
        #
        
        #
        self.model = WellImportModel([well])
        self.dvc.AssociateModel(self.model)
        self.expand_dvc_all_items()

        

    def set_las_file(self, las_file):
        if self.model is not None:
            old_model = self.model
            old_model.Clear()
        else:
            old_model = None

        well = IOWell()
        well.name = las_file.wellname
        well.infos = las_file.header
        #
        run_name = well._get_run_name()
        run = IOWellRun(run_name)
        well.append(run)
        #
        for idx, mnem in enumerate(las_file.curvesnames):
            log = IOWellLog(mnem, 
                            las_file.curvesunits[idx], 
                            las_file.data[idx]
            )
            run.append(log)
        #
        self.model = WellImportModel([well])
        self.dvc.AssociateModel(self.model)
        if old_model:
            del old_model
        self.expand_dvc_all_items()


    def _get_dlis_well_name(self, dlis_file):
        well_name = dlis_file.origin.get('WELL-NAME')
        if not well_name:
            well_name = dlis_file.origin.get('WN')
        return well_name
    

    def _get_lis_well_name(self, liswell):
        for info in liswell.infos:
            if info.type == None or info.type == 'CONS':
#                print('\nINFO.DATA: ', info.data)
                if info.data.get('WN'):
                    name = info.data.get('WN')[0]
                elif info.data.get('WELL'):  
                    name = info.data.get('WELL')[0]
                return name    
        raise Exception('ERROR _get_lis_well_name:', liswell)
        


    def on_toggle_all(self, evt):
        self.model.ToggleAll()
               
    def on_toggle_none(self, evt):
        self.model.ToggleNone()

    def on_import_selected(self, evt):
        # Setting well and run imports flag
        for well in self.model.wells:
            for run in well.data:
                for log in run.data:
                    if log._import:
                        well._import = True
                        run._import = True       
        #         
        OM = ObjectManager()
        PM = ParametersManager.get()
        #
        for well in self.model.wells:
            if well._import:
                well_obj = OM.new('well', name=well.name)
                OM.add(well_obj)	
                #
                for run in well.data:
                    curve_set_obj = OM.new('curve_set', name=run.name)
                    OM.add(curve_set_obj, well_obj.uid)
                    indexes_uid = []
                    #
                    for index in run.get_indexes():
                        if index._import:
                            index_obj = OM.new('data_index', 
                                         index.data, 
                                         name=index.mnem, 
                                         unit=index.unit.lower(), 
                                         datatype=index.datatype
                            )
                            OM.add(index_obj, curve_set_obj.uid)
                            indexes_uid.append(index_obj.uid)     
                            self.model.SetProgress(index, 100)
                            PM.vote_for_datatype(index.mnem, index.datatype)
                    #
                    for log in run.get_logs():    
                        if log._import:
                            log_obj = OM.new('log', 
                                             log.data, 
                                             name=log.mnem, 
                                             unit=log.unit.lower(), 
                                             datatype=log.datatype
                            )
                            OM.add(log_obj, curve_set_obj.uid)
                            log_obj._create_data_index_map(indexes_uid)
                            self.model.SetProgress(log, 100)
                            PM.vote_for_datatype(log.mnem, log.datatype)
        #
        PM.register_votes()



# Here it is NOT MVC!        
class WellImportModel(dv.PyDataViewModel):

    """
    `DataViewModel` is the base class for managing all data to be
    displayed by a `DataViewCtrl`. All other models derive from it and
    must implement several of its methods in order to define a complete
    data model. In detail, you need to override `IsContainer`,
    `GetParent`, `GetChildren`, `GetColumnCount`, `GetColumnType` and
    `GetValue` in order to define the data model which acts as an
    interface between your actual data and the `DataViewCtrl`.
    """
    
    def __init__(self, wells):
        dv.PyDataViewModel.__init__(self)
        self.wells = wells
        
    def GetColumnCount(self):
        return 9
               
    def GetParent(self, item):
        if not item.IsOk():
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)
        #
        if isinstance(obj, IOWell):
            return dv.NullDataViewItem
        #
        elif isinstance(obj, IOWellRun):
            for well in self.wells:
                for run in well.data:
                    if run == obj:
                        return self.ObjectToItem(well)
        # 
        elif isinstance(obj, IOWellLog):
            for well in self.wells:
                for run in well.data:
                    for log in run.data:
                        if log == obj:
                            return self.ObjectToItem(run)
                                           
    def GetChildren(self, parent, children):
        if parent == dv.NullDataViewItem:       
            for well in self.wells:
                children.append(self.ObjectToItem(well)) 
        else:
            obj = self.ItemToObject(parent)
            if isinstance(obj, IOWell):
                for run in obj.data:
                    children.append(self.ObjectToItem(run))
            elif isinstance(obj, IOWellRun):
                for log in obj.data:
                    children.append(self.ObjectToItem(log))
        return len(children)            

    def IsContainer(self, item):
        if not item.IsOk():
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, IOWell) or isinstance(obj, IOWellRun):
            return True
        return False 
    
    def Clear(self):   
        self.wells = []
        self.Cleared()
        
    def ToggleAll(self):
        for well in self.wells:
            item = self.ObjectToItem(well)
            self.SetValue(True, item, 7)
            self.ItemChanged(item)
                     
    def ToggleNone(self):
        for well in self.wells:
            item = self.ObjectToItem(well)
            self.SetValue(False, item, 7)       
            self.ItemChanged(item)
               
            
    def SetProgress(self, log, value):
        log_item = self.ObjectToItem(log)
        self.SetValue(value, log_item, 8)            # progress
        self.ItemChanged(log_item)
        
        # Reloading parents progress bar
#        run_item = self.GetParent(log_item)
#        self.ItemChanged(run_item)
#        well_item = self.GetParent(run_item)
#        self.ItemChanged(well_item)



    def SetValue(self, value, item, col):

        obj = self.ItemToObject(item)
        
#        if col == 8:
#            print('\nSetValue: ', col, value)
#            print (type(obj))
            
        
        if isinstance(obj, IOWell):
            if col == 7:    # import 
                for run in obj.data:
                    run_item = self.ObjectToItem(run)
                    self.SetValue(value, run_item, 7)
                        
            #if col == 8:    # progress
            #    well_item = self.ObjectToItem(obj)
            #    self.SetValue(value, well_item, 8)
    
        elif isinstance(obj, IOWellRun): 
            if col == 7:    # import 
                for log in obj.data:
                    log_item = self.ObjectToItem(log)
                    self.SetValue(value, log_item, 7)                
                
            #if col == 8:    # progress
            #    run_item = self.ObjectToItem(obj)
            #    self.SetValue(value, run_item, 8)
            
            
        elif isinstance(obj, IOWellLog):
            if col == 1:    # tid
                obj.tid = ObjectManager.get_tid(value)
                PM = ParametersManager.get()
                datatypes = PM.get_datatypes(obj.tid)
                # Set first occurrence datatype associated with tid
                self.SetValue(datatypes[0], item, 2)
            elif col == 2:  # datatype
                obj.datatype = value
            elif col == 7:    # import
                obj._import = value
            elif col == 8:    # progress
                obj._progress = value
        return True
    
    
    def GetValue(self, item, col):

        obj = self.ItemToObject(item)
        
        
#        if col == 8:            
#        print('\nGetValue: ', col)
#        print (type(obj))


        if isinstance(obj, IOWell):
            if col == 0: 
                return obj.name      
            elif col == 7:
                for run in obj.data:
                    for log in run.data:
                        if not log._import:
                            return False
                return True       
 
            elif col == 8:
                soma = 0.0
                i = 0
                for run in obj.data:
                    for log in run.data:
                        soma += log._progress
                        i += 1
                if i == 0:
                    return 0.0
                return (soma/i)*100.0  
            else:
                return ""
            
                     
        elif isinstance(obj, IOWellRun):     
            if col == 0: 
                return obj.name
            
            elif col == 7:
                for log in obj.data:
                    if not log._import:
                        return False
                return True
            
            elif col == 8:
                if len(obj.data) == 0:
                    return 0.0
                soma = 0.0
                for log in obj.data:
                    soma += log._progress
                return (soma/len(obj.data))*100.0
          
            else:
                return ""               
                

        elif isinstance(obj, IOWellLog):
            if col == 0:
                return ""
            
            elif col == 1:
                if not obj.tid:
                    return ""
                friendly_tid = ObjectManager.get_tid_friendly_name(obj.tid)
                if friendly_tid is None:
                    return ""
                return friendly_tid
            
            elif col == 2:
                if obj.datatype is None:
                    return ""
                return obj.datatype
            
            elif col == 3:
                return obj.mnem 
            
            elif col == 4:
                first_depth_pos = obj.get_first_occurence_pos()   
                parent_item = self.GetParent(item)
                run = self.ItemToObject(parent_item)
                value = run.get_depth().data[first_depth_pos]
                #return "{0:.2f}".format(value) + ' (' + str(first_depth_pos) +')'
                return "{0:.2f}".format(value)
            
            elif col == 5:
                last_depth_pos = obj.get_last_occurence_pos()
                parent_item = self.GetParent(item)
                run = self.ItemToObject(parent_item)
                value = run.get_depth().data[last_depth_pos]
                #return "{0:.2f}".format(value) + ' (' + str(last_depth_pos) +')'
                return "{0:.2f}".format(value)
            
            elif col == 6:
                return str.lower(obj.unit)
            
            elif col == 7:
                return obj._import
            
            elif col == 8:
                return obj._progress
       


    def HasContainerColumns(self, item):
        obj = self.ItemToObject(item)
        if isinstance(obj, IOWell) or isinstance(obj, IOWellRun):
            return True


    def GetAttr(self, item, col, attr):
        if col == 0:
            attr.SetColour('blue')
            return True
        return False        
 
      
   