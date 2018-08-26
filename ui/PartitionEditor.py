# -*- coding: utf-8 -*-

import wx
import wx.grid

import numpy as np

from classes.om import ObjectManager

from app import app_utils

from basic.colors import COLOR_CYCLE_RGB

# TODO: Tirar a necessidade do uso disso
NAME_UNIT_SEPARATOR = ':::'


COLOUR_DATA = wx.ColourData()
for i, color in enumerate(COLOR_CYCLE_RGB):
    COLOUR_DATA.SetCustomColour(i, color)


#if _iswxphoenix:
#    _gridtablebase = wx.grid.GridTableBase
#else:
#    _gridtablebase = wx.grid.PyGridTableBase


__DEBUG = False

def debugdecorator(func):
    if not __DEBUG:
        return func
    funcname = func.__name__
    def wrapper(*args, **kwargs):
        print (funcname, "IN")
        print ("args:", repr(args))
        print ("kwargs:", repr(kwargs))
        result = func(*args, **kwargs)
        print ("return:", repr(result))
        print (funcname, "OUT")
        return result
    wrapper.__name__ = funcname
    return wrapper



class PartitionTable(wx.grid.GridTableBase):
    
    @debugdecorator
    def __init__(self, partitionuid):
        super(PartitionTable, self).__init__()
        
        self._OM = ObjectManager()
        self.partuid = []
        self.partitionuid = partitionuid
        
        
        self.propmap = [prop.uid for prop in self._OM.list('property', self.partitionuid)]
        self.partmap = [part.uid for part in self._OM.list('part', self.partitionuid)]

#        print self.propmap
        
        if False:  # TODO: rever isso para particoes topo-base -> isinstance(self.partition, TopBottomPartition):
            self.N_COLS = 4
        else:
            self.N_COLS = 2
        self.N_ROWS = 0
    
    
    @debugdecorator
    def AppendCols(self, numCols=1):
#        for part in self._OM.list('part', self.partitionuid):
#            print '\nparts1', part.uid
        for i in range(numCols):
            prop = self._OM.new('property')
            prop.defaultdata = np.nan
#            for part in self.partuid:
#                self._OM.add(prop, part)
#            print '\nparts2', self.partuid
            self._OM.add(prop, self.partitionuid)
            self.propmap.append(prop.uid)

        self.GetView().BeginBatch()
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED, numCols)
        self.GetView().ProcessTableMessage(msg)
        self.GetView().EndBatch()

        return True
    
    @debugdecorator
    def DeleteCols(self, pos=0, numCols=1):
        if pos >= self.N_COLS:
            i = pos - self.N_COLS
            for j in range(numCols)[::-1]:
                self._OM.remove(self.propmap.pop(i + j))

            self.GetView().BeginBatch()
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, pos, numCols)
            self.GetView().ProcessTableMessage(msg)
            self.GetView().EndBatch()

            return True
        else:
            return False
    
    @debugdecorator
    def AppendRows(self, numRows=1):
        part = self._OM.new('part')
        part.defaultdata = np.nan
        self._OM.add(part, self.partitionuid)
        self.partmap.append(part.uid)
        color = self.get_color(0)
        self.set_color(-1,color)

        self.GetView().BeginBatch()
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, numRows)
        self.GetView().ProcessTableMessage(msg)
        self.GetView().EndBatch()

        return True
        
    @debugdecorator
    def DeleteRows(self, pos=0, numRows=1):
        if pos >= self.N_ROWS:
            i = pos - self.N_ROWS
            for j in range(numRows)[::-1]:
                self._OM.remove(self.partmap.pop(i + j))

            self.GetView().BeginBatch()
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, pos, numRows)
            self.GetView().ProcessTableMessage(msg)
            self.GetView().EndBatch()

            return True
        else:
            return False

    @debugdecorator
    def GetColLabelValue(self, col):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            prop = self._OM.get(self.propmap[i])
            label = prop.name
            unit = prop.unit
            if unit:
                label += ' (%s)' % unit
            return label
        elif col == 0:
            return "Nome"
        elif col == 1:
            return "Cor"
        elif col == 2:
#            TODO: rever isso para particoes topo-base
#            label = self.partition.depth.name
#            unit = self.partition.depth.unit
#            if label and unit:
#                label += ' (%s)' % unit
#            if label:
#                return "Topo - " + label
#            else:
            return "Topo"
        elif col == 3:
