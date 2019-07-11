import wx
import wx.dataview as dv


class TextChoiceRenderer(dv.DataViewCustomRenderer):
 
    def __init__(self, size=wx.Size(100, 20)):
        dv.DataViewCustomRenderer.__init__(self, 
                                           mode=dv.DATAVIEW_CELL_EDITABLE
        )
        self._value = None
        self._size = size
  
    def GetValue(self):
        return self._value 
        
    def SetValue(self, value):
        self._value = value
        return True
        
    def GetSize(self):
        return self._size
        
    def Render(self, rect, dc, state):
        self.RenderText(str(self._value), 0, rect, dc, state)
        return True

    def StartEditing(self, item, rect):
        self.item = item 
        super().StartEditing(item, rect)
        return True
         
    def CreateEditorCtrl(self, parent, rect, value):
        msg = 'CreateEditorCtrl need to be implemented by child Class.'
        raise NotImplemented(msg)
        
    def GetValueFromEditorCtrl(self, editor):
        msg = 'GetValueFromEditorCtrl need to be implemented by child Class.'
        raise NotImplemented(msg)