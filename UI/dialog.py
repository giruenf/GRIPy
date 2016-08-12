# -*- coding: utf-8 -*-

import wx
import wx.lib.sized_controls as sc
from OM.Manager import ObjectManager
from collections import OrderedDict
import Parms
#from logplotformat import LogPlotFormat 


class SelectionLogPanel(sc.SizedScrolledPanel):
    def __init__(self, parent):
        sc.SizedScrolledPanel.__init__(self, parent)
        self._OM = ObjectManager(self)
        self.well_uid = None
        self.log_tuple = None
        self.choices = []
        self.SetBackgroundColour('green')
        self.SetSizerType("vertical")
        
     
    def add_choice(self):
        choice = wx.Choice(self)
        choice.SetSizerProps(expand=True)
        choice.Append('')
        for i, log in enumerate(self.log_tuple):       
            choice.Append(log.attributes.get('name', '{}.{}'.format(*log.uid)))
        choice.Bind(wx.EVT_CHOICE, self.on_choice)
        choice.SetSelection(0)
        self.choices.append(choice)
        self.Layout()
        print 'add_choice: ', self.GetSize()
        
    def remove_choice(self, i):
        choice = self.choices.pop(i)
        #self.panel.Sizer.Remove(choice)
        #self.Sizer.Layout()
        choice.Hide()
        del choice

    def on_choice(self, event):
        i = self.choices.index(event.GetEventObject())
        j = event.GetSelection()
        if i == len(self.choices) - 1:
            if j != 0:
                self.add_choice()
        else:
            if j == 0:
                self.remove_choice(i)
        event.Skip(True)

    def get_selection(self):
        selection = []
        for choice in self.choices[:-1]:
            selection.append(self.log_tuple[choice.GetSelection()-1].uid)
        return selection

    def set_well(self, well_uid):
        for i in range(len(self.choices)-1, -1, -1):
            self.remove_choice(i)
        self.well_uid = well_uid
        self.log_tuple = self._OM.list('log', self.well_uid)
        self.choices = []
        if self.well_uid is not None:
            self.add_choice()



