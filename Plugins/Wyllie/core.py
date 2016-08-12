# -*- coding: utf-8 -*-

from Algo.Supervisor import Naive_Bayes

def doinput(self):
    phi = np.arange(0,41,1)/100
    mode=1
        
    if mode==1: 
        Vp_m = 6000
        Vp_fl = 1500
        self.input = dict(mode=mode,Vp_m=Vp_m, Vp_fl=Vp_fl, phi=phi)
        
    elif mode==2:
        
        Vp_m = 6000
        Vp_fl = 1500
        rho_m = 2.75
        rho_fl = 1.0
        Vs_m = 3500
    
        self.input = dict(mode=mode,Vp_m=Vp_m, Vp_fl=Vp_fl, Vs_m=Vs_m, rho_m=rho_m, rho_fl=rho_fl, phi=phi)  
    #elif
    return True

def dojob(self, **kwargs):
    mode = kwargs.get(mode)
    
    if mode==1:
        Vp_m = kwargs.get(Vp_m)
        Vp_fl = kwargs.get(Vp_fl)
        Vp = (phi/Vp_fl +(1-phi)/Vp_m)**-1
        output = dict(mode=mode,Vp=Vp)
    
    elif mode==2:
        Vp_m = kwargs.get(Vp_m)
        Vp_fl = kwargs.get(Vp_fl)
        Vs_m = kwargs.get(Vs_m)
        rho_m = kwargs.get(rho_m)
        rho_fl = kwargs.get(rho_fl)
        Vp = (phi/Vp_fl +(1-phi)/Vp_m)**-1
        Vs = ((1-phi)/Vs_m)**-1
        rho = (phi/rho_fl + (1-phi)/rho_m)
        K = rho*(Vp**2-4/3*Vs**2)
        mi = rho*Vs**2
        output = dict(mode=mode,Vp=Vp,Vs=Vs,rho=rho,k=k,mi=mi)

    return output
    
def dooutput(self):
    parentuid2 = self.input['parentuid2']
    pname = self.input['partitionname']
    Vp = self.output['Vp']
    pinfo = self.output['pinfo']
    
    partition = self._OM.new('partition', name=pname, info=pinfo)
    self._OM.add(partition, parentuid=parentuid2)
    for d in pdata:
        part = self._OM.new('part', d)
        self._OM.add(part, parentuid=partition.uid)
    return True