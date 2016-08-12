# -*- coding: utf-8 -*-

from Algo.Clustering import expectation_maximization

def doinput(self):
    logsuids = [('log', 11), ('log', 15), ('log', 29), ('log', 35)]
    parentuid = ('well', 0)
    k = 5
    partitionname = 'Expectation Maximization'
    
    logdata = [self._OM.get(uid).data for uid in logsuids]
    
    self.input = dict(logdata=logdata, k=k, parentuid=parentuid, partitionname=partitionname)
    return True

def dojob(self, logdata, k, **kwargs):
    pdata, pprob, pinfo = expectation_maximization(logdata, k, 'full', 'all')
    
    output = dict(pdata=pdata, pprob=pprob, pinfo=pinfo)
    return output
    
def dooutput(self):
    parentuid = self.input['parentuid']
    pname = self.input['partitionname']
    pdata = self.output['pdata']
    pprob = self.output['pprob']
    pinfo = self.output['pinfo']
    
    partition = self._OM.new('partition', name=pname, prob=pprob, info=pinfo)
    self._OM.add(partition, parentuid=parentuid)
    for d in pdata:
        part = self._OM.new('part', d)
        self._OM.add(part, parentuid=partition.uid)
    return True