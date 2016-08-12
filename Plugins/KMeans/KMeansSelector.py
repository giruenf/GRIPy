# -*- coding: utf-8 -*-

import wx
from OM.Manager import ObjectManager


class SelectionLogPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(SelectionLogPanel, self).__init__(*args, **kwargs)
        self._OM = ObjectManager(self)
        self.well = None
        self.log_tuple = None
        self.choices = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def add_choice(self):
        choice = wx.Choice(self)
        choice.Append('')
        for i, log in enumerate(self.log_tuple):       
            choice.Append(log.attributes.get('name', '{}.{}'.format(*log.uid)))
        choice.Bind(wx.EVT_CHOICE, self.on_choice)
        choice.SetSelection(0)
        self.choices.append(choice)
        self.sizer.Add(choice, proportion=0, flag=wx.EXPAND | wx.BOTTOM,
                       border=2)
        self.sizer.Layout()

    def remove_choice(self, i):
        choice = self.choices.pop(i)
        self.sizer.Remove(choice)
        self.sizer.Layout()
        choice.Hide()
        del choice

    def on_choice(self, event):
        i = self.choices.index(event.GetEventObject())
        j = event.GetSelection()
        if i == len(self.choices) - 1:
            if j != 0:
                self.add_choice()
        else:
            if j == 0:
                self.remove_choice(i)
        event.Skip(True)

    def get_selection(self):
        selection = []
        for choice in self.choices[:-1]:
            selection.append(self.log_tuple[choice.GetSelection()-1].uid)
        return selection

    def set_well(self, well):
        for i in range(len(self.choices)-1, -1, -1):
            self.remove_choice(i)
        self.well = well
        self.log_tuple = self._OM.list('log', self.well)
        self.choices = []
        if self.well is not None:
            self.add_choice()




class Dialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(Dialog, self).__init__(*args, **kwargs)

        self._OM = ObjectManager(self)
        self._OM.addcallback("add", self.on_wells_change)
        self._OM.addcallback("post-remove", self.on_wells_change)

        self._mapui = []

        sb_well = wx.StaticBox(self, label=u"Poço:")
        sbs_well = wx.StaticBoxSizer(sb_well, wx.VERTICAL)
        self.well_choice = wx.Choice(self)
        self.well_choice.Bind(wx.EVT_CHOICE, self.on_select_well)
        sbs_well.Add(self.well_choice, proportion=1, flag=wx.EXPAND)     

        sb_logs = wx.StaticBox(self, label=u"Perfis de entrada:")
        sbs_logs = wx.StaticBoxSizer(sb_logs, wx.VERTICAL)
        self.selection_log_panel = SelectionLogPanel(self)
        sbs_logs.Add(self.selection_log_panel, proportion=4, flag=wx.EXPAND)

        sb_k = wx.StaticBox(self, label=u"Número de Partições(k):")
        sbs_k = wx.StaticBoxSizer(sb_k, wx.VERTICAL)
        self.spin_k = wx.SpinCtrl(self, value='1', size=(60, -1))
        self.spin_k.SetRange(1, 30)        
        sbs_k.Add(self.spin_k, proportion=1, flag=wx.EXPAND)

        sb_partition_name = wx.StaticBox(self, label=u"Nome:")
        sbs_partition_name = wx.StaticBoxSizer(sb_partition_name, wx.VERTICAL)
        self.partition_name = wx.TextCtrl(self)
        sbs_partition_name.Add(self.partition_name, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)
        
        mainbox = wx.BoxSizer(wx.VERTICAL)
        mainbox.Add(sbs_well, proportion=1, flag=wx.EXPAND)
        mainbox.Add(sbs_logs, proportion=7, flag=wx.EXPAND)
        mainbox.Add(sbs_k, proportion=1, flag=wx.EXPAND)
        mainbox.Add(sbs_partition_name, proportion=1, flag=wx.EXPAND)
        mainbox.Add(button_sizer, flag=wx.ALIGN_CENTER)
        
        self.SetSizer(mainbox)
        self.SetSize((300, 500))
        self.SetTitle(u"Seletor de Parametros do K-Means")
        self.on_wells_change(None)

    def on_wells_change(self, uid):
        wellnames = []
        self._mapui = []
        self.well_choice.Clear()
        self.set_selected_well(None)
        for well in self._OM.list('well'):
            self._mapui.append(well.uid)
            wellnames.append(well.name)
        self.well_choice.AppendItems(wellnames)
        if len(wellnames) == 1:
            self.well_choice.SetSelection(0)
            self.set_selected_well(self._mapui[0])

    def set_selected_well(self, uid):
        self.selection_log_panel.set_well(uid)

    def get_well(self):
        return self._mapui[self.well_choice.GetSelection()]
        
    def get_k(self):
        return self.spin_k.GetValue()
        
    def get_selected_logs(self):
        return self.selection_log_panel.get_selection()

    def get_partition_name(self):
        return self.partition_name.GetValue()

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

    def on_select_well(self, event):
        i = event.GetSelection()
        self.set_selected_well(self._mapui[i])

