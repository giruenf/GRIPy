# -*- coding: utf-8 -*-

from Algo.Supervisor import Naive_Bayes

def doinput(self):
    print "\n"*10
    logsuids = [('log', 4), ('log', 7), ('log', 12), ('log', 16)]       #LAS_files/3LI--0001--RJS.las
    loglitouid = ('log',26)
    parentuid = ('well', 0)
    
    logsuids2 = [('log', 33), ('log', 37), ('log', 46), ('log', 53)]    #LAS_files/3LI--0004--RJS.las
    parentuid2 = ('well', 1)
#    k = 5
    partitionname = 'Naive Bayes'
    
    logdata = [self._OM.get(uid).data for uid in logsuids]
    loglito = self._OM.get(loglitouid).data
    logdata2 = [self._OM.get(uid).data for uid in logsuids2]
    
    self.input = dict(loglito=loglito, logdata=logdata, logdata2=logdata2, parentuid=parentuid, parentuid2=parentuid2, partitionname=partitionname)
    return True

def dojob(self, loglito, logdata, logdata2, **kwargs):
    pdata = Naive_Bayes(loglito, logdata, logdata2)
    pinfo = "pinfo"
    
    output = dict(pdata=pdata, pinfo=pinfo)
    return output
    
def dooutput(self):
    parentuid2 = self.input['parentuid2']
    pname = self.input['partitionname']
    pdata = self.output['pdata']
    pinfo = self.output['pinfo']
    
    partition = self._OM.new('partition', name=pname, info=pinfo)
    self._OM.add(partition, parentuid=parentuid2)
    for d in pdata:
        part = self._OM.new('part', d)
        self._OM.add(part, parentuid=partition.uid)
    return True