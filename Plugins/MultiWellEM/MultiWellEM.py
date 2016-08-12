# -*- coding: utf-8 -*-

import wx
import numpy as np

from Algo import Clustering
from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager
from Basic.Colors import COLOR_CYCLE_RGB

def _multiwellem(data, nc, nullvalue=-1):
        index_bounds = [len(data[0][0])]
        for i in range(1, len(data)):
            index_bounds.append(index_bounds[i-1] + len(data[i][0]))
        
        stacked_data = np.hstack(data).T
        
        nd, nf = stacked_data.shape
        
        nans = Clustering.locate_nans(stacked_data)
        
        clusters_, info = Clustering.expectation_maximization(stacked_data[~nans], nc, req_info=['means', 'covars'])
        clusters_, argsort = Clustering.reorder_clusters(clusters_, info['means'], info['covars'])
        
        clusters = np.empty(nd, dtype=int)
        clusters[:] = nullvalue
        
        clusters[~nans] = clusters_

        splitted_clusters = [clusters[:index_bounds[0]]]
        
        for i in range(len(index_bounds)-1):    
            splitted_clusters.append(clusters[index_bounds[i]:index_bounds[i+1]])
        
        return splitted_clusters


class MultiChoice(wx.Panel):
    def __init__(self, parent, labels, *args, **kwargs):
        super(MultiChoice, self).__init__(parent, *args, **kwargs)
        self.labels = labels
        self.choices = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.add_choice()

    def add_choice(self):
        choice = wx.Choice(self)
        choice.Append('')
        for label in self.labels:
            choice.Append(label)
        choice.Bind(wx.EVT_CHOICE, self.on_choice)
        choice.SetSelection(0)
        self.choices.append(choice)
        self.sizer.Add(choice, proportion=0, flag=wx.EXPAND | wx.BOTTOM, border=2)
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
            selection.append(choice.GetSelection() - 1)
        return selection


class WellSelectionDialog(wx.Dialog):
    def __init__(self, parent, choices, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(WellSelectionDialog, self).__init__(parent, *args, **kwargs)
        
        self.choices = choices
        
        style = wx.LB_MULTIPLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB
        self.listbox = wx.ListBox(self, wx.ID_ANY, choices=self.choices, style=style)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.listbox, proportion=1, flag=wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizerAndFit(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Selecionar poços:")
    
    def get_selection(self):
        return self.listbox.GetSelections()
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)


class MultiWellEMDialog(wx.Dialog):
    def __init__(self, parent, wellnames, lognames, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(MultiWellEMDialog, self).__init__(parent, *args, **kwargs)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        self.multichoices = []
        
        for wn, lns in zip(wellnames, lognames):
            multichoice = MultiChoice(self, lns)
            self.multichoices.append(multichoice)
            
            sb = wx.StaticBox(self, label=wn)
            sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
            sbs.Add(multichoice, proportion=1, flag=wx.EXPAND)
            hbox.Add(sbs, proportion=1, flag=wx.EXPAND)
        
        sb_nc = wx.StaticBox(self, label=u"Número de clusters:")
        sbs_nc = wx.StaticBoxSizer(sb_nc, wx.VERTICAL)
        self.spin_nc = wx.SpinCtrl(self, min=2, max=20, initial=2)
        sbs_nc.Add(self.spin_nc, proportion=1, flag=wx.EXPAND)

        sb_text_name = wx.StaticBox(self, label=u"Nome:")
        sbs_text_name = wx.StaticBoxSizer(sb_text_name, wx.VERTICAL)
        self.text_name = wx.TextCtrl(self)
        sbs_text_name.Add(self.text_name, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=1, flag=wx.EXPAND)
        vbox.Add(sbs_nc)
        vbox.Add(sbs_text_name)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Multi Well EM")
    
    def get_selection(self):
        return [multichoice.get_selection() for multichoice in self.multichoices]
    
    def get_nclusters(self):
        return self.spin_nc.GetValue()
    
    def get_name(self):
        return self.text_name.GetValue()
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
    

class MultiWellEMPlugin(SimpleDialogPlugin):
    def __init__(self):
        super(MultiWellEMPlugin, self).__init__()
        self._OM = ObjectManager(self)

    def run(self, uiparent):
        wellnames = []
        welluids = []
        
        for well in self._OM.list('well'):
            wellnames.append(well.name)
            welluids.append(well.uid)
        
        wsd = WellSelectionDialog(uiparent, wellnames)
        
        if wsd.ShowModal() == wx.ID_OK:
            selection1 = wsd.get_selection()
            
            selwellnames = [wellnames[index] for index in selection1]
            selwelluids = [welluids[index] for index in selection1]
            
            lognames = []
            loguids = []
            
            for welluid in selwelluids:
                lns = []
                lus = []
                
                for log in self._OM.list('log', welluid):
                    lns.append(log.name)
                    lus.append(log.uid)
                
                lognames.append(lns)
                loguids.append(lus)
            
            mwemd = MultiWellEMDialog(uiparent, selwellnames, lognames)
            
            if mwemd.ShowModal() == wx.ID_OK:
                selection2 = mwemd.get_selection()
                nc = mwemd.get_nclusters()
                name = mwemd.get_name()
                
                logdata = []
                for sel, lus in zip(selection2, loguids):
                    logdata.append([self._OM.get(lus[i]).data for i in sel])
                
                clusters = _multiwellem(logdata, nc)
                
                for welluid, cluster in zip(selwelluids, clusters):
                    partition = self._OM.new('partition', name=name)
                    self._OM.add(partition, parentuid=welluid)
                    
                    for i in range(nc):
                        partname = "{}_{:0>3}".format(name, i+1)
                        color = COLOR_CYCLE_RGB[i % len(COLOR_CYCLE_RGB)]
                        part = self._OM.new('part', cluster==i, name=partname, color=color)
                        self._OM.add(part, parentuid=partition.uid)
            
            mwemd.Destroy()
        
        wsd.Destroy()
        