# -*- coding: utf-8 -*-

import wx

import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')

matplotlib.rcParams['lines.linewidth'] = 2.0
matplotlib.rcParams['axes.facecolor'] = '#eeeeee'
matplotlib.rcParams['axes.edgecolor'] = '#bcbcbc'
matplotlib.rcParams['patch.linewidth'] = 0.5
matplotlib.rcParams['patch.edgecolor'] = '#eeeeee'

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import NullLocator, NullFormatter, MaxNLocator


class Label(object):
    __default_layout_properties = {
        'horizontal_margin': 0.025,
        'vertical_margin': 0.25,
        'text_size': 'medium',
        'number_size': 'small',
        'line_size': 0.5
        }

    __valid_line_props = [
        'aa',
        'antialiased',
        'c',
        'color',
        'dash_capstyle',
        'dash_joinstyle',
        'drawstyle',
        'fillstyle',
        'linestyle',
        'linewidth',
        'ls',
        'lw',
        'marker',
        'markeredgecolor',
        'markeredgewidth',
        'markerfacecolor',
        'markerfacecoloralt',
        'markersize',
        'markevery',
        'mec',
        'mew',
        'mfc',
        'mfcalt',
        'ms',
        'solid_capstyle',
        'solid_joinstyle'
        ]

    __id = 0

    @classmethod
    def __get_unique_label(cls):
        label = '%s %i' % (cls.__name__, cls.__id)
        cls.__id += 1
        return label

    @classmethod
    def __get_valid_line_props(cls, props):
        valid_props = {}
        for key, value in props.items():
            if key in cls.__valid_line_props:
                valid_props[key] = value
        return valid_props

    def __init__(self, figure, rect, layout_properties=None):
        if layout_properties is None:
            layout_properties = self.__default_layout_properties
        else:
            for key, value in self.__default_layout_properties.items():
                if key not in layout_properties:
                    layout_properties[key] = value

        self.figure = figure
        self.rect = rect
        self.layout_properties = layout_properties

        label = self.__get_unique_label()
        self.ax = self.figure.add_axes(self.rect, label=label)
        self.ax.xaxis.set_major_locator(NullLocator())
        self.ax.yaxis.set_major_locator(NullLocator())

        t = 1.0 - self.layout_properties['vertical_margin']
        b = self.layout_properties['vertical_margin']
        l = self.layout_properties['horizontal_margin']
        r = 1.0 - self.layout_properties['horizontal_margin']
        ts = self.layout_properties['text_size']
        ns = self.layout_properties['number_size']
        ls = self.layout_properties['line_size']

        self.label = self.ax.text(0.5, t, '', ha='center', va='top', fontsize=ts)
        self.xmin = self.ax.text(l, b, '', ha='left', va='center', fontsize=ns)
        self.xmax = self.ax.text(r, b, '', ha='right', va='center', fontsize=ns)
        self.line = matplotlib.lines.Line2D([0.5 - ls/2, 0.5 + ls/2], [b, b])
        self.ax.add_line(self.line)

    def __del__(self):
        self.figure.delaxes(self.ax)

    def set_position(self, pos):
        self.rect = pos
        self.ax.set_position(pos)

    def get_position(self):
        return self.rect

    def set_xlim(self, xlim):
        xmin, xmax = xlim
        self.xmin.set_text(str(xmin))
        self.xmax.set_text(str(xmax))

    def get_xlim(self):
        xmin = self.xmin.get_text()
        xmax = self.xmax.get_text()
        return xmin, xmax

    def set_text(self, text):
        self.label.set_text(text)

    def get_text(self):
        return self.label.get_text()

    def set_line_properties(self, **props):
        self.line.update(self.__get_valid_line_props(props))

    def get_line_properties(self):
        return self.__get_valid_line_props(self.line.properties())


