# -*- coding: utf-8 -*-

def doinput(self):
    nphiuid = ('log', 11)
    dtuid = ('log', 8)
    rhouid = ('log', 14)
    parentuid = ('well', 0)
    
    rhoma = 2.7
    rhofl = 1.0
    
    dtma = 120.0
    dtfl = 500.0
    
    nphilog = self._OM.get(nphiuid)
    dtlog = self._OM.get(dtuid)
    rholog = self._OM.get(rhouid)
    
    nphidata = nphilog.data
    dtdata = dtlog.data
    rhodata = rholog.data
    
    self.input = dict(nphidata=nphidata, dtdata=dtdata, rhodata=rhodata, parentuid=parentuid, rhoma=rhoma, rhofl=rhofl, dtma=dtma, dtfl=dtfl)
    return True

def dojob(self, nphidata, dtdata, rhodata, rhoma, rhofl, dtma, dtfl, **kwargs):
    sphidata = (dtdata - dtfl)/(dtma - dtfl)
    dphidata = (rhodata - rhofl)/(rhoma - rhofl)
    
    phiedata = ((sphidata**2 + dphidata**2 + nphidata**2)/3.0)**(0.5)
    
    output = dict(phiedata=phiedata, sphidata=sphidata, dphidata=dphidata)
    return output
    
def dooutput(self):
    parentuid = self.input['parentuid']
    sphidata = self.output['sphidata']
    dphidata = self.output['dphidata']
    phiedata = self.output['phiedata']
    
    sphi = self._OM.new('log', sphidata, name="SPHI2", unit="")
    dphi = self._OM.new('log', dphidata, name="DPHI2", unit="")
    phie = self._OM.new('log', phiedata, name="PHIE2", unit="")
    
    self._OM.add(sphi, parentuid=parentuid)
    self._OM.add(dphi, parentuid=parentuid)
    self._OM.add(phie, parentuid=parentuid)
    return True
