# -*- coding: utf-8 -*-

import wx

import operator
from OM.Manager import ObjectManager

_comparison_functions = {'lt': operator.lt,
                         'le': operator.le,
                         'eq': operator.eq,
                         'ne': operator.ne,
                         'ge': operator.ge,
                         'gt': operator.gt,
                         'in': operator.contains}


class _GenericInput(object):
    
    def get_uiobj(self):
        return self._uiobj
    
    def get_input(self):
        pass
    
    def disable(self):
        self._uiobj.Disable()
    
    def enable(self):
        self._uiobj.Enable()
    
    def bind(self, id):
        pass


class _OMSingleInput(_GenericInput):
    
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.Choice(*args, **kwargs)
        self._OM = ObjectManager(self)
        self.tids = None
        self.well_uid = None
        self.index2uid = None
    
    def set_tids(self, tids):
        self.tids = tids
    
    def set_well_uid(self, well_uid):
        self.well_uid = well_uid
    
    def refresh(self):
        if self.well_uid is None or self.tids is None:
            return False
        
        self.index2uid = []
        self.items = []
        
        for tid in self.tids:
            for obj in self._OM.list(tid, self.well_uid):
                self.index2uid.append(obj.uid)
                self.items.append(obj.name)
        
        self._uiobj.Clear()
        self._uiobj.AppendItems(self.items)
    
    # def get_input(self):
        # return self.index2uid[self._uiobj.GetSelection()]
    
    def get_input(self):
        selection = self._uiobj.GetSelection()
        uid = self.index2uid[selection]
        data = self._OM.get(uid).data
        return data
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_CHOICE, handler, id=id)


class _OMMultiInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.CheckListBox(*args, **kwargs)
        self._OM = ObjectManager(self)
        self.tids = None
        self.well_uid = None
        self.index2uid = None
    
    def set_tids(self, tids):
        self.tids = tids
    
    def set_well_uid(self, well_uid):
        self.well_uid = well_uid
    
    def refresh(self):
        if self.well_uid is None or self.tids is None:
            return False
        
        self.index2uid = []
        self.items = []
        
        for tid in self.tids:
            for obj in self._OM.list(tid, self.well_uid):
                self.index2uid.append(obj.uid)
                self.items.append(obj.name)
        
        self._uiobj.Clear()
        self._uiobj.AppendItems(self.items)
    
    # def get_input(self):
        # n = len(self._uiobj.Items)
        # return [self.index2uid[i] for i in range(n) if self._uiobj.IsChecked(i)]
    
    def get_input(self):
        n = len(self._uiobj.Items)
        selection = [i for i in range(n) if self._uiobj.IsChecked(i)]
        uids = [self.index2uid[i] for i in selection]
        data = [self._OM.get(uid).data for uid in uids]
        return data
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_CHECKLISTBOX, handler, id=id)


class _OMLogLikeInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.ComboBox(*args, **kwargs)
        self._OM = ObjectManager(self)
        self.well_uid = None
        self.index2uid = None
        self.propuid2pttnuid = None
        self.items = None
        self.default = None
    
    def set_well_uid(self, well_uid):
        self.well_uid = well_uid
    
    def set_default(self, default):
        self.default = default
        self.refresh()
    
    def refresh(self):
        if self.well_uid is None:
            return False
        
        self.index2uid = []
        self.propuid2pttnuid = {}
        self.items = []
        
        for log in self._OM.list('log', self.well_uid):
            self.index2uid.append(log.uid)
            self.items.append(log.name)
        
        for pttn in self._OM.list('partition', self.well_uid):
            pttn_uid = pttn.uid
            for prop in self._OM.list('property', pttn_uid):
                self.index2uid.append(prop.uid)
                self.items.append(prop.name)
                self.propuid2pttnuid[prop.uid] = pttn_uid
        
        self._uiobj.Clear()
        self._uiobj.SetItems(self.items)
        
        if self.default is not None:
            self._uiobj.SetValue(str(self.default))
    
    def get_input(self):
        sel = self._uiobj.GetSelection()
        if sel == wx.NOT_FOUND:
            value = self._uiobj.GetValue()
            value = float(value)
            return value
        else:
            uid = self.index2uid[sel]
            if uid[0] == 'log':
                data = self._OM.get(uid).data
            elif uid[0] == 'property':
                propuid = uid
                pttnuid = self.propuid2pttnuid[propuid]
                data = self._OM.get(pttnuid).getaslog(propuid)
            return data
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_COMBOBOX, handler, id=id)


class _FloatInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.TextCtrl(*args, **kwargs)
        
        # self.range = None
        self.default = None
        
        # self._uiobj.Bind(wx.EVT_TEXT, self._on_text)
    
    # def set_range(self, range):
        # self.range = range
    
    def set_default(self, default):
        self.default = default
        self._uiobj.SetValue(str(self.default))
    
    def get_input(self):
        try:
            text = self._uiobj.GetValue()
            value = float(text)
            return value
        except:
            return
    
    # def _on_text(self, event):
        # if self.range is None:
            # return
        
        # try:
            # text = self._uiobj.GetValue()
            # value = float(text)
        # except:
            # if self.default is None:
                # return
            # else:
                # return # TODO: ver se é melhor colocar o valor default
        
        # if value < self.range[0]:
            # self._uiobj.ChangeValue(str(self.range[0]))
        # elif value > self.range[1]:
            # self._uiobj.ChangeValue(str(self.range[1]))
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_TEXT, handler, id=id)


