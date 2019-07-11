import wx

from classes.ui import UIManager
from .toplevel import  TopLevelController, TopLevel
from app.app_utils import GripyIcon


class FrameController(TopLevelController):
    tid = 'frame_controller'
         
    def __init__(self, **state):  
        super().__init__(**state)


class Frame(TopLevel, wx.Frame):
    tid = 'frame'

    def __init__(self, controller_uid):
        TopLevel.__init__(self, controller_uid)
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        #
        parent_uid = UIM._getparentuid(self._controller_uid)
        parent_obj = UIM.get(parent_uid)
        if not parent_obj:
            wx_parent = None
        else:
            wx_parent = parent_obj.view
        #
        wx.Frame.__init__(self, wx_parent, wx.ID_ANY, controller.title,
            pos=controller.pos, size=controller.size, 
            style=controller.style              
        ) 
        if controller.icon:   
            self.icon = GripyIcon(controller.icon, wx.BITMAP_TYPE_ICO)        
            self.SetIcon(self.icon)     
        if controller.maximized:
            self.Maximize()               
        # TODO: Bind para a super class???    
        self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)       
        self.Bind(wx.EVT_SIZE, self.on_size)    
        self.Bind(wx.EVT_MOVE, self.on_move)    
        self.Bind(wx.EVT_CLOSE, self.on_close)  
        

    def on_close(self, event):
        print ('\n\nFrame on_close')
#        event.Skip()
#        self._call_self_remove()
        self._auto_removal()
        wx.CallAfter(self.Destroy)
        


