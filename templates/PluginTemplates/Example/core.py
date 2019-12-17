# -*- coding: utf-8 -*-

def doinput(self):
    dtuid = ('log', 9)
    rhouid = ('log', 15)
    parentuid = ('well', 0)

    dtlog = self._OM.get(dtuid)
    rholog = self._OM.get(rhouid)

    dtdata = dtlog.data
    rhodata = rholog.data

    self.input = dict(dtdata=dtdata, rhodata=rhodata, parentuid=parentuid)
    return True


def dojob(self, dtdata, rhodata, **kwargs):
    ipdata = rhodata / dtdata * 3.048E8

    output = dict(ipdata=ipdata)
    return output


def dooutput(self):
    parentuid = self.input['parentuid']
    ipdata = self.output['ipdata']

    ip = self._OM.new('log', ipdata, name="IP", unit="")
    self._OM.add(ip, parentuid=parentuid)
    return True
