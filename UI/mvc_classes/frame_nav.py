# -*- coding: utf-8 -*-
import wx
from OM.Manager import ObjectManager
from UI.uimanager import UIManager

from collections import OrderedDict

from wxgripy import FrameController
from wxgripy import FrameModel
from wxgripy import Frame
from App import log


SLIDER_MARGIN = 5  # Default 6


class RangeSlider(wx.Slider):
    
    def __init__(self, *args, **kwargs):
        wx.Slider.__init__(self, *args, **kwargs)
        self.SetPageSize(1)
        self.calculate_rect()
        self.Bind(wx.EVT_SLIDER, self.on_event)

    def calculate_rect(self):
        self.rect = self.GetClientRect()
        self.rect.width -= 2*SLIDER_MARGIN
        self.rect.x += SLIDER_MARGIN

    def on_event(self, event):
        if event.GetEventType() == wx.EVT_LEFT_DOWN.typeId:
            if self.is_selrange():
                val = self.get_position(event) 
                if val < self.GetValue():
                    self.SetSelection(val, self.GetSelEnd())
                elif val > self.GetValue():    
                    self.SetSelection(self.GetSelStart(), val)
                self.send_change()    
            else:      
                event.Skip()
        elif event.GetEventType() == wx.EVT_SLIDER.typeId:
            self.send_change()

    def send_change(self):
        if self.is_selrange():
            #print 'send_change:', self.GetSelStart(), self.GetSelEnd()+1
            self.GetParent().GetParent().set_values(self.GetSelStart(), self.GetSelEnd()+1)
        else:    
            self.GetParent().GetParent().set_values(self.GetValue())
 
    def is_selrange(self):
        return (self.GetWindowStyle() & wx.SL_SELRANGE)
    
    def set_selrange(self, sel=True, selmin=None, selmax=None):
        if sel:
            self.SetWindowStyle(wx.SL_SELRANGE)
            if selmin is None or selmax is None:
                raise Exception()
            else:
                self.SetSelection(selmin, selmax)
            self.Bind(wx.EVT_LEFT_DOWN, self.on_event)  
        else:
            self.ClearSel()
            if self.is_selrange():
                self.Unbind(wx.EVT_LEFT_DOWN, handler=self.on_event)
            self.SetWindowStyle(wx.SL_BOTTOM)       
            if selmin is None:
                raise Exception()
            super(RangeSlider, self).SetValue(selmin)
       
    def SetSelection(self, minsel, maxsel):
        #print 'Aqui'
        super(RangeSlider, self).SetSelection(minsel, maxsel)
        #print 'aqui nao'
        value = minsel + ((maxsel - minsel)/2)
        super(RangeSlider, self).SetValue(value)
          
    def SetValue(self, value):
        old_min_range = self.GetSelStart()
        old_max_range = self.GetSelEnd()
        old_med_range = old_min_range + ((old_max_range - old_min_range)/2)
        new_min_range = value - (old_med_range - old_min_range)
        new_max_range = value + (old_max_range - old_med_range) 
        if new_min_range < self.GetRange()[0] or \
                                        new_max_range > self.GetRange()[1]:                               
            return False   
        super(RangeSlider, self).SetSelection(new_min_range, new_max_range)
        super(RangeSlider, self).SetValue(value)
        return True
    
    def get_position(self, e):
        click_min = self.rect.x + (self.GetThumbLength()/2)
        click_max = (self.rect.x + self.rect.width) - (self.GetThumbLength()/2)
        click_position = e.GetX()
        result_min = self.GetMin()
        result_max = self.GetMax()
        if click_position > click_min and click_position < click_max:
            result = self.linapp(click_min, click_max,
                                 result_min, result_max,
                                 click_position)
        elif click_position <= click_min:
            result = result_min
        else:
            result = result_max    
        return result
    
    def linapp(self, x1, x2, y1, y2, x):
        proportion = float(x - x1) / (x2 - x1)
        length = y2 - y1
        return round(proportion*length + y1)


