from collections import OrderedDict

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, TextEditMixin, \
    ListCtrlAutoWidthMixin, ListRowHighlighter

from classes.ui import DialogController
from classes.ui import Dialog

MEDIUM_GREY = wx.Colour(224, 224, 224)


class _LASSectionCtrl(wx.ListCtrl, TextEditMixin, CheckListCtrlMixin,
                      ListCtrlAutoWidthMixin, ListRowHighlighter):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        TextEditMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        ListRowHighlighter.__init__(self, color=MEDIUM_GREY, mode=1)

        self.index = 0

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

    def set_section(self, section):
        for line in section.values():
            # index = self.InsertStringItem(sys.maxint, '')
            index = self.InsertItem(self.index, '')
            self.SetItem(index, 1, line["MNEM"])
            self.SetItem(index, 2, line["UNIT"])
            self.SetItem(index, 3, line["DATA"])
            self.SetItem(index, 4, line["DESC"])
            self.index += 1
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


class _LASSectionPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(_LASSectionPanel, self).__init__(*args, **kwargs)

        vbox = wx.BoxSizer(wx.VERTICAL)
        add = wx.Button(self, -1, u'Adicionar linha', size=(100, -1))
        rem = wx.Button(self, -1, u'Remover linhas', size=(100, -1))
        self.Bind(wx.EVT_BUTTON, self.on_add, id=add.GetId())
        self.Bind(wx.EVT_BUTTON, self.on_remove, id=rem.GetId())
        vbox.Add(add, 1, wx.ALIGN_TOP)
        vbox.Add(rem, 1, wx.ALIGN_TOP)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.section_ctrl = _LASSectionCtrl(self)
        hbox.Add(vbox, 0)
        hbox.Add(self.section_ctrl, 1, wx.EXPAND)

        self.SetSizer(hbox)

        self.index = 0

    def set_section(self, section):
        self.section_ctrl.set_section(section)

    def get_section(self):
        return self.section_ctrl.get_section()

    def on_add(self, event):
        # index = self.section_ctrl.InsertStringItem(sys.maxint, '')
        index = self.section_ctrl.InsertItem(self.index, '')
        self.section_ctrl.SetStringItem(index, 1, '')
        self.section_ctrl.SetStringItem(index, 2, '')
        self.section_ctrl.SetStringItem(index, 3, '')
        self.section_ctrl.SetStringItem(index, 4, '')
        self.section_ctrl.RefreshRows()
        self.index += 1

    def on_remove(self, event):
        selection = self.section_ctrl.get_selection()
        for i in selection[::-1]:
            self.section_ctrl.DeleteItem(i)
        self.section_ctrl.RefreshRows()


class HeaderPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        nb = wx.Notebook(self)

        self.version_panel = _LASSectionPanel(nb)
        self.well_panel = _LASSectionPanel(nb)
        self.curve_panel = _LASSectionPanel(nb)
        self.parameter_panel = _LASSectionPanel(nb)
        other_panel = wx.Panel(nb)
        self.other_textctrl = wx.TextCtrl(other_panel, -1,
                                          style=wx.TE_MULTILINE)
        box = wx.BoxSizer()
        box.Add(self.other_textctrl, 1, wx.EXPAND)
        other_panel.SetSizer(box)

        nb.AddPage(self.version_panel, "~VERSION INFORMATION")
        nb.AddPage(self.well_panel, "~WELL INFORMATION")
        nb.AddPage(self.curve_panel, "~CURVE INFORMATION")
        nb.AddPage(self.parameter_panel, "~PARAMETER INFORMATION")
        nb.AddPage(other_panel, "~OTHER INFORMATION")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def set_header(self, header):
        self.version_panel.set_section(header["V"])
        self.well_panel.set_section(header["W"])
        self.curve_panel.set_section(header["C"])
        self.parameter_panel.set_section(header.get("P", OrderedDict()))
        self.other_textctrl.WriteText(header.get("O", ''))

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


class LASHeaderController(DialogController):
    tid = 'las_header_controller'

    def __init__(self, **state):
        super().__init__(**state)
        self.title = 'LAS Header file'
        self.size = (800, 600)


class LASHeader(Dialog):
    tid = 'las_header'

    def __init__(self, controller_uid):
        super().__init__(controller_uid)
        self.header_panel = HeaderPanel(self.mainpanel)
        sizer = self.GetSizer()
        sizer.Add(self.header_panel, 1, wx.EXPAND)

    def set_header(self, las_file_header):
        self.header_panel.set_header(las_file_header)

    def get_results(self):
        return self.header_panel.get_header()
