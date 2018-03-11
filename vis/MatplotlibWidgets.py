# -*- coding: utf-8 -*-

from matplotlib.patches import Rectangle
from matplotlib.transforms import blended_transform_factory


class MultiCursor(object):
    
    def __init__(self, canvas, axes, lineprops):
        self.canvas = canvas
        self.axes = axes
        ymin, ymax = axes[0].get_ylim()
        self.ymid = 0.5*(ymin + ymax)

        self.lineprops = lineprops
        self.lineprops['animated'] = True
        self.lines = [ax.axhline(self.ymid, visible=False, **self.lineprops)
                      for ax in axes]

        self.background = None
        self.needclear = False

        self.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.canvas.mpl_connect('draw_event', self.clear)
        self.canvas.mpl_connect('axes_leave_event', self.onleave)

    def clear(self, event):
        self.background = self.canvas.copy_from_bbox(
            self.canvas.figure.bbox)
        for line in self.lines:
            line.set_visible(False)

    def onmove(self, event):
        if event.inaxes != self.axes[0]:
            return
        if not self.canvas.widgetlock.available(self):
            return
        self.needclear = True
        for line in self.lines:
            line.set_ydata((event.ydata, event.ydata))
            line.set_visible(True)
        self._update()

    def onleave(self, event):
        if event.inaxes == self.axes[0] and event.button != 1:
            self.clear(event)
            self.canvas.draw_idle()

    def _update(self):
        if self.background is not None:
            self.canvas.restore_region(self.background)
        for ax, line in zip(self.axes, self.lines):
            ax.draw_artist(line)
        self.canvas.blit(self.canvas.figure.bbox)

    def add_ax(self, ax):
        self.axes.append(ax)
        self.lines.append(ax.axhline(self.ymid, visible=False,
                                     **self.lineprops))


class SpanSelector(object):
    def __init__(self, canvas, ax, onselect, rectprops):
        self.canvas = canvas
        self.ax = ax

        self.rect = None
        self.background = None
        self.pressv = None

        self.onselect = onselect

        self.buttonDown = False
        self.prev = 0

        self.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.canvas.mpl_connect('button_press_event', self.press)
        self.canvas.mpl_connect('button_release_event', self.release)
        self.canvas.mpl_connect('draw_event', self.update_background)

        trans = blended_transform_factory(self.ax.transAxes,
                                          self.ax.transData)
        self.rect = Rectangle((0, 0), 1, 0, transform=trans, visible=False,
                              **rectprops)

    def update_background(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def ignore(self, event):
        return event.inaxes != self.ax or event.button != 1

    def press(self, event):
        if self.ignore(event):
            return
        self.buttonDown = True

        self.rect.set_visible(True)
        self.pressv = event.ydata
        return False

    def release(self, event):
        if self.ignore(event) and not self.buttonDown:
            return
        if self.pressv is None:
            return
        self.buttonDown = False

        self.rect.set_visible(False)
        self.canvas.draw_idle()
        vmin = self.pressv
        vmax = event.ydata or self.prev

        if vmin > vmax:
            vmin, vmax = vmax, vmin
        self.onselect(vmin, vmax)
        self.pressv = None
        return False

    def update(self):
        if self.background is not None:
            self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.rect)
        self.canvas.blit(self.ax.bbox)
        return False

    def onmove(self, event):
        if self.pressv is None or self.ignore(event):
            return
        self.prev = event.ydata
        minv, maxv = self.prev, self.pressv
        if minv > maxv:
            minv, maxv = maxv, minv
        self.rect.set_y(minv)
        self.rect.set_height(maxv-minv)

        self.update()
        return False
