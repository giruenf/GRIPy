# -*- coding: utf-8 -*-

import sys

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, TextEditMixin, \
    ListCtrlAutoWidthMixin, ListRowHighlighter

from collections import OrderedDict

MEDIUM_GREY = wx.Colour(224, 224, 224)


class _ODTSectionCtrl(wx.ListCtrl, TextEditMixin, CheckListCtrlMixin,
                      ListCtrlAutoWidthMixin, ListRowHighlighter):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        TextEditMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        ListRowHighlighter.__init__(self, color=MEDIUM_GREY, mode=1)

        self.InsertColumn(0, '', width=24)
        self.InsertColumn(1, 'MNEM', width=80)
        self.InsertColumn(2, 'UNIT', width=80)
        self.InsertColumn(3, 'DATA', width=160)
        self.InsertColumn(4, 'DESC')

        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.on_begin_label_edit)

    def on_begin_label_edit(self, event):
        if event.m_col == 0:
            event.Veto()
        else:
            event.Skip()
        
    def set_version(self, section):
        index = self.InsertStringItem(sys.maxint, '')
        self.SetStringItem(index, 1, section[1])
        self.SetStringItem(index, 3, section[0])
        self.SetStringItem(index, 4, section[2])
        self.RefreshRows()
        
    def set_well(self, maxd, mind, step):
        index = self.InsertStringItem(sys.maxint, '')
        self.SetStringItem(index, 1, 'STRT')
#        self.SetStringItem(index, 2, unit)
        self.SetStringItem(index, 3, str(mind))
        self.SetStringItem(index, 4, 'START DEPTH')
        index1 = self.InsertStringItem(sys.maxint, '')
        self.SetStringItem(index1, 1, 'STOP')
#        self.SetStringItem(index1, 2, unit)
        self.SetStringItem(index1, 3, str(maxd))
        self.SetStringItem(index1, 4, 'STOP DEPTH')
        index2 = self.InsertStringItem(sys.maxint, '')
        self.SetStringItem(index2, 1, 'STEP')
#        self.SetStringItem(index1, 2, unit)
        self.SetStringItem(index2, 3, str(step))
        self.SetStringItem(index2, 4, 'STEP')
        self.RefreshRows()
        
    def set_curve(self, logheader):
        index0 = self.InsertStringItem(sys.maxint, '')
        self.SetStringItem(index0, 1, 'DEPT')
        self.SetStringItem(index0, 4, ' DEPT')
        for line in logheader:
            index = self.InsertStringItem(sys.maxint, '')
            self.SetStringItem(index, 1, line['Name'][1:5])
            self.SetStringItem(index, 2, line['Unit of Measure'])
#            self.SetStringItem(index, 3, section[0])
            self.SetStringItem(index, 4, line['Name'])
        self.RefreshRows()

    def get_section(self):
        n = self.GetItemCount()
        section = OrderedDict()
        for i in range(n):
            mnem = self.GetItem(i, 1).GetText()
            unit = self.GetItem(i, 2).GetText()
            data = self.GetItem(i, 3).GetText()
            desc = self.GetItem(i, 4).GetText()
            line = {"MNEM": mnem, "UNIT": unit, "DATA": data, "DESC": desc}
            section[mnem] = line
        return section

    def get_selection(self):
        n = self.GetItemCount()
        selection = []
        for i in range(n):
            if self.IsChecked(i):
                selection.append(i)
        return selection