class Track(object):
    __valid_line_props = [
        'aa',
        'antialiased',
        'c',
        'color',
        'dash_capstyle',
        'dash_joinstyle',
        'drawstyle',
        'fillstyle',
        'linestyle',
        'linewidth',
        'ls',
        'lw',
        'marker',
        'markeredgecolor',
        'markeredgewidth',
        'markerfacecolor',
        'markerfacecoloralt',
        'markersize',
        'markevery',
        'mec',
        'mew',
        'mfc',
        'mfcalt',
        'ms',
        'solid_capstyle',
        'solid_joinstyle'
        ]

    __id = 0

    @classmethod
    def __get_unique_label(cls):
        label = '%s %i' % (cls.__name__, cls.__id)
        cls.__id += 1
        return label

    @classmethod
    def __get_valid_line_props(cls, props):
        valid_props = {}
        for key, value in props.items():
            if key in cls.__valid_line_props:
                valid_props[key] = value
        return valid_props

    def __init__(self, figure, rect):
        self.figure = figure
        self.rect = rect
        label = self.__get_unique_label()
        self.dummy_ax = figure.add_axes(self.rect, label=label)
        self.dummy_ax.xaxis.set_tick_params('major', size=0)
        self.dummy_ax.yaxis.set_tick_params('major', size=0)
        self.dummy_ax.xaxis.set_major_locator(MaxNLocator(5))
        self.dummy_ax.xaxis.set_major_formatter(NullFormatter())
        self.dummy_ax.yaxis.set_major_locator(MaxNLocator(5))
        self.dummy_ax.yaxis.set_major_formatter(NullFormatter())
        self.dummy_ax.grid()

        self.axes = []

    def __del__(self):
        for ax in self.axes:
            self.figure.delaxes(ax)
        self.figure.delaxes(self.dummy_ax)

    def set_xlim(self, i, xlim):
        self.axes[i].set_xlim(xlim)

    def get_xlim(self, i):
        return self.axes[i].get_xlim()

    def auto_xlim(self, i):
        xdata = self.axes[i].lines[0].get_xdata()
        xmin = np.nanmin(xdata)
        xmax = np.nanmax(xdata)
        ticks = self.dummy_ax.xaxis.get_major_locator().tick_values(xmin, xmax)
        self.set_xlim(i, [ticks[0], ticks[-1]])

    def set_ylim(self, ylim):
        self.dummy_ax.set_ylim(ylim)

    def get_ylim(self):
        return self.dummy_ax.get_ylim()

    def auto_ylim(self):
        ymin = np.inf
        ymax = -np.inf
        for ax in self.axes:
            ydata = ax.lines[0].get_ydata()
            ymin_ = np.nanmin(ydata)
            ymax_ = np.nanmax(ydata)
            if ymin_ < ymin:
                ymin = ymin_
            if ymax_ > ymax:
                ymax = ymax_
        self.set_ylim([ymin, ymax])

    def set_position(self, pos):
        self.rect = pos
        self.dummy_ax.set_position(pos)
        for ax in self.axes:
            ax.set_position(pos)

    def get_position(self):
        return self.rect

    def insert_line(self, i, *args, **kwargs):
        if not 0 <= i <= len(self.axes):
            msg = 'Expected index between 0 and %i, got %i' % (len(self.axes), i)
            raise IndexError(msg)
        label = self.__get_unique_label()
        ax = self.figure.add_axes(self.dummy_ax.get_position(True),
                                  sharey=self.dummy_ax, frameon=False,
                                  label=label)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        line = matplotlib.lines.Line2D(*args, **kwargs)
        ax.add_line(line)

        self.axes.insert(i, ax)

    def remove_line(self, i):
        ax = self.axes.pop(i)
        self.figure.delaxes(ax)

    def set_line_properties(self, i, **props):
        self.axes[i].lines[0].update(self.__get_valid_line_props(props))

    def get_line_properties(self, i):
        return self.__get_valid_line_props(self.axes[i].lines[0].properties())

    def set_xdata(self, i, xdata):
        self.axes[i].lines[0].set_xdata(xdata)

    def get_xdata(self, i):
        return self.axes[i].lines[0].get_xdata()

    def set_ydata(self, i, ydata):
        self.axes[i].lines[0].set_ydata(ydata)

    def get_ydata(self, i):
        return self.axes[i].lines[0].get_ydata()


