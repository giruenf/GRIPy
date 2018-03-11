import numpy as np
     
# metodos para calcular a saturacao

def Archie(Rt,phi,Rw,m,n,a):           # Metodo Archie
    phi = phi
    invRt=1.0/Rt
    Sw = (a*Rw*invRt/(phi**m))**(1./n)    
    Sw = np.clip(Sw, 0.0, 1.0)
    
    return Sw*100.0
    
    
def Simandoux(Rt,phi,Vsh,Rw,Rsh,m,n,a):           # Metodo Simandoux 

    invRt=1.0/Rt
    C = ((1-Vsh)*a*Rw)/(phi**m)
    D = C*Vsh/(2*Rsh)
    E = C*invRt
    Sw = (((D**2)+E)**0.5-D)**(2/n)
        
    Sw = np.clip(Sw, 0.0, 1.0)
    
    return Sw*100.0

