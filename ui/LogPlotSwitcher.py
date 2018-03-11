# -*- coding: utf-8 -*-

import wx
from wx.combo import BitmapComboBox
from collections import OrderedDict
from OM.Manager import ObjectManager

class Dialog(wx.Dialog):
    def __init__(self, parent, colors, color_names, i_color, welluid, lims, loguid, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(Dialog, self).__init__(parent, *args, **kwargs)
        
        self._OM = ObjectManager(self)

        self.cur_loguid = loguid
        self.lims = OrderedDict()
        for uid, lim in lims.items():
            self.lims[uid] = [str(a) for a in lim]

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        self.SetTitle(u"Alterar Perfil")

        fgs = wx.FlexGridSizer(3, 2, 4, 4)

        color_label = wx.StaticText(self, label="Cor: ")
        log_label = wx.StaticText(self, label="Perfil: ")
        lim_label = wx.StaticText(self, label="Limites: ")

        self.color_box = BitmapComboBox(self, style=wx.CB_READONLY)
        for c, cn in zip(colors, color_names):
            self.color_box.Append(cn, wx.EmptyBitmapRGBA(32, 2, c[0], c[1],
                                                         c[2], 255))

        self.log_box = wx.Choice(self)
        self.log_box.AppendItems([log.name for log in self._OM.list('log', welluid)])
        self.loguidmap = [log.uid for log in self._OM.list('log', welluid)]
        self.log_box.Bind(wx.EVT_CHOICE, self.on_log_select)

        lim_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lim1_ctrl = wx.TextCtrl(self, style=wx.TE_RIGHT)
        lim_sizer.Add(self.lim1_ctrl, 1, wx.EXPAND)

        self.lim2_ctrl = wx.TextCtrl(self, style=wx.TE_RIGHT)
        lim_sizer.Add(self.lim2_ctrl, 1, wx.EXPAND)

        fgs.AddMany([(color_label), (self.color_box, 1, wx.EXPAND),
                     (log_label), (self.log_box, 1, wx.EXPAND),
                     (lim_label), (lim_sizer, 1, wx.EXPAND)])

        fgs.AddGrowableCol(1, 1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(fgs, flag=wx.ALL | wx.EXPAND, border=8)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT, border=8)

        if i_color is not None:
            self.color_box.SetSelection(i_color)

        if loguid is not None:
            idx = self.loguidmap.index(loguid)
            self.log_box.SetSelection(idx)
            self.lim1_ctrl.SetValue(self.lims[loguid][0])
            self.lim2_ctrl.SetValue(self.lims[loguid][1])

        self.SetSizerAndFit(vbox)

    def on_log_select(self, event):
        idx = event.GetSelection()
        loguid = self.loguidmap[idx]
        if loguid != self.cur_loguid:
            l1 = self.lim1_ctrl.GetValue()
            l2 = self.lim2_ctrl.GetValue()
            if self.cur_loguid is not None:
                self.lims[self.cur_loguid] = [l1, l2]

            self.lim1_ctrl.SetValue(self.lims[loguid][0])
            self.lim2_ctrl.SetValue(self.lims[loguid][1])
            self.cur_loguid = loguid
        event.Skip(True)

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

    def get_loguid(self):
        idx = self.log_box.GetSelection()
        loguid = self.loguidmap[idx]
        return loguid

    def get_i_color(self):
        return self.color_box.GetSelection()

    def get_lim(self):
        return [float(self.lim1_ctrl.GetValue()),
                float(self.lim2_ctrl.GetValue())]
