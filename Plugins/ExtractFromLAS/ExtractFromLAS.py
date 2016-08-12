# -*- coding: utf-8 -*-
import wx
import numpy as np
import os

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager
from IO import LAS

def _remove_nans(data):
    goods = np.ones(len(data[0]), dtype=bool)

    for d in data:
        goods *= np.isfinite(d)
    
    new_data = []
    
    for d in data:
        new_data.append(d[goods])
    
    return new_data

def _interpolate(x, y, v):
    dx = x - v
    n = len(dx)
    c = np.copy(y)
    for i in range(n):
        for j in range(n):
            if i != j:
                c[i] *= dx[j]/(dx[j] - dx[i])
    return sum(c)

def _resample(x, y, new_x):
    if len(x) != len(y): return
    m = len(x)
    n = len(new_x)
    new_y = np.empty_like(new_x)
    new_y.fill(np.nan)
    index = 0
    for i in range(n):
        good = False
        while not good:
            if x[index] < new_x[i] < x[index+1]:
                if 1 <= index <= m-3:
                    new_y[i] = _interpolate(x[index-1:index+3], y[index-1:index+3], new_x[i])
                elif index == 0:
                    new_y[i] = _interpolate(x[:3], y[:3], new_x[i])
                else:
                    new_y[i] = _interpolate(x[-3:], y[-3:], new_x[i])
                good = True
            elif x[index] == new_x[i]:
                new_y[i] = y[index]
                good = True
            else:
                index += 1
    return new_y

def _extractfromlas(depth, newdepth, logs):
    newlogs = []
    
    for log in logs:
        newlog = np.empty(len(depth))
        newlog[:] = np.nan
        
        newdepth_, log_ = _remove_nans([newdepth, log])
        
        where = (depth > np.nanmin(newdepth_))*(depth < np.nanmax(newdepth_))
        
        newlog[where] = _resample(newdepth_, log_, depth[where])
        newlogs.append(newlog)
    
    return newlogs


class FileInput(wx.Panel):
    def __init__(self, parent, title, dirname, wildcard, *args, **kwargs):
        super(FileInput, self).__init__(parent, *args, **kwargs)
        
        self.title = title
        self.dirname = dirname
        self.wildcard = wildcard
        
        self.text_filename = wx.TextCtrl(self)
        
        button = wx.Button(self, wx.ID_ANY, label='...')
        button.Bind(wx.EVT_BUTTON, self.on_button)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(self.text_filename, proportion=1, flag=wx.EXPAND)
        sizer.Add(button)
        
        self.SetSizer(sizer)
    
    def on_button(self, event):
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        fdlg = wx.FileDialog(self, self.title, self.dirname, wildcard=self.wildcard, style=style)
        
        if fdlg.ShowModal() == wx.ID_OK:
            filename = fdlg.GetFilename()
            self.dirname = fdlg.GetDirectory()
            self.text_filename.SetValue(os.path.join(self.dirname, filename))
        
        fdlg.Destroy()
    
    def get_filename(self):
        return self.text_filename.GetValue()


