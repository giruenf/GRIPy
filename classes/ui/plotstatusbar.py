# -*- coding: utf-8 -*-

import wx


class PlotStatusBar(wx.StatusBar):
    def __init__(self, parent, pixelsPerUnit=20):
        wx.StatusBar.__init__(self, parent, -1)
        
        self.pixelsPerUnit = pixelsPerUnit
        self.SetMinHeight(16)
        
        # Dummy panel para encobrir a ScrollBar
        #self.panelDummy = wx.Panel(self)
        #self.panelDummy.SetBackgroundColour('green')
        #self.panelDummy.Show(False)
        

        self.SetFieldsCount(3)
        self.SetStatusWidths([-3, -1, -1])
        #self.SetStatusText("Aqui vai a legenda dos Logs...", 0)


        self.sb = wx.ScrollBar(self)
        self.sb.show = False
        self.sb.SetScrollbar(0, 10, 100, 10)
        self.Bind(wx.EVT_SIZE, self._OnSize)
        
        self.sb.Bind(wx.EVT_SCROLL_THUMBTRACK, self._OnScroll)
        self.sb.Bind(wx.EVT_SCROLL_LINEUP, self._OnScroll)
        self.sb.Bind(wx.EVT_SCROLL_PAGEUP, self._OnScroll)
        self.sb.Bind(wx.EVT_SCROLL_LINEDOWN, self._OnScroll)
        self.sb.Bind(wx.EVT_SCROLL_PAGEDOWN, self._OnScroll)

        self.sb.ultimaPosicao = 0
        self.Reposition()

        #self.timer = wx.PyTimer(self.Notify)
        #self.timer.Start(1000)
        #self.Notify()
    
        self.HideScrollBar()
    

    def SetDefaultHeight(self):
        # SetDefaultHeight chama _OnSize que chama Reposition
        # Reposition soh deve ser chamado por dentro de _OnSize
        x, y = self.GetSize()
        self.SetSizeWH(x, 23)      # Melhorar isso!!!!


    def HideScrollBar(self):
        if self.sb.IsShown():
            self.sb.Show(False)
            #self.panelDummy.Show(True)


    def ShowScrollBar(self):      
        if not self.sb.IsShown():
            self.sb.Show(True)
            #self.panelDummy.Show(False)
                   
    def _OnScroll(self, evt):
        
        self.Parent._DoScroll(self.sb.GetThumbPosition())

    def SetScrollbar(self, position, thumbSize, range, pageSize):
        self.sb.SetScrollbar(position, thumbSize, range, pageSize)
        
    '''    
    def SetDepth(self, depth):
        info = 'Depth: ' + "{:0.1f}".format(depth)
        self.SetStatusText(info, 0)
    '''    
    '''    
    def Notify(self):
        t = time.localtime(time.time())
        st = time.strftime("%d-%b-%Y   %I:%M:%S", t)
        self.SetStatusText(st, 2)
    '''

    def GetPixelsPerUnit(self):
        return self.pixelsPerUnit
        
        
    def SetPixelsPerUnit(self, pixelsPerUnit):   
        self.pixelsPerUnit = pixelsPerUnit
        
        
    def _OnSize(self, evt):
        #x, y = self.sb.GetSize()
        #k, l = self.GetSize()
        #m, n = self.panelDummy.GetSize()
        self.Reposition()
        self.Update()


    # reposition the ScrollBar
    def Reposition(self):
       # print '\nPlotStatusBar.Reposition'
        if self.sb.IsShown():
            rect = self.GetFieldRect(1)
            rect.x += 1
            rect.y += 1
            self.sb.SetPosition([rect.x, rect.y]) 
            size = wx.Size(rect.GetWidth()-2, rect.GetHeight())
            self.sb.SetSize(size)
        else:
            rect = self.GetFieldRect(1)
            rect.x += 1
            rect.y += 1
            #self.panelDummy.SetPosition([rect.x, rect.y]) 
            size = wx.Size(rect.GetWidth()-2, 20)
            #self.panelDummy.SetSize(size)
            