class Dialog(wx.Dialog):   
    _CONTROL_WELL_SELECTOR = 'well_selector'
    _CONTROL_LOG_SELECTOR = 'log_selector'
    _CONTROL_SPIN = 'spin'
    _CONTROL_TEXT_CTRL = 'text_ctrl'    
    
    
    def __init__(self, parent, args=None, dialog_label='', **kwargs):
        #print '\nDialog.__init__'
        self._OM = ObjectManager(self)    
        super(Dialog, self).__init__(parent)
        self.keyword_callback_map = {}
        self.height = 80
        self.width = 250
        self.panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        for item in args:
            function, args, ret_keyword = item
            #print 'function: ', str(function)
            type_control, in_func, out_func = function(self, args)
            if in_func is not None:
                #print 'in_func'
                in_func()
            self.keyword_callback_map[ret_keyword] = type_control, in_func, out_func
        self.panel.SetSizer(self.mainbox)
        vbox.Add(self.panel, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        button_sizer = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        vbox.Add(button_sizer, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        #self.height += 60
        self.SetSizer(vbox)        
        self.SetTitle(dialog_label)
        #print 'self.height: ', self.height
        self.SetSize((self.width, self.height))
        #for sbs in self.mainbox.GetChildren():
        #    print 'sbs.GetSize(): ' , sbs.GetSize()
        #print 'self.GetSize: ', self.GetSize()    
        
    
    def get_results(self):
        map_ = {}
        for ret_keyword, (control_type, cb_in_function, cb_out_function) in \
                                self.keyword_callback_map.items():
            #print ret_keyword, cb_in_function, cb_out_function                         
            map_[ret_keyword] = cb_out_function()
        return map_
        

    def well_selector(self, label):
        #print 'well_selector'
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)       
        choice = wx.Choice(self.panel)
        wells = OrderedDict()
        sbs.Add(choice, proportion=0, flag=wx.EXPAND)
        self.mainbox.Add(sbs, 0, border=3, flag=wx.ALL|wx.EXPAND)
        
        def in_func():
            choice.Clear()
            wells.clear()
            for well in self._OM.list('well'):
                #print 'well.name: ', well.name
                wells[well.uid] = well.name
            choice.AppendItems(wells.values())
            choice.Bind(wx.EVT_CHOICE, lambda event: self._on_select(event, 
                        wells, [Dialog._CONTROL_LOG_SELECTOR]))    
        
        def out_func():
            #print 
            #print self._OM.get(wells.keys()[choice.GetSelection()]).name
            return wells.keys()[choice.GetSelection()]
        self.height += 60    
        return self._CONTROL_WELL_SELECTOR, in_func, out_func
        
        
    def log_selector(self, label):
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        choice = wx.Choice(self.panel)
        logs = OrderedDict()
        sbs.Add(choice, proportion=0, flag=wx.EXPAND)
        self.mainbox.Add(sbs, 0, border=3, flag=wx.ALL|wx.EXPAND)
                 
        def in_func(well_uid=None):
            choice.Clear()
            logs.clear()
            if well_uid is not None:
                for log in self._OM.list('log', well_uid):
                    logs[log.uid] = log.name
            choice.AppendItems(logs.values())
            choice.Bind(wx.EVT_CHOICE, lambda event: self._on_select(event, logs, None))    
        
        def out_func():
            if not logs:
                return None
            return logs.keys()[choice.GetSelection()]
        self.height += 60
        return self._CONTROL_LOG_SELECTOR, in_func, out_func
        
        
    def _on_select(self, evt, obj_map, propagate_list):
        if propagate_list:
            for (type_control, in_func, out_func) in self.keyword_callback_map.values():
                if type_control in propagate_list:
                    in_func(obj_map.keys()[evt.GetSelection()])        
        
        
    def multiple_logs_selector(self, label):    
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        slp = SelectionLogPanel(sb)#, (50, self.width-50))
        sbs.Add(slp, proportion=4, flag=wx.EXPAND)  
        self.mainbox.Add(sbs, 1, border=3, flag=wx.ALL|wx.EXPAND)
                         
        def in_func(well_uid=None):
            if well_uid is not None:
                slp.set_well(well_uid)
                
        def out_func():
            return self.get_selection()
            
        self.height += 200
        return self._CONTROL_LOG_SELECTOR, in_func, slp.get_selection    
        
        
    def text_ctrl(self, label):
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        tc = wx.TextCtrl(self.panel)
        sbs.Add(tc, proportion=1, flag=wx.EXPAND)
        self.mainbox.Add(sbs, 0, border=3, flag=wx.ALL|wx.EXPAND)     
        self.height += 60
        return self._CONTROL_TEXT_CTRL, None, tc.GetValue
    
    
    def spin(self, label, spin_min, spin_max):
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        spin = wx.SpinCtrl(self.panel, value='1', size=(60, -1))
        spin.SetRange(spin_min, spin_max)        
        sbs.Add(spin, proportion=1, flag=wx.EXPAND)
        self.mainbox.Add(sbs, 0, border=3, flag=wx.ALL|wx.EXPAND)
        self.height += 60
        return self._CONTROL_SPIN, None, spin.GetValue
    
    
    def logplotformat_selector(self, label):
        sb = wx.StaticBox(self.panel, label=label)
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)       
        choice = wx.Choice(self.panel)
        sbs.Add(choice, proportion=0, flag=wx.EXPAND)
        self.mainbox.Add(sbs, 0, border=3, flag=wx.ALL|wx.EXPAND)
        
        def in_func():
            choice.Clear()
            choice.AppendItems(Parms.ParametersManager.get().get_PLTs_names())
            #choice.Bind(wx.EVT_CHOICE, lambda event: self._on_select(event, 
            #            wells, [Dialog._CONTROL_LOG_SELECTOR]))    
        
        def out_func():
            #plt = PM.ParametersManager.get().getPLT(choice.GetSelection())
            #lpf = LogPlotFormat.create_from_PLTFile(plt)
            #print lpf
            names = Parms.ParametersManager.get().get_PLTs_names()
            return names[choice.GetSelection()]
        self.height += 60    
        return self._CONTROL_WELL_SELECTOR, in_func, out_func    



"""
if __name__ == '__main__':    

    app = wx.App(False)
    frame = wx.Frame(None)
    dlg = Dialog(frame, [(log_selector, 'Well:', 'poco')],#,
                         #(Dialog.logplotformat_selector, 'Format: ', 'lpf')], 
                'Well Selector')
    if dlg.ShowModal() == wx.ID_OK:
            print dlg.get_results()
           
    dlg.Destroy()
    
    #frame.Show()
    #app.MainLoop()
"""    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    