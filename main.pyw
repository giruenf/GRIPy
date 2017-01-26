# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)

import Basic
import OM
import DT
import Algo
import UI
import Vis
import Plugins

import wx

app = wx.App(False)
mainwindow = UI.UIManager.get().get_main_window()
mainwindow.Show()
app.MainLoop()
