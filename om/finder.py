# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager

class ObjectFinder(object):

    def __init__(self):
        self._OM = ObjectManager(self)
    
    def findobject(self, **kwargs):
        currentuid = None
        for tid, name in kwargs.items():
            found = False
            objs = self._OM.list(tid, currentuid)
            for obj in objs:
                if obj.name == name:
                    currentuid = obj.uid
                    found = True
                    break
            if not found:
                return None        
        obj = self._OM.get(currentuid)        
        return obj

    def finddata(self, **kwargs):
        obj = self.findobject(**kwargs)        
        if obj is None:
            return None        
        return obj.data