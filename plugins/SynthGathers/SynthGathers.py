from OM.Manager import ObjectManager
from Plugins import SimpleDialogPlugin


class SynthGathers(SimpleDialogPlugin):

    def __init__(self):
        super(SynthGathers, self).__init__()
        #self._OM = ObjectManager(self)

    def run(self, uiparent):
        print 'uiparent:', uiparent