#----------------------------------------------------------------------
# Name:        wx.lib.splitter
# Purpose:     A class similar to wx.SplitterWindow but that allows more
#              than a single split
#
# Author:      Robin Dunn
#
# Created:     9-June-2005
# RCS-ID:      $Id$
# Copyright:   (c) 2005 by Total Control Software
# Licence:     wxWindows license
#----------------------------------------------------------------------
"""
This module provides the `MultiSplitterWindow` class, which is very
similar to the standard `wx.SplitterWindow` except it can be split
more than once.
"""

import wx

_RENDER_VER = (2,6,1,1)

#----------------------------------------------------------------------

class MultiSplitterWindow(wx.PyPanel):
    """
    This class is very similar to `wx.SplitterWindow` except that it
    allows for more than two windows and more than one sash.  Many of
    the same styles, constants, and methods behave the same as in
    wx.SplitterWindow.  The key differences are seen in the methods
    that deal with the child windows managed by the splitter, and also
    those that deal with the sash positions.  In most cases you will
    need to pass an index value to tell the class which window or sash
    you are refering to.

    The concept of the sash position is also different than in
    wx.SplitterWindow.  Since the wx.Splitterwindow has only one sash
    you can think of it's position as either relative to the whole
    splitter window, or as relative to the first window pane managed
    by the splitter.  Once there is more than one sash then the
    distinciton between the two concepts needs to be clairified.  I've
    chosen to use the second definition, and sash positions are the
    distance (either horizontally or vertically) from the origin of
    the window just before the sash in the splitter stack.

    NOTE: These things are not yet supported:

        * Using negative sash positions to indicate a position offset
          from the end.
          
        * User controlled unsplitting (with double clicks on the sash
          or dragging a sash until the pane size is zero.)
          
        * Sash gravity
       
    """
    
    def __init__(self, parent, *args, **kwargs):#id=-1,
                 #pos = wx.DefaultPosition, size = wx.DefaultSize,
                 #style = 0, name="multiSplitter", borderSize = 2,
			#	 borderColor=(0,0,0), sashColor=(0,0,0)):
				 
        # always turn on tab traversal
        style = wx.TAB_TRAVERSAL
        # and turn off any border styles
        style &= ~wx.BORDER_MASK
        style |= wx.BORDER_NONE

        # initialize the base class
        wx.PyPanel.__init__(self, parent, *args, **kwargs)#id, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # initialize data members
        self._windows = []
        self._sashes = []
        self._permitUnsplitAlways = self.HasFlag(wx.SP_PERMIT_UNSPLIT)

        self._dragMode = wx.SPLIT_DRAG_NONE
        self._activeSash = -1
        self._oldX = 0
        self._oldY = 0
        self._checkRequestedSashPosition = False
        self._minimumPaneSize = 0
        
        if wx.__version__.startswith('3.0.3'):
            # Phoenix code
            self._sashCursorWE = wx.Cursor(wx.CURSOR_SIZEWE)
        else:
            # wxPython classic code
            self._sashCursorWE = wx.StockCursor(wx.CURSOR_SIZEWE)


        self._needUpdating = False
        self._isHot = False
        self._drawSashInBackgroundColour = False
        
        # Bind event handlers
        self.Bind(wx.EVT_PAINT,        self._OnPaint)
        self.Bind(wx.EVT_IDLE,         self._OnIdle)
        self.Bind(wx.EVT_SIZE,         self._OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self._OnMouse)
		
	  # Novas variaveis
        #self._old_size = (0,0)
        self.borderSize = 1
        self.borderColor = (0,0,0)
        self.sashColor = (0,0,0)
        self.selectedWindowColor = 'green'
        self.trackerCanvas = None
        self.fit = False
        self._ajustes = []
        self._proporcao = []
        self.ajustado = False
        # Tom de azul para sashTrcker
        self.sashTrackerColor = (4, 20, 164) 
        self._sashTrackerPen = wx.Pen(self.sashTrackerColor, self._GetSashSize(), wx.SOLID)


    def GetOrientation(self):
        """
        Returns wx.HORIZONTAL as unique orientation.
        """
        return wx.HORIZONTAL

    def SetBackgroundColour(self,color):
        wx.PyPanel.SetBackgroundColour(self,color)
        self._drawSashInBackgroundColour = True
        if  wx.NullColour == color:
            self._drawSashInBackgroundColour = False
            
        
    def SetMinimumPaneSize(self, minSize):
        """
        Set the smallest size that any pane will be allowed to be
        resized to.
        """
        self._minimumPaneSize = minSize

    def GetMinimumPaneSize(self):
        """
        Returns the smallest allowed size for a window pane.
        """
        return self._minimumPaneSize

    
    def AppendWindow(self, window, sashPos=100):
        """
        Add a new window to the splitter at the right side or bottom
        of the window stack.  If sashPos is given then it is used to
        size the new window.
        """
        self.InsertWindow(len(self._windows), window, sashPos)
        return len(self._windows)
        

    def InsertWindow(self, idx, window, sashPos=100):
        """
        Insert a new window into the splitter at the position given in
        ``idx``.
        """
        assert window not in self._windows, "A window can only be in the splitter once!"
        self._windows.insert(idx, window)
        self._sashes.insert(idx, sashPos)
        if not window.IsShown():
            window.Show()
        self._checkRequestedSashPosition = False
        #self._SizeWindows()
 
 
    def ChangeWindowPosition(self, window, new_pos):
        #assert window in self._windows
        assert window in self._windows, "Cannot change a window position if it is not in the Splitter."
        old_pos = self._windows.index(window)
        sashPos = self._sashes[old_pos]        
        if new_pos == old_pos: 
            #print 'Pos {} jah estava ok'.format(new_pos)            
            return False
        
        #if new_pos < old_pos:
        #    for i in range(new_pos, old_pos):
        #        win = self._windows[i]
        #        win._has_changed_position_to(i+1)

        self.DetachWindow(window)
        self.InsertWindow(new_pos, window, sashPos)
        return True
        #if new_pos < old_pos:
        #    for i in range(new_pos, old_pos):
                
        
    def __len__(self):
        return len(self._windows)


    def DetachWindow(self, window):
        """
        Removes the window from the stack of windows managed by the
        splitter.  The window will still exist so you should `Hide` or
        `Destroy` it as needed.
        """
        ##print '\nDETACHING WINDOW'
        assert window in self._windows, "Unknown window!"
        idx = self._windows.index(window)
        self._windows[idx]._selected = False
        self._draw_window_selection(self._windows[idx])
        del self._windows[idx]
        del self._sashes[idx]
        self._checkRequestedSashPosition = False
        #self._SizeComponent()
        

    def ReplaceWindow(self, oldWindow, newWindow):
        """
        Replaces oldWindow (which is currently being managed by the
        splitter) with newWindow.  The oldWindow window will still
        exist so you should `Hide` or `Destroy` it as needed.
        """
        assert oldWindow in self._windows, "Unknown window!"
        idx = self._windows.index(oldWindow)
        self._windows[idx] = newWindow
        if not newWindow.IsShown():
            newWindow.Show()
        self._checkRequestedSashPosition = False    
        #self._SizeWindows()


    def ExchangeWindows(self, window1, window2):
        """
        Trade the positions in the splitter of the two windows.
        """
        assert window1 in self._windows, "Unknown window!"
        assert window2 in self._windows, "Unknown window!"
        idx1 = self._windows.index(window1)
        idx2 = self._windows.index(window2)
        self._windows[idx1] = window2
        self._windows[idx2] = window1
        #self._SizeWindows()
        self._checkRequestedSashPosition = False


    def IndexOf(self, window):
        assert window in self._windows, "Unknown window!"
        return self._windows.index(window)


    def GetWindow(self, idx):
        """
        Returns the idx'th window being managed by the splitter.
        """
        assert idx < len(self._windows)
        return self._windows[idx]


    def GetSashPosition(self, idx):
        """
        Returns the position of the idx'th sash, measured from the
        left/top of the window preceding the sash.
        """
        assert idx < len(self._sashes)
        return self._sashes[idx]


    def SetSashPosition(self, idx, pos):
        """
        Set the psition of the idx'th sash, measured from the left/top
        of the window preceding the sash.
        """
        ##print 'MultiSplitter.SetSashPosition', idx, pos
        assert idx < len(self._sashes)
        self._sashes[idx] = pos
        self._SizeWindows()
        

    def SizeWindows(self):
        """
        Reposition and size the windows managed by the splitter.
        Useful when windows have been added/removed or when styles
        have been changed.
        """
        self._SizeWindows()
              

    def DoGetBestSize(self):
        """
        Overridden base class virtual.  Determines the best size of
        the control based on the best sizes of the child windows.
        """
        ##print '\nDoGetBestSize', self.GetSize(), self.GetParent().GetSize()
        best = wx.Size(0, 100)
        if not self._windows:
            return best            
        sashsize = self._GetSashSize()
        for idx, sash in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                best.width += max(self._minimumPaneSize, sash)	
        best.height = max(best.height, self.GetClientSize().height - 2*self.borderSize)
        best.width += sashsize * (len(self._windows))
        best.width += self._GetBorderSize()
        best.height += 2*self._GetBorderSize()
        return best

    # -------------------------------------
    # Event handlers
    
    def _OnPaint(self, evt): 
        ##print '_OnPaint', self.GetClientSize(), self.GetBestSize()
        #if self._old_size == self.GetClientSize():
        #    return
            
        #self.SetBestSize(self.GetClientSize())
        #dc = wx.PaintDC(self)
        #self._DrawSash(dc)
        # New below - 28-12-2016
        self._SizeWindows()
        self._old_size = self.GetClientSize()
       # evt.Skip()
        

    def _OnSize(self, evt):
        #print '\n_OnSize', self.GetSize()
        #parent = wx.GetTopLevelParent(self)
        #if parent.IsIconized():
        #evt.Skip()
        #    return
        #self.Refresh()    
        #self._checkRequestedSashPosition = False   
        self._SizeComponent()
        

    def _OnIdle(self, evt):
        evt.Skip()
        # if this is the first idle time after a sash position has
        # potentially been set, allow _SizeWindows to check for a
        # requested size.  
        if not self._checkRequestedSashPosition:
            #print '_OnIdle 1'
            self._checkRequestedSashPosition = True
            self._SizeComponent()

        if self._needUpdating:
            #print '_OnIdle 2'
            self._SizeComponent()

    '''
        Inserir comentarios
    '''
    """
    def AdjustAllSashes(self, vetor):
        for idx, value in enumerate(vetor):
            if self._GetFit():
                # Valor de entrada eh vetor de proporcoes
                self._proporcao[idx] = value
            else:
                # Valor de entrada eh vetor sash positions
                self._SetSashPositionAndNotify(idx, value)
        self._SizeComponent()         
    """    
    
    
    """
    # On testing 29-12-2016
    def _WindowHitTest(self, x, y):
        if len(self._windows) == 0:
            return -1
        if x < self._GetSashSize():
            return -1
        pos = self._GetSashSize()
        for idx, sash in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                pos += sash 
                if x <= pos:
                    return idx
                pos += self._GetSashSize() 
        return -1
    """
 

    def _draw_window_selection(self, window):
    #    #print '\nMultiSplitterWindow._draw_window_selection: ', window.GetRect(), window.is_selected()
        if not window.is_selected() and not window.selectedCanvas:
    #        #print '  nothing to do'
            return
        x, y, w, h = window.GetRect()
        
        if window.is_selected():
            if not window.selectedCanvas:
    #            #print '  construindo'
                #
                panel = wx.Panel(window.GetParent())
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    panel.SetSize(x, y, w, self._GetSashSize())
                else:
                    # wxPython classic code
                    panel.SetDimensions(x, y, w, self._GetSashSize())
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
                #    
    #            #print 1
                panel = wx.Panel(window.GetParent()) 
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    panel.SetSize(x, h, w, self._GetSashSize())
                else:
                    # wxPython classic code
                    panel.SetDimensions(x, h, w, self._GetSashSize())
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
    #            #print 2
                #            
                panel = wx.Panel(window.GetParent()) 
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    panel.SetSize(x, y, self._GetSashSize(), h)
                else:
                    # wxPython classic code
                    panel.SetDimensions(x, y, self._GetSashSize(), h)
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
    #            #print 3
                #            
                panel = wx.Panel(window.GetParent()) 
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    panel.SetSize((x + w - self._GetSashSize()), y, 
                                    self._GetSashSize(), h)
                else:
                    # wxPython classic code
                    panel.SetDimensions((x + w - self._GetSashSize()), y, 
                                    self._GetSashSize(), h)
                panel.SetBackgroundColour(self.selectedWindowColor)
                
                window.selectedCanvas.append(panel)
    #            #print 4
            else:
    #            #print '  atualizando'
            
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    window.selectedCanvas[0].SetSize(x, y, w, self._GetSashSize())
                else:
                    # wxPython classic code
                    window.selectedCanvas[0].SetDimensions(x, y, w, self._GetSashSize())
                window.selectedCanvas[0].Refresh()
                
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    window.selectedCanvas[1].SetSize(x, h, w, self._GetSashSize())
                else:
                    # wxPython classic code
                    window.selectedCanvas[1].SetDimensions(x, h, w, self._GetSashSize())
                window.selectedCanvas[1].Refresh()

                if wx.__version__.startswith('3.0.3'):       
                    # Phoenix code
                    window.selectedCanvas[2].SetSize(x, y, self._GetSashSize(), h)
                else:
                    # wxPython classic code
                    window.selectedCanvas[2].SetDimensions(x, y, self._GetSashSize(), h)
                window.selectedCanvas[2].Refresh()
                
                if wx.__version__.startswith('3.0.3'):       
                    # Phoenix code
                    window.selectedCanvas[3].SetSize((x + w - self._GetSashSize()), y, 
                                        self._GetSashSize(), h)
                else:
                    # wxPython classic code
                    window.selectedCanvas[3].SetDimensions((x + w - self._GetSashSize()), y, 
                                        self._GetSashSize(), h)
                window.selectedCanvas[3].Refresh()                        
                                    
                                    

        else:
            start = len(window.selectedCanvas) - 1
            for i in range(start, -1, -1):
                temp = window.selectedCanvas.pop(i)
                temp.Destroy() 
        #window._selected = not window._selected
        
            
    """    
    def _DragSashTracker(self, x):
        if self.selectedCanvas:
            self.selectedCanvas.SetPosition(wx.Point(x, self._GetSashSize()))
            self.selectedCanvas.Refresh()


    def _DestroySashTracker(self):
        if self.selectedCanvas:
            temp = self.selectedCanvas
            self.selectedCanvas = None
            temp.Destroy()
    """        

