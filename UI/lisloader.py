# -*- coding: utf-8 -*-
import wx
import os
import wx.dataview as dv
from FileIO.LIS import LISFile
from FileIO.LISWELL import LISWells, LISWell, LISWellLog
from OM.Manager import ObjectManager
from collections import OrderedDict
from Parms import ParametersManager
import DT

W_MNEMS = OrderedDict()
W_MNEMS['CN'] = {'LAS_MNEM': 'COMP', 'LAS_DESC': 'CCOMPANY'}
W_MNEMS['WN'] = {'LAS_MNEM': 'WELL', 'LAS_DESC': 'WELL'}
W_MNEMS['WBN'] = {'LAS_MNEM': 'WELL', 'LAS_DESC': 'WELL'}
W_MNEMS['FN'] = {'LAS_MNEM': 'FLD', 'LAS_DESC': 'FIELD'}
#W_MNEMS[''] = {'LAS_MNEM': 'LOC', 'LAS_DESC': 'LOCATION'}
#W_MNEMS[''] = {'LAS_MNEM': 'PROV', 'LAS_DESC': 'PROVINCE'}
#W_MNEMS[''] = {'LAS_MNEM': 'CNTY', 'LAS_DESC': 'COUNTY'}
W_MNEMS['STAT'] = {'LAS_MNEM': 'STAT', 'LAS_DESC': 'STATE'}
W_MNEMS['NATI'] = {'LAS_MNEM': 'CTRY', 'LAS_DESC': 'COUNTRY'}
W_MNEMS['SRVC'] = {'LAS_MNEM': 'SRVC', 'LAS_DESC': 'SERVICE COMPANY'}
W_MNEMS['DATE'] = {'LAS_MNEM': 'DATE', 'LAS_DESC': 'DATE'}
W_MNEMS['UWI'] = {'LAS_MNEM': 'UWI', 'LAS_DESC': 'UNIQUE WELL ID'}
W_MNEMS['API'] = {'LAS_MNEM': 'API', 'LAS_DESC': 'API NUMBER'}
W_MNEMS['APIN'] = {'LAS_MNEM': 'API', 'LAS_DESC': 'API NUMBER'}
W_MNEMS['LATD'] = {'LAS_MNEM': 'LATI', 'LAS_DESC': 'LATITUDE'}
W_MNEMS['LATI'] = {'LAS_MNEM': 'LATI', 'LAS_DESC': 'LATITUDE'}
W_MNEMS['LOND'] = {'LAS_MNEM': 'LONG', 'LAS_DESC': 'LONGITUDE'}
W_MNEMS['LONG'] = {'LAS_MNEM': 'LONG', 'LAS_DESC': 'LONGITUDE'}
#W_MNEMS['TDL'] = {'LAS_MNEM': '', 'LAS_DESC': 'TOTAL DEPTH (LOGGER)'}
#W_MNEMS['TDD'] = {'LAS_MNEM': '', 'LAS_DESC': 'TOTAL DEPTH (DRILLER)'}
#W_MNEMS['UBID'] = {'LAS_MNEM': '', 'LAS_DESC': 'UNIQUE BOREHOLE ID'}
#W_MNEMS['PDAT'] = {'LAS_MNEM': '', 'LAS_DESC': 'PERMANENT DATUM'}
#W_MNEMS['EPD'] = {'LAS_MNEM': 'EPD', 'LAS_DESC': 'ELEVATION OF PERMANENT DATUM'}
#W_MNEMS['LMF'] = {'LAS_MNEM': '', 'LAS_DESC': 'LOGGING MEASURED FROM'}
#W_MNEMS['APD'] = {'LAS_MNEM': '', 'LAS_DESC': 'LMF ELEVATION'}
#W_MNEMS['EDF'] = {'LAS_MNEM': '', 'LAS_DESC': 'ELEVATION OF DERRICK FLOOR'}
#W_MNEMS['EGL'] = {'LAS_MNEM': 'EGL', 'LAS_DESC': 'GROUND ELEVATION'}
#W_MNEMS['EKB'] = {'LAS_MNEM': '', 'LAS_DESC': 'ELEVATION OF KELLY BUSHING'}
#W_MNEMS['TOOT'] = {'LAS_MNEM': '', 'LAS_DESC': 'TOOL TYPE'}
#W_MNEMS['MDEC'] = {'LAS_MNEM': '', 'LAS_DESC': 'MAGNETIC FIELD DECLINATION'}
#W_MNEMS['STATIC_COLOR_THRESHOLDS'] = {'LAS_MNEM': '', 'LAS_DESC': ''}
#W_MNEMS['BS'] = {'LAS_MNEM': '', 'LAS_DESC': 'BIT SIZE'}
#