class _IntInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.SpinCtrl(*args, **kwargs)
        
        self.range = None
        self.default = None
    
    def set_range(self, range):
        self.range = range
        self._uiobj.SetRange(self.range[0], self.range[1])
    
    def set_default(self, default):
        self.default = default
        self._uiobj.SetValue(self.default)
    
    def get_input(self):
        return self._uiobj.GetValue
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_SPINCTRL, handler, id=id)


class _TextInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.TextCtrl(*args, **kwargs)
        
        self.default = None
    
    def set_default(self, default):
        self.default = default
        self._uiobj.SetValue(self.default)
    
    def get_input(self):
        return self._uiobj.GetValue()
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_TEXT, handler, id=id)


class _BoolInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.CheckBox(*args, **kwargs)
        self.default = None
    
    def set_default(self, default):
        self.default = default
        self._uiobj.SetValue(self.default)
    
    def get_input(self):
        return self._uiobj.IsChecked()
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_CHECKBOX, handler, id=id)


class _ChoiceInput(_GenericInput):
    def __init__(self, *args, **kwargs):
        self._uiobj = wx.Choice(*args, **kwargs)
        
        self.choices = None
        self.default = None
    
    def set_items(self, items):
        self.items = items
        self._uiobj.Clear()
        self._uiobj.AppendItems(self.items)
    
    def set_default(self, default):
        self.default = default
        index = self.items.index(self.default)
        self._uiobj.SetSelection(index)
    
    def get_input(self):
        return self.items[self._uiobj.GetSelection()]
    
    def bind(self, handler, id):
        self._uiobj.Bind(wx.EVT_CHOICE, handler, id=id)


