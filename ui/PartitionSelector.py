# -*- coding: utf-8 -*-

import wx
from OM.Manager import ObjectManager

class Dialog(wx.Dialog):
    
    def __init__(self, welluid, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        
        self.welluid = welluid
        self.partitionuid = None
        
        self._OM = ObjectManager(self)
        
        self.partitionmap = [pttn.uid for pttn in self._OM.list('partition', self.welluid)]
        partitionchoiceitems = [pttn.name for pttn in self._OM.list('partition', self.welluid)]
        
        self.partmap = []
        
        self.partitionchoice = wx.Choice(self)
        self.partitionchoice.AppendItems(partitionchoiceitems)
        self.partitionchoice.Bind(wx.EVT_CHOICE, self.on_partition_choice)
        
        self.partslistbox = wx.CheckListBox(self)
        
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.partitionchoice, proportion=0, flag=wx.EXPAND)
        main_sizer.Add(self.partslistbox, proportion=1, flag=wx.EXPAND)
        main_sizer.AddSizer(button_sizer, proportion=0, flag=wx.ALIGN_RIGHT)
        
        self.SetSizer(main_sizer)
        
        if len(self.partitionmap) == 1:
            self.set_partitionuid(self.partitionmap[0])
    
    def reset_partslistbox(self):
        self.partmap = [part.uid for part in self._OM.list('part', self.partitionuid)]
        partslistboxitems = [part.name for part in self._OM.list('part', self.partitionuid)]
        
        self.partslistbox.Clear()
        self.partslistbox.AppendItems(partslistboxitems)
        
    def on_partition_choice(self, event):
        idx = event.GetSelection()
        self.partitionuid = self.partitionmap[idx]
        self.reset_partslistbox()
    
    def get_partitionuid(self):
        return self.partitionuid
    
    def get_partsuids(self):
        return [self.partmap[i] for i in self.partslistbox.GetChecked()]

    def set_partitionuid(self, partitionuid):
        if partitionuid:
            self.partitionuid = partitionuid
            idx = self.partitionmap.index(self.partitionuid)
            self.partitionchoice.SetSelection(idx)
            self.reset_partslistbox()

    def set_partsuids(self, partsuids):
        if partsuids:
            idxs = [self.partmap.index(partuid) for partuid in partsuids]
            self.partslistbox.SetChecked(idxs)
        