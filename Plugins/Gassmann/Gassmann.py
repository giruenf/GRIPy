# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import Algo.RockPhysics.ElasticParameters as ep
import Algo.RockPhysics.Substitution as sbt
import wx

inputdesc = [
            {'type': 'omsingle', 'name': 'vp', 'tids': ['log'], 'dispname': u'Perfil VP'},
            {'type': 'omsingle', 'name': 'vs', 'tids': ['log'], 'dispname': u"Perfil VS"},
            {'type': 'omsingle', 'name': 'dens', 'tids': ['log'], 'dispname': u"Perfil Densidade"},
            {'type': 'omsingle', 'name': 'phi', 'tids': ['log'], 'dispname': u"Perfil Porosidade"},
#             {'type': 'bool', 'name': 'model', 'dispname': u"Archie", 'default': True},
            {'type': 'float', 'name': 'kf1', 'dispname': u"Kf1", 'default': '2.5'},
            {'type': 'float', 'name': 'kf2', 'dispname': u"Kf2", 'default': '1.1'},
            {'type': 'float', 'name': 'km', 'dispname': u"Km", 'default': '5000.'},
            {'type': 'float', 'name': 'rhom', 'dispname': u"Dens_m", 'default': '2.28'},
            {'type': 'float', 'name': 'rhof', 'dispname': u"Dens_f", 'default': '0.87'},
            {'type': 'text', 'name': 'namevp', 'dispname': 'Novo Perfil VP'},
            {'type': 'text', 'name': 'namevs', 'dispname': 'Novo Perfil VS'},
            {'type': 'text', 'name': 'namedens', 'dispname': 'Novo Perfil DENS'},
#            {'type': 'choice', 'name': 'model', 'dispname': 'Modelo'},
            ]

outputdesc = [{'type': 'log', 'name': 'Vp'}, {'type': 'log', 'name': 'Vs'}, {'type': 'log', 'name': 'Rho'}]

def job(**kwargs):
    km = kwargs.get('km', 5000.0)
    kf1 = kwargs.get('kf1', 2.5)
    kf2 = kwargs.get('kf2', 1.1)
    vp = kwargs.get('vp', None)
    vs = kwargs.get('vs', None)
    dens = kwargs.get('dens', None)
    phi = kwargs.get('phi', None)
    rhom = kwargs.get('rhom', None)
    rhof = kwargs.get('rhof', None)
    
    ksat = ep.Ksat(vp, vs, dens)
    mi = ep.Misat(vs,dens)
    kd = ep.Kdry (ksat, km, kf1, phi)
    ksubst = sbt.Gassmann(kd, km, kf2, phi)
    rhos = ep.Dens (rhom, rhof, phi)
    vps = ep.Vp (ksubst, mi, rhos)
    vss = ep.Vs (mi, rhos)
    namevp = kwargs.get('namevp', 'Vp_gass')
    namevs = kwargs.get('namevs', 'Vs_gass')
    namedens = kwargs.get('namedens', 'Rho_gass')
    if not namevp: namevp = 'vp_cor'
    if not namevs: namevs = 'vs_cor'
    if not namedens: namedens = 'dens_cor'
    unit = ''
    print vp,'\n'
    
    if phi is None or vp is None or vs is None or rhom is None:
        return
        
    output = {}
    output['Vp'] = {}
    output['Vp']['name'] = namevp
    output['Vp']['unit'] = unit
    output['Vp']['data'] = vps
    
    output['Vs'] = {}
    output['Vs']['name'] = namevs
    output['Vs']['unit'] = unit
    output['Vs']['data'] = vss
    
    output['Rho'] = {}
    output['Rho']['name'] = namedens
    output['Rho']['unit'] = unit
    output['Rho']['data'] = rhos
    
    return output

class GassmanPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(GassmanPlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Gassmann Plugin")
        
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
