# -*- coding: utf-8 -*-

from Plugins import SimpleDialogPlugin
from OM.Manager import ObjectManager

import wx

from Plugins.Seismic1D import UI
from Plugins.Seismic1D import Wavelet

class Seismic1DPlugin(SimpleDialogPlugin):

    def __init__(self):
        super(Seismic1DPlugin, self).__init__()
        self._OM = ObjectManager(self)

    def run(self, parent):
        dlg = UI.Dialog(parent)    
        if dlg.ShowModal() == wx.ID_OK:
            return True