class LabeledTrack(object):
    __default_layout_properties = {
        'label_height': 0.05
        }

    def __init__(self, figure, rect, layout_properties=None):
        if layout_properties is None:
            layout_properties = self.__default_layout_properties
        else:
            for key, value in self.__default_layout_properties.items():
                if key not in layout_properties \
                        or layout_properties[key] is None:
                    layout_properties[key] = value

        self.figure = figure
        self.rect = rect
        self.layout_properties = layout_properties

        self.track = Track(self.figure, self.rect)
        self.labels = []

    def __get_abs_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [L + l*W, B + b*H, w*W, h*H]

    def __get_rel_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [(l - L)/W, (b - B)/H, w/W, h/H]

    def set_position(self, pos):
        track_pos = self.__get_rel_pos(self.track.get_position())
        labels_pos = []
        for label in self.labels:
            labels_pos.append(self.__get_rel_pos(label.get_position()))

        self.rect = pos

        self.track.set_position(self.__get_abs_pos(track_pos))
        for label_pos, label in zip(labels_pos, self.labels):
            label.set_position(self.__get_abs_pos(label_pos))

    def get_position(self):
        return self.rect

    def set_xlim(self, i, xlim):
        self.track.set_xlim(i, xlim)
        self.labels[i].set_xlim(xlim)

    def get_xlim(self, i):
        return self.track.get_xlim(i)

    def auto_xlim(self, i):
        self.track.auto_xlim(i)
        xlim = self.get_xlim(i)
        self.labels[i].set_xlim(xlim)

    def set_ylim(self, ylim):
        self.track.set_ylim(ylim)

    def get_ylim(self):
        return self.track.get_ylim()

    def auto_ylim(self):
        self.track.auto_ylim()

    def set_text(self, i, text):
        self.labels[i].set_text(text)

    def get_text(self, i):
        return self.labels[i].get_text()

    def insert_label(self, i):
        if not 0 <= i <= len(self.labels):
            msg = 'Expected index between 0 and %i, got %i' % (len(self.labels), i)
            raise IndexError(msg)
        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h -= ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b -= ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

        l = 0.0
        b = 1.0 - (i + 1)*ls
        w = 1.0
        h = ls
        new_label = Label(self.figure, self.__get_abs_pos([l, b, w, h]))
        self.labels.insert(i, new_label)

    def remove_label(self, i):
        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h += ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i+1:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b += ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

        removed_label = self.labels.pop(i)
        del removed_label

    def insert_line(self, i, xdata, ydata, *args, **kwargs):
        self.track.insert_line(i, xdata, ydata, *args, **kwargs)
        props = self.track.get_line_properties(i)
        xlim = self.track.get_xlim(i)

        self.insert_label(i)

        self.labels[i].set_line_properties(**props)
        self.labels[i].set_xlim(xlim)

    def remove_line(self, i):
        self.remove_label(i)
        self.track.remove_line(i)

    def set_line_properties(self, i, **props):
        self.track.set_line_properties(i, **props)
        self.labels[i].set_line_properties(**props)

    def get_line_properties(self, i):
        return self.track.get_line_properties(i)

    def set_xdata(self, i, xdata):
        self.track.set_xdata(i, xdata)

    def get_xdata(self, i):
        return self.track.get_xdata(i)

    def set_ydata(self, i, ydata):
        self.track.set_ydata(i, ydata)

    def get_ydata(self, i):
        return self.track.get_ydata(i)


