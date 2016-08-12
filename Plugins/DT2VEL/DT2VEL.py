# -*- coding: utf-8 -*-
import wx
import numpy as np

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager


class DT2VELDialog(wx.Dialog):
    def __init__(self, parent, wellnames, lognames, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(DT2VELDialog, self).__init__(parent, *args, **kwargs)
        
        self.lognames = lognames
        
        sb_choice_well = wx.StaticBox(self, label=u"Poço:")
        sbs_choice_well = wx.StaticBoxSizer(sb_choice_well, wx.VERTICAL)
        self.choice_well = wx.Choice(self, wx.ID_ANY, choices=wellnames)
        self.choice_well.Bind(wx.EVT_CHOICE, self.on_well_choice)
        sbs_choice_well.Add(self.choice_well, proportion=1, flag=wx.EXPAND)
        
        sb_choice_log = wx.StaticBox(self, label=u"Perfil sônico:")
        sbs_choice_log = wx.StaticBoxSizer(sb_choice_log, wx.VERTICAL)
        self.choice_log = wx.Choice(self, wx.ID_ANY)
        sbs_choice_log.Add(self.choice_log, proportion=1, flag=wx.EXPAND)

        sb_text_name = wx.StaticBox(self, label=u"Nome:")
        sbs_text_name = wx.StaticBoxSizer(sb_text_name, wx.VERTICAL)
        self.text_name = wx.TextCtrl(self)
        sbs_text_name.Add(self.text_name, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sbs_choice_well)
        vbox.Add(sbs_choice_log)
        vbox.Add(sbs_text_name)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(vbox)

        # self.SetSize((400, 800))
        self.SetTitle(u"DT2VEL")
    
    def get_wellselection(self):
        return self.choice_well.GetSelection()
    
    def get_logselection(self):
        return self.choice_log.GetSelection()
    
    def get_name(self):
        return self.text_name.GetValue()
    
    def on_well_choice(self, event):
        idx = self.choice_well.GetSelection()
        
        self.choice_log.Clear()
        self.choice_log.AppendItems(self.lognames[idx])
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

class DT2VELPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(DT2VELPlugin, self).__init__()
        self._OM = ObjectManager(self)
    
    def run(self, uiparent):
        wellnames = []
        welluids = []
        
        lognames = []
        loguids = []
        
        for well in self._OM.list('well'):
            wellnames.append(well.name)
            welluids.append(well.uid)
            
            lns = []
            lus = []
            
            for log in self._OM.list('log', well.uid):
                lns.append(log.name)
                lus.append(log.uid)
            
            lognames.append(lns)
            loguids.append(lus)
        
        d2vd = DT2VELDialog(uiparent, wellnames, lognames)
        
        if d2vd.ShowModal() == wx.ID_OK:
            selwell = d2vd.get_wellselection()
            sellog = d2vd.get_logselection()
            name = d2vd.get_name()
            
            welluid = welluids[selwell]
            loguid = loguids[selwell][sellog]
            
            dtlog = self._OM.get(loguid).data
            
            newvlog = 3.048E5/dtlog
            
            new_log = self._OM.new('log', newvlog, name=name)
            self._OM.add(new_log, parentuid=welluid)
        
        d2vd.Destroy()

    