class ExtractFromLASDialog(wx.Dialog):
    def __init__(self, parent, wellnames, depthnames, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(ExtractFromLASDialog, self).__init__(parent, *args, **kwargs)
        
        self.depthnames = depthnames
        
        sb_fileinput = wx.StaticBox(self, label=u"Arquivo de LAS:")
        sbs_fileinput = wx.StaticBoxSizer(sb_fileinput, wx.VERTICAL)
        self.fileinput = FileInput(self, u"Selecione o arquivo LAS", '', "Arquivos LAS (*.las)|*.las")
        self.fileinput.text_filename.Bind(wx.EVT_TEXT, self.on_file_changed)
        sbs_fileinput.Add(self.fileinput, proportion=1, flag=wx.EXPAND)
        
        sb_choice_well = wx.StaticBox(self, label=u"Poço:")
        sbs_choice_well = wx.StaticBoxSizer(sb_choice_well, wx.VERTICAL)
        self.choice_well = wx.Choice(self, wx.ID_ANY, choices=wellnames)
        self.choice_well.Bind(wx.EVT_CHOICE, self.on_well_choice)
        sbs_choice_well.Add(self.choice_well, proportion=1, flag=wx.EXPAND)
        
        sb_choice_depth = wx.StaticBox(self, label=u"Profundidade:")
        sbs_choice_depth = wx.StaticBoxSizer(sb_choice_depth, wx.VERTICAL)
        self.choice_depth = wx.Choice(self, wx.ID_ANY)
        sbs_choice_depth.Add(self.choice_depth, proportion=1, flag=wx.EXPAND)
        
        sb_choice_newdepth = wx.StaticBox(self, label=u"Nova profundidade:")
        sbs_choice_newdepth = wx.StaticBoxSizer(sb_choice_newdepth, wx.VERTICAL)
        self.choice_newdepth = wx.Choice(self, wx.ID_ANY)
        sbs_choice_newdepth.Add(self.choice_newdepth, proportion=1, flag=wx.EXPAND)
        
        sb_list_newlogs = wx.StaticBox(self, label=u"Novos perfis:")
        sbs_list_newlogs = wx.StaticBoxSizer(sb_list_newlogs, wx.VERTICAL)
        self.list_newlogs = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE)
        sbs_list_newlogs.Add(self.list_newlogs, proportion=1, flag=wx.EXPAND)

        sb_text_name = wx.StaticBox(self, label=u"Nome:")
        sbs_text_name = wx.StaticBoxSizer(sb_text_name, wx.VERTICAL)
        self.text_name = wx.TextCtrl(self)
        sbs_text_name.Add(self.text_name, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sbs_fileinput)
        vbox.Add(sbs_choice_well)
        vbox.Add(sbs_choice_depth)
        vbox.Add(sbs_choice_newdepth)
        vbox.Add(sbs_list_newlogs, proportion=1, flag=wx.EXPAND)
        vbox.Add(sbs_text_name)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(vbox)

        # self.SetSize((400, 800))
        self.SetTitle(u"TVD2MD")
    
    def get_filename(self):
        return self.fileinput.get_filename()
    
    def get_wellselection(self):
        return self.choice_well.GetSelection()
    
    def get_depthselection(self):
        return self.choice_depth.GetSelection()
    
    def get_newdepthselection(self):
        return self.choice_newdepth.GetSelection()
    
    def get_newlogsselection(self):
        return self.list_newlogs.GetSelections()
    
    def get_name(self):
        return self.text_name.GetValue()
        
    def on_file_changed(self, event):
        filename = self.fileinput.get_filename()
        try:
            las_file = LAS.open(filename, 'r')
            las_file.read()
            
            names = las_file.curvesnames
        except:
            names = []
            
        self.choice_newdepth.Clear()
        self.choice_newdepth.AppendItems(names)
        
        self.list_newlogs.Clear()
        self.list_newlogs.AppendItems(names)
    
    def on_well_choice(self, event):
        idx = self.choice_well.GetSelection()
        
        self.choice_depth.Clear()
        self.choice_depth.AppendItems(self.depthnames[idx])
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

class ExtractFromLASPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(ExtractFromLASPlugin, self).__init__()
        self._OM = ObjectManager(self)
    
    def run(self, uiparent):
        wellnames = []
        welluids = []
        
        depthnames = []
        depthuids = []
        
        for well in self._OM.list('well'):
            wellnames.append(well.name)
            welluids.append(well.uid)
            
            dns = []
            dus = []
            
            for depth in self._OM.list('depth', well.uid):
                dns.append(depth.name)
                dus.append(depth.uid)
            
            depthnames.append(dns)
            depthuids.append(dus)
        
        efld = ExtractFromLASDialog(uiparent, wellnames, depthnames)
        
        if efld.ShowModal() == wx.ID_OK:
            selwell = efld.get_wellselection()
            seldepth = efld.get_depthselection()
            name_ = efld.get_name()
            filename = efld.get_filename()
            selnewdepth = efld.get_newdepthselection()
            selnewlogs = efld.get_newlogsselection()
            
            welluid = welluids[selwell]
            depthuid = depthuids[selwell][seldepth]
            
            depth = self._OM.get(depthuid).data
            
            las_file = LAS.open(filename, 'r')
            las_file.read()
            
            newdepth = las_file.data[selnewdepth]
            
            logdata = [las_file.data[i] for i in selnewlogs]
            lognames = [las_file.curvesnames[i] for i in selnewlogs]
            logunits = [las_file.curvesunits[i] for i in selnewlogs]
            
            newlogdata = _extractfromlas(depth, newdepth, logdata)
            
            for name, unit, data in zip(lognames, logunits, newlogdata):
                new_log = self._OM.new('log', data, name='{}_{}'.format(name, name_), unit=unit)
                self._OM.add(new_log, parentuid=welluid)
        
        efld.Destroy()

    