class MultiTrack(object):
    __default_layout_properties = {
        'label_height': 0.05,
        'track_width': 0.1
        }

    def __init__(self, figure, rect, layout_properties=None):
        if layout_properties is None:
            layout_properties = self.__default_layout_properties
        else:
            for key, value in self.__default_layout_properties.items():
                if key not in layout_properties \
                        or layout_properties[key] is None:
                    layout_properties[key] = value

        self.figure = figure
        self.rect = rect
        self.layout_properties = layout_properties

        self.tracks = []
        self.ylim = None  # TODO: Rever isso

    def __get_abs_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [L + l*W, B + b*H, w*W, h*H]

    def __get_rel_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [(l - L)/W, (b - B)/H, w/W, h/H]

    def set_position(self, pos):
        tracks_pos = []
        for track in self.tracks:
            tracks_pos.append(self.__get_rel_pos(track.get_position()))

        self.rect = pos

        for track_pos, track in zip(tracks_pos, self.tracks):
            track.set_position(self.__get_abs_pos(track_pos))

    def get_position(self):
        return self.rect

    def set_xlim(self, i, j, xlim):
        self.tracks[i].set_xlim(j, xlim)

    def get_xlim(self, i, j):
        return self.tracks[i].get_xlim(j)

    def auto_xlim(self, i, j):
        self.tracks[i].auto_xlim(j)

    def set_ylim(self, ylim):
        for track in self.tracks:
            track.set_ylim(ylim)
        self.ylim = ylim

    def get_ylim(self):
        return self.ylim

    def auto_ylim(self):
        ymin = np.inf
        ymax = -np.inf
        for track in self.tracks:
            for ax in track.track.axes:
                ydata = ax.lines[0].get_ydata()
                ymin_ = np.nanmin(ydata)
                ymax_ = np.nanmax(ydata)
                if ymin_ < ymin:
                    ymin = ymin_
                if ymax_ > ymax:
                    ymax = ymax_
        self.set_ylim([ymin, ymax])

    def set_text(self, i, j, text):
        self.tracks[i].set_text(j, text)

    def get_text(self, i, j):
        return self.tracks[i].get_text(j)

    # TODO: Daqui para baixo (COMO LIDAR COM LABEL VAZIA???!!!)

    def insert_label(self, i):
        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h -= ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b -= ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

        l = 0.0
        b = 1.0 - (i + 1)*ls
        w = 1.0
        h = ls
        new_label = Label(self.figure, self.__get_abs_pos([l, b, w, h]))
        self.labels.insert(i, new_label)

    def remove_label(self, i):
        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h += ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i+1:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b += ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

        removed_label = self.labels.pop(i)
        del removed_label

    def insert_line(self, i, xdata, ydata, *args, **kwargs):
        self.track.insert_line(i, xdata, ydata, *args, **kwargs)
        props = self.track.get_line_properties(i)
        xlim = self.track.get_xlim(i)

        self.insert_label(i)

        self.labels[i].set_line_properties(**props)
        self.labels[i].set_xlim(xlim)

    def remove_line(self, i):
        self.remove_label(i)
        self.track.remove_line(i)

    def set_line_properties(self, i, **props):
        self.track.set_line_properties(i, **props)
        self.labels[i].set_line_properties(**props)

    def get_line_properties(self, i):
        return self.track.get_line_properties(i)


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.tracks = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

    def add_track(self, rect):
        self.tracks.append(LabeledTrack(self.figure, rect))


