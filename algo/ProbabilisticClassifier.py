# -*- coding: utf-8 -*-
import numpy as np
from Algo import ProbabilisticModel as PM
from Algo.Classifier import Classifier


class ProbabilisticClassifier(Classifier):
    def __init__(self, classpm_key="uniform", featurepm_key="normal", classpm_kwargs=None, featurepm_kwargs=None):
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
        self.classes = np.unique(target)
        
        self.featurepm = {}
        for cls in self.classes:
            self.featurepm[cls] = PM.get_probabilistic_model(self.featurepm_key)(**self.featurepm_kwargs)
            self.featurepm[cls].fit(data[target==cls])

    def checkclasspmvalidity(self):
        cumsum = 0.0
        try:
            for cls in self.classes:
                cumsum += self.classpm.prob(cls)
            return cumsum == 1.0
        except:
            return False
    
    def loglikelihoods(self, data):
        loglikes = np.empty((len(self.classes), len(data)))  # TODO: prestar atenção no shape de data: saída do amostrador/entrada do calculador
        
        for i in range(len(self.classes)):
            loglikes[i] = self.classpm.logprob(self.classes[i]) + self.featurepm[self.classes[i]].logprob(data)
                
        return loglikes
    
    def probabilities(self, data=None, loglikes=None):
        if loglikes is None:
            loglikes = self.loglikelihoods(data)
        
        probs = np.exp(loglikes)
        
        probs /= np.sum(probs, axis=0)
        
        return probs
        
    def classify(self, data=None, loglikes=None):
        if loglikes is None:
            loglikes = self.loglikelihoods(data)
        
        return self.classes[np.argmax(loglikes, axis=0)]
    
    def error(self, data=None, loglikes=None, probs=None):
        if probs is None:
            if loglikes is None:
                probs = self.probabilities(data)
            else:
                probs = self.loglikelihoods(loglikes=loglikes)
        
        return 1.0 - np.max(probs, axis=0)
        
    def probabilities2(self, data=None):
        probs = np.empty((len(self.classes), len(data)))  # TODO: prestar atenção no shape de data: saída do amostrador/entrada do calculador
        
        for i in range(len(self.classes)):
            probs[i] = self.classpm.prob(self.classes[i])*self.featurepm[self.classes[i]].prob(data)
        
        probs /= np.sum(probs, axis=0)
        
        return probs
        
    def classify2(self, data=None, probs=None):
        if probs is None:
            probs = self.probabilities2(data)
        
        return self.classes[np.argmax(probs, axis=0)]
    
    def error2(self, data=None, probs=None):
        if probs is None:
            probs = self.probabilities2(data)
        
        return 1.0 - np.max(probs, axis=0)
