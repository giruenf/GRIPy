# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

class MonteCarloBayesError(object):
    def __init__(self, classifier):
        self.classifier = classifier

    def calculatematrix(self, n=1000000):
        if not self.classifier.checkclasspmvalidity():
            return None
                
        nclasses = np.random.multinomial(n, [self.classifier.classpm.prob(cls) for cls in self.classifier.classes], size=1)[0]  # TODO: é necessário fazer isso?
    
        matrix = np.empty((len(self.classifier.classes), len(self.classifier.classes)), dtype=float)
        
        for i in range(len(self.classifier.classes)):
            drawnsamples = self.classifier.featurepm[self.classifier.classes[i]].sample(nclasses[i])
            probs = self.classifier.probabilities2(drawnsamples)  # TODO: por que não probabilities()?
            maps = self.classifier.classify2(probs=probs)  # TODO: por que não classify()?
            for j in range(len(self.classifier.classes)):
                matrix[i][j] = np.sum(maps == self.classifier.classes[j])/nclasses[i]
        
        return matrix
    
    def calculateglobalerror(self, matrix=None):
        if matrix is None:
            matrix = self.calculatematrix()
        
        globalerror = 0.0
        for i in range(len(self.classifier.classes)):
            globalerror += self.classifier.classpm.prob(self.classifier.classes[i])*(1.0 - matrix[i][i])
        
        return globalerror
