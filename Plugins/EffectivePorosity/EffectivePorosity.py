# -*- coding: utf-8 -*-

from Plugins import DefaultPlugin
from Plugins.EffectivePorosity import core
from Plugins.Tools.ObjectFinder import ObjectFinder
from OM.Manager import ObjectManager

class EffectivePorosityPlugin(DefaultPlugin):

    def __init__(self):
        super(EffectivePorosityPlugin, self).__init__()
        self._OM = ObjectManager(self)
        self._OF = ObjectFinder()
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
    
    
EffectivePorosityPlugin.reloadcore()
