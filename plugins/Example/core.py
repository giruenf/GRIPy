# -*- coding: utf-8 -*-

def doinput(*args, **kwargs):
    try:
        obj = args[0]
        if not obj:
            return
        well = obj._OF.findobject(well="Entrada_1")
        if not well:
            print 'Example.core.doinput: Well is None'
            return None
        parentuid = well.uid
        dtlog = obj._OF.findobject(well="Entrada_1", log="DTCO")
        rholog = obj._OF.findobject(well="Entrada_1", log="RHOB")
        if not dtlog or not rholog:
            print 'Example.core.doinput: One of logs data is None'
            return None
        dtdata = dtlog.data
        rhodata = rholog.data
        return dict(dtdata=dtdata, rhodata=rhodata, parentuid=parentuid, plugin=obj)
    except Exception as e:
        print e.args
        raise


def dojob(**kwargs):
    try:
        if not kwargs:
            return None    
        parentuid = kwargs.get('parentuid', None)
        dtdata = kwargs.get('dtdata', None)
        rhodata = kwargs.get('rhodata', None)
        if not parentuid or not dtdata or not rhodata:
            return None
        ipdata = rhodata/dtdata*3.048E8
        return dict(ipdata=ipdata, parentuid=parentuid,plugin=kwargs.get('plugin'))
    except Exception as e:
        print e.args
        raise
        
    
def dooutput(**kwargs):
    try:
        obj=kwargs.get('plugin')
        parentuid = kwargs.get('parentuid')
        ipdata = kwargs.get('ipdata')
        ip = obj._OM.new('log', ipdata, name="IP", unit="")
        obj._OM.add(ip, parentuid=parentuid)
        return True
    except Exception as e:
        print e.args
        raise
        
    