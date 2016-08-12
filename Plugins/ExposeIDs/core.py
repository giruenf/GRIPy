# -*- coding: utf-8 -*-

def doinput(self):
    return True

def dojob(self, **kwargs):
    for well in self._OM.list('well'):
        print '{} -> {}'.format(well.attributes.get('name'), well.uid)
        for log in self._OM.list('log', well.uid):
            print '\t{} -> {}'.format(log.attributes.get('name'), log.uid)
    print

def dooutput(self):
    return True
