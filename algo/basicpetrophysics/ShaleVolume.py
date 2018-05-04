from sklearn.mixture import GMM
import numpy as np
     
"""
Functions to calculate shale volum using 
gamma-ray log (GR) or spontaneous potential log (SP)
"""
     
def GRsd (GRlog):
    em = GMM(n_components=3)
    em.fit(GRlog.reshape((-1, 1)))
    idxminmeangr = np.argmin(em.means_)
    grsd = em.means_[idxminmeangr] - em.covars_[idxminmeangr]**0.5
    
    return grsd
    
def GRsh (GRlog):
    em = GMM(n_components=3)
    em.fit(GRlog.reshape((-1, 1)))
    idxmaxmeangr = np.argmax(em.means_)
    grsh = em.means_[idxmaxmeangr] + em.covars_[idxmaxmeangr]**0.5
    
    return grsh     
    
def VshGR(GRlog):
    grsd = GRsd (GRlog)
    grsh = GRsh (GRlog)
    newvshalelog = (GRlog - grsd)/(grsh - grsd)
    newvshalelog = np.clip(newvshalelog, 0.0, 1.0)
    return newvshalelog
    
    
def SPsd (SPlog):
    em = GMM(n_components=3)
    em.fit(SPlog.reshape((-1, 1)))
    idxminmeangr = np.argmin(em.means_)
    spsd = em.means_[idxminmeangr] - em.covars_[idxminmeangr]**0.5
    
    return spsd
    
def SPsh (SPlog):
    em = GMM(n_components=3)
    em.fit(SPlog.reshape((-1, 1)))
    idxmaxmeangr = np.argmax(em.means_)
    spsh = em.means_[idxmaxmeangr] + em.covars_[idxmaxmeangr]**0.5
    
    return spsh     
    
def VshSP(SPlog):
    spsd = SPsd (SPlog)
    spsh = SPsh (SPlog)
    newvshalelog = (SPlog - spsd)/(spsh - spsd)
    newvshalelog = np.clip(newvshalelog, 0.0, 1.0)
    return newvshalelog