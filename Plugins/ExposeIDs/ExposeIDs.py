# -*- coding: utf-8 -*-

from Plugins import DefaultPlugin
from Plugins.ExposeIDs import core
from OM.Manager import ObjectManager

class ExposeIDsPlugin(DefaultPlugin):

    def __init__(self):
        super(ExposeIDsPlugin, self).__init__()
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

ExposeIDsPlugin.reloadcore()
