# -*- coding: utf-8 -*-

import wx


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

        self.wells = None

        self.choice = wx.Choice(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.choice, flag=wx.ALIGN_CENTER)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizer(vbox)

        self.SetSize((300, 200))
        self.SetTitle(u"Seletcione o poço")

    def set_wells(self, wells):
        self.choice.Clear()
        self.choice.AppendItems([str(a) for a in wells])
        if len(wells) == 1:
            self.choice.SetSelection(0)

    def get_well_selection(self):
        return self.choice.GetSelection()

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
