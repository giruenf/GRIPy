import sys

import wx
import wx.lib.agw.ultimatelistctrl as ULC

class Dialog(wx.Dialog):
    def __init__(self, parent, names, units, curvetypes, datatypes, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(Dialog, self).__init__(parent, *args, **kwargs)
        
        self.names = names
        self.units = units
        self.curvetypes = curvetypes
        self.datatypes = datatypes
        
        self.nrows = len(self.names)
        
        style = wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL | ULC.ULC_HAS_VARIABLE_ROW_HEIGHT
        self.list = ULC.UltimateListCtrl(self, wx.ID_ANY, agwStyle=style)

        self._fill_list()

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizerAndFit(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Importar como:")
    
    def _fill_list(self):
        self.list.InsertColumn(0, 'Nome')
        self.list.InsertColumn(1, 'Unidade')
        self.list.InsertColumn(2, 'Tipo de curva')
        self.list.InsertColumn(3, 'Tipo de dado')
        
        self.curvetype_choices = []
        self.datatype_choices = []
        
        for i in range(self.nrows):
            curvetype_choice = wx.Choice(self.list, -1, choices=['']+self.curvetypes)
            datatype_choice = wx.Choice(self.list, -1, choices=['']+self.datatypes)
        
            index = self.list.InsertStringItem(sys.maxint, self.names[i])
            self.list.SetStringItem(index, 1, self.units[i])
            self.list.SetStringItem(index, 2, ' ')
            self.list.SetStringItem(index, 3, ' ')
            
            self.list.SetItemWindow(index, 2, curvetype_choice, expand=True)
            self.list.SetItemWindow(index, 3, datatype_choice, expand=True)
                        
            self.curvetype_choices.append(curvetype_choice)
            self.datatype_choices.append(datatype_choice)

    def set_curvetype(self, i, curvetype):
        if curvetype in self.curvetypes:
            index = 1 + self.curvetypes.index(curvetype)
        else:
            index = 0
        self.curvetype_choices[i].SetSelection(index)
    
    def get_curvetype(self, i):
        index = self.curvetype_choices[i].GetSelection()
        if index == 0:
            return ''
        else:
            return self.curvetypes[index-1]

    def set_curvetypes(self, curvetypes):
        for i in range(self.nrows):
            self.set_curvetype(i, curvetypes[i])
    
    def get_curvetypes(self):
        curvetypes = []
        
        for i in range(self.nrows):
            curvetypes.append(self.get_curvetype(i))
        
        return curvetypes
    
    def set_datatype(self, i, datatype):
        if datatype in self.datatypes:
            index = 1 + self.datatypes.index(datatype)
        else:
            index = 0
        self.datatype_choices[i].SetSelection(index)
    
    def get_datatype(self, i):
        index = self.datatype_choices[i].GetSelection()
        if index == 0:
            return ''
        else:
            return self.datatypes[index-1]

    def set_datatypes(self, datatypes):
        for i in range(self.nrows):
            self.set_datatype(i, datatypes[i])
    
    def get_datatypes(self):
        datatypes = []
        
        for i in range(self.nrows):
            datatypes.append(self.get_datatype(i))
        
        return datatypes

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