#            TODO: rever isso para particoes topo-base
#            label = self.partition.depth.name
#            unit = self.partition.depth.unit
#            if label and unit:
#                label += ' (%s)' % unit
#            if label:
#                return "Base - " + label
#            else:
            return "Base"

    @debugdecorator
    def GetRowLabelValue(self, row):
        return str(row + 1)

#    @debugdecorator
    def SetColLabelValue(self, col, label):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            prop = self._OM.get(self.propmap[i])
            name, unit = label.split(NAME_UNIT_SEPARATOR)
            prop.name = name.strip()
            prop.unit = unit.strip()
        else:
            return

    @debugdecorator
    def SetRowLabelValue(self, row, label):        
        return

    @debugdecorator
    def GetNumberCols(self):
        return len(self.propmap) + self.N_COLS

    @debugdecorator
    def GetNumberRows(self):
        return len(self.partmap)

    @debugdecorator
    def GetAttr(self, row, col, kind):
        
        #if _iswxphoenix:
        attr = wx.grid.GridCellAttr().Clone()
        #else:
        #    attr = wx.grid.GridCellAttr()
        
        if col >= self.N_COLS:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif col == 0:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif col == 1:
            part = self._OM.get(self.partmap[row])
            attr.SetBackgroundColour(part.color)
            attr.SetReadOnly(True)
        elif col == 2:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif col == 3:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        return attr

    @debugdecorator
    def GetValue(self, row, col):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            prop = self._OM.get(self.propmap[i])
            value = prop.getdata(self.partmap[row])
            if not np.isnan(value):
                return str(value)
            else:
                return ''
        elif col == 0:
            part = self._OM.get(self.partmap[row])
            return part.name
        elif col == 1:
            return ''
        elif col == 2:
#            TODO: rever isso para particoes topo-base
#            value = self.partition.tops[row]
#            if not np.isnan(value):
#                return str(value)
#            else:
            return ''
        elif col == 3:
#            TODO: rever isso para particoes topo-base
#            value = self.partition.bottoms[row]
#            if not np.isnan(value):
#                return str(value)
#            else:
            return ''

    @debugdecorator
    def SetValue(self, row, col, value):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            if value:
                value = float(value)
            else:
                value = np.nan
            prop = self._OM.get(self.propmap[i])
            prop.setdata(self.partmap[row], value)
        elif col == 0:
            part = self._OM.get(self.partmap[row])
            part.name = value
        elif col == 1:
            return
        elif col == 2:
#            TODO: rever isso para particoes topo-base
#            if value:
#                value = float(value)
#            else:
#                value = np.nan
#            self.partition.tops[row] = value
            return
        elif col == 3:
#            TODO: rever isso para particoes topo-base
#            if value:
#                value = float(value)
#            else:
#                value = np.nan
#            self.partition.bottoms[row] = value
            return

    @debugdecorator
    def set_color(self, row, color):
        part = self._OM.get(self.partmap[row])
        part.color = color

    @debugdecorator
    def get_color(self, row):
        part = self._OM.get(self.partmap[row])
        return part.color
    
    @debugdecorator
    def get_nameunit(self, col):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            prop = self._OM.get(self.propmap[i])
            return prop.name, prop.unit

    @debugdecorator
    def set_nameunit(self, col, name, unit):
        if col >= self.N_COLS:
            i = col - self.N_COLS
            prop = self._OM.get(self.propmap[i])
            prop.name = name
            prop.unit = unit


class PropertyEntryDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(PropertyEntryDialog, self).__init__(*args, **kwargs)

        fgs = wx.FlexGridSizer(2, 2, 5, 5)
        name_label = wx.StaticText(self, label="Nome: ")
        unit_label = wx.StaticText(self, label="Unidade: ")
        self.name_ctrl = wx.TextCtrl(self)
        self.unit_ctrl = wx.TextCtrl(self)
        fgs.AddMany([(name_label), (self.name_ctrl, 1, wx.EXPAND),
                     (unit_label), (self.unit_ctrl, 1, wx.EXPAND)])
        fgs.AddGrowableCol(1, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        #if _iswxphoenix:
        sizer.Add(fgs, proportion=1, flag=wx.EXPAND)
        sizer.Add(button_sizer, proportion=0, flag=wx.EXPAND)
        #else:
        #    sizer.AddSizer(fgs, proportion=1, flag=wx.EXPAND)
        #    sizer.AddSizer(button_sizer, proportion=0, flag=wx.EXPAND)

        self.SetSizer(sizer)

    def set_value(self, name, unit):
        self.name_ctrl.SetValue(name)
        self.unit_ctrl.SetValue(unit)

    def get_value(self):
        name = self.name_ctrl.GetValue()
        unit = self.unit_ctrl.GetValue()
        return name, unit

class NewPartitionDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (360, 240)
        super(NewPartitionDialog, self).__init__(*args, **kwargs)
#        ico = wx.Icon(r'./icons/plus32x32.ico', wx.BITMAP_TYPE_ICO)
#        self.SetIcon(ico)
        fgs = wx.BoxSizer(wx.HORIZONTAL)
        main_label = wx.StaticText(self, label="Fill up the cell below to create a new partition.")
        name_label = wx.StaticText(self, label="Name Partition: ")
#        unit_label = wx.StaticText(self, label="Unidade: ")
        self.name_ctrl = wx.TextCtrl(self)
#        self.unit_ctrl = wx.TextCtrl(self)
        fgs.Add(name_label, 0, wx.EXPAND)
        fgs.Add(self.name_ctrl, 1, wx.EXPAND)
#        fgs.AddGrowableRow(0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        #if _iswxphoenix:
        sizer.Add(main_label, 1, wx.GROW | wx.EXPAND)
        sizer.Add(fgs, 0, wx.EXPAND)
        sizer.Add(button_sizer, 0, wx.EXPAND)
        #else:
        #    sizer.AddSizer(fgs, proportion=1, flag=wx.EXPAND)
        #    sizer.AddSizer(button_sizer, proportion=0, flag=wx.EXPAND)
#        self.
        self.SetSizer(sizer)
        self.name_ctrl.SetFocus()

    def set_value(self, name):
        self.name_ctrl.SetValue(name)

    def get_value(self):
        name = self.name_ctrl.GetValue()
        return name



class Dialog(wx.Dialog):
    @debugdecorator
    def __init__(self, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (640, 480)
        
        super(Dialog, self).__init__(*args, **kwargs)
        
        # TODO: Adaptar para quando não houver partições
        
        self._OM = ObjectManager()

        self.currentwellindex = 0
        #
        self.wellmap = []
        for well in self._OM.list('well'):
            if self._OM.list('partition', well.uid):
                self.wellmap.append(well.uid)
        #
        self.currentpartitionindex = 0
        
        self.tables = []
        
        if len (self.wellmap) == 0:
            self.wellmap.append('GLOBAL')
            self.partitionmap = [partition.uid for partition in self._OM.list('partition')]
            work_table = []
            for partition in self._OM.list('partition'):
                work_table.append(PartitionTable(partition.uid))
            self.tables.append(work_table)
        else:
            self.partitionmap = [partition.uid for partition in self._OM.list('partition')]
            for welluid in self.wellmap:
                work_table = []
                for partition in self._OM.list('partition'):
                    work_table.append(PartitionTable(partition.uid))
                #if work_table:    
                self.tables.append(work_table)
        
        self.grid = wx.grid.Grid(self)
        self.grid.DisableDragColSize()
        self.grid.DisableDragRowSize()
        self.grid.SetDefaultColSize(100)
        
#        if len (self.wellmap) == 0:
#            self.grid.SetTable(self.tables[self.currentwellindex][self.currentpartitionindex])
#        else:
        self.grid.SetTable(self.tables[self.currentwellindex][self.currentpartitionindex])
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_cell_dlclick)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.on_label_dlclick)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
#        self.item = []
#        self.well_choice = wx.Choice(self)
#        print 'itemx', self._OM.get(welluid).name for welluid in self.wellmap
#        for welluid in self.wellmap:
#            if welluid == 'GLOBAL':
#                self.item.append('globaLE')
#                print 'item1',self.item
##                self.well_choice.AppendItems(self.item)
#            else:
#                self.item.append(self._OM.get(welluid).name)
#                print 'item2', self.item
#        self.well_choice.AppendItems(self.item)
#        self.well_choice.SetSelection(self.currentwellindex)
#        self.well_choice.Bind(wx.EVT_CHOICE, self.on_well_choice)

        self.partition_choice = wx.Choice(self)
        self.partition_choice.AppendItems([self._OM.get(partitionuid).name for partitionuid in self.partitionmap])
        self.partition_choice.SetSelection(self.currentpartitionindex)
        self.partition_choice.Bind(wx.EVT_CHOICE, self.on_partition_choice)

        add_part_button = wx.Button(self, label='ADD PART')
        add_part_button.Bind(wx.EVT_BUTTON, self.on_add_part)
        
        remove_part_button = wx.Button(self, label='REM PART')
        remove_part_button.Bind(wx.EVT_BUTTON, self.on_remove_part)
        
        add_property_button = wx.Button(self, label='ADD PROP')
        add_property_button.Bind(wx.EVT_BUTTON, self.on_add)

        remove_property_button = wx.Button(self, label='REM PROP')
        remove_property_button.Bind(wx.EVT_BUTTON, self.on_remove)

