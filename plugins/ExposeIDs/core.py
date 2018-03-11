# -*- coding: utf-8 -*-

def doinput(*args, **kwargs):
    print 'Running doinput'
    try:
        obj = args[0]
        if not obj:
            return None
        return dict(plugin=obj)    
    except Exception as e:
        print e.args
        raise


def dojob(**kwargs):
    print 'Running dojob'
    obj = kwargs.get('plugin')
    for well in obj._OM.list('well'):
        print '{} -> {}'.format(well.attributes.get('name'), well.uid)
        for log in obj._OM.list('log', well.uid):
            print '\t{} -> {}'.format(log.attributes.get('name'), log.uid)
    print
    return None   # Because it is returning None dooutput will not be called


def dooutput(**kwargs):
    print 'Running dooutput'
    return None
