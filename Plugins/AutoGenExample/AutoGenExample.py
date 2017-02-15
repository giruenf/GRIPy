# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import wx



inputdesc = [{'type': 'omsingle', 'name': 'dt', 'tids': ['log'], 'dispname': u'Sônico'},
             {'type': 'omsingle', 'name': 'rho', 'tids': ['log'], 'dispname': u"Densidade"},
             {'type': 'bool', 'name': 'is_sonic', 'dispname': u"É sônico?", 'default': True},
             {'type': 'text', 'name': 'name', 'dispname': 'Nome'},
             {'type': 'text', 'name': 'unit', 'dispname': 'Unidade'}]

outputdesc = [{'type': 'log', 'name': 'impedance'}]



def job(**kwargs):
    is_sonic = kwargs.get('is_sonic', None)
    rho = kwargs.get('rho', None)
    dt = kwargs.get('dt', None)
    name = kwargs.get('name', 'IP')
    unit = kwargs.get('unit', '')
    
    if is_sonic is None or rho is None or dt is None:
        return
    
    if is_sonic:
        impedancedata = 3.048E5*rho/dt
    else:
        impedancedata = dt*rho
    
    output = {}
    output['impedance'] = {}
    output['impedance']['name'] = name
    output['impedance']['unit'] = unit
    output['impedance']['data'] = impedancedata
    return output




class AutoGenExamplePlugin(AutoGenDataPlugin):
    
    def __init__(self):
        super(AutoGenExamplePlugin, self).__init__()        
        self._OM = ObjectManager(self)        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc        
        #self.menukey = "infer"
        
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Impedance Plugin")
        
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
