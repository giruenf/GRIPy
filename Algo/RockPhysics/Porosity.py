import numpy as np

# metodos para calcular porosidade

def PhiVel(vellog, velma, velfl):       #calculo da porosidade usando o perfil de velocidade
    
    phiv = (vellog-velma)/(velfl-velma)
    phiv = np.clip(phiv, 0.0, 1.0)
    return phiv
    
def PhiDens(denslog, densma, densfl):       #calculo da porosidade usando o perfil de densidade
    
    phid = (denslog-densma)/(densfl-densma)
    phid = np.clip(phid, 0.0, 1.0)
    return phid

def PhiDensNeut(neutlog, denslog, densma, densfl):   #calculo da porosidade usando os perfis de densidade e neutron
    
    phid = (denslog-densma)/(densfl-densma)
    phidn = np.sqrt((phid**2+neutlog**2)/2)
    phidn = np.clip(phidn, 0.0, 1.0)
    return phidn