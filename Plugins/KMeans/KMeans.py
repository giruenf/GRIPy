# -*- coding: utf-8 -*-

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager

import wx
from Algo.Clustering import k_means
from Plugins.KMeans import KMeansSelector

class KMeansPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(KMeansPlugin, self).__init__()
        self._OM = ObjectManager(self)
    
    def run(self, parent):
        dlg = KMeansSelector.Dialog(parent)    
        if dlg.ShowModal() == wx.ID_OK:
            #Entrada
            logdata = [self._OM.get(uid).data for uid in dlg.get_selected_logs()]
            k = dlg.get_k()
            parentuid = dlg.get_well()
            pname = dlg.get_partition_name()
            
            #Lógica
            pdata, pinfo = k_means(logdata, k, 'all')
            
            #Saída
            partition = self._OM.new('partition', name=pname, info=pinfo)
            self._OM.add(partition, parentuid=parentuid)
            for d in pdata:
                part = self._OM.new('part', d)
                self._OM.add(part, parentuid=partition.uid)
        
        dlg.Destroy()
