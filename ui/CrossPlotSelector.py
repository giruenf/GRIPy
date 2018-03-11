# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 15:03:02 2015

@author: fsantos
"""

import wx
from OM.Manager import ObjectManager


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)
        
        self._OM = ObjectManager(self)
        
        self.xselector = wx.Choice(self)
        self.yselector = wx.Choice(self)
        self.zselector = wx.Choice(self)
        self.wselector = wx.Choice(self)
        
        gridsizer = wx.FlexGridSizer(rows=4, cols=2, hgap=5, vgap=5)
        gridsizer.Add(wx.StaticText(self, label="Eixo x: "), 0, wx.ALIGN_RIGHT)
        gridsizer.Add(self.xselector, 1, wx.EXPAND)
        gridsizer.Add(wx.StaticText(self, label="Eixo y: "), 0, wx.ALIGN_RIGHT)
        gridsizer.Add(self.yselector, 1, wx.EXPAND)
        gridsizer.Add(wx.StaticText(self, label="Barra de cor: "), 0, wx.ALIGN_RIGHT)
        gridsizer.Add(self.zselector, 1, wx.EXPAND)
        gridsizer.Add(wx.StaticText(self, label="Particionamento: "), 0, wx.ALIGN_RIGHT)
        gridsizer.Add(self.wselector, 1, wx.EXPAND)
        
        self.SetSizer(gridsizer)
        
        self.xmap = []
        self.ixmap = {}
        self.ymap = []
        self.iymap = {}
        self.zmap = []
        self.izmap = {}
        self.wmap = []
        self.iwmap = {}
        
        self.welluid = None
    
    def set_welluid(self, welluid):
        self.welluid = welluid        
        
        xitems = []
        yitems = []
        zitems = []
        witems = []
        
        self.xmap = []
        self.ymap = []
        self.zmap = []
        self.wmap = []
        
        self.ixmap.clear()
        self.iymap.clear()
        self.izmap.clear()
        self.iwmap.clear()
        
#        zitems.append('')      Permitir seleção vazia para z
#        self.zmap.append(None)
#        
#        witems.append('')      Permitir seleção vazia para w
#        self.wmap.append(None)
        
        for log in self._OM.list('log', welluid):
            xitems.append(log.name)
            self.xmap.append(log.uid)
            self.ixmap[log.uid] = len(self.xmap) - 1
            
            yitems.append(log.name)
            self.ymap.append(log.uid)
            self.iymap[log.uid] = len(self.ymap) - 1
            
            zitems.append(log.name)
            self.zmap.append(log.uid)
            self.izmap[log.uid] = len(self.zmap) - 1
        
        for depth in self._OM.list('depth', welluid):
            zitems.append(depth.name)
            self.zmap.append(depth.uid)
            self.izmap[depth.uid] = len(self.zmap) - 1
        
        for partition in self._OM.list('partition', welluid):
            zitems.append(partition.name)
            self.zmap.append(partition.uid)
            self.izmap[partition.uid] = len(self.zmap) - 1
            
            witems.append(partition.name)
            self.wmap.append(partition.uid)
            self.iwmap[partition.uid] = len(self.wmap) - 1
        
        self.xselector.Clear()
        self.yselector.Clear()
        self.zselector.Clear()
        self.wselector.Clear()
        
        self.xselector.AppendItems(xitems)
        self.yselector.AppendItems(yitems)
        self.zselector.AppendItems(zitems)
        self.wselector.AppendItems(witems)
        
    def set_xuid(self, xuid):
        self.xselector.SetSelection(self.ixmap.get(xuid, wx.NOT_FOUND))
    
    def set_yuid(self, yuid):
        self.yselector.SetSelection(self.iymap.get(yuid, wx.NOT_FOUND))
    
    def set_zuid(self, zuid):
        self.zselector.SetSelection(self.izmap.get(zuid, wx.NOT_FOUND))
    
    def set_wuid(self, wuid):
        self.wselector.SetSelection(self.iwmap.get(wuid, wx.NOT_FOUND))
    
    def get_xuid(self):
        idx = self.xselector.GetSelection()
        if idx is wx.NOT_FOUND:
            return None
        return self.xmap[idx]
    
    def get_yuid(self):
        idx = self.yselector.GetSelection()
        if idx is wx.NOT_FOUND:
            return None
        return self.ymap[idx]
    
    def get_zuid(self):
        idx = self.zselector.GetSelection()
        if idx is wx.NOT_FOUND:
            return None
        return self.zmap[idx]
    
    def get_wuid(self):
        idx = self.wselector.GetSelection()
        if idx is wx.NOT_FOUND:
            return None
        return self.wmap[idx]


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
        #self._OM.addcallback("add", self.on_wells_changed)
        #self._OM.addcallback("post-remove", self.on_wells_changed)
        
        self.wellselector = wx.Choice(self)
        self.wellselector.Bind(wx.EVT_CHOICE, self.on_well_select)

        self.crossplotselector = Panel(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.wellselector, 0, wx.ALIGN_CENTER, 5)
        vbox.Add(self.crossplotselector, 1, wx.ALL|wx.EXPAND, 5)
        vbox.Add(button_sizer, 0, wx.ALIGN_RIGHT, 5)
        self.SetSizer(vbox)

        self.SetSize((400, 600))
        self.Fit()
        self.SetTitle(u"Crossplot")
        
        self.welluid = None
        self.wellmap = []
        self.iwellmap = {}
        
        self.on_wells_changed(None)
    
    def get_welluid(self):
        return self.welluid
    
    def set_welluid(self, welluid):
        self.welluid = welluid
        self.wellselector.SetSelection(self.iwellmap.get(welluid, wx.NOT_FOUND))
        self.crossplotselector.set_welluid(welluid)
    
    def set_xuid(self, xuid):
        self.crossplotselector.set_xuid(xuid)
    
    def set_yuid(self, yuid):
        self.crossplotselector.set_yuid(yuid)
    
    def set_zuid(self, zuid):
        self.crossplotselector.set_zuid(zuid)
    
    def set_wuid(self, wuid):
        self.crossplotselector.set_wuid(wuid)
    
    def get_xuid(self):
        return self.crossplotselector.get_xuid()
    
    def get_yuid(self):
        return self.crossplotselector.get_yuid()
    
    def get_zuid(self):
        return self.crossplotselector.get_zuid()
    
    def get_wuid(self):
        return self.crossplotselector.get_wuid()
    
    def on_well_select(self, event):
        i = event.GetSelection()
        self.set_welluid(self.wellmap[i])
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)

    def on_wells_changed(self, objuid):
        wellnames = []
        self.wellmap = []
        self.iwellmap.clear()
        self.wellselector.Clear()
        self.set_welluid(None)

        for i, well in enumerate(self._OM.list('well')):
            self.wellmap.append(well.uid)
            self.iwellmap[well.uid] = i
            wellnames.append(well.name)

        self.wellselector.AppendItems(wellnames)

        if len(self.wellmap) == 1:
            self.set_welluid(self.wellmap[0])
        
    def __del__(self):
        self._OM.removecallback("add", self.on_wells_changed)
        self._OM.removecallback("post-remove", self.on_wells_changed)
        super(Dialog, self).__del__()
