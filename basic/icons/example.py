import wx
from wx.lib.embeddedimage import PyEmbeddedImage

plane = PyEmbeddedImage(
    "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")

class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.SetIcon(plane.GetIcon())
        self.panel = wx.Panel(self)
        self.Show()

app = wx.App(False)
win = MainWindow(None)
app.MainLoop()