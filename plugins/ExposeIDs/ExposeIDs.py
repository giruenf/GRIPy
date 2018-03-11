# -*- coding: utf-8 -*-

from Plugins import DefaultPlugin
from Plugins.ExposeIDs import core
from OM.Manager import ObjectManager


class ExposeIDsPlugin(DefaultPlugin):

    def __init__(self):
        super(ExposeIDsPlugin, self).__init__()
        #self._parent_menu = 'Precondicionamento'
        self._OM = ObjectManager(self)
        self.register_module(core)

    """
    def run(self):
        self.reload_all_modules()
        output = self.dojob(**self.input)
        if output:
            self.output = output
        else:
            self.output = {}
    """
        
    def run(self):
        self.reload_all_modules()
        try:
            input_ = self.doinput(self)
            if input_:
                job = self.dojob(**input_)
                if job:
                    self.dooutput(**job)
        except Exception as e:
            print e.args
