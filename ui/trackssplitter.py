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

class MultiSplitterWindow(wx.Panel):
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
        wx.Panel.__init__(self, parent, *args, **kwargs)#id, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        # initialize data members
        self._windows = []
        self._sashes = []
        self._permitUnsplitAlways = self.HasFlag(wx.SP_PERMIT_UNSPLIT)

        self._dragMode = wx.SPLIT_DRAG_NONE
        self._working_sash = -1
        self.__absolute_sash_pos = 0
        self._oldY = 0
        self._checkRequestedSashPosition = False
        self._minimumPaneSize = 0
        
        self._sashCursorWE = wx.Cursor(wx.CURSOR_SIZEWE)

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
        self._sash_size = self._border_size = 1
        self.borderColor = (0,0,0)
        self.sashColor = (0,0,0)
        #self.selectedWindowColor = 'green'
        self.trackerCanvas = None
        self.fit = False
        self._ajustes = []
        self._proporcao = []
        self.ajustado = False
        
        # Tom de azul para sashTrcker
        self.sashTrackerColor = 'blue' #(4, 20, 164) 



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
        if window.IsShown():
            #window.Show()
            self._checkRequestedSashPosition = False
        #self._SizeWindows()


    def ShowWindow(self, window, show):
        assert window in self._windows, "Unknown window!"
        window.Show(show)
        self._checkRequestedSashPosition = False
 
    
    def ChangeWindowPosition(self, window, new_pos):
        assert window in self._windows, "Cannot change a window position if it is not in the Splitter."
        old_pos = self._windows.index(window)
        sashPos = self._sashes[old_pos]        
        if new_pos == old_pos:           
            return False
        # Redraw component only if window is being shown
        #if window.IsShown():
        self.DetachWindow(window)
        self.InsertWindow(new_pos, window, sashPos)
        if window.IsShown():
            # Forcing instant redraw 
            self._SizeComponent()
            # No need redraw OnIdle anymore
            self._checkRequestedSashPosition = True
        return True

 
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
        #self._windows[idx]._selected = False
        #self._draw_window_selection(self._windows[idx])
        del self._windows[idx]
        del self._sashes[idx]
        if window.IsShown():
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
        if newWindow.IsShown():
            #newWindow.Show()
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
        # Forcing instant redraw 
        self._SizeComponent()
        # No need redraw OnIdle anymore
        self._checkRequestedSashPosition = True


    def IndexOf(self, window):
        assert window in self._windows, "Unknown window!"
        return self._windows.index(window)


    def GetVisibleIndexOf(self, window):
        ret_val = idx = self.IndexOf(window)
        for i in range(0, idx):
            if not self._windows[i].IsShown():
                ret_val -= 1
        return ret_val        


    def GetWindow(self, idx):
        """
        Returns the idx'th window being managed by the splitter.
        """
        assert idx < len(self._windows)
        return self._windows[idx]



    def get_windows_shown(self):
        windows = []
        if self._windows is None:
            return windows
        for window in self._windows:
            if window.IsShown():
                windows.append(window)
        return windows    


    def get_windows_indexes_shown(self):
        list_ = []
        for idx, window in enumerate(self._windows):
            if window.IsShown:
                list_.append(idx)    
        return list_



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
        best = wx.Size(0, 100)
        if not self._windows:
            return best            
        sashsize = self._sash_size
        for idx, sash in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                best.width += max(self._minimumPaneSize, sash)	
        best.height = max(best.height, self.GetClientSize().height - 2*self._border_size)
        best.width += sashsize * (len(self._windows))
        best.width += self._border_size
        best.height += 2*self._border_size
        return best



    # -------------------------------------
    # Event handlers
    
    def _OnPaint(self, evt): 
        #print '_OnPaint', self.GetClientSize(), self.GetBestSize()
        #if self._old_size == self.GetClientSize():
        #    return
            
        #self.SetBestSize(self.GetClientSize())
        #dc = wx.PaintDC(self)
        #self._DrawSashes(dc)
        
        # New below - 28-12-2016
        self._SizeWindows()
        #self._old_size = self.GetClientSize()
       # evt.Skip()
        

    def _OnSize(self, evt):
     #   print '\n_OnSize', self.GetSize()
        #parent = wx.GetTopLevelParent(self)
        #if parent.IsIconized():
        #evt.Skip()
        #    return
        #self.Refresh()    
        #self._checkRequestedSashPosition = False   
        self._SizeComponent()
        

    def _OnIdle(self, evt):
        #print '\n_OnIdle'
        
        # if this is the first idle time after a sash position has
        # potentially been set, allow _SizeWindows to check for a
        # requested size.  
        if not self._checkRequestedSashPosition:
            #print '_OnIdle 1'
            #self._SizeComponent()
            self._checkRequestedSashPosition = True
            self._SizeComponent()

        if self._needUpdating:
            #print '_OnIdle 2'
            self._SizeComponent()
        evt.Skip()
        

 
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
                panel.SetSize(x, y, w, self._sash_size)
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
                #    
    #            #print 1
                panel = wx.Panel(window.GetParent()) 
                panel.SetSize(x, h, w, self._sash_size)
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
    #            #print 2
                #            
                panel = wx.Panel(window.GetParent()) 
                panel.SetSize(x, y, self._sash_size, h)
                panel.SetBackgroundColour(self.selectedWindowColor)
                window.selectedCanvas.append(panel)
    #            #print 3
                #            
                panel = wx.Panel(window.GetParent()) 
                panel.SetSize((x + w - self._sash_size), y, 
                                    self._sash_size, h)
                panel.SetBackgroundColour(self.selectedWindowColor)              
                window.selectedCanvas.append(panel)
    #            #print 4
            else:
    #            #print '  atualizando'

                window.selectedCanvas[0].SetSize(x, y, w, self._sash_size)
                window.selectedCanvas[0].Refresh()
                
                window.selectedCanvas[1].SetSize(x, h, w, self._sash_size)
                window.selectedCanvas[1].Refresh()

                window.selectedCanvas[2].SetSize(x, y, self._sash_size, h)
                window.selectedCanvas[2].Refresh()
                
                window.selectedCanvas[3].SetSize((x + w - self._sash_size), y, 
                                        self._sash_size, h)
                window.selectedCanvas[3].Refresh()                        
                                    
                                    

        else:
            start = len(window.selectedCanvas) - 1
            for i in range(start, -1, -1):
                temp = window.selectedCanvas.pop(i)
                temp.Destroy() 

    """

    def _OnMouse(self, evt):
        if self.HasFlag(wx.SP_NOSASH):
            return
        posx, posy = evt.GetPosition()
        sash_hit = self._SashHitTest(posx, posy)
       # print 'posx:', posx, sash_hit
        # Entering or Leaving a sash: Change the cursor
        if (evt.Moving() or evt.Leaving() or evt.Entering()) and \
                                        self._dragMode == wx.SPLIT_DRAG_NONE:
            if evt.Leaving() or sash_hit == -1:
                self._OnLeaveSash()
            else:
                self._OnEnterSash()
        
        # Clicou no Sash
        elif evt.LeftDown() and sash_hit != -1:
            #print 'Clicou no Sash:', sash_hit
            self._working_sash = sash_hit
            self._dragMode = wx.SPLIT_DRAG_DRAGGING
            self.SetCursor(self._sashCursorWE)
            self.CaptureMouse()
            
            if self._working_sash == len(self.get_windows_shown())-1:
                # Ultimo sash - cuidado!
                self._relative_sash_pos = self._sashes[len(self.get_windows_shown())-1] 
            else:
                self._relative_sash_pos = self._sashes[self._working_sash]            
            
            self._absolute_sash_pos = self._get_sash_position_x(self._working_sash)
            self._InitSashTracker(self._absolute_sash_pos)
            self._working_sash_shift = 0
            self._old_posx = posx
         #   print 'Fim clicou no sash', self._old_posx, self._absolute_sash_pos, self._relative_sash_pos, '\n'
         #   self._to_redraw_sash = -1
            
        # Dragging the sash
        elif evt.Dragging() and self._dragMode == wx.SPLIT_DRAG_DRAGGING:
            #print 'Arrastando Sash:', sash_hit
            self._working_sash_shift = self._working_sash_shift + (posx - self._old_posx)
            if not self._working_sash_shift:
                return 
          #  print 'self._working_sash_shift:', self._working_sash_shift
            new_sash_pos = self._OnSashPositionChanging(self._working_sash, 
                                            self._relative_sash_pos + self._working_sash_shift
            )
            if new_sash_pos == -1:
                # the change was not allowed
                return
            
            #print 'AAA:', self._absolute_sash_pos, self._relative_sash_pos, new_sash_pos
            new_sash_pos = (self._absolute_sash_pos - self._relative_sash_pos) + new_sash_pos
            self._DragSashTracker(new_sash_pos)
            self._old_posx = posx
          
            
        # LeftUp: Finsish the drag
        elif evt.LeftUp() and self._dragMode == wx.SPLIT_DRAG_DRAGGING:
            #print '\nLargou o Sash'
            self._dragMode = wx.SPLIT_DRAG_NONE
            self.ReleaseMouse()
            self.SetCursor(wx.STANDARD_CURSOR)
            self._DestroySashTracker()
            
          #  print 'self._working_sash_shift:', self._working_sash_shift

            if not self._working_sash_shift:
                return 

            self._SetSashPositionAndNotify(self._working_sash, 
                                self._relative_sash_pos + self._working_sash_shift
            )        

            self._checkRequestedSashPosition = False

 
    

    def _OnEnterSash(self):
        self.SetCursor(self._sashCursorWE)


    def _OnLeaveSash(self):
        self.SetCursor(wx.STANDARD_CURSOR)

                   
    def _OnSashPositionChanging(self, idx, new_pos):
        # Ajusta a posicao e envia como evento para a possivel apreciacao/alteracao 
        # por algum outro objeto.
        #print '_OnSashPositionChanging:', idx, new_pos
        new_pos = self._AdjustSashPosition(idx, new_pos)
        # send the events
        evt = MultiSplitterEvent(wx.wxEVT_COMMAND_SPLITTER_SASH_POS_CHANGING, self)
        evt.SetSashIdx(idx)
        evt.SetSashPosition(new_pos)
        if not self._DoSendEvent(evt):
            # the event handler vetoed the change
            new_pos = -1
        else:
            # or it might have changed the value
            new_pos = evt.GetSashPosition()
        #print '_OnSashPositionChanging({}): {}'.format(idx, new_pos)    
        return new_pos


    def _SetSashPositionAndNotify(self, idx, new_pos): 
        #print '\n_SetSashPositionAndNotify:', idx, new_pos
        self._DoSetSashPosition(idx, new_pos)
        
        evt = MultiSplitterEvent(wx.wxEVT_COMMAND_SPLITTER_SASH_POS_CHANGED, self)
        evt.SetSashIdx(idx)
        evt.SetSashPosition(new_pos)
        self._DoSendEvent(evt)



        

    def _DoSetSashPosition(self, idx, new_pos):
        # Se permitido, altera a posicao no vetor self._sashes e retorna True
        # Senao, retorna False
        
        #print '_DoSetSashPosition:', idx, self.get_windows_indexes_shown()[idx], new_pos
        # Adjust for Hidden windows
        idx = self.get_windows_indexes_shown()[idx]
       
        new_pos = self._AdjustSashPosition(idx, new_pos)
        if new_pos == self._sashes[idx]:
            return False
        if self._GetFit():
            prop = new_pos / float(self._LarguraUtil())
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
            self._sashes[idx] = new_pos 
        return True

    
    def _AdjustSashPosition(self, idx, new_pos):
        # Ajusta a posicao do sash para ele nao ser menor que o minimo permitido
        #entrou = new_pos
        #
        #window = self.GetWindow(idx)
        min_width = 0 #window.GetMinWidth()
        #print 'AAA:', min_width, self._minimumPaneSize
        if min_width == -1 or self._minimumPaneSize > min_width:
            min_width = self._minimumPaneSize
        if new_pos < min_width:
            new_pos = min_width
        #print '_AdjustSashPosition({}, {}): {}'.format(idx, entrou, new_pos)    
        return new_pos    


    def _get_sash_position_x(self, idx):
        if idx < 0:
            return 0
        posx = 0
        i = 0
        for window in self._windows:
                        
            if window.IsShown():
                win_idx = self.IndexOf(window)
                posx += self._sash_size
                posx += self._sashes[win_idx]
                i += 1
            if idx+1 == i:
                #print '_get_sash_position_x:', idx, posx  
                return posx
        raise Exception('ERROR')            

    
    
    #def _GetWindowMin(self, window):
    #    return window.GetMinWidth()

        
    def _get_sash_DC(self):
        dc = wx.ClientDC(self)  
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.sashColor))	
        return dc
    

    def _DrawSashes(self):
        # if there are no splits then we're done.
        if not self._windows:
            return 
        dc = self._get_sash_DC() 
        # Desenhando os Sashes 				
        posx = self._border_size 
        for idx, sash_pos in enumerate(self._sashes):
            if self.GetWindow(idx).IsShown():
                posx += sash_pos 
                dc.DrawRectangle(posx, self._border_size, self._sash_size,
                            self.GetClientSize().height - 2*self._border_size
                )
                posx += self._sash_size   


    def _draw_sash(self, idx):
        if self.GetWindow(idx).IsShown():
           # print '\n\nREDRAWING SASH: {}\n'.format(idx)
            posx = self._get_sash_position_x(idx)
            dc = self._get_sash_DC()
            dc.DrawRectangle(posx, self._border_size, self._sash_size,
                            self.GetClientSize().height - 2*self._border_size
            )
            
    def _DrawBorders(self):
        if self._border_size > 0:
            dc = self._get_sash_DC() 
            # Borda esquerda
            dc.DrawRectangle(0, 0, self._border_size, self.GetClientSize().height)
            # A borda direita eh um sash
            # Borda acima
            dc.DrawRectangle(self._border_size, 0, 
                             self.GetClientSize().width - self._border_size, 
                             self._border_size
            )
            # Borda abaixo
            dc.DrawRectangle(self._border_size, 
                             self.GetClientSize().height - self._border_size, 
                             self.GetClientSize().width - self._border_size, 
                             self._border_size
            )
        


    def _InitSashTracker(self, posx):
     #   print '_InitSashTracker'
        if not self.trackerCanvas:
            border = self._border_size
            height = self.GetClientSize().GetHeight() - 2*border
            sash = self._sash_size     
            self.trackerCanvas = wx.Panel(self.GetParent(), pos=(posx, border),
                                          size=(sash, height)
            )
            self.trackerCanvas.SetBackgroundColour(self.sashTrackerColor)
            self.trackerCanvas.Refresh()


    def _DragSashTracker(self, posx):
        #print '_DragSashTracker:', posx
        if self.trackerCanvas:
            self.trackerCanvas.SetPosition(wx.Point(posx, self._sash_size))
            self.trackerCanvas.Refresh()
            sash_hit_1 = self._SashHitTest(posx, 0)
            sash_hit_2 = self._SashHitTest(posx + self._sash_size, 0)
            if sash_hit_1 != -1:
                self._draw_sash(sash_hit_1)
               # print '\n\nHIT: {}\n\n'.format(sash_hit_1)
                
            if sash_hit_2 != -1 and sash_hit_2 != sash_hit_1:
                self._draw_sash(sash_hit_2)
              #  print '\n\nHIT 2: {}\n\n'.format(sash_hit_2)
                

    def _DestroySashTracker(self):
        #print '_DestroySashTracker'
        if self.trackerCanvas:
            temp = self.trackerCanvas
            self.trackerCanvas = None
            temp.Destroy()



    def _SashHitTest(self, posx, posy):
        # if there are no splits then we're done.
        if not self._windows:
            return -1
        if posx >= 0 and posx <= self._border_size:
            # In the border
            return -1  
        pos = 0
        
        for idx, sash_pos in enumerate(self._sashes):
            window = self.GetWindow(idx)
            if window.IsShown():
                pos += self._sash_size
                pos += sash_pos
                # Tolerancia alem de 1 nao funciona, pois o ponteiro passa a cair
                # nas janelas, que nao sao parte deste objeto
                hitMin = pos - 1
                hitMax = pos + self._sash_size + 1  
                if posx >= hitMin and posx <= hitMax:
                    i = self.GetVisibleIndexOf(window)
                    #print '_SashHitTest:', i
                    return i
        return -1



    def _GetFit(self):
        return self.fit


    def _LarguraUtil(self):
        if self._GetFit():
            w = self.GetParent().GetClientSize().GetWidth() - self._border_size
            w = w - (len(self._sashes) * self._sash_size)
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
            soma += self._border_size
            soma += len(self.get_windows_shown()) * self._sash_size
            self.SetSize([soma, self.GetSize().GetHeight()]) 

         #   #print '    self.SetSize([{}, {}])'.format(soma, self.GetSize().GetHeight()) 
        #self.Bind(wx.EVT_SIZE, self._OnSize)
        
            
        self._SizeWindows()
        
        
    def _SizeWindows(self):
        #print '\n_SizeWindows', self.GetSize(), self.GetParent().GetSize(), self.GetClientSize()
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

        border = self._border_size
        sash   = self._sash_size
        
        if 'wxMSW' in wx.PlatformInfo:
            self.Freeze()
        
        x = y = border
        h = self.GetClientSize().GetHeight() - (2 * border)
               
        for idx, spos in enumerate(self._sashes):
            ##print '    _sash:', idx, spos
            window = self.GetWindow(idx)
            if window.IsShown():
                #print 'window.SetSize({}, {}, {}, {})'.format(x, y, spos, h)
                window.SetSize(x, y, spos, h)
                ##print '    {} - SetDimensions({}, {}, {}, {})'.format(window._view._controller_uid, x, y, spos, h)
                
                #for panel in window.selectedCanvas:
                #    panel.Refresh()                
                #self._draw_window_selection(window)                
                
                x += spos + sash	
                
        if 'wxMSW' in wx.PlatformInfo:
            self.Thaw()
              
        self._DrawSashes()
        self._DrawBorders()  
        
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



