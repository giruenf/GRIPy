# -*- coding: utf-8 -*-

from matplotlib.colors import LinearSegmentedColormap as LSC
from numpy import linspace
from scipy.special import erf

ALMOST_BLACK = "#262626"
DARK_GRAY = "#626262"
MEDIUM_GRAY = "#E0E0E0"
LIGHT_GRAY = "#F8F8F8"

# COLOR_CYCLE_HEX = ['#332288', '#999933', '#aa4499', '#88ccee', '#117733',
#                    '#882255', '#ddcc77', '#44aa99', '#cc6677', '#dddddd']

# COLOR_CYCLE_RGB = [(51, 34, 136), (153, 153, 51), (170, 68, 153),
#                    (136, 204, 238), (17, 119, 51), (136, 34, 85),
#                    (221, 204, 119), (68, 170, 153), (204, 102, 119),
#                    (221, 221, 221)]

# COLOR_CYCLE_NAMES = [a[1:].upper() for a in COLOR_CYCLE_HEX]

"""
COLOR_CYCLE_HEX = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
                   '#e5e52d', '#a65628', '#f781bf', '#999999']

COLOR_CYCLE_RGB = [(228, 26, 28), (55, 126, 184), (77, 175, 74),
                   (152, 78, 163), (255, 127, 0), (229, 229, 45),
                   (166, 86, 40), (247, 129, 191), (153, 153, 153)]

COLOR_CYCLE_NAMES = [u"Vermelho", u"Azul", u"Verde", u"Violeta", "Laranja",
                     u"Amarelo", u"Marrom", u"Rosa", u"Cinza"]
"""
COLOR_CYCLE_HEX = ['#332288', '#6699cc', '#88ccee', '#44aa99',
                   '#117733', '#999933', '#ddcc77', '#661100',
                   '#cc6677', '#aa4466', '#882255', '#aa4499']

COLOR_CYCLE_RGB = [(51, 34, 136), (102, 153, 204), (136, 204, 238),
                   (68, 170, 153), (17, 119, 51), (153, 153, 51),
                   (221, 204, 119), (102, 17, 0), (204, 102, 119),
                   (170, 68, 102), (136, 34, 85), (170, 68, 153)]

COLOR_CYCLE_NAMES = COLOR_CYCLE_HEX[:]
#"""

_COLORS = []
for x in linspace(0, 1, 256):
    r = 0.237 - 2.13*x + 26.92*x**2 - 65.5*x**3 + 63.5*x**4 - 22.36*x**5
    g = ((0.572 + 1.524*x - 1.811*x**2)/(1 - 0.291*x + 0.1574*x**2))**2
    b = 1/(1.579 - 4.03*x + 12.92*x**2 - 31.4*x**3 + 48.6*x**4 - 23.36*x**5)
    _COLORS.append((r, g, b))
COLOR_MAP_DIVERGING = LSC.from_list("Programa_diverging", _COLORS)

_COLORS = []
for x in linspace(0, 1, 256):
    r = (1 - 0.392*(1 + erf((x - 0.869)/0.255)))
    g = (1.021 - 0.456*(1 + erf((x - 0.527)/0.376)))
    b = (1 - 0.493*(1 + erf((x - 0.272)/0.309)))
    _COLORS.append((r, g, b))
COLOR_MAP_LINEAR = LSC.from_list("Programa_linear", _COLORS)

_COLORS = []
for x in linspace(0, 1, 256):
    r = (0.472 - 0.567*x + 4.05*x**2)/(1.0 + 8.72*x - 19.17*x**2 + 14.1*x**3)
    g = 0.108932 - 1.22635*x + 27.284*x**2 - 98.577*x**3 + 163.3*x**4 - \
        131.395*x**5 + 40.634*x**6
    b = 1.0/(1.97 + 3.54*x - 68.5*x**2 + 243.0*x**3 - 297.0*x**4 + 125.0*x**5)
    _COLORS.append((r, g, b))
COLOR_MAP_RAINBOW = LSC.from_list("Programa_rainbow", _COLORS)