class DimensionPanel(wx.Panel):
    
    def __init__(self, data_index_uid, display, is_range, min_idx, max_idx, *args, **kwargs):
        super(DimensionPanel, self).__init__(*args, **kwargs)
        self.SetSize(300, 50)
        #
        self.data_index_uid = data_index_uid
        OM =  ObjectManager(self)
        obj = OM.get(data_index_uid)
        #
        main_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, obj.name)
        #
        self.top_panel = wx.Panel(self)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.check_display = wx.CheckBox(self.top_panel, -1, label='Display')  
        self.check_display.Bind(wx.EVT_CHECKBOX, self._on_check_display)                  
        self.top_sizer.Add(self.check_display, 1, wx.ALIGN_CENTER|wx.LEFT, 30)
        #
        self.check_range = wx.CheckBox(self.top_panel, -1, label='Range')
        self.check_range.Bind(wx.EVT_CHECKBOX, self._on_check_range)   
        self.top_sizer.Add(self.check_range, 1, wx.ALIGN_CENTER|wx.RIGHT, 30)
        self.top_panel.SetSizer(self.top_sizer)
        #
        main_sizer.Add(self.top_panel, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)
        #
        self.label = obj.name
        self.vec = obj.data
        self.display = display
        self.is_range = is_range
        #
        self.bottom_panel = wx.Panel(self)
        self.bottom_sizer = wx.BoxSizer(wx.VERTICAL)
        self.slider = RangeSlider(self.bottom_panel)
        self.bottom_sizer.Add(self.slider, 0, wx.EXPAND)
        self.text_value = wx.StaticText(self.bottom_panel, -1)
        self.bottom_sizer.Add(self.text_value, 0, wx.ALIGN_CENTER)
        self.bottom_panel.SetSizer(self.bottom_sizer)
        #
        main_sizer.Add(self.bottom_panel, 0, wx.EXPAND)
        #
        self.slider.SetRange(0, len(self.vec)-1)
        self.min_idx = min_idx
        self.max_idx = max_idx
        #
        if self.display:
            self.set_check_display(1)
        else:
            self.set_check_display(0)
        # 
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.SetSizer(main_sizer)
        main_sizer.Layout()

    def _on_paint(self, event):
        self.slider.calculate_rect()
        event.Skip()

    def _on_check_display(self, event):
        self.set_check_display(event.GetSelection())

    def _on_check_range(self, event):
        self.set_check_range(event.GetSelection())
        
    def set_check_display(self, value=0):
        self.check_display.SetValue(value)
        if value:
            self.display = True
            self.set_check_range(1)
            self.check_range.Enable()
            
        else:
            self.display = False
            self.set_check_range(0)
            self.check_range.Disable()
               
    def set_check_range(self, value=0):
        #print 'set_check_range:', value
        if self.min_idx > self.max_idx:
            temp = self.min_idx
            self.min_idx = self.max_idx
            self.max_idx = temp
        if value:  
            self.is_range = True
            #self.slider.set_selrange(True, self.min_idx, self.max_idx)
            #self.set_values(self.min_idx, self.max_idx)
        else:
            self.is_range = False
            #self.slider.set_selrange(False, self.min_idx, self.max_idx)
            #self.set_values(self.min_idx, self.max_idx)
        self.slider.set_selrange(self.is_range, self.min_idx, self.max_idx)
        self.set_values(self.min_idx, self.max_idx)            
        self.check_range.SetValue(value)    
        
    
    def set_values(self, min_idx, max_idx=None):
        self.min_idx = min_idx
        if max_idx is not None:
            self.max_idx = max_idx
            from_str = 'From: {}'.format(self.vec[min_idx])
            # TODO: max_idx-1 to max_idx !!!
            to_str = '   To: {}'.format(self.vec[max_idx-1])
            self.text_value.SetLabel(from_str + to_str)
        else:
            val_str = 'Selected: {}'.format(self.vec[min_idx])
            self.text_value.SetLabel(val_str)
        #print 'set_values:', self.min_idx, self.max_idx    
        self.bottom_sizer.Layout()    
           
    
    def get_result(self):
        ret = {}
        ret['uid'] = self.data_index_uid
        ret['display'] = self.display
        ret['is_range'] = self.is_range
        #if self.display:
        ret['start'] = self.min_idx
        ret['end'] = self.max_idx
        #else:
        #    ret['start'] = self.slider.GetValue()
        #    ret['end'] = None
        return ret
    

