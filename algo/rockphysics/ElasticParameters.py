from Algo import KusterToksoz as KT
from numpy import sqrt

def Misat(Vs,Dens):
    
    mis = Vs*Vs*Dens    
    return mis
    
def Ksat(Vp,Vs,Dens):
    
    Ks = Dens*(Vp*Vp - 4.0*Vs*Vs/3.0)    
    return Ks  
    
def Dens (Densm, Densf, phi):

    dens = (Densm*(1 - phi) + Densf*phi)
    return dens
    
def Kdry (Ksat, Kmin, Kfl, phi):
    
    gamma = phi*(Kmin/Kfl - 1.0)
    kd = (Ksat*(gamma + 1.0) - Kmin)/(gamma - 1.0 + Ksat/Kmin)
    return kd
    
def pq_Keys_Xu(Km, Gm, alpha):
    p = KT.T(Km, Gm, alpha)
    q = KT.F(Km, Gm, alpha)
    return p, q

def Keys_Xu(Km, Gm, alpha, phi):
    p, q = pq_Keys_Xu(Km, Gm, alpha)
    Kd = Km*(1.0 - phi)**p
    Gd = Gm*(1.0 - phi)**q
    return Kd, Gd

def XW_dry(Km, Gm, alpha, phi, curphi=0.0):
    _PFACTOR = 10
    nphi = int(phi*_PFACTOR/alpha + 0.5)            #numero de interacoes para incrementar a porosidade
    if not nphi:
        nphi = 1
    dphi = phi/nphi                 # passo da porosidade
    K_ = Km
    G_ = Gm
    Kd = Km
    Gd = Gm
    for i in range(nphi):                           # metodo DEM para calculo dos modulos de bulk e cisalhante da rocha seca
        Kd = KT.Kd(K_, G_, alpha, dphi/(1.0 - curphi - i*dphi))             # a porosidade vai sendo incrementada usando o passo dphi
        Gd = KT.Gd(K_, G_, alpha, dphi/(1.0 - curphi - i*dphi))
        K_ = Kd
        G_ = Gd

    return Kd, Gd
    
#def Vp_kx(Km, Gm, phi, alpha, Kfl, rho):
#    p, q = pq_Keys_Xu(Km, Gm, alpha)
#    Kd, G = Keys_Xu(Km, Gm, phi, p, q)
#    Ks = Gassmann(Kd, Km, Kfl, phi)
#    Vp = sqrt((Ks + 4.0*G/3.0)/rho)
#    return Vp

def Vp(Ks, G, rho):
#    print '\n\n', ((Ks + 4.0*G/3.0)/rho),'\n\n'
    Vp = sqrt((Ks + 4.0*G/3.0)/rho)
    return Vp

def Vs(G, rho):
    
    Vs = (G/rho)**0.5
    return Vs
