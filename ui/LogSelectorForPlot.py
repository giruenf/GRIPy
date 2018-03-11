# -*- coding: utf-8 -*-

import wx
from wx.lib.agw import ultimatelistctrl as ULC

from OM.Manager import ObjectManager

MEDIUM_GREY = wx.Colour(224, 224, 224)


class Panel(wx.Panel):
    CB_COL_WIDTH = 24
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self.ultimate_list = ULC.UltimateListCtrl(self, agwStyle=ULC.ULC_REPORT | ULC.ULC_NO_HEADER | ULC.ULC_NO_HIGHLIGHT)
        self.ultimate_list.InsertColumn(0, '', width=180)
        self.ultimate_list.InsertColumn(1, '', width=self.CB_COL_WIDTH)

        self.state = []

        self._OM = ObjectManager(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.ultimate_list, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(ULC.EVT_LIST_ITEM_CHECKED, self.on_checked, self.ultimate_list)
        self.Bind(ULC.EVT_LIST_ITEM_MIDDLE_CLICK, self.on_middle, self.ultimate_list)

        self._mapui = {}  # TODO: Por que dicionário e não lista?

    def set_well(self, uid):
        self.state = []
        self._mapui.clear()
        self.ultimate_list.DeleteAllItems()
        m = self.ultimate_list.GetColumnCount() - 1
        for i in range(m, 1, -1):
            self.ultimate_list.DeleteColumn(i)

        if not uid:
            return

        for i, log in enumerate(self._OM.list('log', uid)):
            logname = log.attributes.get('name', '{}.{}'.format(*log.uid))
            self.ultimate_list.InsertStringItem(i, logname)
            self.ultimate_list.SetStringItem(i, 1, '', it_kind=1)
            self.state.append([False])
            self._mapui[i] = log.uid

        for i in range(1, self.ultimate_list.GetItemCount(), 2):
            self.ultimate_list.SetItemBackgroundColour(i, MEDIUM_GREY)

    def get_map(self):
        m = len(self.state)
        n = len(self.state[0]) - 1
        map_ = []
        for i in range(n):
            m_ = []
            for j in range(m):
                if self.state[j][i]:
                    m_.append(self._mapui[j])
            map_.append(m_)

        mmax = max(len(a) for a in map_)
        if mmax < 3:
            mmax = 3
        for i in range(n):
            for j in range(len(map_[i]), mmax):
                map_[i].append(None)

        return map_

    def on_checked(self, event):
        i = event.GetIndex()
        n = self.ultimate_list.GetItemCount()
        m = self.ultimate_list.GetColumnCount() - 1
        for j in range(m):
            checked = not self.state[i][j]
            if checked == self.ultimate_list.GetItem(i, j+1).IsChecked():
                self.state[i][j] = checked
                break

        if checked:
            if j == m-1:
                self.ultimate_list.InsertColumn(j+2, '', width=self.CB_COL_WIDTH)
                for i in range(n):
                    self.ultimate_list.SetStringItem(i, j+2, '', it_kind=1)
                    self.state[i].append(False)
        else:
            if not sum(self.state[i][j] for i in range(n)):
                self.ultimate_list.DeleteColumn(j+1)
                for i in range(n):
                    self.state[i].pop(j)

        event.Skip(True)

    def on_middle(self, event):
        print self.get_map()


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
        self._OM.subscribe(self.on_wells_changed, 'add')
        self._OM.subscribe(self.on_wells_changed, 'post_remove')    
        #self._OM.addcallback("add", self.on_wells_change)
        #self._OM.addcallback("post-remove", self.on_wells_change)

        self._mapui = []

        self.choice = wx.Choice(self)

        self.choice.Bind(wx.EVT_CHOICE, self.on_select)

        self.ls_panel = Panel(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.choice, flag=wx.ALIGN_CENTER)
        vbox.Add(self.ls_panel, 1, wx.ALL | wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizer(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Seletor de Perfis para Plotagem")

        self.on_wells_change(None)

    def on_wells_changed(self, objuid):
        wellnames = []
        self._mapui = []
        self.choice.Clear()
        self.set_well(None)

        for well in self._OM.list('well'):
            self._mapui.append(well.uid)
            wellnames.append(well.name)

        self.choice.AppendItems(wellnames)

        if len(wellnames) == 1:
            self.choice.SetSelection(0)
            self.set_well(self._mapui[0])

    def set_well(self, uid):
        self.ls_panel.set_well(uid)

    def get_well(self):
        return self._mapui[self.choice.GetSelection()]

    def get_map(self):
        return self.ls_panel.get_map()

#    def hide_combo_box(self):
#        self.set_wells([])
#        self.choice.Hide()
#
#    def show_combo_box(self):
#        self.choice.Show()

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

    def on_select(self, event):
        i = event.GetSelection()
        self.set_well(self._mapui[i])
    
    def __del__(self):
        self._OM.removecallback("add", self.on_wells_change)
        self._OM.removecallback("post-remove", self.on_wells_change)
        super(Dialog, self).__del__()
