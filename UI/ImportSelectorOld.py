# -*- coding: utf-8 -*-

import wx
from collections import OrderedDict


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        nb = wx.Notebook(self)
        
        self.pages = OrderedDict()
        self.pages["depth"] = wx.CheckListBox(nb)
        self.pages["log"] = wx.CheckListBox(nb)
        self.pages["partition"] = wx.CheckListBox(nb)

        self.pagenames = {}
        self.pagenames["depth"] = u"Profundidade"
        self.pagenames["log"] = u"Perfil"
        self.pagenames["partition"] = u"Partição"
        
        for key in self.pages.iterkeys():
            nb.AddPage(self.pages[key], self.pagenames[key])

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def set_curvesnames(self, curvenames):
        for page in self.pages.itervalues():
            page.Clear()
            page.AppendItems(curvenames)

    def set_selection(self, selection):
        for key, checked in selection.iteritems():
            self.pages[key].SetChecked(checked)

    def get_selection(self):
        selection = {}
        for key, page in self.pages.iteritems():
            selection[key] = page.GetChecked()
        return selection


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

        self.import_panel = Panel(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.import_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizer(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Importar como:")

    def set_curvesnames(self, curvenames):
        self.import_panel.set_curvesnames(curvenames)

    def set_selection(self, selection):
        self.import_panel.set_selection(selection)
    
    def get_selection(self):
        return self.import_panel.get_selection()

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
