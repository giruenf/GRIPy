# -*- coding: utf-8 -*-

import wx



# TODO: Parametros: levar para App.utils ou Parameters.manager
DEFAULT_LABEL_BG_COLOR  = '#B0C4DE' #LightSteelBlue  
SELECTION_WIDTH = 2
SELECTION_COLOR = 'green'



# Mixin for a selectable Panel
class SelectablePanelMixin(object):

    #def __init__(self, selected=False):
    #    self._selected = selected
        
    def is_selected(self):
        return self._selected
    
    def change_selection(self, selected):
        try:
            if self._selected == selected: 
                return
        except AttributeError:
            pass
        self._selected = selected
        if self._selected:
            self.create_selection()
            self.refresh_selection()
            self.Bind(wx.EVT_PAINT, self.on_paint_selection)
        else:
            self.Unbind(wx.EVT_PAINT, handler=self.on_paint_selection)
            self.destroy_selection()
    
    def on_paint_selection(self, event):
        self.refresh_selection()
        event.Skip()
    
    def create_selection(self): 
        # Using pos=(0,0) and size=(0,0) to avoid flicker on selection.
        self._sel_obj_0 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_0.SetBackgroundColour(SELECTION_COLOR)
        self._sel_obj_1 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_1.SetBackgroundColour(SELECTION_COLOR)           
        self._sel_obj_2 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_2.SetBackgroundColour(SELECTION_COLOR)       
        self._sel_obj_3 = wx.Panel(self, pos=(0, 0), size=(0, 0))
        self._sel_obj_3.SetBackgroundColour(SELECTION_COLOR)      
        self._selected = True

    def destroy_selection(self):
        self._sel_obj_0.Destroy()
        self._sel_obj_1.Destroy()
        self._sel_obj_2.Destroy()
        self._sel_obj_3.Destroy()
        self._selected = False
    
    def refresh_selection(self):
        if self._selected:
            self._sel_obj_0.SetSize(0, 0, SELECTION_WIDTH, self.GetSize()[1])
            self._sel_obj_1.SetSize(self.GetSize()[0] - SELECTION_WIDTH, 0, 
                                    SELECTION_WIDTH, self.GetSize()[1]
            )
            self._sel_obj_2.SetSize(0, 0, self.GetSize()[0], SELECTION_WIDTH)
            self._sel_obj_3.SetSize(0, self.GetSize()[1]- SELECTION_WIDTH,
                                    self.GetSize()[0], SELECTION_WIDTH
            )
            self._sel_obj_0.Refresh() 
            self._sel_obj_1.Refresh() 
            self._sel_obj_2.Refresh() 
            self._sel_obj_3.Refresh() 

