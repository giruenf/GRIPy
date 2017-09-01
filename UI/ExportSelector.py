# -*- coding: utf-8 -*-

import wx
from collections import OrderedDict

import wx.lib.agw.customtreectrl as CT

from OM.Manager import ObjectManager


class Panel(wx.Panel):  # TODO: enxugar métodos repetidos (getblabla, setblabla)
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self._OM = ObjectManager(self)
        
        self.welluid = None

        nb = wx.Notebook(self)
        
        self.pages = OrderedDict()
        self.pages["depth"] = wx.CheckListBox(nb)
        self.pages["log"] = wx.CheckListBox(nb)
        self.pages["partition"] = wx.CheckListBox(nb)
        
        agwStyle = CT.TR_DEFAULT_STYLE | CT.TR_HIDE_ROOT
        self.pages["property"] = CT.CustomTreeCtrl(nb, agwStyle=agwStyle)
        
        self.depthmap = []
        self.idepthmap = {}
        
        self.logmap = []
        self.ilogmap = {}
        
        self.partitionmap = []
        self.ipartitionmap = {}
        
        self.ipropertymap = OrderedDict()

        self.pagenames = {}
        self.pagenames["depth"] = u"Profundidade"
        self.pagenames["log"] = u"Perfil"
        self.pagenames["partition"] = u"Partição"
        self.pagenames["property"] = u"Propriedade"
        
        for key in self.pages.iterkeys():
            nb.AddPage(self.pages[key], self.pagenames[key])

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def set_welluid(self, welluid):
        self.welluid = welluid
        self.reset_depth_page()
        self.reset_log_page()
        self.reset_partition_page()
        self.reset_property_page()
    
    def reset_depth_page(self):
        self.depthmap = []
        self.idepthmap.clear()
        self.pages['depth'].Clear()
        if self.welluid is None:
            return
        depthitems = []
        for i, depth in enumerate(self._OM.list('depth', self.welluid)):
            depthitems.append(depth.name)
            self.depthmap.append(depth.uid)
            self.idepthmap[depth.uid] = i
        self.pages['depth'].AppendItems(depthitems)
    
    def reset_log_page(self):
        self.logmap = []
        self.ilogmap.clear()
        self.pages['log'].Clear()
        if self.welluid is None:
            return
        logitems = []
        for i, log in enumerate(self._OM.list('log', self.welluid)):
            logitems.append(log.name)
            self.logmap.append(log.uid)
            self.ilogmap[log.uid] = i

        self.pages['log'].AppendItems(logitems)
    
    def reset_partition_page(self):
        self.partitionmap = []
        self.ipartitionmap = {}
        self.pages['partition'].Clear()
        if self.welluid is None:
            return
        partitionitems = []
        for i, partition in enumerate(self._OM.list('partition', self.welluid)):
            partitionitems.append(partition.name)
            self.partitionmap.append(partition.uid)
            self.ipartitionmap[partition.uid] = i
        
        self.pages['partition'].AppendItems(partitionitems)
    
    def reset_property_page(self):
        tree = self.pages['property']
        self.ipropertymap.clear()
        tree.DeleteAllItems()
        
        root = tree.AddRoot('root')
        for partition in self._OM.list('partition', self.welluid):
            properties = self._OM.list('property', partition.uid)
            if not properties:
                continue
            item = tree.AppendItem(root, partition.name)
            ipropmap = OrderedDict()
            for prop in properties:
                propitem = tree.AppendItem(item, prop.name, ct_type=1)
                tree.SetPyData(propitem, prop.uid)
                ipropmap[prop.uid] = propitem
            self.ipropertymap[partition.uid] = ipropmap
        
    def set_depth_selection(self, selection):
        if self.welluid is None:
            return
        checked = sorted(self.idepthmap[depthuid] for depthuid in selection)
        self.pages['depth'].SetChecked(checked)
    
    def get_depth_selection(self):
        selection = [self.depthmap[i] for i in self.pages['depth'].GetChecked()]
        return selection
    
    def set_log_selection(self, selection):
        if self.welluid is None:
            return
        checked = sorted(self.ilogmap[loguid] for loguid in selection)
        self.pages['log'].SetChecked(checked)
    
    def get_log_selection(self):
        selection = [self.logmap[i] for i in self.pages['log'].GetChecked()]
        return selection
    
    def set_partition_selection(self, selection):
        if self.welluid is None:
            return
        checked = sorted(self.ipartitionmap[partitionuid] for partitionuid in selection)
        self.pages['partition'].SetChecked(checked)
    
    def get_partition_selection(self):
        selection = [self.partitionmap[i] for i in self.pages['partition'].GetChecked()]
        return selection
    
    def set_property_selection(self, selection):
        if self.welluid is None:
            return
        for value in self.ipropertymap.itervalues():
            for item in value.itervalues():
                self.pages['property'].CheckItem(item, False)
        for partitionuid, propertiesuids in selection:
            for propertyuid in propertiesuids:
                item = self.ipropertymap[partitionuid][propertyuid]
                self.pages['property'].CheckItem(item, True)
    
    def get_property_selection(self):
        selection = OrderedDict()
        for partitionuid, value in self.ipropertymap.iteritems():
            propselection = []
            for propertyuid, item in value.iteritems():
                if self.pages['property'].IsItemChecked(item):
                    propselection.append(propertyuid)
            if propselection:
                selection[partitionuid] = propselection
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
        
        self._OM = ObjectManager(self)
        self._OM.subscribe(self.on_wells_changed, 'add')
        self._OM.subscribe(self.on_wells_changed, 'post_remove')
        #self._OM.addcallback('add_object', self.on_wells_changed)
        #self._OM.addcallback('post_remove_object', self.on_wells_changed)
        
        self.well_selector = wx.Choice(self)
        self.well_selector.Bind(wx.EVT_CHOICE, self.on_well_select)

        self.export_panel = Panel(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.well_selector, proportion=0, flag=wx.ALIGN_CENTER)
        vbox.Add(self.export_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizer(vbox)

        self.SetSize((400, 600))
        self.SetTitle(u"Exportar:")
        
        self.welluid = None
        self.wellmap = []
        self.iwellmap = {}
        
        self.on_wells_changed(None)
    
    def get_welluid(self):
        return self.welluid
    
    def set_welluid(self, welluid):
        self.welluid = welluid
        self.well_selector.SetSelection(self.iwellmap.get(welluid, wx.NOT_FOUND))
        self.export_panel.set_welluid(welluid)
    
    def set_depth_selection(self, selection):
        self.export_panel.set_depth_selection(selection)
    
    def get_depth_selection(self):
        return self.export_panel.get_depth_selection()
    
    def set_log_selection(self, selection):
        self.export_panel.set_log_selection(selection)
    
    def get_log_selection(self):
        return self.export_panel.get_log_selection()

    def set_partition_selection(self, selection):
        self.export_panel.set_partition_selection(selection)
    
    def get_partition_selection(self):
        return self.export_panel.get_partition_selection()    
    
    def set_property_selection(self, selection):
        self.export_panel.set_property_selection(selection)
    
    def get_property_selection(self):
        return self.export_panel.get_property_selection()
    
    def on_well_select(self, event):
        i = event.GetSelection()
        self.set_welluid(self.wellmap[i])
        
    def on_wells_changed(self, objuid):
        wellnames = []
        self.wellmap = []
        self.iwellmap.clear()
        self.well_selector.Clear()
        self.set_welluid(None)

        for i, well in enumerate(self._OM.list('well')):
            self.wellmap.append(well.uid)
            self.iwellmap[well.uid] = i
            wellnames.append(well.name)

        self.well_selector.AppendItems(wellnames)

        if len(self.wellmap) == 1:
            self.set_welluid(self.wellmap[0])
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
        
    def __del__(self):
        self._OM.removecallback("add", self.on_wells_changed)
        self._OM.removecallback("post-remove", self.on_wells_changed)
        super(Dialog, self).__del__()
