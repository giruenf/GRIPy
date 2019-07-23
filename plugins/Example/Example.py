from Plugins import DefaultPlugin
from classes.om import ObjectManager


class ExamplePlugin(DefaultPlugin):

    def __init__(self):
        super().__init__()
        #self.register_module(core)
    
    def run(self):
        try:
            input_ = self.doinput(self)
            if input_:
                job = self.dojob(**input_)
                if job:
                    self.dooutput(**job)
        except Exception as e:
            print(e)


