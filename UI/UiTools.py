# -*- coding: utf-8 -*-

import wx


class GenericLogInputPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(GenericLogInputPanel, self).__init__(*args, **kwargs)

        self.create_well_input()

        self.choices = []
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def create_well_choice(self):
        sb_well = wx.StaticBox(self, label=u"Poço:")
        sbs_well = wx.StaticBoxSizer(sb_well, wx.VERTICAL)

        self.well_choice = wx.Choice(self)
        self.well_choice.Bind(wx.EVT_CHOICE, self.on_well_input)

        sbs_well.Add(self.well_choice, proportion=1, flag=wx.EXPAND)
        self.sizer.Add(sbs_well)
        self.selected_well = None

    def create_logs_choices(self, labels):
        sb = wx.StaticBox(self, label=u"Perfis:")
        sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
        fgs = wx.FlexGridSizer(len(labels), 2, 4, 4)

        self.choices = []
        for label in labels:
            st = wx.StaticText(self, label=label + ": ")
            choice = wx.Choice(self)
            fgs.Add(st)
            fgs.Add(choice)
            self.choices.append(choice)

        sbs.Add(fgs, proportion=1, flag=wx.EXPAND)
        self.sizer.Add(sbs)

    def set_wells_info(self, wells_info):
        self.well_choice.Clear()
        self.well_choice.AppendItems([info['name'] for info in wells_info])


class LogInputPanel(wx.Frame):
    def __init__(self, labels, *args, **kwargs):
        super(LogInputPanel, self).__init__(*args, **kwargs)

        fgs = wx.FlexGridSizer(len(labels), 2, 4, 4)

        self.choices = []
        for label in labels:
            st = wx.StaticText(self, label=label + ": ")
            choice = wx.Choice(self)
            fgs.Add(st)
            fgs.Add(choice)
            self.choices.append(choice)
        fgs.AddGrowableCol(1, 1)

        self.SetSizer(fgs)

    def set_logs_info(self, logs_info):
        labels = []
        for info in logs_info:
            label = info['name']
            unit = info.get('unit', '')
            if unit:
                label += ' (%s)' % unit
            labels.append(label)
        for choice in self.choices:
            choice.Clear()
            choice.AppendItems(labels)

    def get_selection(self):
        selection = []
        for choice in self.choices:
            selection.append(choice.GetSelection())
        return selection

    def set_selection(self, selections):
        for choice, sel in zip(self.choices, selections):
            choice.SetSelection(sel)


class GeneralInputPanel(wx.Frame):
    def __init__(self, labels, *args, **kwargs):
        super(LogInputPanel, self).__init__(*args, **kwargs)

        fgs = wx.FlexGridSizer(len(labels), 2, 4, 4)

        self.choices = []
        for label in labels:
            st = wx.StaticText(self, label=label + ": ")
            choice = wx.Choice(self)
            fgs.Add(st)
            fgs.Add(choice)
            self.choices.append(choice)
        fgs.AddGrowableCol(1, 1)

        self.SetSizer(fgs)

    def set_logs_info(self, logs_info):
        labels = []
        for info in logs_info:
            label = info['name']
            unit = info.get('unit', '')
            if unit:
                label += ' (%s)' % unit
            labels.append(label)
        for choice in self.choices:
            choice.Clear()
            choice.AppendItems(labels)

    def get_selection(self):
        selection = []
        for choice in self.choices:
            selection.append(choice.GetSelection())
        return selection

    def set_selection(self, selections):
        for choice, sel in zip(self.choices, selections):
            choice.SetSelection(sel)

if __name__ == '__main__':
    app = wx.App(False)
    mw = LogInputPanel(["VP", "VS", "RHOB"], None)
    mw.Fit()
    names = ['VP', 'VS', 'RHOB', 'NPHI', 'GR']
    units = ['M/S', 'M/S', 'G/CM3', '', 'API']
    info = [dict(name=name, unit=unit) for name, unit in zip(names, units)]
    mw.set_logs_info(info)
    #mw.set_selection([1, 1, 1])
    mw.Show()
    app.MainLoop()