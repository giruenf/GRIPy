# -*- coding: utf-8 -*-

import wx

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator, AutoMinorLocator, LogLocator, NullLocator, NullFormatter
from matplotlib.colors import colorConverter, rgb2hex
from MatplotlibWidgets import SpanSelector, MultiCursor

import numpy as np

from collections import OrderedDict

from Basic.Colors import DARK_GRAY, LIGHT_GRAY, COLOR_CYCLE_HEX, COLOR_CYCLE_RGB, COLOR_CYCLE_NAMES

from UI import LogPlotSwitcher, PartitionSelector

from OM.Manager import ObjectManager


class PlotPanel(wx.Panel):
    ###########################################################################
    ############################ LAYOUT PROPERTIES ############################
    ###########################################################################

    PREF_N_LEGENDS = 3
    PREF_N_TRACKS = 7

    BOTTOM_MARGIN = 0.0
    LEFT_MARGIN = 0.0
    TOP_MARGIN = 0.0
    RIGHT_MARGIN = 0.0

    TRACKS_LEFT_MARGIN = 0.0
    TRACKS_TOP_MARGIN = 0.0
    TRACKS_PAD = 0.0

    LEGENDS_HEIGHT = 0.1/3.0
    LEGENDS_PAD = 0.0

    DEPTH_WIDTH = 0.1/3.0

    LZ_PAD = 0.0
    ZONE_WIDTH = DEPTH_WIDTH

    TRACKS_LEFT = LEFT_MARGIN + DEPTH_WIDTH + LZ_PAD + ZONE_WIDTH + TRACKS_LEFT_MARGIN
    TRACKS_BOTTOM = BOTTOM_MARGIN

    MINIMUM_DLEGEND_HEIGHT = PREF_N_LEGENDS*(LEGENDS_HEIGHT + LEGENDS_PAD) - LEGENDS_PAD
    MAXIMUM_TRACKS_WIDTH = (1.0 - TRACKS_LEFT - RIGHT_MARGIN + TRACKS_PAD)/PREF_N_TRACKS - TRACKS_PAD

    LEGENDS_LEFT = TRACKS_LEFT

    DEPTH_LEFT = LEFT_MARGIN
    DEPTH_BOTTOM = BOTTOM_MARGIN

    DLEGEND_LEFT = DEPTH_LEFT

    DLEGEND_WIDTH = DEPTH_WIDTH

    ZONE_LEFT = DEPTH_LEFT + DEPTH_WIDTH + LZ_PAD
    ZONE_BOTTOM = DEPTH_BOTTOM

    ZLEGEND_LEFT = ZONE_LEFT

    ZLEGEND_WIDTH = ZONE_WIDTH

    ###########################################################################
    ############################# COLOR PROPERTIES ############################
    ###########################################################################

    COLORS = COLOR_CYCLE_HEX
    COLORS_RGBA = COLOR_CYCLE_RGB
    COLORS_NAMES = COLOR_CYCLE_NAMES
    BG_COLOR = LIGHT_GRAY  # '#ffffff'

    ###########################################################################
    ############################# LABEL PROPERTIES ############################
    ###########################################################################

    LABEL_LEFT_MARGIN = 0.025
    LABEL_BOTTOM_MARGIN = 0.25
    LABEL_RIGHT_MARGIN = 0.025
    LABEL_TOP_MARGIN = 0.25
    LABEL_LINE_SIZE = 0.5

    ###########################################################################
    ############################# TEXT PROPERTIES #############################
    ###########################################################################

    TEXT_FONT_SIZE = 'small'
    NUMBER_FONT_SIZE = 'x-small'

    ###########################################################################
    ############################# ZOOM PROPERTIES #############################
    ###########################################################################

    SCROLL_RANGE = 1000
    ZOOM_LEVELS = [1.0, 1.0/2.0, 1.0/3.0, 1.0/4.0]

    ###########################################################################
    ###########################################################################
    ###########################################################################

    def __init__(self, welluid, loguidmap, *args, **kwargs):
        super(PlotPanel, self).__init__(*args, **kwargs)
        self._OM = ObjectManager(self)
        self.welluid = welluid
        self.loguidmap = loguidmap
        self.depthuid = self._OM.list('depth', welluid)[0].uid

        self.partitionuid = None
        self.partsuids = []

        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.dummy_axes = []
        self.tracks = []
        self.legends = []
        self.depth_ax = None
        self.zones_ax = None
        self.dlegend = None
        self.zlegend = None

        self.ylim = None
        self.position = None
        self.window_size = None

        self.start_layout()

        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)

        self.canvas.Bind(wx.EVT_SCROLLWIN_LINEUP, self.on_line_up)
        self.canvas.Bind(wx.EVT_SCROLLWIN_LINEDOWN, self.on_line_down)
        self.canvas.Bind(wx.EVT_SCROLLWIN_PAGEUP, self.on_page_up)
        self.canvas.Bind(wx.EVT_SCROLLWIN_PAGEDOWN, self.on_page_down)
        self.canvas.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.on_thumb_track)
        self.canvas.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

        rectprops = dict(alpha=0.25, facecolor=DARK_GRAY)
        self.span = SpanSelector(self.canvas, self.depth_ax, self.on_span, rectprops)

        lineprops = dict(color=DARK_GRAY)
        self.cursor = MultiCursor(self.canvas, [self.depth_ax, self.zones_ax] + self.dummy_axes, lineprops)

        self.status_bar = self.Parent.StatusBar

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

        self.get_ylim()
        self.reset_depth()

    @staticmethod
    def set_line_properties(line, **kwargs):
        line.update(kwargs)

    @staticmethod
    def get_legend_info(legend):
        label = legend.texts[0].get_text()
        vmin = None
        vmax = None
        t1 = legend.texts[1].get_text()
        if t1:
            vmin = float(t1)
        t2 = legend.texts[2].get_text()
        if t2:
            vmax = float(t2)
        return label, vmin, vmax

    @staticmethod
    def move_ax(ax, dl, db):
        l, b = ax.get_position().min
        w, h = ax.get_position().size
        rect = [l + dl, b + db, w, h]
        ax.set_position(rect)

    @staticmethod
    def resize_ax(ax, dw, dh):
        l, b = ax.get_position().min
        w, h = ax.get_position().size
        rect = [l, b, w + dw, h + dh]
        ax.set_position(rect)

    def get_layout_params(self):
        self.N_TRACKS = len(self.loguidmap)
        self.N_LEGENDS = max(len(a) for a in self.loguidmap)

        LEGENDS_TOTAL_HEIGHT = (self.LEGENDS_HEIGHT + self.LEGENDS_PAD)*self.N_LEGENDS - self.LEGENDS_PAD
        if LEGENDS_TOTAL_HEIGHT < self.MINIMUM_DLEGEND_HEIGHT:
            LEGENDS_TOTAL_HEIGHT = self.MINIMUM_DLEGEND_HEIGHT
        self.LEGENDS_BOTTOM = 1.0 - self.TOP_MARGIN - LEGENDS_TOTAL_HEIGHT

        self.DLEGEND_BOTTOM = self.LEGENDS_BOTTOM

        self.ZLEGEND_BOTTOM = self.LEGENDS_BOTTOM

        self.TRACKS_WIDTH = (1.0 - self.TRACKS_LEFT - self.RIGHT_MARGIN + self.TRACKS_PAD)/self.N_TRACKS - self.TRACKS_PAD
        if self.TRACKS_WIDTH > self.MAXIMUM_TRACKS_WIDTH:
            self.TRACKS_WIDTH = self.MAXIMUM_TRACKS_WIDTH
        self.TRACKS_HEIGHT = self.LEGENDS_BOTTOM - self.BOTTOM_MARGIN - self.TRACKS_TOP_MARGIN

        self.LEGENDS_WIDTH = self.TRACKS_WIDTH

        self.DEPTH_HEIGHT = self.TRACKS_HEIGHT

        self.ZONE_HEIGHT = self.DEPTH_HEIGHT

        self.DLEGEND_HEIGHT = LEGENDS_TOTAL_HEIGHT

        self.ZLEGEND_HEIGHT = self.DLEGEND_HEIGHT

    def start_layout(self):
        self.get_layout_params()
        self.create_depth()
        self.create_dlegend()

        self.create_zone()
        self.create_zlegend()

        for i in range(len(self.loguidmap)):
            self.dummy_axes.append(None)
            self.tracks.append([])
            self.legends.append([])
            for j in range(len(self.loguidmap[i])):
                self.tracks[i].append(None)
                self.legends[i].append(None)

        for i in range(len(self.loguidmap)):
            self.create_dummy_ax(i)
            for j in range(len(self.loguidmap[i])):
                self.create_ax(i, j)
                self.create_legend(i, j)

    def refresh_layout(self):
        self.get_layout_params()
        rect = [self.DEPTH_LEFT, self.DEPTH_BOTTOM, self.DEPTH_WIDTH, self.DEPTH_HEIGHT]
        self.depth_ax.set_position(rect)
        rect = [self.DLEGEND_LEFT, self.DLEGEND_BOTTOM, self.DLEGEND_WIDTH, self.DLEGEND_HEIGHT]
        self.dlegend.set_position(rect)

        for i in range(len(self.loguidmap)):
            left = self.TRACKS_LEFT + (self.TRACKS_PAD + self.TRACKS_WIDTH)*i
            rect = [left, self.TRACKS_BOTTOM, self.TRACKS_WIDTH, self.TRACKS_HEIGHT]
            self.dummy_axes[i].set_position(rect)

        for i in range(len(self.loguidmap)):
            left = self.TRACKS_LEFT + (self.TRACKS_PAD + self.TRACKS_WIDTH)*i
            rect = [left, self.TRACKS_BOTTOM, self.TRACKS_WIDTH, self.TRACKS_HEIGHT]
            for j in range(len(self.loguidmap[i])):
                self.tracks[i][j].set_position(rect)

        for i in range(len(self.loguidmap)):
            left = self.LEGENDS_LEFT + (self.TRACKS_PAD + self.LEGENDS_WIDTH)*i
            for j in range(len(self.loguidmap[i])):
                bottom = self.LEGENDS_BOTTOM + (self.LEGENDS_HEIGHT + self.LEGENDS_PAD)*j
                rect = [left, bottom, self.LEGENDS_WIDTH, self.LEGENDS_HEIGHT]
                self.legends[i][j].set_position(rect)

    def create_depth(self):
        rect = [self.DEPTH_LEFT, self.DEPTH_BOTTOM, self.DEPTH_WIDTH, self.DEPTH_HEIGHT]
        ax = self.figure.add_axes(rect)

        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())

        self.depth_ax = ax

    def create_zone(self):
        rect = [self.ZONE_LEFT, self.ZONE_BOTTOM, self.ZONE_WIDTH, self.ZONE_HEIGHT]
        ax = self.figure.add_axes(rect)

        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())

        self.zones_ax = ax

    def create_dlegend(self):
        rect = [self.DLEGEND_LEFT, self.DLEGEND_BOTTOM, self.DLEGEND_WIDTH, self.DLEGEND_HEIGHT]
        ax = self.figure.add_axes(rect)

        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())

        depthname = self._OM.get(self.depthuid).name

        ax.text(0.5, 0.5, depthname, ha='center', va='center',
                rotation='vertical', fontsize=self.TEXT_FONT_SIZE)

        self.dlegend = ax

    def create_zlegend(self):
        rect = [self.ZLEGEND_LEFT, self.ZLEGEND_BOTTOM, self.ZLEGEND_WIDTH, self.ZLEGEND_HEIGHT]
        ax = self.figure.add_axes(rect)

        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())

        ax.text(0.5, 0.5, 'Zonas', ha='center', va='center',
                rotation='vertical', fontsize=self.TEXT_FONT_SIZE)

        self.zlegend = ax

    def create_dummy_ax(self, i):
        left = self.TRACKS_LEFT + (self.TRACKS_PAD + self.TRACKS_WIDTH)*i
        rect = [left, self.TRACKS_BOTTOM, self.TRACKS_WIDTH, self.TRACKS_HEIGHT]
        ax = self.figure.add_axes(rect)

        ax.grid(axis='x', which='major', linestyle=':')
        ax.grid(axis='y', which='major', linestyle='-.')
        ax.grid(axis='y', which='minor', linestyle=':')

        ax.xaxis.set_major_formatter(NullFormatter())

        ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax.yaxis.set_major_formatter(NullFormatter())

        self.dummy_axes[i] = ax

    def create_ax(self, i, j):
        ax = self.dummy_axes[i].twiny()

        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.xaxis.set_major_formatter(NullFormatter())

        x = [0, 1]
        y = [0, 1]
        color = self.BG_COLOR
        if self.loguidmap[i][j] is not None:
            x = self._OM.get(self.loguidmap[i][j]).data
            y = self._OM.get(self.depthuid).data
            color = self.COLORS[j]
        ax.plot(x, y, color)

        self.tracks[i][j] = ax

    def create_legend(self, i, j):
        left = self.LEGENDS_LEFT + (self.TRACKS_PAD + self.LEGENDS_WIDTH)*i
        bottom = self.LEGENDS_BOTTOM + (self.LEGENDS_HEIGHT + self.LEGENDS_PAD)*j

        rect = [left, bottom, self.LEGENDS_WIDTH, self.LEGENDS_HEIGHT]
        ax = self.figure.add_axes(rect, label="legend %i %i" % (i, j))

        ax.xaxis.set_major_locator(NullLocator())
        ax.yaxis.set_major_locator(NullLocator())

        label = ''
        vmin = ''
        vmax = ''
        color = self.BG_COLOR
        if self.loguidmap[i][j] is not None:
            log = self._OM.get(self.loguidmap[i][j])
            label = log.name
            xmin, xmax = self.tracks[i][j].get_xlim()
            vmin = "%g" % xmin
            vmax = "%g" % xmax
            color = self.COLORS[j]

        ax.text(0.5, 1.0 - self.LABEL_TOP_MARGIN, label, ha='center', va='top', fontsize=self.TEXT_FONT_SIZE)
        ax.text(self.LABEL_LEFT_MARGIN, self.LABEL_BOTTOM_MARGIN, vmin, ha='left', va='center', fontsize=self.NUMBER_FONT_SIZE)
        ax.text(1.0 - self.LABEL_RIGHT_MARGIN, self.LABEL_BOTTOM_MARGIN, vmax, ha='right', va='center', fontsize=self.NUMBER_FONT_SIZE)
        ax.plot([0.5 - self.LABEL_LINE_SIZE/2, 0.5 + self.LABEL_LINE_SIZE/2], [self.LABEL_BOTTOM_MARGIN, self.LABEL_BOTTOM_MARGIN], color, lw=2)

        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)

        self.legends[i][j] = ax

    def get_ylim(self):
        ylim = [-np.inf, np.inf]
        depth = self._OM.get(self.depthuid)
        for m in self.loguidmap:
            for loguid in m:
                if loguid is not None:
                    valid_depth = depth.data[~np.isnan(self._OM.get(loguid).data)]
                    if len(valid_depth):
                        ymin = np.nanmin(valid_depth)
                        ymax = np.nanmax(valid_depth)
                        if ymin < ylim[1] or ymax > ylim[0]:
                            ylim = [max(ymax, ylim[0]), min(ymin, ylim[1])]
        if np.isinf(ylim).any():
            ylim = [np.nanmax(depth.data), np.nanmin(depth.data)]
        self.ylim = ylim

    def set_position(self, position):
        self.position = position
        ylim = (self.position + self.window_size, self.position)
        for ax in self.dummy_axes:
            ax.set_ylim(ylim)
        self.depth_ax.set_ylim(ylim)
        self.zones_ax.set_ylim(ylim)

    def set_window_size(self, window_size):
        self.window_size = window_size
        ylim = (self.position + self.window_size, self.position)

        for ax in self.dummy_axes:
            ax.set_ylim(ylim)
        locs = ax.get_yticks()[1:-1]
        step = locs[1] - locs[0]
        loc_min = locs[0] - int((locs[0] - self.ylim[1])/step)*step
        loc_max = locs[-1] + int((self.ylim[0] - locs[-1])/step)*step
        locs = np.arange(loc_min, loc_max+step, step)

        self.depth_ax.clear()
        for loc in locs:
            self.depth_ax.text(0.5, loc, "%g" % loc, ha='center', va='center', fontsize=self.NUMBER_FONT_SIZE)
        self.depth_ax.set_ylim(ylim)
        self.zones_ax.set_ylim(ylim)
        self.depth_ax.xaxis.set_major_locator(NullLocator())
        self.depth_ax.yaxis.set_major_locator(NullLocator())

    def reset_scrollbar(self):
        self.scroll_thumb_size = int(self.window_size/(self.ylim[0] - self.ylim[1])*self.SCROLL_RANGE)
        scroll_pos = self.get_scroll_pos(self.position)
        self.canvas.SetScrollbar(wx.VERTICAL, scroll_pos, self.scroll_thumb_size, self.SCROLL_RANGE)

    def reset_depth(self):
        self.position = self.ylim[1]
        self.window_size = self.ylim[0] - self.ylim[1]
        self.set_window_size(self.window_size)
        self.set_position(self.position)

    def set_dlegend(self, label):
        self.dlegend.texts[0].set_text(label)

    def set_log(self, i, j, loguid=None, xlim=None, **kwargs):
        if loguid is not None and loguid != self.loguidmap[i][j]:
            self.loguidmap[i][j] = loguid
            log = self._OM.get(loguid)
            depth = self._OM.get(self.depthuid)
            logname = log.name
            self.tracks[i][j].lines[0].set_xdata(log.data)
            self.tracks[i][j].lines[0].set_ydata(depth.data)
            self.legends[i][j].texts[0].set_text(logname)
            if xlim is None:
                self.tracks[i][j].set_xlim(np.nanmin(log.data), np.nanmax(log.data))
                xticks = self.tracks[i][j].get_xticks()
                xmin = xticks[0]
                xmax = xticks[-1]
                xlim = (xmin, xmax)

        if self.loguidmap[i][j] is None:
            return

        if xlim is not None:
            self.tracks[i][j].set_xlim(xlim)
            self.legends[i][j].texts[1].set_text("%g" % xlim[0])
            self.legends[i][j].texts[2].set_text("%g" % xlim[1])

        if kwargs:
            self.set_line_properties(self.tracks[i][j].lines[0], **kwargs)
            self.set_line_properties(self.legends[i][j].lines[0], **kwargs)

    def set_log_scale(self, i):
        # TODO Implementar escala logaritmica
        self.dummy_axes[i].set_xscale('log')
        for ax, legend in zip(self.tracks[i], self.legends[i]):
            ax.set_xscale('log')
            ax.xaxis.set_major_locator(LogLocator())
            ax.xaxis.set_major_formatter(NullFormatter())
            xticks = ax.get_xticks()
            xmin = xticks[0]/10.0
            xmax = xticks[-1]*10.0
            ax.set_xlim((xmin, xmax))
            if legend.texts[0].get_text():
                legend.texts[1].set_text("%g" % xmin)
                legend.texts[2].set_text("%g" % xmax)

    def add_track(self):  # TODO: Continuar aqui
        self.loguidmap.append([])
        self.get_layout_params()

        self.dummy_axes.append(None)
        self.create_dummy_ax(self.N_TRACKS - 1)
        self.dummy_axes[-1].set_ylim(self.depth_ax.get_ylim())
        self.cursor.add_ax(self.dummy_axes[-1])

        self.tracks.append([])
        self.legends.append([])

        self.refresh_layout()

    def add_legend(self, i):  # TODO: Continuar aqui
        j = len(self.loguidmap[i])
        self.loguidmap[i].append(None)
        self.tracks[i].append(None)
        self.legends[i].append(None)
        self.get_layout_params()
        self.create_ax(i, j)
        self.dummy_axes[i].set_ylim(self.depth_ax.get_ylim())
        self.create_legend(i, j)
        self.refresh_layout()

    def on_press(self, event):
        if event.inaxes is None:
            return
        left, bottom = event.inaxes.get_position().min
        onlegend = left >= self.LEGENDS_LEFT and bottom >= self.LEGENDS_BOTTOM
        onzone = left == self.ZONE_LEFT and bottom == self.LEGENDS_BOTTOM
        if event.dblclick and onlegend:
            i = int((left - self.LEGENDS_LEFT)/(self.LEGENDS_WIDTH + self.TRACKS_PAD) + 0.5)
            j = int((bottom - self.LEGENDS_BOTTOM)/(self.LEGENDS_HEIGHT + self.LEGENDS_PAD) + 0.5)
            self.launch_switch_dialog(i, j)
        elif event.dblclick and onzone:
            self.launch_zones_dialog()

    def on_move(self, event):
        if event.inaxes is None:
            return
        left, bottom = event.inaxes.get_position().min
        onaxes = left >= self.TRACKS_LEFT and bottom == self.TRACKS_BOTTOM
        ondepth = left == self.DEPTH_LEFT and bottom == self.DEPTH_BOTTOM
        onzone = left == self.ZONE_LEFT and bottom == self.ZONE_BOTTOM
        if onaxes:
            i = int((left - self.TRACKS_LEFT)/(self.TRACKS_WIDTH + self.TRACKS_PAD) + 0.5)
            info = ["%s = %g" % (self.dlegend.texts[0].get_text(), event.ydata)]
            transform = None
            scale = event.inaxes.get_xscale()
            xmin, xmax = event.inaxes.get_xlim()
            x = event.xdata
            if scale == 'linear':
                transform = lambda vmin, vmax: vmin + (vmax - vmin)*(x - xmin)/(xmax - xmin)
            elif scale == 'log':
                transform = lambda vmin, vmax: vmin*(vmax/vmin)**(np.log(x/xmin)/np.log(xmax/xmin))
            for ax, legend in zip(self.tracks[i], self.legends[i]):
                label, vmin, vmax = self.get_legend_info(legend)
                if vmin is None or vmax is None:
                    continue
                val = transform(vmin, vmax)
                info.append("%s = %g" % (label, val))
            self.status_bar.SetStatusText("        ".join(info))
        elif ondepth:
            info = "%s = %g" % (self.dlegend.texts[0].get_text(), event.ydata)
            self.status_bar.SetStatusText(info)
        elif onzone:
            info = ["%s = %g" % (self.dlegend.texts[0].get_text(), event.ydata)]

            depthdata = self._OM.get(self.depthuid).data

            idx = np.searchsorted(depthdata, event.ydata)
            if np.abs(depthdata[idx] - event.ydata) > np.abs(depthdata[idx-1] - event.ydata):
                idx -= 1

            for partuid in self.partsuids:
                part = self._OM.get(partuid)
                if part.data[idx]:
                    info.append("PART = {}".format(part.name))
                    break

            self.status_bar.SetStatusText("        ".join(info))

    def on_span(self, ymin, ymax):
        if (ymax - ymin)/self.window_size < 0.01:
            self.reset_depth()
        else:
            nymin = self.snap_to_nearest_scroll_pos(ymin)
            nymax = self.snap_to_nearest_scroll_pos(ymax)
            self.set_window_size(nymax - nymin)
            self.set_position(nymin)
        self.canvas.draw_idle()
        self.reset_scrollbar()

    def snap_to_nearest_scroll_pos(self, pos):
        f = (pos - self.ylim[1])/(self.ylim[0] - self.ylim[1])
        nf = float(int(f*self.SCROLL_RANGE + 0.5))/self.SCROLL_RANGE
        return self.ylim[1] + nf*(self.ylim[0] - self.ylim[1])

    def get_scroll_pos(self, pos):
        f = (pos - self.ylim[1])/(self.ylim[0] - self.ylim[1])
        return int(f*self.SCROLL_RANGE)

    def on_line_up(self, event):
        pos = self.position - self.window_size/10.0
        if pos < self.ylim[1]:
            pos = self.ylim[1]

        if pos == self.position:
            return

        self.set_position(pos)
        scroll_pos = self.get_scroll_pos(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def on_line_down(self, event):
        pos = self.position + self.window_size/10.0
        if pos > self.ylim[0] - self.window_size:
            pos = self.ylim[0] - self.window_size

        if pos == self.position:
            return

        self.set_position(pos)
        scroll_pos = self.get_scroll_pos(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def on_page_up(self, event):
        pos = self.position - self.window_size/2.0
        if pos < self.ylim[1]:
            pos = self.ylim[1]

        if pos == self.position:
            return

        self.set_position(pos)
        scroll_pos = self.get_scroll_pos(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def on_page_down(self, event):
        pos = self.position + self.window_size/2.0
        if pos > self.ylim[0] - self.window_size:
            pos = self.ylim[0] - self.window_size

        if pos == self.position:
            return

        self.set_position(pos)
        scroll_pos = self.get_scroll_pos(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def on_thumb_track(self, event):
        scroll_pos = event.GetPosition()
        f = float(scroll_pos)/self.SCROLL_RANGE
        pos = self.ylim[1] + f*(self.ylim[0] - self.ylim[1])

        if pos == self.position:
            return

        self.set_position(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def on_mouse_wheel(self, event):
        wheel_rotation = event.GetWheelRotation()
        delta = event.GetWheelDelta()
        n = wheel_rotation/delta

        pos = self.position - n*self.window_size/10.0
        if pos < self.ylim[1]:
            pos = self.ylim[1]
        elif pos > self.ylim[0] - self.window_size:
            pos = self.ylim[0] - self.window_size

        if pos == self.position:
            return

        self.set_position(pos)
        scroll_pos = self.get_scroll_pos(pos)
        self.canvas.draw_idle()
        self.canvas.SetScrollPos(wx.VERTICAL, scroll_pos)

    def launch_zones_dialog(self):  # TODO: usar escolha anterior, caso exista
        dlg = PartitionSelector.Dialog(self.welluid, self)
        dlg.set_partitionuid(self.partitionuid)
        dlg.set_partsuids(self.partsuids)
        if dlg.ShowModal() == wx.ID_OK:
            partitionuid = dlg.get_partitionuid()
            partsuids = dlg.get_partsuids()

            if partitionuid == self.partitionuid and partsuids == self.partsuids:
                return

            self.partitionuid = partitionuid
            self.partsuids = partsuids

            self.zones_ax.clear()
            self.zones_ax.set_ylim(self.depth_ax.get_ylim())
            self.zones_ax.xaxis.set_major_locator(NullLocator())
            self.zones_ax.yaxis.set_major_locator(NullLocator())

            depthdata = self._OM.get(self.depthuid).data
            xmin, xmax = self.zones_ax.get_xlim()
            ymin = np.nanmax(depthdata)
            ymax = np.nanmin(depthdata)
            extent = (xmin, xmax, ymin, ymax)

            for uid in self.partsuids:
                part = self._OM.get(uid)
                wxcolor = part.color
                mplcolor = [float(c)/255.0 for c in wxcolor]
                color = colorConverter.to_rgba_array(mplcolor[:3])
                im = np.tile(color, (part.data.shape[0], 1)).reshape(-1, 1, 4)
                im[:, 0, -1] = part.data
                self.zones_ax.imshow(im, aspect='auto', extent=extent, interpolation='none')

            self.canvas.draw_idle()

    def launch_switch_dialog(self, i, j):  # TODO: rever a parte das cores
        loguid = self.loguidmap[i][j]
        i_color = None

        fun = self.tracks[i][j].xaxis.get_major_locator().tick_values
        lims = OrderedDict()
        for log in self._OM.list('log', self.welluid):
            t = fun(np.nanmin(log.data), np.nanmax(log.data))
            lims[log.uid] = (t[0], t[-1])

        lim = [None, None]
        if loguid is not None:
            color = self.tracks[i][j].lines[0].get_color()
            if type(color) == tuple:
                color = rgb2hex(color)
            i_color = self.COLORS.index(color)
            lim = self.tracks[i][j].get_xlim()
            lims[loguid] = lim

        dialog = LogPlotSwitcher.Dialog(self, self.COLORS_RGBA, self.COLORS_NAMES, i_color, self.welluid, lims, loguid)
        if dialog.ShowModal() == wx.ID_OK:
            new_i_color = dialog.get_i_color()
            new_lim = dialog.get_lim()
            new_loguid = dialog.get_loguid()

            k = None
            xlim = None
            kwargs = {}
            if loguid != new_loguid:
                k = new_loguid
            if lim[0] != new_lim[0] or lim[1] != new_lim[1]:
                xlim = new_lim
            if i_color != new_i_color:
                kwargs['color'] = self.COLORS[new_i_color]

            self.set_log(i, j, k, xlim, **kwargs)

            if k is not None:
                prev_ylim = self.ylim
                self.get_ylim()
                if prev_ylim != self.ylim:
                    self.set_window_size(self.window_size)
                    self.reset_scrollbar()

            self.canvas.draw_idle()
