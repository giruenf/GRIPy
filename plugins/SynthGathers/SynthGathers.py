from OM.Manager import ObjectManager
from Plugins import SimpleDialogPlugin


class SynthGathers(SimpleDialogPlugin):

    def __init__(self):
        super(SynthGathers, self).__init__()
        #OM = ObjectManager()

    def run(self, uiparent):
        print 'uiparent:', uiparent