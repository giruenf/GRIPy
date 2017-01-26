# -*- coding: utf-8 -*-

from Basic import Colors

import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')

matplotlib.rcParams['text.color'] = Colors.ALMOST_BLACK
matplotlib.rcParams['axes.facecolor'] = Colors.LIGHT_GRAY
matplotlib.rcParams['axes.edgecolor'] = Colors.ALMOST_BLACK
matplotlib.rcParams['xtick.major.size'] = 0
matplotlib.rcParams['xtick.minor.size'] = 0
matplotlib.rcParams['ytick.major.size'] = 0
matplotlib.rcParams['ytick.minor.size'] = 0
matplotlib.rcParams['grid.color'] = Colors.DARK_GRAY
matplotlib.rcParams['figure.facecolor'] = Colors.MEDIUM_GRAY
matplotlib.rcParams['figure.edgecolor'] = Colors.ALMOST_BLACK
matplotlib.rcParams['legend.numpoints'] = 1

import CrossPlot
import LogPlot
import MatplotlibWidgets
