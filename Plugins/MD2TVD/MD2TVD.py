# -*- coding: utf-8 -*-
import wx
import numpy as np
import os

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager

def _md2tvd(MD, md, incl, tvd):
    TVD = np.empty(len(MD))
    INCL = np.empty(len(MD))
    for i in range(len(md)-1):
        w = (MD >= md[i])*(MD <= md[i+1])
        if incl[i] == incl[i+1]:
            theta = np.ones(np.sum(w), dtype=np.float64)*incl[i]
            TVD[w] = tvd[i] + (MD[w] - md[i])*np.cos(theta)
            INCL[w] = theta
        else:
            theta = (incl[i]*(md[i+1] - MD[w]) + incl[i+1]*(MD[w] - md[i]))/(md[i+1] - md[i])
            TVD[w] = tvd[i] + (md[i+1] - md[i])*(np.sin(theta) - np.sin(incl[i]))/(incl[i+1] - incl[i])
            INCL[w] = theta
    
    return TVD, INCL

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


class MD2TVDDialog(wx.Dialog):
    def __init__(self, parent, wellnames, depthnames, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(MD2TVDDialog, self).__init__(parent, *args, **kwargs)
        
        self.depthnames = depthnames
        
        sb_fileinput = wx.StaticBox(self, label=u"Arquivo de inclinação:")
        sbs_fileinput = wx.StaticBoxSizer(sb_fileinput, wx.VERTICAL)
        self.fileinput = FileInput(self, u"Selecione o arquivo de inclinação", '', '*.*')
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

        sb_text_name = wx.StaticBox(self, label=u"Nome:")
        sbs_text_name = wx.StaticBoxSizer(sb_text_name, wx.VERTICAL)
        self.text_name = wx.TextCtrl(self)
        sbs_text_name.Add(self.text_name, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sbs_fileinput, proportion=1, flag=wx.EXPAND)
        vbox.Add(sbs_choice_well)
        vbox.Add(sbs_choice_depth)
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
    
    def get_name(self):
        return self.text_name.GetValue()
    
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

class MD2TVDPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(MD2TVDPlugin, self).__init__()
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
        
        m2td = MD2TVDDialog(uiparent, wellnames, depthnames)
        
        if m2td.ShowModal() == wx.ID_OK:
            selwell = m2td.get_wellselection()
            seldepth = m2td.get_depthselection()
            name = m2td.get_name()
            filename = m2td.get_filename()
            
            welluid = welluids[selwell]
            depthuid = depthuids[selwell][seldepth]
            
            MD = self._OM.get(depthuid).data
            
            md, incl, tvd = np.loadtxt(filename).T
            
            TVD, INCL = _md2tvd(MD, md, incl*np.pi/180.0, tvd)
            INCL *= 180.0/np.pi
            
            new_depth = self._OM.new('depth', TVD, name='TVD_{}'.format(name))
            self._OM.add(new_depth, parentuid=welluid)
            
            new_log = self._OM.new('log', INCL, name='INCL_{}'.format(name))
            self._OM.add(new_log, parentuid=welluid)
        
        m2td.Destroy()

    
