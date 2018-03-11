# -*- coding: utf-8 -*-

import numpy as np

from sklearn.cluster import KMeans
from sklearn.mixture import GMM
from sklearn.preprocessing import scale
from sklearn import metrics

def locate_nans(data):
    return np.sum(np.isnan(data), axis=1, dtype=bool)

def reorder_clusters(clusters, centers, covars=None):
    nc = centers.shape[0]
    nf = centers.shape[1]
    if covars is None:
        covars = np.empty((nc, nf, nf))
        for i in range(nc):
            covars[i] = np.eye(nf)
    
    d2 = np.empty(nc)
    
    for i in range(nc):
        d2[i] = np.dot(np.dot(centers[i], covars[i]), centers[i].T)
    
    argsort = np.argsort(d2)
    
    new_clusters = np.empty_like(clusters)
    
    for i in range(nc):
        new_clusters[clusters == argsort[i]] = i
    
    return new_clusters, argsort

def k_means(data, nc, req_info=None):
    means = np.mean(data, axis=0)
    stds = np.std(data, axis=0)
    
    sdata = (data - means)/stds
    
    km = KMeans(init='k-means++', n_clusters=nc, n_init=10)
    km.fit(sdata)
    
    if req_info == 'all':
        req_info = ['silhouette', 'inertia', 'centers']
    elif req_info is None:
        req_info = []

    info = {}

    if 'silhouette' in req_info:
        info['silhouette'] = metrics.silhouette_score(data, km.labels_)
    if 'inertia' in req_info:
        info['inertia'] = km.inertia_
    if 'centers' in req_info:
        info['centers'] = km.cluster_centers_*stds + means
    
    return km.labels_, info

def expectation_maximization(data, nc, cv_type='full', req_info=None):
    gmm = GMM(n_components=nc, covariance_type=cv_type, thresh=1.0E-4, n_init=10)
    gmm.fit(data)

    labels = gmm.predict(data)

    if req_info == 'all':
        req_info = ['aic', 'bic', 'converged', 'weights', 'means', 'covars',
                    'silhouette', 'proba']
    elif req_info is None:
        req_info = []

    info = {}
    if 'aic' in req_info:
        info['aic'] = gmm.aic(data)
    if 'bic' in req_info:
        info['bic'] = gmm.bic(data)
    if 'converged' in req_info:
        info['converged'] = gmm.converged_
    if 'weights' in req_info:
        info['weights'] = gmm.weights_
    if 'means' in req_info:
        info['means'] = gmm.means_
    if 'covars' in req_info:
        if cv_type == 'full':
            info['covars'] = gmm.covars_
        elif cv_type == 'tied':
            cov = np.empty((nc, gmm.covars_.shape[0], gmm.covars_.shape[1]))
            for i in range(nc):
                cov[i] = gmm.covars_.copy()
            info['covars'] = cov
        else:
            cov = np.empty((nc, gmm.covars_.shape[0], gmm.covars_.shape[1]))
            for i in range(nc):
                cov[i] = np.diag(gmm.covars_[i])
            info['covars'] = cov
    if 'silhouette' in req_info:
        info['silhouette'] = metrics.silhouette_score(data, labels)
    if 'proba' in req_info:
        info['proba'] = gmm.predict_proba(data).T

    return labels, info