if __name__ == '__main__':
    import numpy as np

    class TestMixin(object):
        def __init__(self):
            self.cid_press = self.canvas.mpl_connect('button_press_event',
                                                     self.on_press)
            self.cid_motion = self.canvas.mpl_connect('motion_notify_event',
                                                      self.on_motion)
            self.cid_release = self.canvas.mpl_connect('button_release_event',
                                                       self.on_release)
            self.num_clicks = 0

            self.add_track([0.1, 0.1, 0.8, 0.8])
            self.canvas.draw()

            self.moving_ax = self.figure.add_axes([0, 0, 1, 1], label='Moving ax', zorder=1000)
            self.moving_ax.xaxis.set_visible(False)
            self.moving_ax.yaxis.set_visible(False)
            self.moving_ax.patch.set_fill(False)
            self.moving_ax.patch.set_lw(3)
            self.moving_ax.patch.set_color('#434343')
            self.moving_ax.patch.set_edgecolor('#434343')
            self.moving_ax.set_visible(False)

            self.x0y0 = None

        def _on_press(self, event):
            if self.num_clicks % 6 == 0:
                y = np.linspace(0, 5, 1000)
                x = np.sin(2.0*np.pi*y)
                self.tracks[0].insert_line(0, x, y)
                self.tracks[0].set_text(0, '$\sin(2 \pi y)$')
                self.tracks[0].set_line_properties(0, color='r')
                self.tracks[0].auto_xlim(0)
                self.tracks[0].auto_ylim()
                self.canvas.draw()
            elif self.num_clicks % 6 == 1:
                y = np.linspace(0, 5, 1000)
                x = np.cos(2.0*np.pi*y)
                self.tracks[0].insert_line(0, x, y)
                self.tracks[0].set_text(0, '$\cos(2 \pi y)$')
                self.tracks[0].set_line_properties(0, color='g')
                self.tracks[0].auto_xlim(0)
                self.tracks[0].auto_ylim()
                self.canvas.draw()
            elif self.num_clicks % 6 == 2:
                l, b, w, h = self.tracks[0].get_position()
                l -= 0.05
                b -= 0.05
                w += 0.1
                h += 0.1
                self.tracks[0].set_position([l, b, w, h])
                self.canvas.draw()
            elif self.num_clicks % 6 == 3:
                l, b, w, h = self.tracks[0].get_position()
                l += 0.05
                b += 0.05
                w -= 0.1
                h -= 0.1
                self.tracks[0].set_position([l, b, w, h])
                self.canvas.draw()
            elif self.num_clicks % 6 == 4:
                self.tracks[0].remove_line(0)
                self.canvas.draw()
            elif self.num_clicks % 6 == 5:
                self.tracks[0].remove_line(0)
                self.canvas.draw()
            self.num_clicks += 1

        def on_press(self, event):
            x0y0 = self.figure.transFigure.inverted().transform([event.x, event.y])
            l, b, w, h = self.tracks[0].get_position()
            if (l <= x0y0[0] <= l + w) and (b <= x0y0[1] <= b + h):
                """
                self.moving_ax.set_position(self.tracks[0].get_position())
                self.moving_ax.set_visible(True)
                #"""
                self.x0y0 = x0y0

            else:
                self._on_press(event)

        def on_motion(self, event):
            if self.x0y0 is None:
                return
            xy = self.figure.transFigure.inverted().transform([event.x, event.y])
            dx = xy[0] - self.x0y0[0]
            dy = xy[1] - self.x0y0[1]
            self.x0y0 = xy
            #"""
            l, b, w, h = self.tracks[0].get_position()
            """
            bbox = self.moving_ax.get_position()
            l = bbox.x0
            b = bbox.y0
            w = bbox.x1 - l
            h = bbox.y1 - b
            #"""
            l += dx
            b += dy
            #"""
            self.tracks[0].set_position([l, b, w, h])
            """
            self.moving_ax.set_position([l, b, w, h])
            #"""
            self.canvas.draw_idle()

        def on_release(self, event):
            if self.x0y0 is not None:
                """
                bbox = self.moving_ax.get_position()
                l = bbox.x0
                b = bbox.y0
                w = bbox.x1 - l
                h = bbox.y1 - b
                self.tracks[0].set_position([l, b, w, h])

                self.moving_ax.set_visible(False)
                self.canvas.draw_idle()
                #"""
                self.x0y0 = None

    class TestPanel(Panel, TestMixin):
        def __init__(self, *args, **kwargs):
            super(TestPanel, self).__init__(*args, **kwargs)
            TestMixin.__init__(self)

    app = wx.App(False)
    frm = wx.Frame(None)
    pnl = TestPanel(frm)

    frm.Show()
    app.MainLoop()