class LISImportFrame(wx.Frame):
        
    def __init__(self, *args, **kwargs):
        self.filename = None
        super(LISImportFrame, self).__init__(*args, **kwargs)
        self.SetTitle('GRIPy LIS Loader')
        self.panel = wx.Panel(self)
        self.menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, u"&Open LIS File")
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.menu_bar.Append(file_menu, u"&File")
        self.SetMenuBar(self.menu_bar)
        self.status_bar = self.CreateStatusBar()
        self.model = None
        self.dvc = None
        self._OM = ObjectManager(self)         
        
    def on_open(self, evt):
        print 'xxx', os.getcwd()
        dlg = wx.FileDialog(
                self, message="Choose a file",
                defaultDir=os.getcwd(), 
                defaultFile="",
                #wildcard=wildcard,
                style=wx.OPEN | wx.CHANGE_DIR
        )
        print 'yyy',os.getcwd()
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            if paths[0]:
                print os.getcwd()
                self.dirname, self.filename = os.path.split(paths[0])
                self.status_bar.SetStatusText(paths[0])
                print os.getcwd()
                if self.dvc is None:    
                    self.create_inside_panel()
                if self.model is not None:
                    old_model = self.model
                    old_model.Clear()
                else:
                    old_model = None
                self.model = self.get_model_from_LIS(paths[0])
                print os.getcwd()
                self.dvc.AssociateModel(self.model)
                if old_model:
                    del old_model
                
                
    def create_inside_panel(self):
        self.dvc = dv.DataViewCtrl(self.panel, style=wx.BORDER_THEME | dv.DV_VERT_RULES | dv.DV_MULTIPLE | dv.DV_ROW_LINES) 
        dv_col = self.dvc.AppendTextColumn("Seq",  0, width=45, align=wx.ALIGN_CENTER)    
        dv_col.SetMinWidth(45)
        dv_col = self.dvc.AppendTextColumn("Well Name",  1, width=85)      
        dv_col.SetMinWidth(55)
        dv_col = self.dvc.AppendTextColumn("Start",  2, width=85)      
        dv_col.SetMinWidth(55)        
        dv_col = self.dvc.AppendTextColumn("End",  3, width=85)      
        dv_col.SetMinWidth(55)
        dv_col = self.dvc.AppendTextColumn("Unit",  4, width=85)      
        dv_col.SetMinWidth(55)
        dv_col = self.dvc.AppendToggleColumn("Import",  5, width=90, mode=dv.DATAVIEW_CELL_ACTIVATABLE)      
        dv_col.SetMinWidth(90)
        #dv_col = self.dvc.AppendTextColumn("LAS File Name",  6, width=100)      
        #dv_col.SetMinWidth(100)
        #dv_col = self.dvc.AppendTextColumn("Progress",  6, width=85)    
        dv_col = self.dvc.AppendProgressColumn ("Progress",  6, width=85)#, mode=dv.DATAVIEW_CELL_INERT)
        dv_col.SetMinWidth(80) 
        for dv_col in self.dvc.Columns:
            dv_col.Renderer.Alignment = wx.ALIGN_CENTER 
            dv_col.SetAlignment(wx.ALIGN_CENTER)  
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dvc, 1, wx.EXPAND|wx.ALL, border=10)
        sizer.Add(self.getPanelBottomButtons(),  0, wx.EXPAND|wx.BOTTOM|wx.TOP)
        self.panel.SetSizer(sizer)
        self.panel.Layout()
    

        
        
    def get_model_from_LIS(self, filename):
        print '\nINICIO\n'
        print os.getcwd()
        lis = LISFile()
        lis.read_file(filename)
        print 'FIM READ FILE'
        lis.read_physical_records()
        print 'FIM READ PHYSICAL'
        lis.read_logical_records()
        print 'FIM READ LOGICAL'   
        wells = LISWells(lis)     
        return LISModel(wells.data)


    def getPanelBottomButtons(self):
        panel = wx.Panel(self.panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        b1 = wx.Button(panel, -1, "Selecionar Todos")
        sizer.Add(b1, 0, wx.ALIGN_RIGHT, border=5)
        b2 = wx.Button(panel, -1, "Desmarcar Todos")
        sizer.Add(b2, 0, wx.ALIGN_RIGHT, border=5)
        b3 = wx.Button(panel, -1, "Importar Selecionados")
        sizer.Add(b3, 0, wx.LEFT|wx.RIGHT, border=5)
        b1.Bind(wx.EVT_BUTTON, self._OnToggleAll)      
        b2.Bind(wx.EVT_BUTTON, self._OnToggleNone)
        b3.Bind(wx.EVT_BUTTON, self._OnImportToggled)
        panel.SetSizer(sizer)
        return panel     


    def _OnToggleAll(self, evt):
        self.model.ToggleAll()
        
    def _OnToggleNone(self, evt):
        self.model.ToggleNone()      

    def _OnImportToggled(self, evt):
      
        for idx, lis_well, filename in self.model.get_selected_wells():
            well_header = OrderedDict()
            for info in lis_well.infos:
                if info.type is None:# or info.type == 'CONS':
                    W = OrderedDict()
                    well_header['W'] = W
                    for lis_key, las_dict in W_MNEMS.items():
                        if info.data.get(lis_key):
                            map_ = {}
                            map_['MNEM'] = las_dict.get('LAS_MNEM')
                            map_['DATA'] = info.data.get(lis_key)[0]
                            map_['UNIT'] = ''
                            map_['DESC'] = las_dict.get('LAS_DESC')
                            W[las_dict.get('LAS_MNEM')] = map_
                            
            well = self._OM.new('well', name=well_header.get('W').get('WELL').get('DATA'), LASheader=well_header)
            self._OM.add(well)
            # depth is a LISWellLog object
            depth_curve = lis_well.get_depth()
            depth = self._OM.new('depth', depth_curve.data, name=depth_curve.mnem, unit=depth_curve.unit, curvetype='Depth')
            self._OM.add(depth, well.uid)            
        
            PM = ParametersManager.get()
            # Implementar selecao de datatypes e curvetypes a moda Vizeu
            for lis_well_log in lis_well.get_logs():
                logtype = PM.getcurvetypefrommnem(lis_well_log.mnem)
                datatype = PM.getdatatypefrommnem(lis_well_log.mnem)
                if not datatype:
                    datatype = 'Log'
                if datatype == 'Log':    
                    log = self._OM.new('log', lis_well_log.data, name=lis_well_log.mnem, unit=lis_well_log.unit, curvetype=logtype)
                    self._OM.add(log, well.uid)
                elif datatype == 'Partition':  
                    booldata, codes = DT.DataTypes.Partition.getfromlog(lis_well_log.data)
                    partition = self._OM.new('partition', name=lis_well_log.name, curvetype=logtype)
                    self._OM.add(partition, well.uid)
                    for idx in range(len(codes)):
                        part = self._OM.new('part', booldata[idx], code=int(codes[idx]), curvetype=logtype)
                        self._OM.add(part, partition.uid)
                
            self.model.SetProgress(idx, 100)
            

        
class LISModel(dv.PyDataViewModel):

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
        self.objmapper.UseWeakRefs(True)
        self.wells = wells
        self.las_filenames = []
        self.responses = []
        self.progresses = []
        for i in range(len(self.wells)):
            self.las_filenames.append('file_'+str(i)+'.las')
            self.responses.append(True)
            self.progresses.append(0)
    
    def GetColumnCount(self):
        return 8
    
    def GetParent(self, item):
        if not item.IsOk():
            return dv.NullDataViewItem
        obj = self.ItemToObject(item)
        if isinstance(obj, LISWell):
            return dv.NullDataViewItem
        elif isinstance(obj, LISWellLog):
            for well in self.wells:
                for log in well.logs:
                    if log == obj:
                        return self.ObjectToItem(well)
                        
        
    def GetChildren(self, parent, children):
        if parent == dv.NullDataViewItem:       
            for well in self.wells:
                children.append(self.ObjectToItem(well)) 
        else:
            obj = self.ItemToObject(parent)
            if isinstance(obj, LISWell):
                for log in obj.logs:
                    children.append(self.ObjectToItem(log))
            #elif isinstance(obj, LISWellLog):
            #    return 0
        return len(children)            


    def IsContainer(self, item):
        if not item.IsOk():
            return True
        obj = self.ItemToObject(item)
        if isinstance(obj, LISWell):
            return True
        return False      
   
   
    def Clear(self):   
        self.wells = []
        self.las_filenames = []
        self.responses = []
        self.Cleared()
        
   
    def ToggleAll(self):
        #print 'ToggleAll'
        for well in self.wells:
            item = self.ObjectToItem(well)
            self.SetValue(True, item, 5)
            self.ItemChanged(item)
            
    def ToggleNone(self):
        #print 'ToggleNone'
        for well in self.wells:
            item = self.ObjectToItem(well)
            self.SetValue(False, item, 5)       
            self.ItemChanged(item)
            
    def get_selected_wells(self):
        list_ = []
        for idx, well in enumerate(self.wells):
            item = self.ObjectToItem(well)
            if self.GetValue(item, 5):
                #print 'selected: ', idx
                list_.append((idx, well, self.las_filenames[idx]))
        return list_                
            
            
    def SetProgress(self, pos, value):
        item = self.ObjectToItem(self.wells[pos])
        self.SetValue(value, item, 7)        
        self.ItemChanged(item)
       
       
    def SetValue(self, value, item, col):
        obj = self.ItemToObject(item)
        if isinstance(obj, LISWell): 
            if col == 5:
                well = self.ItemToObject(item)
                for idx, w in enumerate(self.wells):
                    if well == w:
                        self.responses[idx] = value 
            if col == 7:
                well = self.ItemToObject(item)
                for idx, w in enumerate(self.wells):
                    if well == w:
                        self.progresses[idx] = value 
 
 
    def GetValue(self, item, col):
        #print 'GetValue: ', col
        obj = self.ItemToObject(item)
        #print type(obj)
        if isinstance(obj, LISWell):
            #print 'col: ', col
            if col == 0: 
                for idx, well in enumerate(self.wells):
                    if well == obj:
                        return str(idx+1)
            elif col == 1:
                for info in obj.infos:
                    if info.type == None or info.type == 'CONS':
                        #print 'INFO.DATA: ', info.data
                        return info.data.get('WN')[0] 
            elif col == 2:
                for well in self.wells:
                    if well == obj:
                        return "{0:.2f}".format(well.get_start_depth())
            elif col == 3:
                for  well in self.wells:
                    if well == obj:
                        return "{0:.2f}".format(well.get_end_depth())
            elif col == 4:
                for well in self.wells:
                    if well == obj:
                        return str.lower(well.get_depth_unit())              
            elif col == 5:
                for idx, well in enumerate(self.wells):
                    if well == obj:
                        return self.responses[idx]              
            #elif col == 6:
            #    for idx, well in enumerate(self.wells):
            #        if well == obj:
            #            return self.las_filenames[idx]                     
            elif col == 6:
                for idx, well in enumerate(self.wells):
                    if well == obj:
                        return self.progresses[idx]  
                        
        elif isinstance(obj, LISWellLog):
            if col == 0:
                return ''
            elif col == 1:
                return obj.mnem
            elif col == 2:
                first_depth_pos = obj.get_first_occurence_pos()   
                parent_item = self.GetParent(item)
                well = self.ItemToObject(parent_item)
                value = well.get_depth().data[first_depth_pos]
                return "{0:.2f}".format(value) + ' (' + str(first_depth_pos) +')'
            elif col == 3:
                last_depth_pos = obj.get_last_occurence_pos()
                parent_item = self.GetParent(item)
                well = self.ItemToObject(parent_item)
                value = well.get_depth().data[last_depth_pos]
                #return "{0:.2f}".format(value) + ' (' + str(last_depth_pos) +')'
                return str(value) + ' (' + str(last_depth_pos) +')'
            elif col == 4:
                return str.lower(obj.unit)
            elif col == 6:
                return ''    
            else:
                return 'ainda nao'
         
    def HasContainerColumns(self, item):
        obj = self.ItemToObject(item)
        if isinstance(obj, LISWell):
            return True

    def GetAttr(self, item, col, attr):
        if col == 0:
            attr.SetColour('blue')
            return True
        return False        
 
      


        
