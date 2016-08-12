# -*- coding: utf-8 -*-

from Plugins import FCPlugin
from Plugins.EMaximization import core
from OM.Manager import ObjectManager

class EMaximizationPlugin(FCPlugin):

    def __init__(self):
        super(EMaximizationPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self.input = {}
        self.output = {}

    @classmethod
    def reloadcore(cls):
        reload(core)
        setattr(cls, 'doinput', core.doinput)
        setattr(cls, 'dojob', core.dojob)
        setattr(cls, 'dooutput', core.dooutput)
    
    def run(self):
        output = self.dojob(**self.input)
        if output:
            self.output = output
        else:
            self.output = {}
    
    
EMaximizationPlugin.reloadcore()
