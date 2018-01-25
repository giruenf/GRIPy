# -*- coding: utf-8 -*-

import wx
import wx.grid
from UI.uimanager import UIManager
import numpy as np
from os import getcwd as cwd

from OM.Manager import ObjectManager
from Algo import RockPhysics as RP
import App.app_utils

from Basic.Colors import COLOR_CYCLE_RGB


COLOUR_DATA = wx.ColourData()
for i, color in enumerate(COLOR_CYCLE_RGB):
    COLOUR_DATA.SetCustomColour(i, color)

__DEBUG = False

def debugdecorator(func):
    if not __DEBUG:
        return func
    funcname = func.__name__
    def wrapper(*args, **kwargs):
        print funcname, "IN"
        print "args:", repr(args)
        print "kwargs:", repr(kwargs)
        result = func(*args, **kwargs)
        print "return:", repr(result)
        print funcname, "OUT"
        return result
    wrapper.__name__ = funcname
    return wrapper


class RockTable(wx.grid.GridTableBase):
    @debugdecorator
    def __init__(self, rocktableuid):
        super(RockTable, self).__init__()
        
        self._OM = ObjectManager(self)
        self.rocktypeuid = []
        self.rocktableuid = rocktableuid
        
        self.rocktypemap = [rocktype.uid for rocktype in self._OM.list('rocktype', self.rocktableuid)]
        self.N_COLS = 4
        self.N_ROWS = 0
    
    @debugdecorator
    def AppendRows(self, numRows=1):
        rocktype = self.GrainEntry()