class AutoGenPanel(wx.Panel):
    def __init__(self, parent, inputdesc, *args, **kwargs):
        super(AutoGenPanel, self).__init__(parent, *args, **kwargs)
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        
        self.widgets = {}
        self.eventmap = {}
        self.well_uid = None
        
        self._create_widgets(self.inputdesc)
        self._bind_conditions(self.inputdesc)
        self._layout_widgets(self.inputdesc)
        self._process_all_events()
    
    def _layout_widgets(self, inputdesc):
        nwidgets = len(self.widgets)
        
        fgridsizer = wx.FlexGridSizer(nwidgets, 2, 5, 5)
        
        for i, idesc in enumerate(inputdesc):
            dispname = idesc['dispname'] + ":"
            name = idesc['name']
            widget = self.widgets[name]
            
            label = wx.StaticText(self, label=dispname)
            
            fgridsizer.Add(label, proportion=0.0, flag=wx.ALIGN_RIGHT)
            
            fgridsizer.Add(widget.get_uiobj(), proportion=1.0, flag=wx.EXPAND)
            
            if idesc['type'] == 'ommulti':
                fgridsizer.AddGrowableRow(i)
            
            # if idesc['type'] == 'ommulti':
                # fgridsizer.Add(widget.get_uiobj(), proportion=1.0, flag=wx.EXPAND)
            # else:
                # fgridsizer.Add(widget.get_uiobj(), proportion=0.0, flag=wx.EXPAND)
        
        fgridsizer.AddGrowableCol(1)
        
        self.SetSizerAndFit(fgridsizer)
    
    def _bind_conditions(self, inputdesc):
        for idesc in inputdesc:
            if 'conditions' in idesc:
                name1 = idesc['name']
                for condition in idesc['conditions']:
                    name2 = condition[0]
                    widget = self.widgets[name2]
                    evt_id = wx.NewId()
                    widget.bind(self._process_event, evt_id)
                    self.eventmap[evt_id] = (name1, condition)
        #print self.eventmap
    
    def _process_event(self, event):
        evt_id = event.GetId()
        self._process_condition(evt_id)
    
    def _process_all_events(self):
        for evt_id in self.eventmap:
            self._process_condition(evt_id)
    
    def _process_condition(self, evt_id):
        name1, condition = self.eventmap[evt_id]
        name2, comparison, target = condition
        
        widget1 = self.widgets[name1]
        widget2 = self.widgets[name2]
        
        comparison_function = _comparison_functions[comparison]
        
        value = widget2.get_input()
        
        if comparison == 'in':
            value, target = target, value
        
        if comparison_function(value, target):
            widget1.enable()
        else:
            widget1.disable()
        
    def _create_widgets(self, inputdesc):
        for idesc in inputdesc:
            name = idesc['name']
            self.widgets[name] = self._create_widget(idesc)
        
    def _create_widget(self, inputdesc):
        input_type = inputdesc['type']
        
        if input_type == 'bool':
            widget = self._create_widget_bool(inputdesc)
        elif input_type == 'choice':
            widget = self._create_widget_choice(inputdesc)
        elif input_type == 'text':
            widget = self._create_widget_text(inputdesc)
        elif input_type == 'int':
            widget = self._create_widget_int(inputdesc)
        elif input_type == 'float':
            widget = self._create_widget_float(inputdesc)
        elif input_type == 'omsingle':
            widget = self._create_widget_omsingle(inputdesc)
        elif input_type == 'ommulti':
            widget = self._create_widget_ommulti(inputdesc)
        elif input_type == 'omloglike':
            widget = self._create_widget_omloglike(inputdesc)
        else:
            return
        
        return widget
        
    def _create_widget_bool(self, inputdesc):
        widget = _BoolInput(self)
        
        default = inputdesc.get('default', None)
        if default is not None:
            widget.set_default(default)
        
        return widget
        
    def _create_widget_choice(self, inputdesc):
        widget = _ChoiceInput(self)
        
        choices = inputdesc.get('items', None)
        if choices is None:
            return
        widget.set_items(choices)
        
        default = inputdesc.get('default', None)
        if default is not None:
            widget.set_default(default)
        
        return widget
        
    def _create_widget_text(self, inputdesc):
        widget = _TextInput(self)
        
        default = inputdesc.get('default', None)
        if default is not None:
            widget.set_default(default)
        
        return widget
        
    def _create_widget_int(self, inputdesc):
        widget = _IntInput(self)
        
        range = inputdesc.get('range', None)
        if range is not None:
            widget.set_range(range)
        
        default = inputdesc.get('default', None)
        if default is not None:
            widget.set_default(default)
        
        return widget
        
    def _create_widget_float(self, inputdesc):
        widget = _FloatInput(self)
        
        # range = inputdesc.get('range', None)
        # if range is not None:
            # widget.set_range(range)
        
        default = inputdesc.get('default', None)
        if default is not None:
            widget.set_default(default)
        
        return widget
        
    def _create_widget_omsingle(self, inputdesc):
        widget = _OMSingleInput(self)
        
        tids = inputdesc.get('tids', None)
        if tids is None:
            return
        
        widget.set_well_uid(self.well_uid)
        
        widget.set_tids(tids)
        
        widget.refresh()
        
        return widget
        
    def _create_widget_ommulti(self, inputdesc):
        widget = _OMMultiInput(self)
        
        tids = inputdesc.get('tids', None)
        if tids is None:
            return
        
        widget.set_well_uid(self.well_uid)
        
        widget.set_tids(tids)
        
        widget.refresh()
        
        return widget
    
    def _create_widget_omloglike(self, inputdesc):
        widget = _OMLogLikeInput(self)
        
        default = inputdesc.get('default', None)
        
        if default is not None:
            widget.set_default(default)
        
        widget.set_well_uid(self.well_uid)
        
        widget.refresh()
        
        return widget        
    
    def set_well_uid(self, well_uid):
        self.well_uid = well_uid
        
        for idesc in self.inputdesc:
            input_type = idesc['type']
            if input_type in ('omsingle', 'ommulti', 'omloglike'):
                name = idesc['name']
                widget = self.widgets[name]
                widget.set_well_uid(self.well_uid)
                widget.refresh()
    
    def get_input(self):
        input = {}
        
        for idesc in self.inputdesc:
            name = idesc['name']
            input_type = idesc['type']
            
            widget = self.widgets[name]
            
            # if input_type == 'omsingle':
                # uid = widget.get_input()
                # obj = self._OM.get(uid)
                # value = obj.data
            # elif input_type == 'ommulti':
                # uids = widget.get_input()
                # value = []
                # for uid in uids:
                    # obj = self._OM.get(uid)
                    # value.append(obj.data)
            
            input[name] = widget.get_input()
        
        return input


class AutoGenDialog(wx.Dialog):
    
    def __init__(self, uiparent, inputdesc, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None
        
        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None
        
        super(AutoGenDialog, self).__init__(uiparent, *args, **kwargs)
        
        self._OM = ObjectManager(self)
        
        well_label = wx.StaticText(self, label=u"Poço:")
        self.well_choice = self._create_well_choice()
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(well_label, proportion=0, flag=wx.ALL, border=5)
        hbox.Add(self.well_choice, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        
        self.autogenpanel = AutoGenPanel(self, inputdesc)
        
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.autogenpanel, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        
        self.SetSizerAndFit(vbox)

        # self.SetSize((400, 800))
    
    def _create_well_choice(self):
        self.index2uid = []
        items = []
        
        for well in self._OM.list('well'):
            uid = well.uid
            name = well.name
            
            self.index2uid.append(uid)
            items.append(name)
        
        well_choice = wx.Choice(self)
        well_choice.AppendItems(items)
        well_choice.Bind(wx.EVT_CHOICE, self.on_well_choice)
        
        return well_choice
    
    def get_well_uid(self):
        selection = self.well_choice.GetSelection()
        wuid = self.index2uid[selection]
        return wuid
    
    def get_input(self):
        return self.autogenpanel.get_input()
    
    def on_well_choice(self, event):
        selection = self.well_choice.GetSelection()
        wuid = self.index2uid[selection]
        self.autogenpanel.set_well_uid(wuid)
    
    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
