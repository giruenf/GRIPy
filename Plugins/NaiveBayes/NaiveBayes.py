# -*- coding: utf-8 -*-

from Plugins import FCPlugin
from Plugins.NaiveBayes import core
from OM.Manager import ObjectManager


class NaiveBayesPlugin(FCPlugin):

    def __init__(self):
        super(NaiveBayesPlugin, self).__init__()
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
    
    
NaiveBayesPlugin.reloadcore()
