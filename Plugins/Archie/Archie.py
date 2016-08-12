# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
from Algo.BasicPetrophysics.WaterSaturation import Archie
import wx

inputdesc = [
            # {'type': 'omsingle', 'name': 'rxo', 'tids': ['log'], 'dispname': u'Resistividade Curta'},
            {'type': 'float', 'name': 'rxo', 'dispname': u'Resistividade da Água', 'default': 0.5},
            {'type': 'omsingle', 'name': 'rt', 'tids': ['log'], 'dispname': u"Resistividade Longa"},
            {'type': 'omsingle', 'name': 'phi', 'tids': ['log'], 'dispname': u"Porosidade"},
#            {'type': 'choice', 'name': 'model', 'dispname': u'Modelo','items': ['Archie', 'Simandoux'], 'default': 'Archie'},
            {'type': 'float', 'name': 'a', 'dispname': u"A", 'default': 0.62},
            {'type': 'float', 'name': 'm', 'dispname': u"M", 'default': 2.0},
            {'type': 'float', 'name': 'n', 'dispname': u"N", 'default': 2.0},
            {'type': 'text', 'name': 'name', 'dispname': 'Novo Perfil'},
#            {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}
            ]

outputdesc = [{'type': 'log', 'name': 'Sw'}]

def job(**kwargs):
#    a=0.62
#    m=2.
#    n=2.
#    is_sonic = kwargs.get('is_sonic', None)
#    model = kwargs.get('model', None)
#    print '\n\n', model, 'model'
    a = kwargs.get('a', 0.62)
    m = kwargs.get('m', 2.)
    n = kwargs.get('n', 2.)
    rxo = kwargs.get('rxo', None)
    rt = kwargs.get('rt', None)
    phi = kwargs.get('phi', None)
    name = kwargs.get('name', 'Sw')
    if not name: name = 'Sw'
#    unit = kwargs.get('unit', '')
    unit = ''
    
    if phi is None or rxo is None or rt is None:
        return
    
#    if model == 'Archie':
#        print 'arcchhhh'
##        impedancedata = 3.048E5*rho/dt
##        Sw = Archie(rt,phi,rxo,m,n,a)
#    if model == 'Simandoux':
#        print 'simaaaa'
##        Sw = Simandoux(rt,phi,Vsh,Rw,Rsh,m,n,a)
##        impedancedata = dt*rho
    Sw = Archie(rt,phi,rxo,m,n,a)
    print Sw
    output = {}
    output['Sw'] = {}
    output['Sw']['name'] = name
    output['Sw']['unit'] = unit
    output['Sw']['data'] = Sw
#    print '\n output', Sw, output
    return output

class ArchiePlugin(AutoGenDataPlugin):
    def __init__(self):
        super(ArchiePlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Archie Plugin")
        
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
