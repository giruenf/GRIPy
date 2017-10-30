from Algo import KusterToksoz as KT
from numpy import sqrt

import numpy as np
     
def rho(phi, rho_gr, rho_fl):
    return phi*rho_fl + (1.0 - phi)*rho_gr

def pq_Keys_Xu(Km, Gm, alpha):
    p = KT.T(Km, Gm, alpha)
    q = KT.F(Km, Gm, alpha)
    return p, q

def Keys_Xu(Km, Gm, phi, p, q):
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
    
def Vp_kx(Km, Gm, phi, alpha, Kfl, rho):
    p, q = pq_Keys_Xu(Km, Gm, alpha)
    Kd, G = Keys_Xu(Km, Gm, phi, p, q)
    Ks = Gassmann(Kd, Km, Kfl, phi)
    Vp = sqrt((Ks + 4.0*G/3.0)/rho)
    return Vp
    
def Vp(Ks, G, rho):
#    print '\n\n', ((Ks + 4.0*G/3.0)/rho),'\n\n'
    Vp = sqrt((Ks + 4.0*G/3.0)/rho)
    return Vp

def Vs(G, rho):
    
    Vs = (G/rho)**0.5
    return Vs
    
def PhiDens(denslog, densma, densfl, denscl):       #calculo da porosidade usando o perfil de densidade, sem o perfil de saturacao
    
    phid = 100*(denslog-densma)/(densfl-densma)

    return phid
    
def PhiDensS(denslog,Sw,densma,densH20,densO):  #calculo da porosidade usando o perfil de densidade, com o perfil de saturacao
    
    densfl = Rhof(Sw,densH20,densO)
    phid = 100*(denslog-densma)/(densfl-densma)
    
    return phid
    
def Rhof(Sw,densH20,densO):                 # calculo do perfil de densidade do fluido
    densfl = Sw*densH20 + (1-Sw)*densO
    
    return densfl
        

def PhiDensNeut(neutlog, denslog,densma, densfl, denscl):   #calculo da porosidade usando os perfis de densidade e neutron, sem o perfil de saturacao 
    
    phid = 100*(denslog-densma)/(densfl-densma)
    phidn = (phid+neutlog)/2
#    phid.name='PHID'
#    phid.unit = '%'
   
    return phidn
    
def PhiDensNeutS(neutlog, denslog,Sw,densma,densH20,densO):   #calculo da porosidade usando os perfis de densidade e neutron, com o perfil de saturacao 
    
    densfl = Rhof(Sw,densH20,densO)
    phid = 100*(denslog-densma)/(densfl-densma)
    phidn = (phid+neutlog)/2
#    phid.name='PHID'
#    phid.unit = '%'
    return phidn
    
#Metodo para calcular o Volume de Argila
    
def VshGR(GRlog,itmin,itmax):       # Usando o perfil GR
    
 
    GRmin = np.nanmin(GRlog)
    GRminInt = GRlog[(GRlog<=(GRmin*(1+itmin/100)))]    # Valores do GRmin 
    GRminm = np.mean(GRminInt)                          # Media dos valores de GRmin
    
    GRmax = np.nanmax(GRlog)
    GRmaxInt = GRlog[(GRlog>=(GRmax*(1-itmax/100)))]        # Valores de GRmax
    GRmaxm = np.mean(GRmaxInt)                              # Media dos valores de GRmax 
    
    Vsh = 100*(GRlog-GRminm)/(GRmaxm-GRminm)                # Volume de argila
    
    for i in range(len(Vsh)):
        if (Vsh[i] > 100):
            Vsh[i] = 100
            
        elif (Vsh[i] < 0):
            Vsh[i] = 0
        
    
    print GRmin, GRminm, GRmax, GRmaxm, np.nanmin(Vsh), np.nanmax(Vsh)
    
    return Vsh
    
def VshSP(SPlog,itmin,itmax):       # Usando o perfil SP
    
 
    SPmin = np.nanmin(SPlog)
    SPminInt = SPlog[(SPlog<=(SPmin*(1+itmin/100)))]    # Valores do SPmin 
    SPminm = np.mean(SPminInt)                          # Media dos valores de SPmin
    
    SPmax = np.nanmax(SPlog)
    SPmaxInt = SPlog[(SPlog>=(SPmax*(1-itmax/100)))]        # Valores de SPmax
    SPmaxm = np.mean(SPmaxInt)                              # Media dos valores de SPmax 
    
    Vsh = 100*(SPlog-SPminm)/(SPmaxm-SPminm)                # Volume de argila
    
    for i in range(len(Vsh)):
        if (Vsh[i] > 100):
            Vsh[i] = 100
            
        elif (Vsh[i] < 0):
            Vsh[i] = 0
        
    
    print SPmin, SPminm, SPmax, SPmaxm, np.nanmin(Vsh), np.nanmax(Vsh)
    
    return Vsh
    
    
