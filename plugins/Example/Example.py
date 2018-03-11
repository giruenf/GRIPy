# -*- coding: utf-8 -*-
from Plugins import DefaultPlugin
from Plugins.Example import core
from OM.Manager import ObjectManager
from OM.Finder import ObjectFinder

class ExamplePlugin(DefaultPlugin):

    def __init__(self):
        super(ExamplePlugin, self).__init__()
        #self._parent_menu = 'Precondicionamento'
        self._OM = ObjectManager(self)
        self._OF = ObjectFinder()
        self.register_module(core)
    
    def run(self):
        try:
            input_ = self.doinput(self)
            if input_:
                job = self.dojob(**input_)
                if job:
                    self.dooutput(**job)
        except Exception as e:
            print e.args


