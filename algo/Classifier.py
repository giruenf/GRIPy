# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
import time
from scipy import stats

class Classifier(object):
    def train(self, data, target):
        pass
    
    def classify(self, data):
        pass


def benchmark_classifier(classifier, traindata, traintarget, testdata, testtarget):
    t0 = time.time()
    classifier.train(traindata, traintarget)
    t1 = time.time()
    testresult = classifier.classify(testdata)
    t2 = time.time()
    
    trainresult = classifier.classify(traindata)
    
    traintime = t1 - t0
    testtime = t2 - t1
    trainaccuracy = np.sum(trainresult == traintarget)/len(traintarget)
    testaccuracy = np.sum(testresult == testtarget)/len(testtarget)
    
    benchmark = {}
    benchmark['time'] = dict(train=traintime, test=testtime)
    benchmark['accuracy'] = dict(train=trainaccuracy, test=testaccuracy)
    benchmark['result'] = dict(train=trainresult, test=testresult)
    
    return benchmark

def compare_classifiers(classifiers, traindata, traintarget, testdata, testtarget, classifiersnames=None):
    if classifiersnames is None:
        classifiersnames = range(len(classifiers))

    benchmarks = {}

    for classifier, classifiername in zip(classifiers, classifiersnames):
        benchmark = benchmark_classifier(classifier, traindata, traintarget, testdata, testtarget)
        benchmarks[classifiername] = benchmark

    return benchmarks

def batch_compare_classifiers(classifiers, traindata, traintarget, testdata, testtarget, classifiersnames=None, datanames=None):
    if datanames is None:
        datanames = range(len(traindata))
        
    benchmarks = {}
    
    for traindata_, traintarget_, testdata_, testtarget_, dataname in zip(traindata, traintarget, testdata, testtarget, datanames):
        benchmark = compare_classifiers(classifiers, traindata_, traintarget_, testdata_, testtarget_, classifiersnames)
        benchmarks[dataname] = benchmark
    
    return benchmarks

def split_train_and_test(data, target, ratio=0.5):
    train = stats.bernoulli.rvs(ratio, size=data.shape[0]).astype(bool)
    test = ~train
    
    dataset = dict(traindata=data[train], traintarget=target[train], testdata=data[test], testtarget=target[test])
    
    return dataset
