# -*- coding: utf-8 -*-
"""
Created on Wed Jul 6 15:14:47 2016

@author: rtabelini
"""

import wx
import numpy as np
import os

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager

class FileInput(wx.Panel):
    def __init__(self, parent, title, dirname, wildcard, text_name, *args, **kwargs):
        super(FileInput, self).__init__(parent, *args, **kwargs)
        
        self.title = title
        self.dirname = dirname
        self.wildcard = wildcard
        
        self.text_filename = wx.TextCtrl(self)
        self.text_name = text_name
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
            self.text_name.SetValue (filename)
                    
        fdlg.Destroy()
    
    def get_filename(self):
        return self.text_filename.GetValue()


class CORE(wx.Dialog):
    def __init__(self, parent, wellnames, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(CORE, self).__init__(parent, *args, **kwargs)
        
        self.radiowell = wx.RadioButton(self,-1, "Op1", style=wx.RB_GROUP)
        self.radiogeneral = wx.RadioButton(self,-1, "Op2")
        self.choice_well = wx.Choice(self, wx.ID_ANY, choices=wellnames)
        self.text_name = wx.TextCtrl(self)
        self.text_core = wx.TextCtrl(self)

        sb_fileinput = wx.StaticBox(self, label=u"Arquivo de dados .h5:")
        sbs_fileinput = wx.StaticBoxSizer(sb_fileinput, wx.HORIZONTAL)
        self.fileinput = FileInput(self, u"Selecione o arquivo h5", '', "Arquivos h5 (*.h5)|*.h5", self.text_core)
        sbs_fileinput.Add(self.fileinput, proportion=1, flag=wx.EXPAND)
                
        sb_choice_well = wx.StaticBox(self)                
        sbs_choice_well = wx.StaticBoxSizer(sb_choice_well, wx.VERTICAL)        
        sbs_choice_well.Add(self.choice_well, proportion=1, flag=wx.EXPAND)        
        sbs_choice_well.Add(self.text_name, proportion=1, flag=wx.EXPAND)
        
        sbs_radio_well = wx.FlexGridSizer(rows=2, cols=2, hgap=5, vgap=5)
        sbs_radio_well.Add(self.radiowell,  proportion=2)
        sbs_radio_well.Add(self.choice_well, proportion=1, flag=wx.EXPAND)
        sbs_radio_well.Add(self.radiogeneral,  proportion=1)        
        sbs_radio_well.Add(self.text_name, proportion=1, flag=wx.EXPAND)
        radiobox = wx.BoxSizer(wx.HORIZONTAL)
        radiobox.Add(sbs_radio_well)
        self.text_name.Enable(False)
        for eachRadio in [self.radiowell, self.radiogeneral]:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, eachRadio)
        self.selectedText = self.choice_well
        self.texts = {"Op1": self.choice_well, "Op2": self.text_name}

        sb_text_name = wx.StaticBox(self, label=u"Nome:")
        sbs_text_name = wx.StaticBoxSizer(sb_text_name, wx.VERTICAL)
#        self.text_core = wx.TextCtrl(self)
        sbs_text_name.Add(self.text_core, proportion=1, flag=wx.EXPAND)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)
        

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(sbs_fileinput)
        vbox.Add(sbs_radio_well)
        vbox.Add(sbs_text_name)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        
        self.SetSizerAndFit(vbox)
        self.SetTitle(u"DB Load")
        
        
    def OnRadio(self, event):
        if self.selectedText:
            self.selectedText.Enable(False)
        radioSelected = event.GetEventObject()
        text = self.texts[radioSelected.GetLabel()]
        text.Enable(True)
        self.selectedText = text
            
    def get_filename(self):
        return self.fileinput.get_filename()
    
    def get_wellselection(self):
        if self.choice_well.IsEnabled():
            return self.choice_well.GetSelection()
        if self.text_name.IsEnabled():
            return self.text_name.GetValue()
        else:
            print 'no well selected'
        
    def get_newcoreselection(self):
        return self.text_core.GetValue()
    
    def get_name(self):
        return self.text_name.GetValue()
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

class COREPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(COREPlugin, self).__init__()
        self._OM = ObjectManager(self)
    
    def run(self, uiparent):
        self.wellnames = []
        self.welluids = []
        
        for well in self._OM.list('well'):
            self.wellnames.append(well.name)
            self.welluids.append(well.uid)

        efld = CORE(uiparent, self.wellnames)
        
        if efld.ShowModal() == wx.ID_OK:
            selwell = efld.get_wellselection()
#            dbtext = efld.get_filename()
            nome = efld.get_newcoreselection()
            x = np.empty(0)
            if len(self._OM.list('well')) == 0:
                well = self._OM.new('well', name=selwell)
                self._OM.add(well)
                core = self._OM.new('core', x, name=nome)
                self._OM.add (core, well.uid)
            else:
                core = self._OM.new('core', x, name=nome)
                self._OM.add (core, self.welluids[selwell])
        efld.Destroy()

    
