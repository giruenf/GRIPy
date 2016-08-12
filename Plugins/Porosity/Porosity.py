# -*- coding: utf-8 -*-

from Plugins import AutoGenDataPlugin
from Plugins.Tools.AutoGenUI import AutoGenDialog
from OM.Manager import ObjectManager
import Algo.RockPhysics.Porosity as pr
import wx

inputdesc = [
            {'type': 'omsingle', 'name': 'vp', 'tids': ['log'], 'dispname': u'Perfil VP'},
            {'type': 'float', 'name': 'vpma', 'dispname': u"Vp mineral", 'default': 5.2},
            {'type': 'float', 'name': 'vpfl', 'dispname': u"Vp fluido", 'default': 1.41},
            {'type': 'omsingle', 'name': 'rho', 'tids': ['log'], 'dispname': u"Perfil Densidade"},
            {'type': 'float', 'name': 'rhoma', 'dispname': u"Densidade mineral", 'default': 2.65},
            {'type': 'float', 'name': 'rhofl', 'dispname': u"Densidade fluido", 'default': 1.1},
            {'type': 'omsingle', 'name': 'neut', 'tids': ['log'], 'dispname': u"Perfil Porosidade Neutron"},
#             {'type': 'bool', 'name': 'model', 'dispname': u"Archie", 'default': True},
#            {'type': 'float', 'name': 'kf1', 'dispname': u"K fluido", 'default': '2.5'},
#            {'type': 'float', 'name': 'kf2', 'dispname': u"Kf2", 'default': '1.1'},
#            {'type': 'float', 'name': 'km', 'dispname': u"K mineral", 'default': '5000.0'},
#            {'type': 'float', 'name': 'alpha', 'dispname': u"Razão aspecto", 'default': '1.0'},
#            {'type': 'float', 'name': 'rhof', 'dispname': u"Dens_f", 'default': '0.87'},
#            {'type': 'text', 'name': 'namevs', 'dispname': 'Novo Perfil VS'},
#            {'type': 'text', 'name': 'namedens', 'dispname': 'Novo Perfil DENS'},
            {'type': 'choice', 'name': 'model', 'items': [u'Sônico', 'Densidade', 'Densidade&Neutron'], 'dispname': u'Modelo de Cálculo', 'default': u'Sônico'},
            {'type': 'text', 'name': 'namephi', 'dispname': u'Novo Perfil Porosidade'},
            ]

outputdesc = [{'type': 'log', 'name': 'Phi'}]

def job(**kwargs):
    vp = kwargs.get('vp', None)
    vpma = kwargs.get('vpma', None)
    vpfl = kwargs.get('vpfl', None)
    rho = kwargs.get('rho', None)
    rhoma = kwargs.get('rhoma', None)
    rhofl = kwargs.get('rhofl', None)
    neut = kwargs.get('neut', None)
    
#    km = kwargs.get('km', 5000.0)
#    kf1 = kwargs.get('kf1', 2.5)
#    ksat = kwargs.get('ksat', 1.1)
#    gsat = kwargs.get('ksat', 1.1)

#    vs = kwargs.get('vs', None)
    model = kwargs.get('model', None)
#    phi = kwargs.get('phi', None)
#    alpha = kwargs.get('alpha', None)
#    rhof = kwargs.get('rhof', None)
#    
#    ksat = ep.Ksat(vp, vs, dens)
#    mi = ep.Misat(vs,dens)
    if model == u'Sônico':
        phi = pr.PhiVel(vp, vpma, vpfl)
    elif model == 'Densidade':
        phi = pr.PhiDens(rho, rhoma, rhofl)
    elif model == 'Densidade&Neutron':
        phi = pr.PhiDensNeut(neut, rho, rhoma, rhofl)
    else:
        return
#    ksubst = sbt.Gassmann(kd, km, kf2, phi)
#    rhos = ep.Dens (rhom, rhof, phi)
#    vps = ep.Vp (ksubst, mi, rhos)
#    vss = ep.Vs (mi, rhos)
    namephi = kwargs.get('namephi', 'PHI_cor')
#    namevs = kwargs.get('namevs', 'Vs_gass')
#    namedens = kwargs.get('namedens', 'Rho_gass')
    if not namephi: namephi = 'PHI_cor'
#    if not namevs: namevs = 'vs_cor'
#    if not namedens: namedens = 'dens_cor'
    unit = ''
    
#    if phi is None or vp is None or vs is None or rhom is None:
#        return
        
    output = {}
    output['Phi'] = {}
    output['Phi']['name'] = namephi
    output['Phi']['unit'] = unit
    output['Phi']['data'] = phi
    
    return output

class PorosityPlugin(AutoGenDataPlugin):
    def __init__(self):
        super(PorosityPlugin, self).__init__()
        
        self._OM = ObjectManager(self)
        
        self.inputdesc = inputdesc
        self.outputdesc = outputdesc
        self.menukey = 'interp'
    
    def run(self, uiparent):
        agd = AutoGenDialog(uiparent, self.inputdesc)
        agd.SetTitle("Efective Porosity Plugin")
        
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
