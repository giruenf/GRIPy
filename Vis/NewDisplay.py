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

COLOR_CYCLE = ['#348ABD', '#A60628', '#7A68A6', '#467821', '#D55E00',
               '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2']

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
        self.dummy_ax.set_zorder(-100)
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
        self.set_ylim([ymax, ymin])

    def set_position(self, pos):
        self.rect = pos
        self.dummy_ax.set_position(pos)
        for ax in self.axes:
            ax.set_position(pos)

    def get_position(self):
        return self.rect

    def insert_line(self, i, *args, **kwargs):
        if not 0 <= i <= len(self.axes):
            raise IndexError('index out of range')
        label = self.__get_unique_label()
        ax = self.figure.add_axes(self.dummy_ax.get_position(True),
                                  sharey=self.dummy_ax, frameon=False,
                                  label=label)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

        if 'zorder' not in kwargs:
            kwargs['zorder'] = 100

        line = matplotlib.lines.Line2D(*args, **kwargs)
        ax.add_line(line)

        self.axes.insert(i, ax)

    def insert_ax(self, i, ax):
        ax.set_position(self.rect)
        self.axes.insert(i, ax)

    def pop_ax(self, i):
        return self.axes.pop(i)

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
        self.spots = []

    def __get_abs_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [L + l*W, B + b*H, w*W, h*H]

    def __get_rel_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [(l - L)/W, (b - B)/H, w/W, h/H]

    def __get_true_index(self, i):
        i_ = self.spots[:i+1].count(True)
        return i_ - 1
        if i_ == 0:
            return None
        else:
            return i_ - 1

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
        i_ = self.__get_true_index(i)
        self.track.set_xlim(i_, xlim)
        self.labels[i_].set_xlim(xlim)

    def get_xlim(self, i):
        i_ = self.__get_true_index(i)
        return self.track.get_xlim(i_)

    def auto_xlim(self, i):
        i_ = self.__get_true_index(i)
        self.track.auto_xlim(i_)
        xlim = self.get_xlim(i_)
        self.labels[i_].set_xlim(xlim)

    def set_ylim(self, ylim):
        self.track.set_ylim(ylim)

    def get_ylim(self):
        return self.track.get_ylim()

    def auto_ylim(self):
        self.track.auto_ylim()

    def set_text(self, i, text):
        i_ = self.__get_true_index(i)
        self.labels[i_].set_text(text)

    def get_text(self, i):
        i_ = self.__get_true_index(i)
        return self.labels[i_].get_text()

    def create_spot(self, i):
        if not 0 <= i <= len(self.spots):
            raise IndexError('index out of range')

        self.spots.insert(i, False)  # TODO: Verificar se isso nao deveria estar no fim da funcao

        i_ = self.__get_true_index(i)

        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h -= ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i_+1:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b -= ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

    def fill_spot(self, i, xdata, ydata, *args, **kwargs):
        if not 0 <= i < len(self.spots):
            raise IndexError('index out of range')
        if self.spots[i]:
            raise IndexError('spot arlready filled')

        self.spots[i] = True

        i_ = self.__get_true_index(i)

        self.track.insert_line(i_, xdata, ydata, *args, **kwargs)
        props = self.track.get_line_properties(i_)
        xlim = self.track.get_xlim(i_)

        ls = self.layout_properties['label_height']

        l = 0.0
        b = 1.0 - (i + 1)*ls
        w = 1.0
        h = ls
        new_label = Label(self.figure, self.__get_abs_pos([l, b, w, h]))
        new_label.set_line_properties(**props)
        new_label.set_xlim(xlim)

        self.labels.insert(i_, new_label)

    def fill_spot_with(self, i, label, ax):
        if not 0 <= i < len(self.spots):
            raise IndexError('index out of range')
        if self.spots[i]:
            raise IndexError('spot arlready filled')

        self.spots[i] = True

        i_ = self.__get_true_index(i)

        self.track.insert_ax(i_, ax)

        ls = self.layout_properties['label_height']

        l = 0.0
        b = 1.0 - (i + 1)*ls
        w = 1.0
        h = ls

        label.set_position(self.__get_abs_pos([l, b, w, h]))

        self.labels.insert(i_, label)

    def pop_spot(self, i):
        if not 0 <= i < len(self.spots):
            raise IndexError('index out of range')
        i_ = self.__get_true_index(i)

        ax = self.track.pop_ax(i_)
        label = self.labels.pop(i_)

        self.spots[i] = False

        return label, ax

    def clear_spot(self, i):
        if not 0 <= i < len(self.spots):
            raise IndexError('index out of range')
        i_ = self.__get_true_index(i)

        self.track.remove_line(i_)
        removed_label = self.labels.pop(i_)
        del removed_label

        self.spots[i] = False

    def remove_spot(self, i):
        i_ = self.__get_true_index(i)

        ls = self.layout_properties['label_height']

        l, b, w, h = self.__get_rel_pos(self.track.get_position())
        h += ls
        self.track.set_position(self.__get_abs_pos([l, b, w, h]))

        for label in self.labels[i_+1:]:
            l, b, w, h = self.__get_rel_pos(label.get_position())
            b += ls
            label.set_position(self.__get_abs_pos([l, b, w, h]))

        self.spots.pop(i)

    def set_line_properties(self, i, **props):
        i_ = self.__get_true_index(i)
        self.track.set_line_properties(i_, **props)
        self.labels[i_].set_line_properties(**props)

    def get_line_properties(self, i):
        i_ = self.__get_true_index(i)
        return self.track.get_line_properties(i_)

    def set_xdata(self, i, xdata):
        i_ = self.__get_true_index(i)
        self.track.set_xdata(i_, xdata)

    def get_xdata(self, i):
        i_ = self.__get_true_index(i)
        return self.track.get_xdata(i_)

    def set_ydata(self, i, ydata):
        i_ = self.__get_true_index(i)
        self.track.set_ydata(i_, ydata)

    def get_ydata(self, i):
        i_ = self.__get_true_index(i)
        return self.track.get_ydata(i_)