# metodos para calcular a saturacao

def SwAr(Rt,phi,Rw,m,n,a):           # Metodo Archie
    
    invRt=1.0/Rt
    Sw = (a*Rw*invRt/(phi**m))**(1/n)
    
    for i in range(len(Sw)):
        if (Sw[i] > 1):
            Sw[i] = 1
            
        elif (Sw[i] < 0):
            Sw[i] = 0
    
    return Sw    
    
    
def SwSi(invRt,phi,Vsh,Rw,Rsh,m,n,a):           # Metodo Simandoux 
    
    C = ((1-Vsh)*a*Rw)/(phi**m)
    D = C*Vsh/(2*Rsh)
    E = C*invRt
    Sw = (((D**2)+E)**0.5-D)**(2/n)
        
    for i in range(len(Sw)):
        if (Sw[i] > 100):
            Sw[i] = 100
            
        elif (Sw[i] < 0):
            Sw[i] = 0
    
    return Sw
    
def velocity(dt):          # transforma o perfil de vagarosidade (us/ft) em velocidade (m/s)

    us_m = dt* (1/0.3048);          # Passando a vagarosidade para us/m
    s_m = us_m * (1e-6);	       # Passando o tempo de us para s
    vel = 1./s_m;			       # Passando de vagarosidade para velocidade

    return vel
    
def Misat(vels,rho):
    
    mis = vels*vels*rho
    
    return mis
    
def Ksat(vel,vels,rho):
    
    Ks = rho*(vel*vel - 4.0*vels*vels/3.0)
    
    return Ks
  
def Voigt (k1, f1, k2):
    
    kvoigt = f1*k1 + (1-f1)*k2    
    return kvoigt
    
def Reuss (k1, f1, k2):
    
    kreuss = (f1/k1 + (1-f1)/k2)**(-1)    
    return kreuss
        
def VRHill ():
    
#    kvoigt = Voigt (k1, f1, k2)
#    kreuss = Reuss (k1, f1, k2)
#    kvrh = (kvoigt+kreuss)*0.5    
#    return kvrh
    return 'TEST'
    
def Dens (rhom, rhof, phi):

    dens = (rhom*(1 - phi) + rhof*phi)
    return dens
    
def Kd (Ks, Km, Kf, phi):
    
    gamma = phi*(Km/Kf - 1.0)
    kd = (Ks*(gamma + 1.0) - Km)/(gamma - 1.0 + Ks/Km)
    return kd
    
def Gassmann(Kd, Km, Kfl, phi):
    """
    B = (1.0 - Kd/Km)
    Ks = Kd + B*B/(phi/Kfl - phi/Km + B/Km)
    """
    Ks = Kd + (1.0 - Kd/Km)**2/(phi/Kfl + (1.0 - phi)/Km - Kd/Km**2)
    return Ks

def highestvals(vector,percent):         # maiores valores de um array
#
    iv = int((percent/100.0)*len(vector)) 
    ivec = np.argpartition(-vector,iv)
    ivechv = ivec[:iv]
    return ivechv
    
def curveadjust(Kpss,phis,ks,phi):

    errototal=[]
    ksp=ks[~np.isnan(ks)]
    phip=phi[~np.isnan(ks)]
    phipn=[round(elem, 0) for elem in phip ]
    
    for i in range(len(Kpss)):

        errop=[]

        for j in range(len(ksp)):

            #porpn=[round(elem, 0) for elem in porp ]
            #porpn=int(porp[j])
            a = int(phipn[j])
            erro = abs(ksp[j]-Kpss[i][a])


            errop.append(erro)
            

        errototal.append(sum(errop)/len(ksp))

    erromin=min(errototal)
    n = np.array(range(len(Kpss)))
    
    nb = int(np.array(n[(errototal==erromin)]))
    Kbest = Kpss[nb][:]
    
    return Kbest