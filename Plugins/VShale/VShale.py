# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
from Algo.BasicPetrophysics.ShaleVolume import VshGR, VshSP
import wx

inputdesc = [
            {'type': 'choice', 'name': 'model', 'dispname': u'Método de Cálculo','items': ['Gamma-Ray', 'SP']},
            {'type': 'omsingle', 'name': 'log', 'tids': ['log'], 'dispname': u'Perfil do Método'},
#            {'type': 'omsingle', 'name': 'gr', 'tids': ['log'], 'dispname': u"Gamma-Ray"},
#             {'type': 'bool', 'name': 'model', 'dispname': u"Archie", 'default': True},
            {'type': 'text', 'name': 'name', 'dispname': 'Nome', 'default': 'Vsh'},

#            {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}
            ]

outputdesc = [{'type': 'log', 'name': 'Vsh'}]

def job(**kwargs):
    model = kwargs.get('model', None)
    log = kwargs.get('log', None)
    name = kwargs.get('name', 'Vsh')
    if not name: name = 'SW'
    unit = '%'
    
    if model is None or log is None:
        return
#    print '\n\n', model, 'model'

    if model == 'Gamma-Ray':
        Vsh = VshGR(log)
    if model == 'SP':
        Vsh = VshSP(log, itmin = 5., itmax = 5.)
#    Res2 = rt[vsh > 0.85]
#    rsh = np.percentile(Res2,50)
#    Vsh = Simandoux(rt,phi,vsh,rxo,rsh,m,n,a)
    
    output = {}
    output['Vsh'] = {}
    output['Vsh']['name'] = name
    output['Vsh']['unit'] = unit
    output['Vsh']['data'] = Vsh
#    print '\n output', Sw, output
    return output

class VShalePlugin(AutoGenDataPlugin):
    def __init__(self):
        super(VShalePlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Vsh Plugin")
        
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
