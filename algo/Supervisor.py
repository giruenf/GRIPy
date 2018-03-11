# -*- coding: utf-8 -*-

import numpy as np
from sklearn.preprocessing import scale
#import matplotlib
#import matplotlib.pyplot as plt
#import partition as ptt
#from sklearn.neighbors import KNeighborsClassifier as KNC
from sklearn.naive_bayes import GaussianNB

def Naive_Bayes(lito, logs, logs2):
    
           
    n = len(logs[0])
    goods = np.ones(n, dtype=bool)
    for log in logs:
        goods *= ~np.isnan(log)
    idxs = np.arange(n)[goods]
    data = scale(np.array([log[goods] for log in logs])).T
    
    lito1 = lito[idxs]
    
    vfacies = np.unique(lito1)
    nfacies = len(vfacies)
    
    print nfacies
    
    n2 = len(logs2[0])
    goods2 = np.ones(n2, dtype=bool)
    for log2 in logs2:
        goods2 *= ~np.isnan(log2)
    idxs2 = np.arange(n2)[goods2]
    data2 = scale(np.array([log2[goods2] for log2 in logs2])).T
    
    clf = GaussianNB()
    clf.fit(data, lito1)
    labels = clf.predict(data2)
    labels_proba = clf.predict_proba(data2)
    
    print labels.shape
    
    
    clusters = np.zeros((nfacies, n), dtype=bool)
    for i in range(nfacies):
        clusters[i][idxs2[labels == vfacies[i]]] = True
        
    print clusters.shape
        
    return clusters