###############################################################################
###############################################################################


class NavigatorController(FrameController):
    tid = 'navigator_controller'
    
    def __init__(self):
        super(NavigatorController, self).__init__()
 
    def PostInit(self):
        OM = ObjectManager(self)
        df = OM.get(('data_filter', self.model.data_filter_oid))
        data_indexes = df.data[::-1]
        for (di_uid, display, is_range, first, last) in data_indexes:
            #obj = OM.get(di_uid)
            #print '\n', obj.name, display, is_range, first, last
            self.view.add_panel(di_uid, display, is_range, first, last)  
        self.view.add_bottom_panel()    


    def Set(self, results):
        print 'NavigatorController.Set:', results
        OM = ObjectManager(self)
        df = OM.get(('data_filter', self.model.data_filter_oid))
        new_data = []
        for result in results[::-1]:
            new_data.append((result['uid'], result['display'], 
                            result['is_range'], result['start'], result['end'])
            ) 
            #print result
        df.data = new_data
        df.reload_data()
        print 'NavigatorController.Set ENDED'
        
            
class NavigatorModel(FrameModel):
    tid = 'navigator_model'

    _ATTRIBUTES = OrderedDict()
    _ATTRIBUTES['data_filter_oid'] = {
            'default_value': None,
            'type': int
    }  
    _ATTRIBUTES.update(FrameModel._ATTRIBUTES) 
     
    def __init__(self, controller_uid, **base_state): 
        super(NavigatorModel, self).__init__(controller_uid, **base_state) 


class Navigator(Frame):
    tid = 'navigator'

    def __init__(self, controller_uid):
        super(Navigator, self).__init__(controller_uid)
        self.basepanel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.basepanel.SetSizer(self.sizer)
        self.panels = []

    def add_panel(self, data_index_uid, display, is_range, start, end):
        panel = DimensionPanel(data_index_uid, display, is_range, start, end, self.basepanel)
        self.panels.append(panel)
        self.sizer.Add(panel, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5) #wx.ALIGN_CENTER
        self.sizer.Layout()
           
    def add_bottom_panel(self):
        buttons_panel = wx.Panel(self.basepanel)
        #buttons_panel.SetBackgroundColour('yellow')
        buttons_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.ok_button = wx.Button(buttons_panel, label='Ok')
        self.ok_button.Bind(wx.EVT_BUTTON, self.onOk)
        self.apply_button = wx.Button(buttons_panel, label='Apply')
        self.apply_button.Bind(wx.EVT_BUTTON, self.onApply)
        self.cancel_button = wx.Button(buttons_panel, label='Cancel')
        self.cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)
        #
        buttons_panel_sizer.Add(self.ok_button, 0,
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        buttons_panel_sizer.Add(self.apply_button, 0, 
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        buttons_panel_sizer.Add(self.cancel_button, 0, 
                                wx.ALIGN_CENTER|wx.LEFT|wx.TOP|wx.BOTTOM, 10
        )
        #
        buttons_panel.SetSizer(buttons_panel_sizer)
        #buttons_panel.Layout()
        self.sizer.Add(buttons_panel, 0, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 5) #wx.ALIGN_CENTER
        self.sizer.Layout()
        #

    def onOk(self, event):
        self._doOK()

    def onApply(self, event):
        self._doApply()
        
    def onCancel(self, event):
        self._doCancel()  

    def _doOk(self):
        self._doApply()
        self._doCancel()

    def _doApply(self):
        print '\n_doApply'
        results = []
        for panel in self.panels:
            results.append(panel.get_result())
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)    
        controller.Set(results)
        print '_doApply'
    def _doCancel(self):
        self.Close()  

     