###########


    def _OnMouse(self, evt):
        if self.HasFlag(wx.SP_NOSASH):
            return
        x, y = evt.GetPosition()
        
       # #print '_OnMouse: '#, self._WindowHitTest(x, y)
        
       # if evt.LeftDown() and self._WindowHitTest(x, y) != -1:         
       #     #print 'Clicou na janela', self._WindowHitTest(x, y)
       # 
        if evt.LeftDown() and self._SashHitTest(x, y) != -1:
            self._activeSash = self._SashHitTest(x, y)
            self._dragMode = wx.SPLIT_DRAG_DRAGGING
            self.CaptureMouse()
            self._SetResizeCursor()
            #if not isLive:
            if self._activeSash == len(self.get_windows_shown())-1:#len(self._sashes)-1:
             # Ultimo sash - cuidado!
                self._pendingPos = self._sashes[len(self.get_windows_shown())-1] #self._activeSash]
            else:
                self._pendingPos = self._sashes[self._activeSash]            
            self._InitSashTracker(x)
            self._oldX = x
            self._oldY = y
            return
            
        # LeftUp: Finsish the drag
        elif evt.LeftUp() and self._dragMode == wx.SPLIT_DRAG_DRAGGING:
            ##print '\nSash released! 0\n'
            self._dragMode = wx.SPLIT_DRAG_NONE
            self.ReleaseMouse()
            self.SetCursor(wx.STANDARD_CURSOR)
            self._DestroySashTracker()
            diff = self._GetMotionDiff(x, y)
            ##print '\nSash released! 0.1\n'
            oldPos1 = self._pendingPos
            newPos1 = self._OnSashPositionChanging(self._activeSash, oldPos1 + diff)                             
            if newPos1 == -1:
                # the change was not allowed
                return
            ##print '\nSash released! 0.2\n'    
            self._SetSashPositionAndNotify(self._activeSash, newPos1)        
            ##print '\nSash released! 0.3\n'   
            self._activeSash = -1
            self._pendingPos = (-1, -1) 
            self._checkRequestedSashPosition = False
            ##print '\nSash released!\n'
        # Entering or Leaving a sash: Change the cursor
        elif (evt.Moving() or evt.Leaving() or evt.Entering()) and self._dragMode == wx.SPLIT_DRAG_NONE:
            if evt.Leaving() or self._SashHitTest(x, y) == -1:
                self._OnLeaveSash()
            else:
                self._OnEnterSash()
                
        # Dragging the sash
        elif evt.Dragging() and self._dragMode == wx.SPLIT_DRAG_DRAGGING:
            diff = self._GetMotionDiff(x, y)
            if not diff:
                return  
            oldPos1 = self._pendingPos
            newPos1 = self._OnSashPositionChanging(self._activeSash, oldPos1 + diff)
            if newPos1 == -1:
                # the change was not allowed
                return
            if newPos1 == self._sashes[self._activeSash]:
                return  # nothing was changed
            x = self._SashToCoord(self._activeSash, newPos1)
            # Remember old positions
            self._oldX = x
            self._oldY = y
            self._pendingPos = newPos1
            self._DragSashTracker(self._oldX)




    # -------------------------------------
    # Internal helpers
    
    def _RedrawIfHotSensitive(self, isHot):
        if not wx.VERSION >= _RENDER_VER:
            return
        if wx.RendererNative.Get().GetSplitterParams(self).isHotSensitive:
            self._isHot = isHot
            dc = wx.ClientDC(self)
            self._DrawSash(dc)


    def _OnEnterSash(self):
        self._SetResizeCursor()
        self._RedrawIfHotSensitive(True)

    def _OnLeaveSash(self):
        self.SetCursor(wx.STANDARD_CURSOR)
        self._RedrawIfHotSensitive(False)

    def _SetResizeCursor(self):
        self.SetCursor(self._sashCursorWE)

                   
    def _OnSashPositionChanging(self, idx, new_pos):
      #  #print 'MultiSplitterWindow._OnSashPositionChanging', idx, new_pos
        new_pos = self._AdjustSashPosition(idx, new_pos)
        # sanity check
        if new_pos <= 0:
            new_pos = 0 
        # send the events
        evt = MultiSplitterEvent(
            wx.wxEVT_COMMAND_SPLITTER_SASH_POS_CHANGING, self)
        evt.SetSashIdx(idx)
        evt.SetSashPosition(new_pos)
        if not self._DoSendEvent(evt):
            # the event handler vetoed the change
            new_pos = -1
        else:
            # or it might have changed the value
            new_pos = evt.GetSashPosition()
        return new_pos

    
    def _AdjustSashPosition(self, idx, newPos1):
        window = self.GetWindow(idx)
        minSize = self._GetWindowMin(window)
        if minSize == -1 or self._minimumPaneSize > minSize:
            minSize = self._minimumPaneSize
        if newPos1 < minSize:
            newPos1 = minSize
        return (newPos1)    



    def _DoSetSashPosition(self, idx, newPos1):
        newPos1 = self._AdjustSashPosition(idx, newPos1)
        if newPos1 == self._sashes[idx]:
            return False
            
        if self._GetFit():
            prop = newPos1 / float(self._LarguraUtil())
            diff_prop = prop - self._proporcao[idx] 
            inc_prop = diff_prop / (len(self._proporcao)-1) 
            soma = 0
            
            for i in range(len(self._proporcao)):
                if i == idx:
                    self._proporcao[i] = prop
                else:
                    self._proporcao[i] -= inc_prop
                soma +=  self._proporcao[i]
                       
        else:    
            self._sashes[idx] = newPos1 
        ##print 'FIM _DoSetSashPosition'
        #self._draw_window_selection(self._windows[idx])
        return True
            
       
    def _SetSashPositionAndNotify(self, idx, new_pos): 
       # #print 'MultiSplitterWindow._SetSashPositionAndNotify', idx, new_pos
        self._DoSetSashPosition(idx, new_pos)
        evt = MultiSplitterEvent(
            wx.wxEVT_COMMAND_SPLITTER_SASH_POS_CHANGED, self)
        evt.SetSashIdx(idx)
        evt.SetSashPosition(new_pos)
        self._DoSendEvent(evt)
 

    def _GetMotionDiff(self, x, y):
        return x - self._oldX


    def _SashToCoord(self, idx, sashPos):
        coord = self.borderSize
        for i in range(idx):
            window = self.GetWindow(i)
            if window.IsShown():
                coord += self._sashes[i]
                coord += self._GetSashSize()
        coord += sashPos
        return coord


    def _GetWindowMin(self, window):
        return window.GetMinWidth()

      
    def _GetSashSize(self):
        if self.HasFlag(wx.SP_NOSASH):
            return 0
        return self.borderSize


    def _GetBorderSize(self):
        return self.borderSize
        

    def _DrawSash(self, dc):
        ##print '_DrawSash', self.GetClientSize()
        if wx.VERSION >= _RENDER_VER:
            if self.HasFlag(wx.SP_3DBORDER):
                wx.RendererNative.Get().DrawSplitterBorder(
                    self, dc, self.GetClientRect())

        # if there are no splits then we're done.
        if not self._windows:
            return
    #    # if we are not supposed to use a sash then we're done.
    #    if self.HasFlag(wx.SP_NOSASH):
    #        return

        # Desenhando as bordas esquerda, acima e abaixo.
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.sashColor))	

        # Desenhando os Sashes				
        pos = self.borderSize
        for idx, sash in enumerate(self._sashes):
            ##print 'drawing sash {} na pos {}'.format(idx, sash)
            if self.GetWindow(idx).IsShown():
                pos += sash
                sashsize = self._GetSashSize()
                x = pos
                y = self.borderSize
                w = sashsize
                h = self.GetClientSize().height - 2*self.borderSize
                ##print 'dc.DrawRectangle({}, {}, {}, {})'.format(x, y, w, h)
                dc.DrawRectangle(x, y, w, h)
                pos += self._GetSashSize()
                #
             #   self._draw_window_selection(self.GetWindow(idx)) 
                #
        
        if self.borderSize > 0:
           # Borda esquerda
           dc.DrawRectangle(0, 0, self.borderSize, self.GetClientSize().height)
		# Borda acima
           dc.DrawRectangle(self.borderSize, 0, pos - self.borderSize, self.borderSize)
		# Borda abaixo
           dc.DrawRectangle(self.borderSize, self.GetClientSize().height - self.borderSize, 
			pos - self.borderSize, self.borderSize)
        
        #for panel in window.selectedCanvas:
        #    panel.Refresh()                
        #for window in self._windows:        
        #    self._draw_window_selection(window)              
        
        ##print 'FIM DRAW SASH\n'


    def _InitSashTracker(self, posx):
        if not self.trackerCanvas:
            self.trackerCanvas = wx.Panel(self.GetParent()) 
            self.trackerCanvas.SetBackgroundColour("blue")
            border = self._GetBorderSize()
            h = self.GetClientSize().GetHeight() - 2*border
            sash = self._GetSashSize()
            if wx.__version__.startswith('3.0.3'):
                # Phoenix code            
                self.trackerCanvas.SetSize(posx, border, sash, h)
            else:    
                # wxPython classic code
                self.trackerCanvas.SetDimensions(posx, border, sash, h)
        
    def _DragSashTracker(self, x):
        if self.trackerCanvas:
            self.trackerCanvas.SetPosition(wx.Point(x, self._GetSashSize()))
            self.trackerCanvas.Refresh()


    def _DestroySashTracker(self):
        if self.trackerCanvas:
            temp = self.trackerCanvas
            self.trackerCanvas = None
            temp.Destroy()



    def _SashHitTest(self, x, y, tolerance=5):
        # if there are no splits then we're done.
        if len(self._windows) < 1:
            return -1
        z = x
        pos = 0
        for idx, sash in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                pos += sash
                hitMin = pos - tolerance
                hitMax = pos + self._GetSashSize() + tolerance    
                if z >= hitMin and z <= hitMax:
                    return idx
                pos += self._GetSashSize() 
        return -1



    def _GetFit(self):
        return self.fit


    def get_windows_shown(self):
        windows = []
        if self._windows is None:
            return windows
        for window in self._windows:
            if window.IsShown():
                windows.append(window)
        return windows        


    def _LarguraUtil(self):
        if self._GetFit():
            w = self.GetParent().GetClientSize().GetWidth() - self._GetBorderSize()
            w = w - (len(self._sashes) * self._GetSashSize())
            return w
        else:
            soma = 0
            for idx, spos in enumerate(self._sashes):
                window = self.GetWindow(idx)
                if window.IsShown():
                    soma += spos
            return soma
         
         
    def _GetSomaSashes(self):
        soma = 0
        for idx, spos in enumerate(self._sashes): 
            window = self.GetWindow(idx)
            if window.IsShown():
                soma += spos
        return soma
     
         
    def _SetFit(self, boolean):
        self.fit = boolean
        if boolean:
            self.largUtilOriginal = self._GetSomaSashes()
            self._CalcProporcao()
        else:
            usado = 0
            for idx, prop in enumerate(self._proporcao): 
                if idx == len(self._proporcao)-1:
                    self._sashes[idx] = max(self._minimumPaneSize,
                        self.largUtilOriginal - usado)
                else:
                    self._sashes[idx] = max(self._minimumPaneSize,
                        (prop * self.largUtilOriginal))
                    usado += round(prop * self.largUtilOriginal)
            self._proporcao = []
            self.largUtilOriginal = -1
        self._SizeComponent()


    def _CalcProporcao(self):
        soma = self._GetSomaSashes()
        self._proporcao = []
        for idx, spos in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                self._proporcao.append(spos/float(soma))        


    def _SizeComponent(self):
        #print '_SizeComponent'
        if not self._windows:
            self.SetSize([0, self.GetSize().GetHeight()]) 
          #  #print '    self.SetSize([{}, {}])'.format(0, self.GetSize().GetHeight())

        #self.Unbind(wx.EVT_SIZE)
        elif self._GetFit():
            self.SetSize([self.GetParent().GetClientSize().GetWidth(),
                          self.GetSize().GetHeight()])
                          
        else:
            soma = self._LarguraUtil()
            soma += self._GetBorderSize()
            soma += len(self.get_windows_shown()) * self._GetSashSize()
            self.SetSize([soma, self.GetSize().GetHeight()]) 

         #   #print '    self.SetSize([{}, {}])'.format(soma, self.GetSize().GetHeight()) 
        #self.Bind(wx.EVT_SIZE, self._OnSize)
        

        self.SetBestSize(self.GetSize())    
        self._SizeWindows()
        
        
    def _SizeWindows(self):
        #print '_SizeWindows', self.GetSize(), self.GetParent().GetSize(), self.GetClientSize()
        if not self._windows:
            return       
        if len(self.get_windows_shown()) == 0:
            return
        
        largUtil = self._LarguraUtil()
    
        if self._GetFit():
            usado = 0
            for idx, spos in enumerate(self._sashes):
               # #print '_sash fit:', idx, spos
                if idx < len(self._sashes)-1:
                    self._sashes[idx] = round(self._proporcao[idx] * largUtil)
                    usado += round(self._proporcao[idx] * largUtil)
                else:
                    self._sashes[idx] = largUtil - usado                    

        border = self._GetBorderSize()
        sash   = self._GetSashSize()
        
        if 'wxMSW' in wx.PlatformInfo:
            self.Freeze()
        
        x = y = border
        h = self.GetClientSize().GetHeight() - (2 * border)
               
        for idx, spos in enumerate(self._sashes):
            ##print '    _sash:', idx, spos
            window = self.GetWindow(idx)
            if window.IsShown():
                if wx.__version__.startswith('3.0.3'):
                    # Phoenix code
                    window.SetSize(x, y, spos, h)
                else:
                    # wxPython classic code
                    window.SetDimensions(x, y, spos, h)
                ##print '    {} - SetDimensions({}, {}, {}, {})'.format(window._view._controller_uid, x, y, spos, h)
                
                #for panel in window.selectedCanvas:
                #    panel.Refresh()                
                self._draw_window_selection(window)                
                
                x += spos + sash	
                
        if 'wxMSW' in wx.PlatformInfo:
            self.Thaw()
            
        dc = wx.ClientDC(self)    
        self._DrawSash(dc)
       # self._needUpdating = False
        
        ##print
        
    def _DoSendEvent(self, evt):
        return not self.GetEventHandler().ProcessEvent(evt) or evt.IsAllowed()
    
    
    
#----------------------------------------------------------------------

class MultiSplitterEvent(wx.PyCommandEvent):
    """
    This event class is almost the same as `wx.SplitterEvent` except
    it adds an accessor for the sash index that is being changed.  The
    same event type IDs and event binders are used as with
    `wx.SplitterEvent`.
    """
    def __init__(self, type=wx.wxEVT_NULL, splitter=None):
        wx.PyCommandEvent.__init__(self, type)
        if splitter:
            self.SetEventObject(splitter)
            self.SetId(splitter.GetId())
        self.sashIdx = -1
        self.sashPos = -1
        self.isAllowed = True

    def SetSashIdx(self, idx):
        self.sashIdx = idx
        
    def SetSashPosition(self, pos):
        self.sashPos = pos
        
    def GetSashIdx(self):
        return self.sashIdx
        
    def GetSashPosition(self):
        return self.sashPos
    # methods from wx.NotifyEvent
    def Veto(self):
        self.isAllowed = False
        
    def Allow(self):
        self.isAllowed = True
        
    def IsAllowed(self):
        return self.isAllowed
        


#----------------------------------------------------------------------



