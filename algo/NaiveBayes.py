# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from Algo import ProbabilisticModel as PM

class NaiveBayes(object):
    def __init__(self, classpm_key="uniform", featurepm_key="normal-1d", classpm_kwargs=None, featurepm_kwargs=None):
        self.classpm_key = classpm_key
        self.featurepm_key = featurepm_key
        if classpm_kwargs is None:
            self.classpm_kwargs = {}
        else:
            self.classpm_kwargs = classpm_kwargs
        if featurepm_kwargs is None:
            self.featurepm_kwargs = {}
        else:
            self.featurepm_kwargs = featurepm_kwargs
        self.classpm = None
        self.featurepm = {}

    def train(self, data, target):
        self.classpm = PM.get_probabilistic_model(self.classpm_key)(**self.classpm_kwargs)
        self.classpm.fit(target)
        classes = np.unique(target)
        
        self.featurepm = {}
        n_features = data.shape[1]
        
        for cls in classes:
            self.featurepm[cls] = []
            classdata = data[target==cls]
            for i in range(n_features):
                fpm = PM.get_probabilistic_model(self.featurepm_key)(**self.featurepm_kwargs)
                fpm.fit(classdata[:, i])
                self.featurepm[cls].append(fpm)
    
    def classify(self, data):
        classprior = np.array([self.classpm.prob(cls) for cls in self.featurepm.keys()])
        prob = np.tile(classprior, (data.shape[0], 1))
        for i, cls in enumerate(self.featurepm.keys()):
            for j in range(data.shape[1]):
                prob[:, i] *= self.featurepm[cls][j].prob(data[:, j])
        
        classification = np.argmax(prob, axis=1)
        
        bs = []
        for i in range(len(classprior)):
            bs.append(classification == i)
        
        for i, cls in enumerate(self.featurepm.keys()):
            classification[bs[i]] = cls
        
        return classification
        