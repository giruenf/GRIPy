# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
from Algo.BasicPetrophysics.WaterSaturation import Simandoux
from Algo.BasicPetrophysics.ShaleVolume import VshGR
import wx
import numpy as np

inputdesc = [
            {'type': 'omsingle', 'name': 'rxo', 'tids': ['log'], 'dispname': u'Resistividade Curta'},
            {'type': 'omsingle', 'name': 'rt', 'tids': ['log'], 'dispname': u"Resistividade Longa"},
            {'type': 'omsingle', 'name': 'phi', 'tids': ['log'], 'dispname': u"Porosidade"},
            {'type': 'omsingle', 'name': 'vsh', 'tids': ['log'], 'dispname': u"Gamma-Ray"},
#             {'type': 'bool', 'name': 'model', 'dispname': u"Archie", 'default': True},
            {'type': 'float', 'name': 'a', 'dispname': u"A", 'default': '0.62'},
            {'type': 'float', 'name': 'm', 'dispname': u"M", 'default': '2.0'},
            {'type': 'float', 'name': 'n', 'dispname': u"N", 'default': '2.0'},
            {'type': 'float', 'name': 'rsh', 'dispname': u"Resistividade folhelho"},
            {'type': 'text', 'name': 'name', 'dispname': 'Novo Perfil'},
#            {'type': 'choice', 'name': 'model', 'dispname': 'Modelo'},
#            {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}
            ]

outputdesc = [{'type': 'log', 'name': 'Sw'}]

def job(**kwargs):
#    a=1.
#    m=2.
#    n=2.
#    is_sonic = kwargs.get('is_sonic', None)
#    model = kwargs.get('model', 'Archie')
    a = kwargs.get('a', 0.62)
    m = kwargs.get('m', 2.)
    n = kwargs.get('n', 2.)
    rsh = kwargs.get('rsh', None)
    rxo = kwargs.get('rxo', None)
    rt = kwargs.get('rt', None)
    phi = kwargs.get('phi', None)
    vsh = kwargs.get('vsh', None)
    name = kwargs.get('name', 'SW')
    if not name: name = 'SW'
#    unit = kwargs.get('unit', '')
    unit = ''
    
    if phi is None or rxo is None or rt is None or vsh is None:
        return
    
#    if model:
##        impedancedata = 3.048E5*rho/dt
#        Sw = Archie(rt,phi,rxo,m,n,a)
#    else:
#        Sw = Simandoux(rt,phi,Vsh,Rw,Rsh,m,n,a)
#        impedancedata = dt*rho
#    vsh = VshGR(gr, itmin = 5., itmax = 5.)
    Sw = Simandoux(rt,phi,vsh,rxo,rsh,m,n,a)
    
    output = {}
    output['Sw'] = {}
    output['Sw']['name'] = name
    output['Sw']['unit'] = unit
    output['Sw']['data'] = Sw
#    print '\n output', Sw, output
    return output

class SimandouxPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(SimandouxPlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Simandoux Plugin")
        
        if agd.ShowModal() == wx.ID_OK:
            input = agd.get_input()
            well_uid = agd.get_well_uid()
            output = job(**input)
            for odesc in self.outputdesc:
                name = odesc['name']
                output_type = odesc['type']
                obj = self._OM.new(output_type, **output[name])
                self._OM.add(obj, well_uid)
        
        agd.Destroy()