#        toolbar_sizer.Add(self.well_choice, 1, wx.ALIGN_LEFT)
        toolbar_sizer.Add(self.partition_choice, 1, wx.ALIGN_LEFT)
        toolbar_sizer.Add(add_part_button, 0, wx.ALIGN_LEFT)
        toolbar_sizer.Add(remove_part_button, 0, wx.ALIGN_LEFT)
        toolbar_sizer.Add(add_property_button, 0, wx.ALIGN_LEFT)
        toolbar_sizer.Add(remove_property_button, 0, wx.ALIGN_LEFT)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(toolbar_sizer, proportion=0, flag=wx.EXPAND)
        main_sizer.Add(self.grid, proportion=1, flag=wx.EXPAND)

        self.SetSizer(main_sizer)

#    @debugdecorator
#    def on_well_choice(self, event):
#        idx = event.GetSelection()
#        if idx != self.currentwellindex:
#            self.currentwellindex = idx
#            self.currentpartitionindex = 0
#            self.partitionmap = [partition.uid for partition in self._OM.list('partition', self.wellmap[self.currentwellindex])]
#            self.partition_choice.Clear()
#            self.partition_choice.AppendItems([self._OM.get(partitionuid).name for partitionuid in self.partitionmap])
#            self.partition_choice.SetSelection(self.currentpartitionindex)
#            #print idx, self.currentpartitionindex
#            self.grid.SetTable(self.tables[idx][self.currentpartitionindex])
#            self.grid.ForceRefresh()

    @debugdecorator
    def on_partition_choice(self, event):
        idx = event.GetSelection()
        if idx != self.currentpartitionindex:
            self.currentpartitionindex = idx
            self.grid.SetTable(self.tables[self.currentwellindex][self.currentpartitionindex])

            self.grid.ForceRefresh()

    @debugdecorator
    def on_add(self, event):
        dlg = PropertyEntryDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            name, unit = dlg.get_value()
            label = name + NAME_UNIT_SEPARATOR + unit
            n = self.grid.GetNumberCols()

            self.grid.AppendCols()
            self.grid.SetColLabelValue(n, label)

            self.grid.ForceRefresh()
            
    @debugdecorator
    def on_add_part(self, event):
#        to_remove = self.grid.GetSelectedRows()
#        to_add = self.grid.GetSelectedRows()
#        self.grid.ClearSelection()
        self.grid.AppendRows()
#        self.grid.SetFocus()
#        self.grid.SelectedRows()
        self.grid.ForceRefresh()

    
    def on_remove_part(self, event):
#        to_remove = self.grid.GetSelectedCols()
        to_remove = self.grid.GetSelectedRows()
        self.grid.ClearSelection()
        for i in to_remove[::-1]:
            self.grid.DeleteRows(i)

        self.grid.ForceRefresh()

    @debugdecorator
    def on_remove(self, event):
        to_remove = self.grid.GetSelectedCols()
        self.grid.ClearSelection()
        for i in to_remove[::-1]:
            self.grid.DeleteCols(i)

        self.grid.ForceRefresh()
        
    @debugdecorator
    def on_cell_dlclick(self, event):
        if event.GetCol() == 1:
            row = event.GetRow()
            table = self.tables[self.currentwellindex][self.currentpartitionindex]
            color = table.get_color(row)

            global COLOUR_DATA
            COLOUR_DATA.SetColour(color)

            dlg = wx.ColourDialog(self, COLOUR_DATA)

            if dlg.ShowModal() == wx.ID_OK:
                COLOUR_DATA = dlg.GetColourData()
                color = COLOUR_DATA.GetColour().Get(True)
                # TODO: alpha
                table.set_color(row, color)
                self.grid.ForceRefresh()
                
                ###
                
            dlg.Destroy()
        else:
            event.Skip()

    @debugdecorator
    def on_label_dlclick(self, event):
        row = event.GetRow()
        col = event.GetCol()
        table = self.tables[self.currentwellindex][self.currentpartitionindex]
        if row == -1 and col >= table.N_COLS:
            name, unit = table.get_nameunit(col)
            dlg = PropertyEntryDialog(self)
            dlg.set_value(name, unit)

            if dlg.ShowModal() == wx.ID_OK:
                name, unit = dlg.get_value()
                table.set_nameunit(col, name, unit)
                self.grid.ForceRefresh()