# TODO: implementar track não preenchido horizontalmente (verticalmente???)


class MultiTracks(object):
    __default_layout_properties = {
        'label_height': 0.05,
        'track_width': 1.0  # TODO: trocar
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
        self.track_spots = []
        self.n_label_spots = 0
        self.ylim = None  # TODO: Rever isso

    def __get_abs_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [L + l*W, B + b*H, w*W, h*H]

    def __get_rel_pos(self, rect):
        l, b, w, h = rect
        L, B, W, H = self.rect
        return [(l - L)/W, (b - B)/H, w/W, h/H]

    def __get_true_index(self, i):
        i_ = self.track_spots[:i+1].count(True)
        return i_ - 1
        if i_ == 0:
            return None
        else:
            return i_ - 1

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
        i_ = self.__get_true_index(i)
        self.tracks[i_].set_xlim(j, xlim)

    def get_xlim(self, i, j):
        i_ = self.__get_true_index(i)
        return self.tracks[i_].get_xlim(j)

    def auto_xlim(self, i, j):
        i_ = self.__get_true_index(i)
        self.tracks[i_].auto_xlim(j)

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
        self.set_ylim([ymax, ymin])

    def set_text(self, i, j, text):
        i_ = self.__get_true_index(i)
        self.tracks[i_].set_text(j, text)

    def get_text(self, i, j):
        i_ = self.__get_true_index(i)
        return self.tracks[i_].get_text(j)

    def create_label_spot(self, i):
        for track in self.tracks:
            track.create_spot(i)
        self.n_label_spots += 1

    def fill_label_spot(self, i, j, xdata, ydata, *args, **kwargs):
        i_ = self.__get_true_index(i)
        self.tracks[i_].fill_spot(j, xdata, ydata, *args, **kwargs)

    def clear_label_spot(self, i, j):
        i_ = self.__get_true_index(i)
        self.tracks[i_].clear_spot(j)

    def remove_label_spot(self, i):
        for track in self.tracks:
            track.remove_spot(i)
        self.n_label_spots -= 1

    def create_track_spot(self, i):
        if not 0 <= i <= len(self.track_spots):
            raise IndexError('index out of range')

        self.track_spots.insert(i, False)

        i_ = self.__get_true_index(i)

        tw = self.layout_properties['track_width']

        for track in self.tracks[i_+1:]:
            l, b, w, h = self.__get_rel_pos(track.get_position())
            l += tw
            track.set_position(self.__get_abs_pos([l, b, w, h]))

    def fill_track_spot(self, i):
        if not 0 <= i < len(self.track_spots):
            raise IndexError('index out of range')
        if self.track_spots[i]:
            raise IndexError('spot arlready filled')

        self.track_spots[i] = True

        i_ = self.__get_true_index(i)

        tw = self.layout_properties['track_width']

        l = i*tw
        b = 0.0
        w = tw
        h = 1.0

        new_track = LabeledTrack(self.figure, self.__get_abs_pos([l, b, w, h]))
        for i in range(self.n_label_spots):
            new_track.create_spot(i)

        self.tracks.insert(i_, new_track)

    def clear_track_spot(self, i):
        if not 0 <= i < len(self.track_spots):
            raise IndexError('index out of range')
        i_ = self.__get_true_index(i)

        removed_track = self.tracks.pop(i_)
        del removed_track

        self.track_spots[i] = False

    def remove_track_spot(self, i):
        i_ = self.__get_true_index(i)

        tw = self.layout_properties['track_width']

        for track in self.tracks[i_+1:]:
            l, b, w, h = self.__get_rel_pos(track.get_position())
            l -= tw
            track.set_position(self.__get_abs_pos([l, b, w, h]))

        self.track_spots.pop(i)

    def move_between_spots(self, from_i, from_j, to_i, to_j):
        from_i_ = self.__get_true_index(from_i)
        to_i_ = self.__get_true_index(to_i)

        if not self.track_spots[from_i]:
            raise IndexError('empty spot')
        if not self.tracks[from_i_].spots[from_j]:
            raise IndexError('empty spot')

        if self.track_spots[to_i] and self.tracks[to_i_].spots[to_j]:
            raise IndexError('spot arlready filled')

        if not self.track_spots[to_i]:
            self.fill_track_spot(to_i)
            to_i_ += 1

        label, ax = self.tracks[from_i_].pop_spot(from_j)
        self.tracks[to_i_].fill_spot_with(to_j, label, ax)

    def set_line_properties(self, i, j, **props):
        i_ = self.__get_true_index(i)
        self.tracks[i_].set_line_properties(j, **props)

    def get_line_properties(self, i, j):
        i_ = self.__get_true_index(i)
        return self.tracks[i_].get_line_properties(j)

    def set_xdata(self, i, j, xdata):
        i_ = self.__get_true_index(i)
        self.tracks[i_].set_xdata(j, xdata)

    def get_xdata(self, i, j):
        i_ = self.__get_true_index(i)
        return self.tracks[i_].get_xdata(j)

    def set_ydata(self, i, j, ydata):
        i_ = self.__get_true_index(i)
        self.tracks[i_].set_ydata(j, ydata)

    def get_ydata(self, i, j):
        i_ = self.__get_true_index(i)
        return self.tracks[i_].get_ydata(j)


class Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(Panel, self).__init__(*args, **kwargs)

        self.figure = Figure()
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.tracks = MultiTracks(self.figure, [0.05, 0.05, 0.125, 0.9])

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

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
            self.n_clicks = 0
            self._init_data()
            self.funs = [self._f00]

            self.canvas.draw()

            self.moving_ax = self.__create_aux_ax('#00ff00', [0, 0, 1, 1],
                                                  zorder=1000,
                                                  label='Moving ax')
            self.highlight_ax = self.__create_aux_ax('#ff0000', [0, 0, 1, 1],
                                                     zorder=1000,
                                                     label='Hightlight ax')
            self.x0y0 = None
            self._on_press(None)

        def __create_aux_ax(self, color, *args, **kwargs):
            ax = self.figure.add_axes(*args, **kwargs)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.patch.set_fill(False)
            ax.patch.set_lw(3)
            ax.patch.set_alpha(0.5)
            ax.patch.set_ec(color)
            ax.set_visible(False)
            return ax

        def _init_data(self):
            y = np.linspace(0, 5, 300)
            x0 = np.cos(2.0*np.pi*y)
            x1 = np.sin(2.0*np.pi*y)
            x2 = np.cos(2.0*np.pi*(1.0 + y/10.0)*y)
            x3 = np.sin(2.0*np.pi*(1.0 + y/10.0)*y)
            x4 = np.cos(2.0*np.pi*y)*np.exp(-y/10.0)
            x5 = np.sin(2.0*np.pi*y)*np.exp(-y/10.0)
            self.y = y
            self.x = [x0, x1, x2, x3, x4, x5]
            self.names = [r'$\cos(2 \pi y)$', r'$\sin(2 \pi y)$',
                          r'$\cos(2 \pi (1 + y/10) y)$', r'$\sin(2 \pi (1 + y/10) y)$',
                          r'$e^{-y/10} \cos(2 \pi y)$', r'$e^{-y/10} \sin(2 \pi y)$']

        def _on_press(self, event):
            self.funs[self.n_clicks % len(self.funs)]()
            self.tracks.auto_ylim()
            self.canvas.draw()
            self.n_clicks += 1

        def _f00(self):
            self.tracks.create_track_spot(0)
            self.tracks.fill_track_spot(0)
            self.tracks.create_label_spot(0)
            self.tracks.fill_label_spot(0, 0, self.x[0], self.y)
            self.tracks.set_text(0, 0, self.names[0])
            self.tracks.set_line_properties(0, 0, color=COLOR_CYCLE[0])
            self.tracks.auto_xlim(0, 0)

            self.tracks.create_label_spot(0)
            self.tracks.fill_label_spot(0, 0, self.x[1], self.y)
            self.tracks.set_text(0, 0, self.names[1])
            self.tracks.set_line_properties(0, 0, color=COLOR_CYCLE[1])
            self.tracks.auto_xlim(0, 0)

        def on_press(self, event):
            largura = self.figure.get_figwidth()*self.figure.get_dpi()
            altura = self.figure.get_figheight()*self.figure.get_dpi()
            x0y0 = self.figure.transFigure.inverted().transform([event.x, event.y])
            print x0y0
            print event.x/largura
            print event.y/altura
            l, b, w, h = self.tracks.get_position()
            if (l <= x0y0[0] <= l + w) and (b <= x0y0[1] <= b + h):
                #"""
                self.moving_ax.set_position(self.tracks.get_position())
                self.moving_ax.set_visible(True)
                self.highlight_ax.set_position(self.tracks.get_position())
                self.highlight_ax.set_visible(True)
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
            """
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
            """
            self.tracks[0].set_position([l, b, w, h])
            """
            self.moving_ax.set_position([l, b, w, h])
            #"""
            self.canvas.draw_idle()

        def on_release(self, event):
            if self.x0y0 is not None:
                #"""
                bbox = self.moving_ax.get_position()
                l = bbox.x0
                b = bbox.y0
                w = bbox.x1 - l
                h = bbox.y1 - b
                self.tracks.set_position([l, b, w, h])

                self.moving_ax.set_visible(False)
                self.highlight_ax.set_visible(False)
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