#        rocktype = self._OM.new('rocktype')
        rocktype.defaultdata = np.nan
        self._OM.add(rocktype, self.rocktableuid)
        
        self.rocktypemap.append(rocktype.uid)
        color = self.get_color(0)
        self.set_color(-1,color)

        self.GetView().BeginBatch()
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, numRows)
        self.GetView().ProcessTableMessage(msg)
        self.GetView().EndBatch()

        return True
    
    @debugdecorator 
    def GrainEntry(self):
        UIM = UIManager()
        dlg = UIM.create('dialog_controller', title='Rock creator')
        cont_grain = dlg.view.AddCreateContainer('StaticBox', label='Grain Parts', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        cont_matr = dlg.view.AddCreateContainer('StaticBox', label='Matrix Parts', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
        
        json_file = '\\Temp\\min.json'
#        fullpath_json = 'C:\\Users\\rtabelini\\Documents\\Github\\GRIPy'+json_file
        fullpath_json = cwd()+json_file

        dictmin = App.app_utils.read_json_file(fullpath_json)
        
        def on_change_mineral(name, old_value, new_value, **kwargs):
            print 'new\n', name, new_value, new_value['name'], dictmin.iterkeys()
            if name == 'mineralgrain':
                textctrl_k = dlg.view.get_object('kmod1')
                textctrl_g = dlg.view.get_object('gmod1')
                textctrl_rho = dlg.view.get_object('dens1')
            elif name == 'mineralmatrix':
                textctrl_k = dlg.view.get_object('kmod2')
                textctrl_g = dlg.view.get_object('gmod2')
                textctrl_rho = dlg.view.get_object('dens2')
                
            if new_value['name'] in dictmin.iterkeys():
                textctrl_k.set_value(new_value['K'])
                textctrl_g.set_value(new_value['G'])
                textctrl_rho.set_value(new_value['Dens'])
                
        dlg.view.AddChoice(cont_grain, widget_name='mineralgrain', options=dictmin, flag=wx.EXPAND)
        choice_grain = dlg.view.get_object('mineralgrain')
        choice_grain.set_trigger(on_change_mineral)
        
        dlg.view.AddChoice(cont_matr, widget_name='mineralmatrix', options=dictmin, flag=wx.EXPAND)
        choice_matrix = dlg.view.get_object('mineralmatrix')
        choice_matrix.set_trigger(on_change_mineral)
        
        gr_frac = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(gr_frac, proportion=1,initial='Fraction ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(gr_frac, proportion=1, widget_name='frac1', initial='0.8',flag=wx.ALIGN_RIGHT)
        
        gr_poro = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(gr_poro, proportion=1,initial='Porosity ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(gr_poro, proportion=1, widget_name='poro1', initial='0.20',flag=wx.ALIGN_RIGHT)
        
        gr_kmod = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(gr_kmod, proportion=1,widget_name='K_Modulus', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(gr_kmod, proportion=1, widget_name='kmod1', initial='36.5', flag=wx.ALIGN_RIGHT)
        
        gr_gmod = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(gr_gmod, proportion=1,widget_name='G_Modulus', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(gr_gmod, proportion=1,widget_name='gmod1', initial='78.6', flag=wx.ALIGN_RIGHT)
        
        gr_dens = dlg.view.AddCreateContainer('BoxSizer', cont_grain, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(gr_dens, proportion=1,widget_name='Density', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(gr_dens, proportion=1,widget_name='dens1', initial='2.65', flag=wx.ALIGN_RIGHT)
        
        mtr_frac = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(mtr_frac, proportion=1,widget_name='fraction2', initial='Fraction ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(mtr_frac, proportion=1,widget_name='frac2', initial='0.2', flag=wx.ALIGN_LEFT)
        
        mtr_poro = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(mtr_poro, proportion=1,initial='Porosity ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(mtr_poro, proportion=1, widget_name='poro2', initial='0.10',flag=wx.ALIGN_RIGHT)
        
        mtr_kmod = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(mtr_kmod, proportion=1,widget_name='K_Modulus2', initial='K Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(mtr_kmod, proportion=1,widget_name='kmod2', initial='36.5', flag=wx.ALIGN_LEFT)
        
        mtr_gmod = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(mtr_gmod,proportion=1, widget_name='G_Modulus2', initial='G Modulus (GPa) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(mtr_gmod,proportion=1, widget_name='gmod2', initial='78.6', flag=wx.ALIGN_LEFT)
        
        mtr_dens = dlg.view.AddCreateContainer('BoxSizer', cont_matr, orient=wx.HORIZONTAL, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        dlg.view.AddStaticText(mtr_dens,proportion=1, widget_name='Density2', initial='Density (g/cc) ',flag=wx.ALIGN_RIGHT)
        dlg.view.AddTextCtrl(mtr_dens, proportion=1,widget_name='dens2', initial='2.65', flag=wx.ALIGN_LEFT)
    #        
        try:
            if dlg.view.ShowModal() == wx.ID_OK:
                results = dlg.get_results()     
                gr_f = results.get('frac1')
                mtr_f = results.get('frac2')
                ngrain = results.get('mineralgrain')['name']
                nmatrix = results.get('mineralmatrix')['name']
                gr_phi = results.get('poro1')
                gr_k = results.get('kmod1')
                gr_mi = results.get('gmod1')
                gr_rho = results.get('dens1')
                mtr_phi = results.get('poro2')
                mtr_k = results.get('kmod2')
                mtr_mi = results.get('gmod2')
                mtr_rho = results.get('dens2')
#                kk = RP.VRHill (gr_k, gr_f, mtr_k)
#                g = RP.VRHill (gr_mi, gr_f, mtr_mi)
                print '\ngrd', gr_k, gr_f, mtr_k, type(float(mtr_k))
                rocktype = self._OM.new('rocktype', fracgrain = gr_f, fracmatrix = mtr_f, grain = ngrain, matrix = nmatrix, k=10, mi=20)#vp=vp, vs=vs, rho = rho, k=k, mi=mi, poi=poi        
                return rocktype

        except Exception as e:
            print 'ERROR:', e
        finally:
            UIM.remove(dlg.uid)
            
    @debugdecorator
    def DeleteRows(self, pos=0, numRows=1):
        if pos >= self.N_ROWS:
            i = pos - self.N_ROWS
            for j in range(numRows)[::-1]:
                self._OM.remove(self.rocktypemap.pop(i + j))

            self.GetView().BeginBatch()
            msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, pos, numRows)
            self.GetView().ProcessTableMessage(msg)
            self.GetView().EndBatch()

            return True
        else:
            return False

    @debugdecorator
    def GetColLabelValue(self, col):
        if col == 0:
            return "Nome"
        elif col == 1:
            return "Cor"
        elif col == 2:
            return "Grain"
        elif col == 3:
            return "Matrix"
        else:
            return

    @debugdecorator
    def GetRowLabelValue(self, row):
        return str(row + 1)

    @debugdecorator
    def SetRowLabelValue(self, row, label):        
        return

    @debugdecorator
    def GetNumberCols(self):
        return self.N_COLS
#        return len(self.propmap) + self.N_COLS

    @debugdecorator
    def GetNumberRows(self):
        return len(self.rocktypemap)

    @debugdecorator
    def GetAttr(self, row, col, kind):
        
        #if _iswxphoenix:
        attr = wx.grid.GridCellAttr().Clone()
        
        if col >= self.N_COLS:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif col == 0:
            attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
        elif col == 1:
            rocktype = self._OM.get(self.rocktypemap[row])
            attr.SetBackgroundColour(rocktype.color)
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
            value = prop.getdata(self.rocktypemap[row])
            if not np.isnan(value):
                return str(value)
            else:
                return ''
        elif col == 0:
            rocktype = self._OM.get(self.rocktypemap[row])
            return rocktype.name
        elif col == 1:
            return ''
        elif col == 2:
            rocktype = self._OM.get(self.rocktypemap[row])
            return rocktype.fracgrain + ' ' + rocktype.grain
        elif col == 3:
            rocktype = self._OM.get(self.rocktypemap[row])
            return rocktype.fracmatrix + ' ' + rocktype.matrix

    @debugdecorator
    def SetValue(self, row, col, value):        
        if col >= self.N_COLS:
            i = col - self.N_COLS
            if value:
                value = float(value)
            else:
                value = np.nan
            prop = self._OM.get(self.propmap[i])
            prop.setdata(self.rocktypemap[row], value)
        elif col == 0:
            rocktype = self._OM.get(self.rocktypemap[row])
            rocktype.name = value
        elif col == 1:
            return
        elif col == 2:
            return
        elif col == 3:
            return
    @debugdecorator
    def set_color(self, row, color):
        rocktype = self._OM.get(self.rocktypemap[row])
        rocktype.color = color

    @debugdecorator
    def get_color(self, row):
        rocktype = self._OM.get(self.rocktypemap[row])
        return rocktype.color
    
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
        
        sizer.Add(fgs, proportion=1, flag=wx.EXPAND)
        sizer.Add(button_sizer, proportion=0, flag=wx.EXPAND)
        self.SetSizer(sizer)

    def set_value(self, name, unit):
        self.name_ctrl.SetValue(name)
        self.unit_ctrl.SetValue(unit)

    def get_value(self):
        name = self.name_ctrl.GetValue()
        unit = self.unit_ctrl.GetValue()
        return name, unit



class NewRockTableDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        if 'size' not in kwargs:
            kwargs['size'] = (360, 240)
        super(NewRockTableDialog, self).__init__(*args, **kwargs)
#        ico = wx.Icon(r'./icons/plus32x32.ico', wx.BITMAP_TYPE_ICO)
#        self.SetIcon(ico)
        fgs = wx.BoxSizer(wx.HORIZONTAL)
        main_label = wx.StaticText(self, label="Fill up the cell below to create a new rock table.")
        name_label = wx.StaticText(self, label="Name Rock Table: ")
#        unit_label = wx.StaticText(self, label="Unidade: ")
        self.name_ctrl = wx.TextCtrl(self)
#        self.unit_ctrl = wx.TextCtrl(self)
        fgs.Add(name_label, 0, wx.EXPAND)
        fgs.Add(self.name_ctrl, 1, wx.EXPAND)
#        fgs.AddGrowableRow(0)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        sizer.Add(main_label, 1, wx.GROW | wx.EXPAND)
        sizer.Add(fgs, 0, wx.EXPAND)
        sizer.Add(button_sizer, 0, wx.EXPAND)
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
        
        self._OM = ObjectManager(self)

        self.currentwellindex = 0
        self.currentrocktableindex = 0
        
        self.tables = []
        
        self.rocktablemap = [rocktable.uid for rocktable in self._OM.list('rocktable')]
        work_table = []
        for rocktable in self._OM.list('rocktable'):
            work_table.append(RockTable(rocktable.uid))
        self.tables.append(work_table)
        self.grid = wx.grid.Grid(self)
        self.grid.SetDefaultColSize(100)
        
#        else:
        self.grid.SetTable(self.tables[self.currentwellindex][self.currentrocktableindex])
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_cell_dlclick)
        self.grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.on_label_dlclick)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.rocktable_choice = wx.Choice(self)
        self.rocktable_choice.AppendItems([self._OM.get(rocktableuid).name for rocktableuid in self.rocktablemap])
        self.rocktable_choice.SetSelection(self.currentrocktableindex)
        self.rocktable_choice.Bind(wx.EVT_CHOICE, self.on_rocktable_choice)

        add_rocktype_button = wx.Button(self, label='ADD ROCK TYPE')
        add_rocktype_button.Bind(wx.EVT_BUTTON, self.on_add_rocktype)
        
        remove_rocktype_button = wx.Button(self, label='REM ROCK TYPE')
        remove_rocktype_button.Bind(wx.EVT_BUTTON, self.on_remove_rocktype)
        
        toolbar_sizer.Add(self.rocktable_choice, 1, wx.ALIGN_LEFT)
        toolbar_sizer.Add(add_rocktype_button, 0, wx.ALIGN_LEFT)
        toolbar_sizer.Add(remove_rocktype_button, 0, wx.ALIGN_LEFT)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(toolbar_sizer, proportion=0, flag=wx.EXPAND)
        main_sizer.Add(self.grid, proportion=1, flag=wx.EXPAND)

        self.SetSizer(main_sizer)

    @debugdecorator
    def on_rocktable_choice(self, event):
        idx = event.GetSelection()
        if idx != self.currentrocktableindex:
            self.currentrocktableindex = idx
            self.grid.SetTable(self.tables[self.currentwellindex][self.currentrocktableindex])

            self.grid.ForceRefresh()

    @debugdecorator
    def on_add_rocktype(self, event):
        self.grid.AppendRows()
        self.grid.ForceRefresh()

    
    def on_remove_rocktype(self, event):
        to_remove = self.grid.GetSelectedRows()
        self.grid.ClearSelection()
        for i in to_remove[::-1]:
            self.grid.DeleteRows(i)
        self.grid.ForceRefresh()

        
    @debugdecorator
    def on_cell_dlclick(self, event):
        if event.GetCol() == 1:
            row = event.GetRow()
            table = self.tables[self.currentwellindex][self.currentrocktableindex]
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
            dlg.Destroy()
        else:
            event.Skip()

    @debugdecorator
    def on_label_dlclick(self, event):
        row = event.GetRow()
        col = event.GetCol()
        table = self.tables[self.currentwellindex][self.currentrocktableindex]
        if row == -1 and col >= table.N_COLS:
            name, unit = table.get_nameunit(col)
            dlg = PropertyEntryDialog(self)
            dlg.set_value(name, unit)

            if dlg.ShowModal() == wx.ID_OK:
                name, unit = dlg.get_value()
                table.set_nameunit(col, name, unit)
                self.grid.ForceRefresh()