class _ODTSectionPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(_ODTSectionPanel, self).__init__(*args, **kwargs)

        vbox = wx.BoxSizer(wx.VERTICAL)
        add = wx.Button(self, -1, u'Adicionar linha', size=(100, -1))
        rem = wx.Button(self, -1, u'Remover linhas', size=(100, -1))
        self.Bind(wx.EVT_BUTTON, self.on_add, id=add.GetId())
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=rem.GetId())
        vbox.Add(add, 1, wx.ALIGN_TOP)
        vbox.Add(rem, 1, wx.ALIGN_TOP)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.section_ctrl = _ODTSectionCtrl(self)
        hbox.Add(vbox, 0)
        hbox.Add(self.section_ctrl, 1, wx.EXPAND)

        self.SetSizer(hbox)
        
    def set_version(self, fileheader):
        self.section_ctrl.set_version(fileheader)
    
    def set_well(self, maxd, mind, step):
        self.section_ctrl.set_well(maxd, mind, step)
        
    def set_curve(self, logheader):
        self.section_ctrl.set_curve(logheader)

    def get_section(self):
        return self.section_ctrl.get_section()
        
    def on_add(self, event):
        index = self.section_ctrl.InsertStringItem(sys.maxint, '')
        self.section_ctrl.SetStringItem(index, 1, '')
        self.section_ctrl.SetStringItem(index, 2, '')
        self.section_ctrl.SetStringItem(index, 3, '')
        self.section_ctrl.SetStringItem(index, 4, '')
        self.section_ctrl.RefreshRows()

    def on_remove(self, event):
        selection = self.section_ctrl.get_selection()
        for i in selection[::-1]:
            self.section_ctrl.DeleteItem(i)
        self.section_ctrl.RefreshRows()


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        nb = wx.Notebook(self)

        self.version_panel = _ODTSectionPanel(nb)
        self.well_panel = _ODTSectionPanel(nb)
        self.curve_panel = _ODTSectionPanel(nb)
        self.parameter_panel = _ODTSectionPanel(nb)
        other_panel = wx.Panel(nb)
        self.other_textctrl = wx.TextCtrl(other_panel, -1,
                                          style=wx.TE_MULTILINE)
        box = wx.BoxSizer()
        box.Add(self.other_textctrl, 1, wx.EXPAND)
        other_panel.SetSizer(box)
        print '\nno panel', self.version_panel
        nb.AddPage(self.version_panel, "~VERSION INFORMATION")
        print '\nno panel'
        nb.AddPage(self.well_panel, "~WELL INFORMATION")
        nb.AddPage(self.curve_panel, "~CURVE INFORMATION")
        nb.AddPage(self.parameter_panel, "~PARAMETER INFORMATION")
        nb.AddPage(other_panel, "~OTHER INFORMATION")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def set_fileheader(self, fileheader):
        self.version_panel.set_version(fileheader)   
        
    def set_logheader(self, maxd, mind, step):
        self.well_panel.set_well (maxd, mind, step)  

    def set_curveheader(self, logheader):
        self.curve_panel.set_curve(logheader)
        
    def get_header(self):  # TODO: Manter os nomes das seções originais
        header = OrderedDict()
        header["V"] = self.version_panel.get_section()
        header["W"] = self.well_panel.get_section()
        header["C"] = self.curve_panel.get_section()
        psection = self.parameter_panel.get_section()
        if psection:
            header["P"] = psection
        osection = self.other_textctrl.GetValue()
        if osection:
            header["O"] = osection
        header["A"] = ''
        return header


class Dialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        if 'on_ok_callback' in kwargs:
            self.on_ok_callback = kwargs.pop('on_ok_callback')
        else:
            self.on_ok_callback = None

        if 'on_cancel_callback' in kwargs:
            self.on_cancel_callback = kwargs.pop('on_cancel_callback')
        else:
            self.on_cancel_callback = None

        super(Dialog, self).__init__(*args, **kwargs)

        self.header_panel = Panel(self)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, self.on_button)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.header_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        vbox.Add(button_sizer, flag=wx.ALIGN_RIGHT)
        self.SetSizer(vbox)

        self.SetSize((800, 600))
        self.SetTitle(u"Editor de Cabeçalho ODT")

    def set_header(self, fileheader, logheader, ndepth):
        maxd = ndepth[-1]
        mind = ndepth[0]
        step = ndepth[1] - ndepth[0]
        self.header_panel.set_fileheader (fileheader)
        self.header_panel.set_logheader (maxd, mind, step)
        self.header_panel.set_curveheader (logheader)

    def get_header(self):
        return self.header_panel.get_header()

    def on_button(self, event):
        evt_id = event.GetId()
        if evt_id == wx.ID_OK and self.on_ok_callback is not None:
            self.on_ok_callback(event)
        elif evt_id == wx.ID_CANCEL and self.on_cancel_callback is not None:
            self.on_cancel_callback(event)
        event.Skip(True)
