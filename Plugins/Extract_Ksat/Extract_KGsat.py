# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import Algo.RockPhysics.ElasticParameters as ep
import wx

inputdesc = [
            {'type': 'omsingle', 'name': 'vp', 'tids': ['log'], 'dispname': u'Perfil VP'},
            {'type': 'omsingle', 'name': 'vs', 'tids': ['log'], 'dispname': u"Perfil VS"},
            {'type': 'omsingle', 'name': 'dens', 'tids': ['log'], 'dispname': u"Perfil Densidade"},
#            {'type': 'omsingle', 'name': 'phi', 'tids': ['log'], 'dispname': u"Perfil Porosidade"},
#             {'type': 'bool', 'name': 'model', 'dispname': u"Archie", 'default': True},
#            {'type': 'float', 'name': 'kf1', 'dispname': u"K fluido", 'default': '2.5'},
#            {'type': 'float', 'name': 'kf2', 'dispname': u"Kf2", 'default': '1.1'},
#            {'type': 'float', 'name': 'km', 'dispname': u"K mineral", 'default': '5000.0'},
#            {'type': 'float', 'name': 'alpha', 'dispname': u"Razão aspecto", 'default': '1.0'},
#            {'type': 'float', 'name': 'rhof', 'dispname': u"Dens_f", 'default': '0.87'},
#            {'type': 'text', 'name': 'namevs', 'dispname': 'Novo Perfil VS'},
#            {'type': 'text', 'name': 'namedens', 'dispname': 'Novo Perfil DENS'},
#            {'type': 'choice', 'name': 'model', 'items': ['Classico', 'Keys&Xu', 'Xu&White'], 'dispname': u'Modelo de Cálculo'},
            {'type': 'text', 'name': 'nameksat', 'dispname': 'Novo Perfil Ksat'},
            {'type': 'text', 'name': 'namegsat', 'dispname': 'Novo Perfil Gsat'},
            ]

outputdesc = [{'type': 'log', 'name': 'Ksat'}, {'type': 'log', 'name': 'Gsat'}]

def job(**kwargs):
#    km = kwargs.get('km', 5000.0)
#    kf1 = kwargs.get('kf1', 2.5)
#    ksat = kwargs.get('ksat', 1.1)
#    gsat = kwargs.get('ksat', 1.1)
    vp = kwargs.get('vp', None)
    vs = kwargs.get('vs', None)
    dens = kwargs.get('dens', None)
#    model = kwargs.get('model', None)
#    phi = kwargs.get('phi', None)
#    alpha = kwargs.get('alpha', None)
#    rhof = kwargs.get('rhof', None)
#    
    ksat = ep.Ksat(vp, vs, dens)
    gsat = ep.Misat(vs,dens)
#    mi = ep.Misat(vs,dens)
#    if model == 'Classico':
#        kd = ep.Kdry (ksat, km, kf1, phi)
#    elif model == 'Keys&Xu':
#        kd = ep.Keys_Xu(km, gsat, alpha, phi)
#    elif model == 'Keys&Xu':
#        kd = ep.XW_dry(km, gsat, alpha, phi, curphi=0.0)
#    else:
#        return
#    ksubst = sbt.Gassmann(kd, km, kf2, phi)
#    rhos = ep.Dens (rhom, rhof, phi)
#    vps = ep.Vp (ksubst, mi, rhos)
#    vss = ep.Vs (mi, rhos)
    nameksat = kwargs.get('nameksat', 'K_sat')
    namegsat = kwargs.get('namegsat', 'G_sat')
#    namevs = kwargs.get('namevs', 'Vs_gass')
#    namedens = kwargs.get('namedens', 'Rho_gass')
    if not nameksat: nameksat = 'K_sat'
    if not namegsat: namegsat = 'G_sat'
#    if not namevs: namevs = 'vs_cor'
#    if not namedens: namedens = 'dens_cor'
    unit = ''
    
#    if phi is None or vp is None or vs is None or rhom is None:
#        return
        
    output = {}
    output['Ksat'] = {}
    output['Ksat']['name'] = nameksat
    output['Ksat']['unit'] = unit
    output['Ksat']['data'] = ksat
    
    output['Gsat'] = {}
    output['Gsat']['name'] = namegsat
    output['Gsat']['unit'] = unit
    output['Gsat']['data'] = gsat
    
    return output

class KGPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(KGPlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Extract Kdry Plugin")
        
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
